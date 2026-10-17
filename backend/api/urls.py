from django.urls import path
from .views import AnalyzeView, HistoryView, DashboardStatsView

urlpatterns = [
    path('analyze/', AnalyzeView.as_view(), name='analyze'),
    path('history/', HistoryView.as_view(), name='history'),
    path('stats/', DashboardStatsView.as_view(), name='stats'),
]
