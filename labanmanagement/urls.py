from django.urls import path
from labanmanagement import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('customers', views.customers, name='customers'),
    path('customers/<str:slug>', views.handleCustomerAccounts, name='handleCustomerAccounts'),
    path("payasyoubuy", views.pay_as_you_buy, name="payAsYouBuy"),
    path('extras', views.extras, name='extras'),
    path('login', views.handlelogin, name='login'),
    path('logout', views.handlelogout, name='logout'),
    path('milkProductionCow', views.milkProductionCow, name='milkProductionCow'),
    path('milkProductionDaily', views.milkProductionDaily, name='milkProductionDaily'),
    path("cows", views.cows, name="cows"),
    path("calves", views.calves, name="calves"),
    path("cows/<str:slug>", views.handlecows, name="handlecows"),
    path('cows/<str:slug>/milk', views.milkrecord, name='milk'),
    path('cows/<str:slug>/medication', views.medication, name='medication'),
    path('revenue', views.revenue, name="revenue"),
    path('expenditure', views.expenditure, name="expenditure"),
]
