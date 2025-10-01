from django.db import models

class Case(models.Model):
    cnr_number = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="CNR Number")

    # one-to-one related objects for case_details, case_status, category_details, petitioner/respondent
    petitioner = models.TextField(verbose_name="Petitioner and Advocate")
    respondent = models.TextField(verbose_name="Respondent and Advocate")

    def __str__(self):
        return self.cnr_number


class CaseDetails(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="details")
    filing_number = models.CharField(max_length=255)
    filing_date = models.DateField()
    registration_number = models.CharField(max_length=255)
    registration_date = models.DateField()

    def __str__(self):
        return f"Details for {self.case.cnr_number}"


class CaseStatus(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="status")
    first_hearing_date = models.DateField(null=True, blank=True)
    next_hearing_date = models.DateField(null=True, blank=True)
    stage_of_case = models.CharField(max_length=255, blank=True, null=True)
    court_number_and_judge = models.CharField(max_length=255, blank=True, null=True)
    bench_type = models.CharField(max_length=100, blank=True, null=True)
    judicial_branch = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    not_before_me = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Status for {self.case.cnr_number}"


class CategoryDetails(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="category_details")
    category = models.CharField(max_length=512, blank=True, null=True)
    sub_category = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return f"Category for {self.case.cnr_number}"


class CaseHistory(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="history")
    cause_list_type = models.CharField(max_length=100, blank=True, null=True)
    judge = models.CharField(max_length=255, blank=True, null=True)
    business_on_date = models.DateField(null=True, blank=True)
    hearing_date = models.DateField(null=True, blank=True)
    purpose_of_hearing = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"History for {self.case.cnr_number} on {self.hearing_date}"


class Order(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=50)
    order_on = models.CharField(max_length=255)
    judge = models.CharField(max_length=255)
    order_date = models.DateField()
    pdf_url = models.URLField(max_length=1024)

    def __str__(self):
        return f"Order {self.order_number} for {self.case.cnr_number}"


class IADetail(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="ia_details")
    ia_number = models.CharField(max_length=255)
    party = models.CharField(max_length=255, blank=True, null=True)
    date_of_filing = models.CharField(max_length=50)
    next_date = models.CharField(max_length=50)
    ia_status = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.ia_number} for {self.case.cnr_number}"
