from django.urls import path
from .views import PopulateView, GenerateReportView, ShowReportView

urlpatterns = [
    path('populate', PopulateView.as_view()),
    path('trigger_report', GenerateReportView.as_view()),
    path('get_report/<str:report_id>', ShowReportView.as_view())
]