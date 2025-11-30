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


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

from .models import Application



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


import io
from datetime import date

from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

from .models import Application


@login_required
def download_certificate(request, pk):
    """
    Генерация красивого PDF-сертификата для заявки pk.
    """
    application = get_object_or_404(Application, pk=pk)

    # Нельзя скачивать чужой сертификат (кроме staff)
    if application.user != request.user and not request.user.is_staff:
        return HttpResponse("У вас нет доступа к этому сертификату", status=403)

    # Проверяем, что есть опубликованный результат
    if not hasattr(application, "result") or not application.result.published:
        return HttpResponse("Результат ещё не опубликован", status=400)

    result = application.result
    competition = application.competition

    # ---- ШРИФТЫ ----
    font_dir = settings.BASE_DIR / "fonts"
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(font_dir / "DejaVuSans-Bold.ttf")))

    # ---- ЛИСТ ----
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 20 * mm
    inner_margin = 28 * mm

    primary_color = HexColor("#9f1239")
    border_light = HexColor("#e5e7eb")
    text_color = HexColor("#111827")

    # Внешняя рамка
    p.setStrokeColor(primary_color)
    p.setLineWidth(4)
    p.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # Внутренняя рамка
    p.setStrokeColor(border_light)
    p.setLineWidth(1.5)
    p.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin)

    # Заголовок
    title_y = height - 70 * mm
    p.setFillColor(text_color)
    p.setFont("DejaVuSans-Bold", 32)
    p.drawCentredString(width / 2, title_y, "СЕРТИФИКАТ")

    p.setFont("DejaVuSans", 16)
    p.setFillColor(primary_color)
    p.drawCentredString(width / 2, title_y - 12 * mm, "участника образовательного конкурса")

    # Основной текст
    p.setFillColor(text_color)
    text_y = title_y - 30 * mm
    line_step = 9 * mm

    p.setFont("DejaVuSans", 14)
    p.drawCentredString(width / 2, text_y, "Настоящим подтверждается, что")
    text_y -= line_step

    participant_name = (
        application.full_name
        or application.user.get_full_name()
        or application.user.username
    )
    p.setFont("DejaVuSans-Bold", 20)
    p.drawCentredString(width / 2, text_y, participant_name)
    text_y -= line_step

    # Линия под ФИО
    p.setStrokeColor(border_light)
    p.setLineWidth(0.8)
    p.line(width / 2 - 60 * mm, text_y + 4 * mm, width / 2 + 60 * mm, text_y + 4 * mm)
    text_y -= line_step * 0.4

    # Информация о конкурсе
    p.setFont("DejaVuSans", 13)
    p.setFillColor(text_color)
    p.drawCentredString(
        width / 2,
        text_y,
        f"принял(а) участие в конкурсе «{competition.title}».",
    )
    text_y -= line_step

    place_text = f"место: {result.place}" if result.place else "место: участие"
    score_text = f"баллы: {result.score}" if result.score is not None else ""
    info_line = place_text + (f", {score_text}" if score_text else "")
    p.drawCentredString(width / 2, text_y, info_line)
    text_y -= line_step

    if application.school:
        p.setFont("DejaVuSans", 12)
        p.setFillColor(HexColor("#4b5563"))
        p.drawCentredString(width / 2, text_y, f"Учреждение: {application.school}")
        text_y -= line_step

    # ---- НИЖНИЙ БЛОК: ОРГАНИЗАТОР, ФИО, ПОДПИСЬ, ДАТА ----
    footer_y = inner_margin + 25 * mm
    left_x = inner_margin + 10 * mm

    p.setFont("DejaVuSans", 12)
    p.setFillColor(text_color)

    # Организатор + ФИО
    p.drawString(left_x, footer_y + 18 * mm, "Организатор:")

    fio_line_start = left_x + 35 * mm
    fio_line_end = fio_line_start + 60 * mm
    p.setStrokeColor(border_light)
    p.setLineWidth(0.8)
    p.line(fio_line_start, footer_y + 18.5 * mm, fio_line_end, footer_y + 18.5 * mm)

    p.setFont("DejaVuSans", 10)
    p.setFillColor(HexColor("#6b7280"))
    
    p.setFont("DejaVuSans", 12)
    p.setFillColor(text_color)
    p.drawString(left_x, footer_y + 6 * mm, "Подпись:")
    sign_line_start = left_x + 30 * mm
    sign_line_end = sign_line_start + 50 * mm
    p.setStrokeColor(border_light)
    p.setLineWidth(0.8)
    p.line(sign_line_start, footer_y + 6.5 * mm, sign_line_end, footer_y + 6.5 * mm)

    p.setFont("DejaVuSans", 10)
    p.setFillColor(HexColor("#6b7280"))

    # Дата
    cert_date = competition.end_date or date.today()
    try:
        date_str = cert_date.strftime("%d.%m.%Y")
    except Exception:
        date_str = str(cert_date)

    p.setFont("DejaVuSans", 11)
    p.setFillColor(text_color)
    p.drawRightString(
        width - inner_margin - 10 * mm,
        footer_y + 12 * mm,
        f"Дата: {date_str}",
    )

    # Завершение
    p.showPage()
    p.save()

    buffer.seek(0)
    filename = f"certificate_{application.pk}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)

