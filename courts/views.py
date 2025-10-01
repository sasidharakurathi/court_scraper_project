from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import Count, Q
from .models import QueryLog

import time
import json

from .scraper import HighCourtScraper, HighCourtCauseListScraper
from .utils import *
from datetime import datetime

SCRAPER_STORE = {}

# ================================================== VIEWS ===================================================

def home(request):
    # highcourt_scraper.navigate_to_case_status()
    # print(': ',os.getcwd())
    return render(request, "home.html")

def high_court_scraper_view(request):
    return render(request, "high_court.html")

def district_court_scraper_view(request):
    return render(request, "district_court.html")

def query_logs_view(request):
    # Get the 10 most recent logs for the table
    recent_logs = QueryLog.objects.order_by('-requested_at')[:10]

    # 1. EFFICIENT OVERALL STATS (No change needed here)
    overall_stats_data = QueryLog.objects.aggregate(
        total=Count('id'),
        successful=Count('id', filter=Q(status='Success'))
    )
    total_queries = overall_stats_data.get('total', 0)
    successful_queries = overall_stats_data.get('successful', 0)
    failed_queries = total_queries - successful_queries
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 100

    # 2. STATS BY QUERY TYPE (No change to the query itself)
    stats_by_type = list(QueryLog.objects.values('query_type')
        .annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(status='Success'))
        )
        .order_by('-total')
    )
    
    # --- THIS IS THE FIX ---
    # Create a mapping from the choices to avoid hitting the database in a loop
    display_name_map = dict(QueryLog.QUERY_TYPE_CHOICES)

    # Post-process to add more details
    for item in stats_by_type:
        item['failed'] = item['total'] - item['successful']
        item['success_rate'] = (item['successful'] / item['total'] * 100) if item['total'] > 0 else 100
        # Use the dictionary lookup (very fast) instead of a DB query
        item['display_name'] = display_name_map.get(item['query_type'], item['query_type'])

    # Get most searched states (this query is fine)
    top_states = (
        QueryLog.objects.values('state')
        .annotate(query_count=Count('state'))
        .order_by('-query_count')[:3]
    )

    context = {
        'logs': recent_logs,
        'stats': {
            'total': total_queries,
            'successful': successful_queries,
            'failed': failed_queries,
            'success_rate': f"{success_rate:.1f}",
        },
        'stats_by_type': stats_by_type,
        'top_states': top_states,
    }
    return render(request, 'query_logs.html', context)


# ================================================== API ===================================================

@csrf_exempt
def get_high_courts(request):
    highcourt_scraper = get_high_court_case_scraper_for_session(request)
    highcourt_scraper.navigate_to_case_status()
    data = highcourt_scraper.fetch_highcourt_list()
    return JsonResponse(data , safe=False)

@csrf_exempt
def get_benches(request, highcourt_id):
    highcourt_scraper = get_high_court_case_scraper_for_session(request)
    highcourt_scraper.select_highcourt_by_id(highcourt_id)
    time.sleep(3)
    data = highcourt_scraper.fetch_bench_list()
    return JsonResponse(data, safe=False)
    

@csrf_exempt
def get_case_types(request, bench_id):
    highcourt_scraper = get_high_court_case_scraper_for_session(request)
    highcourt_scraper.select_bench_by_id(bench_id)
    time.sleep(3)
    data = highcourt_scraper.fetch_case_types()
    return JsonResponse(data, safe=False)
    

@csrf_exempt
def get_highcourt_case_captcha(request):
    highcourt_scraper = get_high_court_case_scraper_for_session(request)
    b64_image = highcourt_scraper.get_captcha_image()
    
    return JsonResponse({"image_base64" : b64_image})
    

@csrf_exempt
def fetch_case(request):
    data = json.loads(request.body.decode('utf-8'))
    # print(f"{data = }")
    
    case_type_id = data.get("caseType")
    case_number = data.get("caseNumber")
    year = data.get("year")
    captcha = data.get("captchaText")
    case_type_text = data.get("caseTypeText")
    
    highcourt_scraper = get_high_court_case_scraper_for_session(request)
    scraped_data = highcourt_scraper.fetch_case(case_type_id, case_number, year, captcha, case_type_text)
    
    if scraped_data == "Invalid Captcha":
        log_data = {
            'query_type': 'HC_CASE_DETAILS',
            'state': None,
            'district': None,
            'case_number': None,
        }

        status = 'Failed'
        
        save_query_log(log_data, status, None, "Invalid Captcha")
        
        return JsonResponse({"result": "Invalid Captcha" , "success": False})
    
    elif scraped_data == "Record Not Found":
        log_data = {
            'query_type': 'HC_CASE_DETAILS',
            'state': None,
            'district': None,
            'case_number': None,
        }

        status = 'Failed'
        
        save_query_log(log_data, status, None, "Record Not Found")
        
        return JsonResponse({"result": "Record Not Found" , "success": False})
    
    log_data = {
        'query_type': 'HC_CASE_DETAILS',
        'state': None,
        'district': None,
        'case_number': scraped_data['case_details']['Registration Number'],
    }

    status = 'Success'
    
    save_query_log(log_data, status, scraped_data, None)
    
    case = save_case_from_json(scraped_data)
    
    
    return JsonResponse(scraped_data, safe=False)

@csrf_exempt
def get_high_court_cl(request):
    highcourt_cause_scraper = get_high_court_cause_scraper_for_session(request)
    highcourt_cause_scraper.navigate_to_cause_list()
    data = highcourt_cause_scraper.fetch_highcourt_list()
    return JsonResponse(data , safe=False)
    

@csrf_exempt
def get_benches_cl(request, highcourt_id):
    highcourt_cause_scraper = get_high_court_cause_scraper_for_session(request)
    highcourt_cause_scraper.select_highcourt_by_id(highcourt_id)
    time.sleep(3)
    data = highcourt_cause_scraper.fetch_bench_list()
    return JsonResponse(data, safe=False)

@csrf_exempt
def select_bench_cl(request, bench_id):
    highcourt_cause_scraper = get_high_court_cause_scraper_for_session(request)
    highcourt_cause_scraper.select_bench_by_id(bench_id)
    return JsonResponse({"result": True}, safe=False)
    
@csrf_exempt
def get_highcourt_cause_captcha(request):
    highcourt_cause_scraper = get_high_court_cause_scraper_for_session(request)
    b64_image = highcourt_cause_scraper.get_captcha_image()
    
    return JsonResponse({"image_base64" : b64_image})

@csrf_exempt
def fetch_cause_lists(request):
    data = json.loads(request.body.decode('utf-8'))
    print(f"{data = }")
    
    high_court = data.get("highCourt")                  # '1'
    cause_bench = data.get("causeBench")                # '1'
    cause_date = data.get("causeDate")                  # '2025-10-02'
    cause_captcha = data.get("causeCaptchaText")        # 'n5guw4'
    
    cause_date_ddmmyyyy = datetime.strptime(cause_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    
    highcourt_cause_scraper = get_high_court_cause_scraper_for_session(request)
    scraped_data = highcourt_cause_scraper.fetch_cause_lists(high_court, cause_bench, cause_date_ddmmyyyy, cause_captcha)
    
    
    if scraped_data == "Invalid Captcha":
        
        log_data = {
            'query_type': 'HC_CAUSE_LIST',
            'state': None,
            'district': None,
            'case_number': None,
        }

        status = 'Failed'
        
        save_query_log(log_data, status, None, "Invalid Captcha")
        
        return JsonResponse({"result": "Invalid Captcha", "success": False} , safe=False)
    
    elif scraped_data == "Invalid Data":
        
        log_data = {
            'query_type': 'HC_CAUSE_LIST',
            'state': None,
            'district': None,
            'case_number': None,
        }

        status = 'Failed'
        
        save_query_log(log_data, status, None, "Invalid Data")
        
        
        return JsonResponse({"result": "Invalid Data", "success": False} , safe=False)
    
    elif scraped_data == "No cause List Available for this date...!!":
        
        log_data = {
            'query_type': 'HC_CAUSE_LIST',
            'state': None,
            'district': None,
            'case_number': None,
        }

        status = 'Failed'
        
        save_query_log(log_data, status, None, "No cause List Available for this date...!!")
        
        
        return JsonResponse({"result": "No cause List Available for this date...!!", "success": False} , safe=False)
    
    log_data = {
        'query_type': 'HC_CAUSE_LIST',
        'state': None,
        'district': None,
        'case_number': None,
    }

    status = 'Success'
    
    save_query_log(log_data, status, scraped_data, None)
    
    
    cause_list = save_cause_list_from_json(scraped_data, cause_date)
    return JsonResponse(scraped_data, safe=False)
    
    
# ================================================ UTILITY ===================================================


def get_high_court_case_scraper_for_session(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    key = (session_key, "case")
    scraper = SCRAPER_STORE.get(key)
    if not scraper:
        scraper = HighCourtScraper()
        # scraper.navigate_to_case_status()
        SCRAPER_STORE[key] = scraper
    # scraper.navigate_to_case_status()

    return scraper

def get_high_court_cause_scraper_for_session(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    key = (session_key, "cause")
    scraper = SCRAPER_STORE.get(key)
    if not scraper:
        scraper = HighCourtCauseListScraper()
        # scraper.navigate_to_cause_list()
        SCRAPER_STORE[key] = scraper
    # scraper.navigate_to_cause_list()

    return scraper