from django.contrib import admin
from .models import Applicant, ApplicationResult

# Customizing the Applicant Admin
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'date_of_birth', 'phone', 'caste_category', 'aadhar_number')
    search_fields = ('user__username', 'name', 'phone', 'aadhar_number')
    list_filter = ('caste_category', 'university', 'course', 'year_of_passing')
    ordering = ('-id',)

    # Display documents and file paths in the admin panel
    fields = ('user', 'name', 'date_of_birth', 'phone', 'address', 'caste_category', 'aadhar_number', 
              'aadhaar_document', 'ews_certificate_document', 'caste_certificate_document', 'income_certificate_document', 
              'marksheet_document', 'university', 'course', 'year_of_passing', 'percentage', 
               )


# Customizing the ApplicationResult Admin
class ApplicationResultAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ('applicant', 'application_date',  'mismatch_plot_path','document_type')

    # Add filtering options
    list_filter = ('application_date', 'mismatch_percentage')

    # Add search capability for applicant names
    search_fields = ('applicant__name',)

    # Make fields editable directly from the list view
   # list_editable = ('mismatch_plot_path')

    # Show a more detailed view for each result
    fields=('applicant','application_date','document_type',
            'extracted_data','expected_json','mismatches','mismatch_percentage','mismatch_plot_path',
            
            )

    # Optionally, make certain fields read-only
    readonly_fields = ('application_date',)

    # Limit the number of results displayed per page
    list_per_page = 20
    


# Register the models with the admin interface
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(ApplicationResult, ApplicationResultAdmin)
