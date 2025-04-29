from django.db import models
from django.contrib.auth.models import User
from googletrans import Translator
from datetime import timedelta

def translate_name_to_marathi(name):
    try:
        translator = Translator()
        result = translator.translate(name, src='en', dest='mr')
        return result.text
    except Exception as e:
        print(f"[Translation Error] {e}")
        return name  # fallback to original name if translation fails

class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    name_devnagiri = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    caste_category = models.CharField(max_length=10, null=True, blank=True)
    aadhar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)

    # Location Details
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    tehsil_taluka = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    # EWS Certificate
    ews_certificate_number = models.CharField(max_length=50, null=True, blank=True)
    ews_issuing_authority = models.CharField(max_length=100, null=True, blank=True)
    ews_date_of_issue = models.DateField(null=True, blank=True)
    ews_validity_period = models.DateField(null=True, blank=True)
    ews_family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ews_family_assets = models.TextField(null=True, blank=True)
    ews_certificate_document = models.FileField(upload_to="documents/ews/", null=True, blank=True)

    # Caste Certificate
    caste_certificate_number = models.CharField(max_length=50, null=True, blank=True)
    caste_issuing_authority = models.CharField(max_length=100, null=True, blank=True)
    caste_date_of_issue = models.DateField(null=True, blank=True)
    caste_validity_period = models.DateField(null=True, blank=True)
    caste_certificate_document = models.FileField(upload_to="documents/caste/", null=True, blank=True)

    # Income Certificate
    income_certificate_number = models.CharField(max_length=50, null=True, blank=True)
    income_issuing_authority = models.CharField(max_length=100, null=True, blank=True)
    income_date_of_issue = models.DateField(null=True, blank=True)
    income_validity_period = models.DateField(null=True, blank=True)
    annual_family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    income_certificate_document = models.FileField(upload_to="documents/income/", null=True, blank=True)

    # Academic Info
    university = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    year_of_passing = models.IntegerField(null=True)
    percentage = models.FloatField(null=True, blank=True)
    marksheet_document = models.FileField(upload_to="documents/marksheet/", null=True, blank=True)

    # Aadhaar
    aadhaar_document = models.FileField(upload_to="documents/aadhaar/", null=True, blank=True)

    def save(self, *args, **kwargs):
         # Translate name to Marathi if set
         if self.name:
             self.name_devnagiri = translate_name_to_marathi(self.name)
     
         # Auto-set EWS validity period
         if self.ews_date_of_issue and not self.ews_validity_period:
             self.ews_validity_period = self.ews_date_of_issue + timedelta(days=365)
     
         super().save(*args, **kwargs)


class ApplicationResult(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('aadhaar', 'Aadhaar'),
        ('marksheet', 'Marksheet'),
        ('ews', 'EWS Certificate'),
        ('income', 'Income Certificate'),
        ('caste', 'Caste Certificate'),
    ]
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    extracted_data = models.JSONField(null=True, blank=True)
    expected_json = models.JSONField(null=True, blank=True)
    mismatches = models.JSONField(null=True, blank=True)
    mismatch_percentage = models.FloatField(null=True, blank=True)
    mismatch_plot_path = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.applicant.name} - {self.get_document_type_display()} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"