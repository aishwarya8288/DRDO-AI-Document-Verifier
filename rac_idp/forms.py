from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Applicant

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']


class ApplicantForm(forms.ModelForm):
    CASTE_CHOICES = [
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('EWS', 'EWS'),
    ]
    
    caste_category = forms.ChoiceField(choices=CASTE_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    
    # Common Details
    state = forms.CharField(max_length=100, required=False)
    district = forms.CharField(max_length=100, required=False)
    tehsil_taluka = forms.CharField(max_length=100, required=False)
    pincode = forms.CharField(max_length=10, required=False)

    # ---------------------- EWS Certificate Fields ----------------------
    ews_certificate_number = forms.CharField(max_length=50, required=False)
    ews_issuing_authority = forms.CharField(max_length=100, required=False)
    ews_date_of_issue = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    ews_family_income = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    ews_family_assets = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows': 2}))
    ews_certificate_document = forms.FileField(required=False)

    # ---------------------- Caste Certificate Fields ----------------------
    caste_certificate_number = forms.CharField(max_length=50, required=False)
    caste_issuing_authority = forms.CharField(max_length=100, required=False)
    caste_date_of_issue = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    caste_validity_period = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    caste_certificate_document = forms.FileField(required=False)

    # ---------------------- Income Certificate Fields ----------------------
    income_certificate_number = forms.CharField(max_length=50, required=False)
    income_issuing_authority = forms.CharField(max_length=100, required=False)
    income_date_of_issue = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    income_validity_period = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    annual_family_income = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    income_certificate_document = forms.FileField(required=False)

    # ---------------------- Other Documents ----------------------
    aadhaar_document = forms.FileField(required=False)
    marksheet_document = forms.FileField(required=False)
    experience_certificate = forms.FileField(required=False)

    class Meta:
        model = Applicant
        fields = [
            'name', 'name_devnagiri','date_of_birth', 'phone', 'address', 'caste_category', 'aadhar_number',
            'state', 'district', 'tehsil_taluka', 'pincode', 'university','course','year_of_passing','percentage',
            
            # EWS Certificate Fields
            'ews_certificate_number', 'ews_issuing_authority', 'ews_date_of_issue', 'ews_validity_period',
            'ews_certificate_document',
        
            # Caste Certificate Fields
            'caste_certificate_number', 'caste_issuing_authority', 'caste_date_of_issue', 'caste_validity_period',
            'caste_certificate_document',
            
            # Income Certificate Fields
            'income_certificate_number', 'income_issuing_authority', 'income_date_of_issue', 'income_validity_period',
            'annual_family_income', 'income_certificate_document',

            # Other Information
            'aadhaar_document', 'marksheet_document', 'university', 'course', 'year_of_passing', 'percentage',
            
        ]

    def __init__(self, *args, **kwargs):
         super(ApplicantForm, self).__init__(*args, **kwargs)
         for field in self.fields.values():
             field.widget.attrs['class'] = 'form-control'
     
         # Add a class instead of using inline styles
         hidden_fields = [
             # EWS Fields
             'ews_certificate_number', 'ews_issuing_authority', 'ews_date_of_issue', 'ews_validity_period',
             'ews_family_income', 'ews_family_assets', 'ews_certificate_document',
     
             # Caste Fields
             'caste_certificate_number', 'caste_issuing_authority', 'caste_date_of_issue', 'caste_validity_period',
             'caste_certificate_document',
     
             # Income Fields
             'income_certificate_number', 'income_issuing_authority', 'income_date_of_issue', 'income_validity_period',
             'annual_family_income', 'income_certificate_document'
         ]
     
         for field in hidden_fields:
             self.fields[field].widget.attrs['class'] += ' hidden-field' 

   
