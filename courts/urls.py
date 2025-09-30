from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("high-court/", views.high_court_scraper_view, name="high_court"),
    path("district-court/", views.district_court_scraper_view, name="district_court"),
    path("query-logs/", views.query_logs, name="query_logs"),
    
    
    path("api/highcourts/", views.get_high_courts, name="get_high_courts"),
    path("api/benches/<int:highcourt_id>/", views.get_benches, name="get_benches"),
    path("api/casetypes/<int:bench_id>/", views.get_case_types, name="get_case_types"),
    path("api/captcha/", views.get_captcha, name="get_captcha"),
    path("api/fetch-case/", views.fetch_case, name="fetch_case"),
]
