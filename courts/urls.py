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
    path("api/highcourt/case/captcha/", views.get_highcourt_case_captcha, name="get_highcourt_case_captcha"),
    path("api/fetch-case/", views.fetch_case, name="fetch_case"),
    
    # High Court Cause List URLs
    path("api/highcourts/causelist/", views.get_high_court_cl, name="get_high_courts_cl"),
    path("api/benches/causelist/<int:highcourt_id>/", views.get_benches_cl, name="get_benches_cl"),
    path("api/select-bench/<int:bench_id>/", views.select_bench_cl, name="select_bench_cl"),
    path("api/highcourt/cause/captcha/", views.get_highcourt_cause_captcha, name="get_highcourt_cause_captcha"),
    path("api/fetch-causelist/", views.fetch_cause_lists, name="fetch_cause_lists"),
    
]
