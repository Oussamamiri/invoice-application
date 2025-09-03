from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.HomeView.as_view(), name='home'),
    path('add-customer', views.AddCustomerView.as_view(), name='add-customer'),
    path('add-invoice', views.AddInvoiceView.as_view(), name='add-invoice'),
    path('view-invoice/<int:pk>', views.InvoiceVisualizationView.as_view(), name='view-invoice'),
    path('invoice-pdf/<int:pk>', views.get_invoice_pdf, name="invoice-pdf"),
    # Form Filling Agent URLs
    path('form-agent', views.FormAgentView.as_view(), name='form-agent'),
    path('api/get-form-data', views.get_form_data, name='get-form-data'),
    path('api/create-sample-data', views.create_sample_data, name='create-sample-data'),
]