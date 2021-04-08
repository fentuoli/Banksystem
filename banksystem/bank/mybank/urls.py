"""bank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index),
    path('logout/',views.logout),
    path('trans_login_bank/',views.trans_login_bank),
    path('trans_login_employee/',views.trans_login_employee),
    path('trans_login_customer/',views.trans_login_customer),
    path('login_bank/',views.login_bank),
    path('login_employee/',views.login_employee),
    path('login_customer/',views.login_customer),
    
    path('register/',views.register),    
    path('employee/<str:employee_id>/', views.trans_employee),
    path('employee/<str:employee_id>/a_alter/', views.alter_employee),
    path('employee/a_alter/', views.alter_employee),
    
    path('client/', views.client),
    path('client/add/', views.add_client),
    path('client/a_alter/', views.alter_client),
    path('client/<str:client_id>/a_alter/', views.alter_client),
    path('client/<str:client_id>/', views.trans_client),
    path('client/<str:client_id>/delete/', views.del_client),

    path('s_account/', views.s_account, name='account'),
    path('s_account/add/', views.add_saccount, name='add_saccount'),
    path('s_account/a_alter/', views.alter_saccount),
    path('s_account/<int:account_id>/', views.trans_saccount, name='trans_account'),
    path('s_account/<int:account_id>/a_alter/', views.alter_saccount),
    path('s_account/<int:account_id>/delete/', views.del_saccount),

    path('c_account/', views.c_account, name='account'),
    path('c_account/add/', views.add_caccount),
    path('c_account/a_alter/', views.alter_caccount),
    path('c_account/<int:account_id>/', views.trans_caccount),
    path('c_account/<int:account_id>/a_alter/', views.alter_caccount),
    path('c_account/<int:account_id>/delete/', views.del_caccount),

    path('loan/', views.loan),
    path('loan/add/', views.add_loan),
    path('loan/a_alter/', views.alter_loan),
    path('loanpay/a_alter/', views.alter_loanpay),
    path('loan/<int:loan_id>/', views.trans_loan),
    path('loan/<int:loan_id>/a_alter/', views.alter_loan),
    path('loan/<int:loan_id>/delete/', views.del_loan),
    path('loan/<int:loan_id>/addpay/', views.add_loanpay),

    path('statistics/', views.statistics, name='statistics'),
]

