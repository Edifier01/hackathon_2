from django.contrib import admin
from .models import Competition, Application, Result


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'category')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'competition', 'status', 'created_at')
    list_filter = ('status', 'competition')
    search_fields = ('full_name', 'email', 'school')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('application', 'score', 'place', 'published')
    list_filter = ('published',)
