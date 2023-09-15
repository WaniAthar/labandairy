from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from labanmanagement.models import *





#?###########################################################
#?###########################################################
#!######################### VIEWS ###########################
#!#####################START FROM HERE#######################
#?###########################################################
#?###########################################################

# TODO: when customer table is updated, daily total milk record doesnt get updated

@login_required(login_url='/login')
def dashboard(request):
    dailyMilkObjects = DailyTotalMilk.objects
    total_milk_today = dailyMilkObjects.last().total_milk
    sold_milk_today = dailyMilkObjects.last().sold_milk
    unsold = dailyMilkObjects.last().remaining_milk
    prev_day = (dailyMilkObjects.all().order_by("-date").exclude(id=dailyMilkObjects.last().id).first().total_milk)
    percentage_prev_day = ((total_milk_today - prev_day)/prev_day) * 100
    context = {
        "total": total_milk_today,
        "sold" : sold_milk_today,
        "unsold" : unsold,
        "percentage" : percentage_prev_day,
    }
    print(percentage_prev_day)
    return render(request,'dashboard.html', context)

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
        user = authenticate(request=request,username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, "Welcome {username}".format(username=username))
            return redirect('dashboard')
        else:
            messages.error(request, "You are not authorised, please check your credentials and try again later")
            return redirect('login')
    else:
        return render(request, 'login.html') 

def handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('login')

def cows(request):
    return render(request,"cows.html")

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

