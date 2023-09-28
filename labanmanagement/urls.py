from django.urls import path
from labanmanagement import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('customers', views.customers, name='customers'),
    path('customers/<str:slug>', views.handleCustomerAccounts, name='handleCustomerAccounts'),
    path('payasyougo', views.pay_as_you_go, name="payAsYouGo"),
    path('extras', views.extras, name='extras'),
    path('login', views.handlelogin, name='login'),
    path('logout', views.handlelogout, name='logout'),
    path('milkProductionDaily', views.milkProductionDaily, name='milkProductionDaily'),
    path('cows', views.cows, name="cows"),
    path("calves", views.calves, name="calves"),
    path("cows/offSpring/<str:slug>", views.handleOffspring, name='offspring'),
    path("cows/<str:slug>", views.handlecows, name="handlecows"),
    path('cows/<str:slug>/milk', views.milkRecordCow, name='milkCow'),
    path('cows/<str:slug>/medication', views.medicationCow, name='medicationCow'),
    path('cows/<str:slug>/birthevents', views.birthEventCow, name='birthEventCow'),
    path('cows/<str:slug>/dryperiods', views.dryPeriodsCow, name='dryPeriodsCow'),
    path('cows/<str:slug>/heatperiods', views.heatPeriodsCow, name='heatPeriodsCow'),
    path('revenue', views.revenue, name="revenue"),
    path('expenditure', views.expenditure, name="expenditure"),
]
