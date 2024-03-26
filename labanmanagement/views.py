from django.urls import reverse
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from labanmanagement.models import *
from datetime import date, timedelta


#?###########################################################
#?###########################################################
#!######################### VIEWS ###########################
#!#####################START FROM HERE#######################
#?###########################################################
#?###########################################################

def handle404Notfound(request, exception):
    return render(request, '404.html', status=404)

class DashboardData:
    def __init__(self, request):
        self.request = request
        self.today = date.today()
        self.yesterday = self.today - timedelta(days = 1)

    def get_pending_bulk_orders(self):
        one_day_before = self.today + timedelta(days=1)
        pending_orders = BulkOrder.objects.filter(
            date_of_delivery=one_day_before,
            delivered=False,
        )
        reminder_messages = []
        for order in pending_orders:
            reminder_message = f"Don't forget! Order for <a href='{reverse('bulkorder')}'>{order.name_of_client}</a> is scheduled for delivery tomorrow."
            reminder_messages.append(reminder_message)
        messages.info(self.request, reminder_messages)

    def get_total_milk_data(self):
        dailyMilkObjects = DailyTotalMilk.objects
        total_milk_today = dailyMilkObjects.filter(date=self.today).values_list('total_milk', flat=True).aggregate(sum=models.Sum('total_milk'))['sum'] or 0
        sold_milk_today = dailyMilkObjects.filter(date=self.today).values_list('sold_milk', flat=True).aggregate(sum=models.Sum('sold_milk'))['sum'] or 0
        unsold = dailyMilkObjects.filter(date=self.today).values_list('remaining_milk', flat=True).aggregate(sum=models.Sum('remaining_milk'))['sum'] or 0
        prev_day = dailyMilkObjects.filter(date=self.yesterday).values().first()

        if not prev_day:
            percentage_prev_day_total_milk = 0
            percentage_prev_day_sold_milk = 0
        else:
            prev_day_sold_milk = prev_day['sold_milk'] or 0
            prev_day_total_milk = prev_day['total_milk'] or 0

            if prev_day_sold_milk == 0 or prev_day_total_milk == 0:
                percentage_prev_day_total_milk = 0
                percentage_prev_day_sold_milk = 0
            else:
                percentage_prev_day_total_milk = round(((total_milk_today - prev_day_total_milk) / prev_day_total_milk) * 100, 2)
                percentage_prev_day_sold_milk = round(((sold_milk_today - prev_day_sold_milk) / prev_day_sold_milk) * 100, 2)

        return total_milk_today, sold_milk_today, unsold, percentage_prev_day_total_milk, percentage_prev_day_sold_milk
    def get_customer_data(self):
        pay_as_you_go_quantity = PayAsYouGoCustomer.objects.filter(date=self.today).aggregate(total_qty=models.Sum('qty'))["total_qty"]
        subscription_sold_quantity = HandleCustomer.objects.filter(date=self.today).aggregate(total_qty=models.Sum('qty'))['total_qty']
        customers = Customer.objects.all().count()
        pay_as_you_go_customers = PayAsYouGoCustomer.objects.filter(date=self.today).count()
        pending_payment_customers = Customer.objects.all().filter(balance__gt = 0).count()
        pending_payment_payasyougo = PayAsYouGoCustomer.objects.filter(balance__gt=0).count()
        pending_bulk_order_payment = BulkOrder.objects.all().filter(balance__gt=0).count()
        pending_payments = pending_payment_customers + pending_payment_payasyougo + pending_bulk_order_payment

        return pay_as_you_go_quantity, subscription_sold_quantity, customers, pay_as_you_go_customers, pending_payments

    def get_balance_data(self):
        balanceCustomer = Customer.objects.all().filter(balance__gt=0).aggregate(total_sum=models.Sum('balance'))['total_sum'] or 0
        balancePayAsYouGo = PayAsYouGoCustomer.objects.all().filter(balance__gt=0).aggregate(total_sum=models.Sum('balance'))['total_sum'] or 0
        balanceBulkOrder = BulkOrder.objects.all().filter(balance__gt=0).aggregate(total_sum=models.Sum('balance'))['total_sum'] or 0
        balance = balancePayAsYouGo + balanceCustomer + balanceBulkOrder
        return balance

    def get_revenue_and_expenditure_data(self):
        revenue = Revenue.objects.filter(date=self.today).values_list('revenue', flat=True).aggregate(sum=models.Sum('revenue'))['sum'] or 0
        expenditure = Expenditure.objects.filter(date=self.today).values('amount').aggregate(sum=models.Sum('amount'))['sum'] or 0
        return revenue, expenditure

    def get_cow_data(self):
        cowTagsQuerySet = Cow.objects.order_by('tag_id').values('tag_id')
        milkPerCowTodayQuerySet = MilkProduction.objects.order_by('cow__tag_id').filter(date=self.today).values('cow__tag_id', 'total_milk') or None
        milkPerCowYesterdayQuerySet = MilkProduction.objects.order_by('cow__tag_id').filter(date=self.yesterday).values('cow__tag_id', 'total_milk') or None
        return cowTagsQuerySet, milkPerCowTodayQuerySet, milkPerCowYesterdayQuerySet

    def get_dashboard_context(self):
        self.get_pending_bulk_orders()
        total_milk_today, sold_milk_today, unsold, percentage_prev_day_total_milk, percentage_prev_day_sold_milk = self.get_total_milk_data()
        pay_as_you_go_quantity, subscription_sold_quantity, customers, pay_as_you_go_customers, pending_payments = self.get_customer_data()
        balance = self.get_balance_data()
        revenue, expenditure = self.get_revenue_and_expenditure_data()
        cow_data = self.get_cow_data()

        context = {
            "total": total_milk_today,
            "sold": sold_milk_today,
            "unsold": unsold,
            "percentage_total_milk": percentage_prev_day_total_milk,
            "percentage_sold_milk": percentage_prev_day_sold_milk,
            "subcription": subscription_sold_quantity,
            "payasyougoqty": pay_as_you_go_quantity,
            "customers": customers,
            "payasyougocustomers": pay_as_you_go_customers,
            "pendingpayments": pending_payments,
            "balance": balance,
            "revenue": revenue,
            "expenditure": expenditure,
            "cow_data": {
                "tagId": cow_data[0],
                "todayMilkPerCow": cow_data[1],
                "yesterdayMilkPerCow": cow_data[2]
            }
        }
        return context



@login_required(login_url='/login')
def dashboard(request):
    dashboard_data = DashboardData(request)
    context = dashboard_data.get_dashboard_context()
    return render(request, 'dashboard.html', context)


def customers(request):
    customers_data_query = Customer.objects.values().order_by('-start_date')
    context = {
        "customer":customers_data_query
    }
    return render(request, 'customer.html', context)


def pay_as_you_go(request):
    customers = PayAsYouGoCustomer.objects.values().order_by('-date')
    context = {
        'customer':customers
    }
    return render(request, 'payasyougo.html', context)

def handlelogin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(
            request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(
                request, "Welcome {username}".format(username=username))
            return redirect('dashboard')
        else:
            messages.error(
                request, "You are not authorised, please check your credentials and try again later")
            return redirect('login')
    else:
        return render(request, 'login.html')

@login_required(login_url='/login')
def handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('login')


def cows(request):
    allCows = Cow.objects.all().values('id','tag_id', 'nickname', 'date_of_arrival', 'offspring', 'breed', 'remarks').order_by('id')
    context = {
        'cows':allCows
    }
    return render(request, "cows.html", context)

def handleOffspring(request, slug):
    calves = Calf.objects.filter(dam__id=slug)
    context = {
        'calf':calves
    } 
    return render(request, "handleOffspring.html", context)

def calves(request):
    calves = Calf.objects.all().values('tag_id', 'nickname', 'dob', 'dam', 'father','breed', 'remarks', 'id', 'dam__id').order_by('tag_id')
    context = {
        "calf":calves
    }
    return render(request, "calves.html", context)


def milkProductionDaily(request):
    milk_production = DailyTotalMilk.objects.all().order_by('-date').values()
    context = {"totalmilk":milk_production}
    return render(request, "milkproductiondaily.html", context)


def revenue(request):
    revenue = Revenue.objects.all().order_by("-date")
    context = {"revenue":revenue}
    return render(request, "revenue.html", context)


def expenditure(request):
    expenditure = Expenditure.objects.all().order_by("-date")
    context = {"expenditure":expenditure}
    return render(request, "expenditure.html", context)


def handlecows(request, slug):
    milk_record_count = MilkProduction.objects.filter(cow__id=slug).count()
    medication_record = Medication.objects.filter(cows__id=slug).count()
    birth_events = BirthEvent.objects.filter(dam_id=slug).count()
    dry_periods = DryPeriod.objects.filter(cow__id=slug).count()
    heat_periods = HeatPeriod.objects.filter(cow__id=slug).count()
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    if cow_name:
        tag = cow_name+f" ({cow_tag})"
    else:
        tag = cow_tag
    context = {
        "slug":slug,
        "tag": tag,
        "milk_record_count": milk_record_count,
        "medication_record_count": medication_record,
        "birth_event_count":birth_events,
        "dry_period_count":dry_periods,
        "heat_period_count":heat_periods
    }
    return render(request, "handlecows.html", context)


def handleCustomerAccounts(request, slug):
    customer = HandleCustomer.objects.filter(account__id=slug).values('qty', 'rate', 'amount', 'balance', 'remarks','paid','date').order_by('-date')
    end_date_of_customer = Customer.objects.filter(id=slug).values('end_date')[0]['end_date'] 
    name = Customer.objects.filter(id=slug).values('name')[0]['name'].capitalize()
    customer_data = [
        {
            'rate': item['rate'],
            'qty': item['qty'],
            'amount': item['amount'],
            'balance': item['balance'],
            'remarks': item['remarks'],
            'paid': item['paid'],
            'date':item['date'],
        }
        for item in customer
    ]
    context = {
        'name':name,
        'customer': customer_data,
        'end_date': end_date_of_customer
    }
    return render(request, 'handleCustomerAccounts.html', context)


def medicationCow(request, slug):
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    medication_record = Medication.objects.filter(cows__id=slug).order_by('-date').values("date", 'Diagnosis', 'Medication', 'doctor', 'remarks')
    if cow_name:
        tag = cow_name+f" ({cow_tag})"
    else:
        tag = cow_tag
    context = {
        "slug":slug,
        "tag":tag,
        "medication":medication_record
    }
    return render(request, "cowmedication.html", context)

def milkRecordCow(request, slug):
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    milk_record = MilkProduction.objects.filter(cow_id=slug).order_by('-date').values()
    if cow_name:
        tag = cow_name+f" ({cow_tag})"
    else:
        tag = cow_tag
    context = {
        "slug":slug,
        "tag":tag,
        "milk":milk_record
    }
    return render(request, 'cowmilk.html', context)

def birthEventCow(request, slug):
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    birthEvent = BirthEvent.objects.filter(dam_id=slug).order_by('-date').values()
    if cow_name:
        tag = cow_name+f" ({cow_tag})"
    else:
        tag = cow_tag
    context = {
        "slug":slug,
        "tag":tag,
        "birthevents": birthEvent
    }
    return render(request, 'cowBirthevent.html', context)


def heatPeriodsCow(request, slug):
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    heat_period = HeatPeriod.objects.filter(cow_id=slug).order_by('-start_date').values()
    if cow_name:
        tag = cow_name+f" ({cow_tag})"
    else:
        tag = cow_tag
    context = {
        "slug":slug,
        "tag":tag,
        "heat_period":heat_period
    }
    return render(request, 'heatperiodcow.html', context)

def dryPeriodsCow(request, slug):
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    dry_period = DryPeriod.objects.filter(cow_id=slug).order_by('-start_date').values()
    if cow_name:
        tag = cow_name+f" ({cow_tag})"
    else:
        tag = cow_tag
    context = {
        "slug":slug,
        "tag":tag,
        "dryperiod":dry_period
    }
    return render(request, 'dryperiodcow.html', context)

def bulkorder(request):
    one_day_before = today + timedelta(days=1)
    pending_orders = BulkOrder.objects.filter(
        date_of_delivery=one_day_before,
        delivered=False,
    )
    for order in pending_orders:

        reminder_message = f"Don't forget! Order for <a href='{reverse('bulkorder')}'>{order.name_of_client}</a> is scheduled for delivery tomorrow."
        messages.info(request, reminder_message)

    orders = BulkOrder.objects.all().values().order_by('-date_of_delivery')
    context = {'bulkorder':orders}
    return render(request, 'bulkorder.html', context)