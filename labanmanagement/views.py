from itertools import zip_longest
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from labanmanagement.models import *
from datetime import date, timedelta
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery

# ///TODO: Make pages for the navigations
# ///!BUG: FIX the alignment of the cards in dashboard.html
# ///!BUG: When customer table is updated, daily total milk record doesnt get updated
# TODO: Test the website
# ///TODO: Add filter to the charts
# ///!BUG: Milk sold record not updating automatically
# TODO: Automatic Backup of Database everyday
# TODO: Downloadable data in excel



#?###########################################################
#?###########################################################
#!######################### VIEWS ###########################
#!#####################START FROM HERE#######################
#?###########################################################
#?###########################################################

today = date.today()
yesterday = today - timedelta(days = 1)

def handle404Notfound(request, exception):
    return render(request, '404.html', status=404)

@login_required(login_url='/login')
def dashboard(request):
    print(today)
    dailyMilkObjects = DailyTotalMilk.objects
    total_milk_today = dailyMilkObjects.filter(date=today).values_list('total_milk', flat=True).aggregate(sum=models.Sum('total_milk'))['sum'] or 0
    sold_milk_today =dailyMilkObjects.filter(date=today).values_list('sold_milk', flat=True).aggregate(sum=models.Sum('sold_milk'))['sum'] or 0
    unsold = dailyMilkObjects.filter(date=today).values_list('remaining_milk', flat=True).aggregate(sum=models.Sum('remaining_milk'))['sum'] or 0   
    prev_day = (dailyMilkObjects.all().order_by(
        "-date").exclude(id=dailyMilkObjects.last().id).first().total_milk) if dailyMilkObjects.exists() else 0   
    if prev_day == 0:
        percentage_prev_day = 0
    else:
        percentage_prev_day = round(((total_milk_today - prev_day)/prev_day) * 100, 2)
    pay_as_you_go_quantity = PayAsYouGoCustomer.objects.filter(
        date=today).aggregate(total_qty=models.Sum('qty'))["total_qty"]
    subscription_sold_quantity = HandleCustomer.objects.filter(
        date=today).aggregate(total_qty=models.Sum('qty'))['total_qty']
    customers = Customer.objects.all().count()
    pay_as_you_go_customers = PayAsYouGoCustomer.objects.filter(
        date=today).count()
    pending_payment_customers = Customer.objects.filter(
        handlecustomer__balance__gt=0).count()
    pending_payment_payasyougo = PayAsYouGoCustomer.objects.filter(
        balance__gt=0).count()
    pending_payments = pending_payment_customers + pending_payment_payasyougo

    '''
    The below code is as good as executing this SQL query 
    
    SELECT max(id), account_id, balance, date
    FROM labanmanagement_handlecustomer 
    group by account_id;

    '''
    latest_ids = HandleCustomer.objects.filter(account=OuterRef('account')).values('account').annotate(
    latest_id=models.Max('id')).values('latest_id')

    latest_records = HandleCustomer.objects.filter(id__in=Subquery(latest_ids))

    balanceCustomer = latest_records.values('id', 'account__id', 'balance', 'date').aggregate(balance=models.Sum('balance'))['balance'] or 0
    balancePayAsYouGo = PayAsYouGoCustomer.objects.all().aggregate(total_sum = models.Sum('balance'))['total_sum'] or 0
    balance = balancePayAsYouGo + balanceCustomer

    revenue= Revenue.objects.filter(date=today).values_list('revenue', flat=True).aggregate(sum=models.Sum('revenue'))['sum'] or 0
    expenditure = Expenditure.objects.filter(date=today).values('amount').aggregate(sum=models.Sum('amount'))['sum'] or 0

    cowTagsQuerySet = Cow.objects.order_by('tag_id').values('tag_id')
    milkPerCowTodayQuerySet = MilkProduction.objects.order_by('cow__tag_id').filter(date=today).values('cow__tag_id','total_milk')
    milkPerCowYesterdayQuerySet = MilkProduction.objects.order_by('cow__tag_id').filter(date=yesterday).values('cow__tag_id','total_milk')
    cowTagId = [i['tag_id'] for i in cowTagsQuerySet]
    todayMilkPerCow = [i['total_milk'] for i in milkPerCowTodayQuerySet]
    yesterdayMilkPerCow = [i['total_milk'] for i in milkPerCowYesterdayQuerySet]  
    
    today_milk_dict = {tag_id: milk for tag_id, milk in zip(cowTagId, todayMilkPerCow)}
    yesterday_milk_dict = {tag_id: milk for tag_id, milk in zip(cowTagId, yesterdayMilkPerCow)}

    all_cow_tags = set(cow['tag_id'] for cow in cowTagsQuerySet)

    # Initialize empty lists to store milk data
    todayMilkPerCow = []
    yesterdayMilkPerCow = []

    # Create dictionaries to store milk data for quick lookup
    today_data_dict = {data['cow__tag_id']: data['total_milk'] for data in milkPerCowTodayQuerySet}
    yesterday_data_dict = {data['cow__tag_id']: data['total_milk'] for data in milkPerCowYesterdayQuerySet}

    # Iterate through all cow tags
    for tag_id in all_cow_tags:
        # Get milk data for today and yesterday (or set to 0 if missing)
        today_milk = today_data_dict.get(tag_id, 0)
        yesterday_milk = yesterday_data_dict.get(tag_id, 0)
        
        todayMilkPerCow.append(today_milk)
        yesterdayMilkPerCow.append(yesterday_milk)

    context = {
    "total": total_milk_today,
    "sold": sold_milk_today,
    "unsold": unsold,
    "percentage": percentage_prev_day,
    "subcription": subscription_sold_quantity,
    "payasyougoqty": pay_as_you_go_quantity,
    "customers": customers,
    "payasyougocustomers": pay_as_you_go_customers,
    "pendingpayments": pending_payments,
    "balance":balance,
    "revenue":revenue,
    "expenditure":expenditure,
    "cow_data":{
        "tagId":cowTagId,
        "todayMilkPerCow":todayMilkPerCow,
        "yesterdayMilkPerCow":yesterdayMilkPerCow
    }
    }
    return render(request, 'dashboard.html', context)


def customers(request):
    customers_data_query = Customer.objects.values('id', 'name', 'phone_no', 'qty', 'rate', 'start_date', 'end_date')
    context = {
        "customer":customers_data_query
    }
    # print(customers_data)
    return render(request, 'customer.html', context)


def pay_as_you_go(request):
    customers = PayAsYouGoCustomer.objects.values('name', 'amount', 'qty', 'rate', 'paid', 'balance', 'remarks', 'date')
    context = {
        'customer':customers
    }
    return render(request, 'payasyougo.html', context)


def extras(request):
    return render(request, "tables.html")


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
    allCows = Cow.objects.all().values('id','tag_id', 'nickname', 'date_of_arrival', 'offspring', 'breed', 'remarks')
    print(allCows)
   
    context = {
        'cows':allCows
    }
    return render(request, "cows.html", context)

def handleOffspring(request, slug):
    calves = Calf.objects.filter(mother__id=slug)
    print(calves)
    context = {
        'calf':calves
    } 
    return render(request, "handleOffspring.html", context)

def calves(request):
    calves = Calf.objects.all().values('tag_id', 'nickname', 'dob', 'mother', 'father','breed', 'remarks', 'id', 'mother__id')
    print(calves)
    context = {
        "calf":calves
    }
    return render(request, "calves.html", context)


def milkProductionCow(request):
    return HttpResponse("{'hello':'hello'}")


def milkProductionDaily(request):
    milk_production = DailyTotalMilk.objects.order_by("-date").all()
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
    birth_events = BirthEvent.objects.filter(mother_id=slug).count()
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
    customer = HandleCustomer.objects.filter(account__id=slug).values('qty', 'rate', 'amount', 'balance', 'remarks','paid','date').order_by('-date')  #!++++++out of order date (unsorted)+++++++
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
    print([i['date'] for i in customer_data])
    context = {
        'name':name,
        'customer': customer_data,
        'end_date': end_date_of_customer
    }
    return render(request, 'handleCustomerAccounts.html', context)


def milkrecord(request, slug):
    return HttpResponse('milk record page')


def medication(request):
    return HttpResponse('this is the medication page')

def medicationCow(request, slug):
    cow_tag = Cow.objects.filter(id=slug).values('tag_id')[0]['tag_id']
    cow_name = Cow.objects.filter(id=slug).values('nickname')[0]['nickname']
    medication_record = Medication.objects.filter(cows__id=slug).order_by('-date').values("date", 'Diagnosis', 'Medication', 'doctor', 'remarks')
    print(medication_record)
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
    milk_record = MilkProduction.objects.filter(cow_id=slug).order_by('-date').values()    #fetching all values
    print(milk_record)
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
    birthEvent = BirthEvent.objects.filter(mother_id=slug).order_by('-date').values()
    print(birthEvent)
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
    print(heat_period)
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