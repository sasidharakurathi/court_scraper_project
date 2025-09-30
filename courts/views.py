from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import time
import json
import os
# from .models import QueryLog, Case

from .scraper import HighCourtScraper
highcourt_scraper = HighCourtScraper(url="https://hcservices.ecourts.gov.in/hcservices/main.php")

def home(request):
    # highcourt_scraper.navigate_to_case_status()
    # print(': ',os.getcwd())
    return render(request, "home.html")

def high_court_scraper_view(request):
    return render(request, "high_court.html")

def district_court_scraper_view(request):
    return render(request, "district_court.html")

def query_logs(request):
    # logs = QueryLog.objects.all().order_by("-requested_at")[:50]
    # stats = {
    #     "total_queries": QueryLog.objects.count(),
    #     "cases_found": Case.objects.count(),
    # }
    # return render(request, "query_logs.html", {"logs": logs, "stats": stats})
    pass


# ================================================== API ===================================================

@csrf_exempt
def get_high_courts(request):
    highcourt_scraper.navigate_to_case_status()
    data = highcourt_scraper.fetch_highcourt_list()
    return JsonResponse(data , safe=False)

@csrf_exempt
def get_benches(request, highcourt_id):
    highcourt_scraper.select_highcourt_by_id(highcourt_id)
    time.sleep(3)
    data = highcourt_scraper.fetch_bench_list()
    return JsonResponse(data, safe=False)
    

@csrf_exempt
def get_case_types(request, bench_id):
    highcourt_scraper.select_bench_by_id(bench_id)
    time.sleep(3)
    data = highcourt_scraper.fetch_case_types()
    return JsonResponse(data, safe=False)
    

@csrf_exempt
def get_captcha(request):
    b64_image = highcourt_scraper.get_captcha_image()
    
    return JsonResponse({"image_base64" : b64_image})
    

@csrf_exempt
def fetch_case(request):
    data = json.loads(request.body.decode('utf-8'))
    print(f"{data = }")
    
    case_type_id = data.get("caseType")
    case_number = data.get("caseNumber")
    year = data.get("year")
    captcha = data.get("captchaText")
    case_type_text = data.get("caseTypeText")
    
    
    data = highcourt_scraper.fetch_case(case_type_id, case_number, year, captcha, case_type_text)
    return JsonResponse(data, safe=False)
    