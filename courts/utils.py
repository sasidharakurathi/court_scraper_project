from .models import (
    Case, CaseDetails, CaseStatus, CategoryDetails,
    CaseHistory, Order, IADetail
)
from datetime import datetime

def parse_date(date_str):
    """Helper: parse DD-MM-YYYY or '15th July 2024' etc."""
    if not date_str or date_str.strip() in ["--", ""]:
        return None
    
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # handle formats like "15th July 2024"
    try:
        clean_str = (
            date_str.replace("st", "")
                    .replace("nd", "")
                    .replace("rd", "")
                    .replace("th", "")
        )
        return datetime.strptime(clean_str.strip(), "%d %B %Y").date()
    except Exception:
        return None


def save_case_from_json(data: dict):
    """
    Save the entire JSON structure into the database models.
    """

    # ================= CASE ROOT =================
    cnr_number = data["case_details"]["CNR Number"]
    case, _ = Case.objects.get_or_create(
        cnr_number=cnr_number,
        defaults={
            "petitioner": data.get("petitioner", ""),
            "respondent": data.get("respondent", ""),
        },
    )

    # update petitioner/respondent in case they change
    case.petitioner = data.get("petitioner", "")
    case.respondent = data.get("respondent", "")
    case.save()

    # ================= CASE DETAILS =================
    cd = data["case_details"]
    CaseDetails.objects.update_or_create(
        case=case,
        defaults={
            "filing_number": cd.get("Filing Number"),
            "filing_date": parse_date(cd.get("Filing Date")),
            "registration_number": cd.get("Registration Number"),
            "registration_date": parse_date(cd.get("Registration Date")),
        },
    )

    # ================= CASE STATUS =================
    cs = data.get("case_status", {})
    CaseStatus.objects.update_or_create(
        case=case,
        defaults={
            "first_hearing_date": parse_date(cs.get("First Hearing Date")),
            "next_hearing_date": parse_date(cs.get("Next Hearing Date")),
            "stage_of_case": cs.get("Stage of Case", ""),
            "court_number_and_judge": cs.get("Court Number and Judge", ""),
            "bench_type": cs.get("Bench Type", ""),
            "judicial_branch": cs.get("Judicial Branch", ""),
            "state": cs.get("State", ""),
            "district": cs.get("District", ""),
            "not_before_me": cs.get("Not Before Me", ""),
        },
    )

    # ================= CATEGORY DETAILS =================
    cat = data.get("category_details", {})
    if cat:
        CategoryDetails.objects.update_or_create(
            case=case,
            defaults={
                "category": cat.get("Category", ""),
                "sub_category": cat.get("Sub Category", ""),
            },
        )

    # ================= CASE HISTORY =================
    CaseHistory.objects.filter(case=case).delete()
    for hist in data.get("case_history", []):
        CaseHistory.objects.create(
            case=case,
            cause_list_type=hist.get("Cause List Type", ""),
            judge=hist.get("Judge", ""),
            business_on_date=parse_date(hist.get("Business On Date")),
            hearing_date=parse_date(hist.get("Hearing Date")),
            purpose_of_hearing=hist.get("Purpose of hearing", ""),
        )

    # ================= ORDERS =================
    Order.objects.filter(case=case).delete()
    for order in data.get("orders", []):
        Order.objects.create(
            case=case,
            order_number=order.get("Order Number", ""),
            order_on=order.get("Order on", ""),
            judge=order.get("Judge", ""),
            order_date=parse_date(order.get("Order Date")),
            pdf_url=order.get("PDF URL", ""),
        )

    # ================= IA DETAILS =================
    IADetail.objects.filter(case=case).delete()
    for ia in data.get("ia_details", []):
        IADetail.objects.create(
            case=case,
            ia_number=ia.get("IA Number", ""),
            party=ia.get("Party", ""),
            date_of_filing=ia.get("Date of Filing", ""),
            next_date=ia.get("Next Date", ""),
            ia_status=ia.get("IA Status", ""),
        )

    return case
