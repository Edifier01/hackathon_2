from django.urls import path
from . import views

app_name = 'competitions'

urlpatterns = [
    path('', views.CompetitionListView.as_view(), name='competition_list'),
    path('competition/<int:pk>/', views.CompetitionDetailView.as_view(), name='competition_detail'),
    path('competition/<int:pk>/apply/', views.application_create, name='application_create'),
    path('competition/<int:pk>/results/', views.CompetitionResultsView.as_view(), name='competition_results'),
    path('certificate/<int:pk>/', views.download_certificate, name='download_certificate'),
]
