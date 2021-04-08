from django.db import models
from django.contrib.auth.models import User
import datetime


class Branch(models.Model):
    city = models.CharField(max_length=20)
    bankname = models.CharField(max_length=50, unique=True)
    money = models.DecimalField(default=0.0, decimal_places=2, max_digits=15)
    password = models.CharField(default='123456',max_length=6)
    def __str__(self):
        return f'{self.city} {self.bankname}'


class Department(models.Model):
    id = models.CharField(max_length=4,primary_key=True)
    departname = models.CharField(max_length=20)
    departtype = models.CharField(max_length=15)
    manager = models.CharField(max_length=18)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments')
    def __str__(self):
        return f'{self.branch} {self.departname}'

class Customer(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=10)
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=50)
    contact_name = models.CharField(max_length=10)
    contact_phone = models.CharField(max_length=11)
    contact_email = models.EmailField(null=True)
    relation = models.CharField(max_length=10)
    password = models.CharField(default='123456',max_length=6)

    def __str__(self):
        return f'{self.name} ({self.id})'
    
class Account(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='accounts')
    owners = models.ManyToManyField(Customer, related_name='accounts')
    left_money = models.DecimalField(default=0.0, decimal_places=2, max_digits=15)
    creation_time = models.DateTimeField()
    visit_time = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return f'{self.pk}'


class SavingAccount(Account):
    currency_type = models.IntegerField()
    interest_rate = models.DecimalField(decimal_places=2, max_digits=15)

    def __str__(self):
        return f'S{self.pk}'


class CheckingAccount(Account):
    overdraw = models.DecimalField(decimal_places=2, max_digits=15)

    def __str__(self):
        return f'C{self.pk}'


class Employee(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    empname = models.CharField(max_length=20)
    empphone = models.CharField(max_length=11)
    empaddr = models.CharField(max_length=50)
    emptype = models.CharField(max_length=1,default=0)
    empstart = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    password = models.CharField(default='123456',max_length=6)
    
    def __str__(self):
        return f'{self.empname} ({self.id})'


class Loan(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='loans')
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    customers = models.ManyToManyField(Customer)
    date = models.DateTimeField()
    count = models.DecimalField(decimal_places=2, max_digits=15)

    def __str__(self):
        return f'{self.pk}'


class LoanPay(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(decimal_places=6, max_digits=19)
    date = models.DateTimeField()
    class Meta:
        unique_together=("loan","amount","date")
    def __str__(self):
        return f'{self.loan} {self.amount} {self.date}'

class CusEmp(models.Model):
    empID = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='served')
    cusID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='serves')
    servicetype = models.CharField(max_length=10)

    
# class CusSaving(models.Model):
#     branch = models.ManyToManyField(Branch)
#     cusID = models.ManyToManyField(Customer)
#     accountID = models.ForeignKey(SavingAccount, on_delete=models.CASCADE , related_name='owns')
#     visit = models.DateField()
#     #class Meta:
#     #    unique_together=("branch","cusID")

               
# class CusCheckingAccount(models.Model):
#     branch = models.ManyToManyField(Branch)
#     cusID = models.ManyToManyField(Customer)
#     accountID = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE, related_name='owns')
#     visit = models.DateField()
#     #class Meta:
#     #    unique_together=("branch","cusID")

# class SavingAccount(models.Model):
#     id = models.CharField(max_length=6,primary_key=True)
#     money = models.DecimalField(default=0.0,decimal_places=2,max_digits=15)
#     currency_type = models.CharField(max_length=1)
#     interestrate = models.DecimalField(decimal_places=2, max_digits=15)
#     settime = models.DateField()
#     password = models.CharField(default=123456,max_length=6)
#     def __str__(self):
#         return f'S{self.pk}'


# class CheckingAccount(models.Model ):
#     id = models.CharField(max_length=6,primary_key=True)
#     money = models.DecimalField(default=0.0,decimal_places=2,max_digits=15)
#     settime = models.DateField()
#     overdraw = models.DecimalField(decimal_places=2, max_digits=15)
#     password = models.CharField(default=123456,max_length=6)
    
#     def __str__(self):
#         return f'C{self.pk}'       