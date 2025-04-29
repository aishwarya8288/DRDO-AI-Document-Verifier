from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import *
from .models import *
import os
import json
from .utils import *
import requests
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail,EmailMessage



def landing_page(request):
    return render(request, "landing.html")

def features_page(request):
    return render(request, 'features.html')

def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_content = request.POST.get('message')

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_content}"

        # Email sent "from" the user to you (your default email)
        email_message = EmailMessage(
            subject=f"New Contact Form Submission from {name}",
            body=full_message,
            from_email=email,  # This will appear as sender
            to=[settings.DEFAULT_FROM_EMAIL],
            reply_to=[email],  # Ensures reply goes to user
        )

        try:
            email_message.send()
            messages.success(request, "Thanks for contacting us! We'll get back to you soon.")
            return redirect('contact')
        except Exception as e:
            messages.error(request, "Oops! Something went wrong. Please try again later.")

    return render(request, 'contact.html')


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Create an Applicant record for the user after successful signup
            Applicant.objects.create(user=user)  # Automatically create the applicant profile
            return redirect('login')  # Redirect to applicant dashboard after signup
        else:
            print(form.errors)
    else:
        
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('applicant_dashboard')  # Redirect to applicant dashboard after login
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out.")
    return redirect('landing')

@login_required
def applicant_dashboard(request):
    # Fetch the applicant profile for the logged-in user
    applicant = get_object_or_404(Applicant, user=request.user)

    # Check if the applicant has already submitted an application
    has_applied = ApplicationResult.objects.filter(applicant=applicant).exists()

    # Fetch past application results if available
    past_results = ApplicationResult.objects.filter(applicant=applicant).order_by('-timestamp')

    return render(request, "dashboard.html", {
        "has_applied": has_applied,
        "past_results": past_results
    })
# View to handle document submission and analysis
@login_required
def submit_application(request):
    user = request.user  # Logged-in user

    try:
        # Try to fetch the existing applicant for the user
        applicant = Applicant.objects.get(user=user)
    except Applicant.DoesNotExist:
        applicant = None  # If not found, set to None

    if request.method == 'POST':
        if applicant:
            applicant_form = ApplicantForm(request.POST, request.FILES, instance=applicant)  # Update existing applicant
        else:
            applicant_form = ApplicantForm(request.POST, request.FILES)  # Create new applicant
        
        if applicant_form.is_valid():
            applicant = applicant_form.save(commit=False)
            applicant.user = user  # Assign the logged-in user
            applicant.save()
            
            return redirect('verify_document', applicant_id=applicant.id)  # Redirect after successful submission
        else:
            print(applicant_form.errors)  # Debugging

    else:
        applicant_form = ApplicantForm(instance=applicant)  # Load form with existing data if any

    return render(request, 'submit_application.html', {'form': applicant_form})


@login_required
def view_result(request, result_id):
    # Fetch application result or return 404
    result = get_object_or_404(ApplicationResult, id=result_id, applicant__user=request.user)

    # Parse mismatches JSON string into a Python dictionary
    mismatches_data = json.loads(result.mismatches)

    return render(request, "view_results.html", {
        "result": result,
        "mismatches": mismatches_data.get("mismatches", {}),
        "similarities": mismatches_data.get("similarities", {}),
        "missing_fields": mismatches_data.get("missing_fields", []),
        "extra_fields": mismatches_data.get("extra_fields", []),
        "mismatch_plot_path": result.mismatch_plot_path  # Pass this to the template
    })





@login_required
def verify_document(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)



    if request.method == "POST":
        document_type = request.POST.get("document_type")  # Get document type selected by user

        # Define mapping of document types to model fields
        document_fields = {
            "aadhaar": "aadhaar_document",
            "marksheet": "marksheet_document",
            "ews": "ews_certificate_document",
            "income": "income_certificate_document",
            "caste": "caste_certificate_document",
        }


        
        # Get document field name from mapping
        document_field = document_fields.get(document_type)
       
        if not document_field:
            messages.error(request, "Invalid document type selected.")
            return redirect("verify_document", applicant_id=applicant.id)

        # Get the actual document file from the Applicant model
        document_file = getattr(applicant, document_field, None)

        if not document_file:
            messages.error(request, f"{document_type.capitalize()} document not found.")
            return redirect("verify_document", applicant_id=applicant.id)

        document_path = document_file.path

        if not os.path.exists(document_path):
            print(f"❌ {document_type.capitalize()} document file not found: {document_path}")
            return redirect("error")  # Redirect to an error page or handle as necessary

        try:
            # Extract text from document
            extracted_text = process_document(document_path)

            if not extracted_text or not extracted_text.strip():
                messages.error(request, "No readable text extracted from document.")
                return redirect("verify_document", applicant_id=applicant.id)

            # Prepare expected data based on document type
            expected_data = {}

            if document_type == "aadhaar":
                expected_data = {
                    "name": applicant.name,
                    "date_of_birth": applicant.date_of_birth.strftime("%Y-%m-%d") if applicant.date_of_birth else None,
                    "address": applicant.address,
                    "aadhar_number": applicant.aadhar_number,
                    "phone": applicant.phone,
                }
            elif document_type == "marksheet":
                expected_data = {
                    "name": applicant.name,
                    "date_of_birth": applicant.date_of_birth.strftime("%Y-%m-%d") if applicant.date_of_birth else None,
                    "university": applicant.university,
                    "course": applicant.course,
                    "year_of_passing": applicant.year_of_passing,
                    "percentage": applicant.percentage,
                }
            elif document_type == "ews":
                expected_data = {
                    "name": applicant.name_devnagiri,
                    "ews_certificate_number": applicant.ews_certificate_number,
                    "ews_issuing_authority": applicant.ews_issuing_authority,
                    "ews_date_of_issue": applicant.ews_date_of_issue.strftime("%Y-%m-%d") if applicant.ews_date_of_issue else None,
                    "ews_validity_period": applicant.ews_validity_period.strftime("%Y-%m-%d") if applicant.ews_validity_period else None,
                    
                    
                }
            elif document_type == "income":
                expected_data = {
                    "name": applicant.name_devnagiri,
                    "income_certificate_number": applicant.income_certificate_number,
                    "income_issuing_authority": applicant.income_issuing_authority,
                    "income_date_of_issue": applicant.income_date_of_issue.strftime("%Y-%m-%d") if applicant.income_date_of_issue else None,
                    "income_validity_period": applicant.income_validity_period.strftime("%Y-%m-%d") if applicant.income_validity_period else None,
                    "annual_family_income": str(applicant.annual_family_income) if applicant.annual_family_income else None,
                }
            elif document_type == "caste":
                expected_data = {
                    "name": applicant.name,
                    "caste_certificate_number": applicant.caste_certificate_number,
                    "caste_issuing_authority": applicant.caste_issuing_authority,
                    "caste_date_of_issue": applicant.caste_date_of_issue.strftime("%Y-%m-%d") if applicant.caste_date_of_issue else None,
                    "caste_validity_perdefiod": applicant.caste_validity_period.strftime("%Y-%m-%d") if applicant.caste_validity_period else None,
                    "caste": applicant.caste_category,
                }

            # Send extracted text & expected data to Gemini API for validation
            gemini_response = send_to_gemini(extracted_text, expected_data)

            if not gemini_response or "error" in gemini_response:
                messages.error(request, "Error validating document with AI.")
                return redirect("verify_document", applicant_id=applicant.id)

            # Process and save extracted data
            extracted_fields = {str(k): v for k, v in gemini_response.items()}  # Ensure JSON serializability

            # Validate extracted data against expected data
            validation_result = validate_gemini_response(expected_data, extracted_fields)

            # Calculate overall mismatch percentage
            total_mismatches = sum(mismatch["Mismatch %"] for mismatch in validation_result["mismatches"].values())
            num_fields = len(expected_data)
            overall_mismatch_percentage = round(total_mismatches / num_fields, 2) if num_fields else 0
            

            # Save ApplicationResult with mismatches
            application_result = ApplicationResult.objects.create(
                applicant=applicant,
                document_type=document_type,
                extracted_data=json.dumps(extracted_fields, indent=2),
                expected_json=json.dumps(expected_data, indent=2),
                mismatches=json.dumps(validation_result, indent=2),
                mismatch_percentage=overall_mismatch_percentage,
            )
            application_result.save()

            # Generate mismatch visualization if mismatches exist
            if validation_result.get("mismatches") or validation_result.get("missing_fields"):
                visualize_mismatches(validation_result, applicant.id)

            messages.success(request, f"{document_type.capitalize()} document verified successfully!")
            return redirect("applicant_results", applicant_id=applicant.id)

        except Exception as e:
            print(f"❌ Error processing document: {e}")
            messages.error(request, "Error processing document.")
            return redirect("verify_document", applicant_id=applicant.id)

    return render(request, "verify_documents.html", {"applicant": applicant})


@login_required
def applicant_results(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id, user=request.user)

    application_result = ApplicationResult.objects.filter(applicant_id=applicant_id).order_by('-timestamp').first()

    if not application_result:
        messages.info(request, "No verification results found for this applicant.")
        return render(request, "results.html", {
            "applicant": applicant,
            "application_results": [],
            "mismatch_plot_path": None,
        })

    extracted_data = json.loads(application_result.extracted_data) if application_result.extracted_data else {}
    expected_data = json.loads(application_result.expected_json) if application_result.expected_json else {}
    mismatches = json.loads(application_result.mismatches) if application_result.mismatches else {}

    formatted_mismatches = []
    for field, details in mismatches.get("mismatches", {}).items():
        formatted_mismatches.append({
            "field": field,
            "expected": details.get("Expected", ""),
            "extracted": details.get("Extracted", ""),
            "mismatch_percentage": details.get("Mismatch %", 0),
        })

    mismatch_plot_url = None
    if mismatches:
        mismatch_plot_path = visualize_mismatches(mismatches, applicant.id)
        if mismatch_plot_path:
            mismatch_plot_url = settings.MEDIA_URL + os.path.basename(mismatch_plot_path)
            application_result.mismatch_plot_path = mismatch_plot_url
            application_result.save()

    return render(request, "results.html", {
        "applicant": applicant,
        "application_results": [application_result],  # Use list to keep template logic simple
        "formatted_mismatches": formatted_mismatches,
        "mismatch_plot_path": mismatch_plot_url,
    })
