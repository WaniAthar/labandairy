from django.contrib import admin
from .models import *
from django.forms import TextInput, Textarea
from django.db import models


class HandleCustomerAdmin(admin.ModelAdmin):
    list_display = ['account', 'rate', 'amount',
                    'qty', 'paid', 'balance', 'remarks', 'date']
    search_fields = ['account__name','account', 'rate', 'amount',
                    'qty', 'paid', 'balance', 'remarks', 'date']  # Allow searching by Customer name
    formfield_overrides = {
        models.IntegerField: {'widget': TextInput(attrs={'size': '100'})},
        models.DecimalField: {'widget': TextInput(attrs={'size': '100'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add placeholders for the fields in the form
        form.base_fields['amount'].widget.attrs['placeholder'] = 'Enter custom amount or leave empty to calculate amount automatically'
        form.base_fields['qty'].widget.attrs['placeholder'] = 'Enter custom quantity or leave empty to get the quantity from Customer Account'
        form.base_fields['paid'].widget.attrs['placeholder'] = 'Enter paid amount'
        form.base_fields['rate'].widget.attrs['placeholder'] = 'Enter custom rate or leave empty to get the fixed rate from Customer Account'
        form.base_fields['balance'].widget.attrs['placeholder'] = 'Enter custom balance or leave empty to calculate the balance automatically'
        form.base_fields['remarks'].widget.attrs['placeholder'] = 'Enter remarks'
        form.base_fields['date'].widget.attrs['placeholder'] = 'Enter date'
        return form


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_no', 'qty',
                    'rate', 'start_date', 'end_date']
    search_fields = ['name', 'phone_no', 'qty',
                     'rate', 'start_date', 'end_date']


class CowAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'nickname',
                    'date_of_arrival', 'breed', 'remarks']
    search_fields = ['tag_id', 'nickname',
                     'date_of_arrival', 'breed', 'remarks']


class CalfAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'nickname', 'dob',
                    'breed', 'mother', 'father', 'remarks']
    search_fields = ['tag_id', 'nickname', 'dob',
                     'breed', 'mother', 'father', 'remarks']


class MedicationAdmin(admin.ModelAdmin):
    list_display = ['date', 'Diagnosis', 'Medication', 'doctor', 'remarks']
    search_fields = ['date', 'Diagnosis', 'Medication', 'doctor', 'remmarks']


class MilkProductionAdmin(admin.ModelAdmin):
    list_display = ['cow', 'date', 'morning_milk_quantity',
                    'evening_milk_quantity', 'morning_time', 'evening_time', 'total_milk']
    search_fields = ['cow', 'date', 'morning_milk_quantity',
                     'evening_milk_quantity', 'morning_time', 'evening_time', 'total_milk']


class DailyTotalMilkAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_milk', 'sold_milk', 'remaining_milk']
    search_fields = ['date', 'total_milk', 'sold_milk', 'remaining_milk']
class PayAsYouGoAdmin(admin.ModelAdmin):
    list_display = ['name','amount','rate','qty','balance','paid', 'remarks','date']
    search_fields = ['name','amount','rate','qty','balance','paid', 'remarks','date']

class RevenueAdmin(admin.ModelAdmin):
    list_display = ['date', 'revenue']
    search_fields = ['date', 'revenue']

class ExpenditureAdmin(admin.ModelAdmin):
    list_display=['date','time', 'particulars','amount','remarks']
    search_fields=['date','time', 'particulars','amount','remarks']

admin.site.register(PayAsYouGoCustomer,PayAsYouGoAdmin)
admin.site.register(HandleCustomer, HandleCustomerAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Cow, CowAdmin)
admin.site.register(MilkProduction, MilkProductionAdmin)
admin.site.register(Medication, MedicationAdmin)
admin.site.register(DryPeriod)
admin.site.register(HeatPeriod)
admin.site.register(BirthEvent)
admin.site.register(Calf, CalfAdmin)
admin.site.register(DailyTotalMilk, DailyTotalMilkAdmin)
admin.site.register(Revenue, RevenueAdmin)
admin.site.register(Expenditure,ExpenditureAdmin)
