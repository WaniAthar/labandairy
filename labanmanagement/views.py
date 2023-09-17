from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from labanmanagement.models import *
from datetime import date
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery

# TODO: Make pages for the navigations
# ///!BUG: FIX the alignment of the cards in dashboard.html
# !BUG: When customer table is updated, daily total milk record doesnt get updated
# TODO: Test the website
# TODO: Add filter to the charts
# TODO: Automatic Backup of Database everyday
# TODO: Downloadable data in excel

#?###########################################################
#?###########################################################
#!######################### VIEWS ###########################
#!#####################START FROM HERE#######################
#?###########################################################
#?###########################################################

today = date.today()

@login_required(login_url='/login')
def dashboard(request):
    print(today)
    dailyMilkObjects = DailyTotalMilk.objects
    total_milk_today = dailyMilkObjects.filter(date=today).values_list('total_milk', flat=True).aggregate(sum=models.Sum('total_milk'))['sum'] or 0
    sold_milk_today =dailyMilkObjects.filter(date=today).values_list('sold_milk', flat=True).aggregate(sum=models.Sum('sold_milk'))['sum'] or 0
    unsold = dailyMilkObjects.filter(date=today).values_list('remaining_milk', flat=True).aggregate(sum=models.Sum('remaining_milk'))['sum'] or 0   
    prev_day = (dailyMilkObjects.all().order_by(
        "-date").exclude(id=dailyMilkObjects.last().id).first().total_milk)    #!++++++++++++++Red flag++++++++++++++++++
    percentage_prev_day = ((total_milk_today - prev_day)/prev_day) * 100
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
    
    SELECT max(id), laag_account_id, balance, date
    FROM labanmanagement_handlecustomer 
    group by laag_account_id;

    '''
    latest_ids = HandleCustomer.objects.filter(laag_account=OuterRef('laag_account')).values('laag_account').annotate(
    latest_id=models.Max('id')).values('latest_id')

    latest_records = HandleCustomer.objects.filter(id__in=Subquery(latest_ids))

    balanceCustomer = latest_records.values('id', 'laag_account__id', 'balance', 'date').aggregate(balance=models.Sum('balance'))['balance']
    balancePayAsYouGo = PayAsYouGoCustomer.objects.all().aggregate(total_sum = models.Sum('balance'))['total_sum']
    balance = balancePayAsYouGo + balanceCustomer
    revenue= Revenue.objects.filter(date=today).values_list('revenue', flat=True).aggregate(sum=models.Sum('revenue'))['sum'] or 0
    expenditure = Expenditure.objects.filter(date=today).values('amount').aggregate(sum=models.Sum('amount'))['sum'] 
    
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
    }
    return render(request, 'dashboard.html', context)


def customers(request):
    return HttpResponse('this is the customers page')


def pay_as_you_buy(request):
    return HttpResponse("hello this is a dummy text")


def extras(request):
    return render(request, "404.html")


def handlelogin(request):
    if request.method == 'POST':
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


def handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('login')


def cows(request):
    return render(request, "cows.html")


def calves(request):
    return render(request, "calves.html")


def milkProductionCow(request):
    return HttpResponse("{'hello':'hello'}")


def milkProductionDaily(request):
    return HttpResponse("{'hello':'hello'}")


def revenue(request):
    return HttpResponse("revenue")


def expenditure(request):
    return HttpResponse("expenditure")


def handlecows(request, slug):
    return HttpResponse('handle cows')


def handleLaagAccounts(request, slug):
    return HttpResponse('handle laag accounts page')


def milkrecord(request, slug):
    return HttpResponse('milk record page')


def medication(request, slug):
    return HttpResponse('this is the medication page')
