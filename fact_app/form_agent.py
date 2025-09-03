"""
Form Filling Agent Module

This module provides automated form filling capabilities for the invoice application.
It can generate sample data and automatically populate customer and invoice forms.
"""

import random
from faker import Faker
from django.contrib.auth.models import User
from .models import Customer, Invoice, Article
from django.utils import timezone


class FormFillingAgent:
    """
    Agent class that handles automated form filling for customers and invoices
    """
    
    def __init__(self):
        self.fake = Faker()
        
    def generate_customer_data(self):
        """
        Generate sample customer data for form filling
        
        Returns:
            dict: Dictionary containing customer form data
        """
        return {
            'name': self.fake.name(),
            'email': self.fake.email(),
            'phone': self.fake.phone_number()[:15],  # Limit phone length
            'address': self.fake.address().replace('\n', ', ')[:64],  # Format address
            'sex': random.choice(['M', 'F']),
            'age': random.choice(['0-15', '15-25', '25-35', '35-45', '45-55', '55+']),
            'city': self.fake.city()[:32],
            'zip_code': self.fake.zipcode()[:16]
        }
    
    def generate_invoice_data(self, customer_id=None):
        """
        Generate sample invoice data for form filling
        
        Args:
            customer_id (int, optional): ID of customer to use, if None uses random customer
            
        Returns:
            dict: Dictionary containing invoice form data
        """
        # Get available customers
        customers = Customer.objects.all()
        if not customers.exists():
            return None
            
        if customer_id:
            try:
                customer = customers.get(id=customer_id)
            except Customer.DoesNotExist:
                customer = customers.first()
        else:
            customer = random.choice(customers)
            
        # Generate article data
        num_articles = random.randint(1, 5)
        articles = []
        total_amount = 0
        
        for i in range(num_articles):
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10, 500), 2)
            article_total = quantity * unit_price
            total_amount += article_total
            
            articles.append({
                'name': f"{self.fake.catch_phrase()} {self.fake.word().title()}",
                'quantity': quantity,
                'unit_price': unit_price,
                'total': article_total
            })
        
        return {
            'customer_id': customer.id,
            'invoice_type': random.choice(['R', 'P', 'I']),
            'articles': articles,
            'total': round(total_amount, 2),
            'comments': self.fake.text(max_nb_chars=200) if random.choice([True, False]) else ''
        }
    
    def create_sample_customer(self, user):
        """
        Create a sample customer using generated data
        
        Args:
            user: Django User object for save_by field
            
        Returns:
            Customer: Created customer object
        """
        data = self.generate_customer_data()
        data['save_by'] = user
        
        return Customer.objects.create(**data)
    
    def create_sample_invoice(self, user, customer_id=None):
        """
        Create a sample invoice with articles using generated data
        
        Args:
            user: Django User object for save_by field
            customer_id (int, optional): ID of customer to use
            
        Returns:
            Invoice: Created invoice object or None if no customers exist
        """
        invoice_data = self.generate_invoice_data(customer_id)
        if not invoice_data:
            return None
            
        # Create invoice
        invoice = Invoice.objects.create(
            customer_id=invoice_data['customer_id'],
            save_by=user,
            total=invoice_data['total'],
            invoice_type=invoice_data['invoice_type'],
            comments=invoice_data['comments']
        )
        
        # Create articles
        articles = []
        for article_data in invoice_data['articles']:
            articles.append(Article(
                invoice=invoice,
                name=article_data['name'],
                quantity=article_data['quantity'],
                unit_price=article_data['unit_price'],
                total=article_data['total']
            ))
        
        Article.objects.bulk_create(articles)
        
        return invoice

    def get_form_fill_data_json(self, form_type='customer', customer_id=None):
        """
        Get form data in JSON format suitable for frontend form filling
        
        Args:
            form_type (str): 'customer' or 'invoice'
            customer_id (int, optional): For invoice forms, specific customer ID
            
        Returns:
            dict: Form data ready for JavaScript form filling
        """
        if form_type == 'customer':
            return self.generate_customer_data()
        elif form_type == 'invoice':
            return self.generate_invoice_data(customer_id)
        else:
            return {}