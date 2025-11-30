from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required

from .models import Competition, Application, Result
from .forms import ApplicationForm

from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import io

from django.http import HttpResponse, FileResponse
from django.conf import settings


class CompetitionListView(ListView):
    model = Competition
    template_name = 'competitions/competition_list.html'
    context_object_name = 'competitions'

    def get_queryset(self):
        return Competition.objects.filter(status='published').order_by('-start_date')


class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'competitions/competition_detail.html'
    context_object_name = 'competition'


class CompetitionResultsView(DetailView):
    model = Competition
    template_name = 'competitions/competition_results.html'
    context_object_name = 'competition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = Result.objects.filter(
            application__competition=self.object,
            published=True,
        ).select_related('application')
        return context


@login_required
def application_create(request, pk):
    competition = get_object_or_404(Competition, pk=pk, status='published')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.competition = competition
            application.save()
            return redirect('accounts:dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'competitions/application_form.html', {
        'competition': competition,
        'form': form,
    })






@login_required
def download_certificate(request, pk):
    
    application = get_object_or_404(Application, pk=pk)

    if application.user != request.user and not request.user.is_staff:
        return HttpResponse("У вас нет доступа к этому сертификату", status=403)

    if not hasattr(application, 'result') or not application.result.published:
        return HttpResponse("Результат ещё не опубликован", status=400)

    result = application.result
    competition = application.competition

    font_path = settings.BASE_DIR / "fonts" / "DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("DejaVuSans", 26)
    p.drawString(100, 780, "СЕРТИФИКАТ УЧАСТНИКА")

    p.setFont("DejaVuSans", 18)
    p.drawString(100, 740, f"Конкурс: {competition.title}")
    p.drawString(100, 710, f"ФИО: {application.full_name}")
    if application.school:
        p.drawString(100, 680, f"Учреждение: {application.school}")
    p.drawString(100, 650, f"Место: {result.place if result.place else '-'}")
    p.drawString(100, 620, f"Баллы: {result.score if result.score is not None else '-'}")

    p.setFont("DejaVuSans", 14)
    p.drawString(100, 580, "Благодарим за участие в образовательном конкурсе!")

    p.setFont("DejaVuSans", 12)
    p.drawString(100, 150, "Подпись организатора: ________________________")

    p.showPage()
    p.save()

    buffer.seek(0)
    filename = f"certificate_{application.pk}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)
