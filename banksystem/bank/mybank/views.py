from django.http import HttpResponse
from django.db import Error
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncYear, TruncQuarter
from django.db.models.query import Q
from django.template import loader
from django.shortcuts import get_list_or_404, render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import dateparse
import json
import datetime
import calendar
import decimal
from .models import *

def index(request):
    if not request.session.get('is_login', None):
        return redirect('/mybank/trans_login_customer/')
    return render(request, 'index.html')

def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/mybank/trans_login_customer/')

    request.session.flush()
    # del request.session['is_login']
    return redirect("/mybank/trans_login_customer/")

def trans_login_bank(request):
    return render(request,'login_bank.html')

def trans_login_employee(request):
    return render(request,'login_employee.html')
    
def trans_login_customer(request):
    return render(request,'login_customer.html')
        
def login_bank(request):
    if request.method == 'POST':
        name = request.POST['name']
        try:
            bank = Branch.objects.get(bankname=name)
        except:
            messages.error(request,"该支行未注册!")
            return render(request, 'login_bank.html')
        if bank.password == request.POST['password']:
            messages.info(request,"登录成功!")
            return redirect('/mybank/statistics/')
        else:
            messages.error(request,"密码输入错误!")
            return render(request, 'login_bank.html')
    else:
        messages.error(request, '错误的请求方式')
        return redirect('/mybank/index/')

def login_employee(request):
    if request.method == 'POST':
        empid = request.POST['empid']
        try:
            employee = Employee.objects.get(id=empid)
        except:
            messages.error(request,"该员工未注册!")
            return render(request, 'login_employee.html')
        if employee.password == request.POST['password']:
            messages.info(request,"登录成功!")
            return render(request, 'base.html')
        else:
            messages.error(request,"密码输入错误!")
            return render(request, 'login_employee.html')
    else:
        messages.error(request, '错误的请求方式')
        return redirect('/mybank/index/')

def login_customer(request):
    if request.method == 'POST':
        cusid = request.POST['cusid']
        try:
            customer = Customer.objects.get(id=cusid)
        except:
            messages.error(request,"该用户未注册!")
            return render(request, 'login_customer.html')
        if customer.password == request.POST['password']:
            messages.info(request,"登录成功!")
            request.session['is_login'] = True
            request.session['user_id'] = cusid
            return render(request, 'base.html')
        else:
            messages.error(request,"密码输入错误!")
            return render(request, 'login_customer.html')
    else:
        messages.error(request, '错误的请求方式')
        return redirect('/mybank/index/')

def register(request):
    return render(request, 'register.html')

def trans_employee(request, employee_id):
    detail = get_object_or_404(Employee, pk=employee_id)
    return HttpResponse(render(request, 'form.html', {'default': detail, 'page': 'employee', 'department': Department.objects.all(), 'branches': Branch.objects.all(), 'department_id': detail.department.id}))

def alter_employee(request, employee_id=None):
    if request.method != 'POST':
        messages.error(request, '错误的请求方式')
        return redirect('/')
    if employee_id:
        # Update
        employee = get_object_or_404(Employee, id=employee_id)
        employee.id = request.POST['id']
        employee.department = Department.objects.all().filter(id=request.POST['department'])[0]
        employee.empname = request.POST['empname']
        employee.empphone = request.POST['empphone']
        employee.empaddr = request.POST['empaddr']
        employee.empstart = request.POST['empstart']
        employee.password = request.POST['password']
        if employee.id=='' or employee.department=='' or employee.empname=='' or employee.empphone=='' or employee.empaddr=='' or employee.empstart=='' or employee.password=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
        employee.save()
    else:
        # Create
        employee = Employee.objects.create(
            pk=request.POST['id'],
            department = Department.objects.all().filter(id=request.POST['department'])[0],
            empname=request.POST['empname'],
            empphone=request.POST['empphone'],
            empaddr=request.POST['empaddr'],
            empstart=request.POST['empstart'],
            password = request.POST['password']
        )
        if employee.pk=='' or employee.department=='' or employee.empname=='' or employee.empphone=='' or employee.empaddr=='' or employee.empstart=='' or employee.password=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
        employee_id = employee.pk
    return trans_employee(request, employee_id)

def client(request):
    q = None
    if 'q1' in request.GET:
        q1 = request.GET['q1']
        q = Q(id__icontains=q1)
    if 'q2' in request.GET:
        q2 = request.GET['q2']
        if not q is None:
            q = q & Q(name__icontains=q2)
        else:
            q = Q(name__icontains=q2)
    if 'q3' in request.GET:
        q3 = request.GET['q3']
        if not q is None:
            q = q & Q(phone__icontains=q3)
        else:
            q = Q(phone__icontains=q3)
    if 'q4' in request.GET:
        q4 = request.GET['q4']
        if not q is None:
            q = q & Q(address__icontains=q4)
        else:
            q = Q(address__icontains=q4)
    if not q is None:
        l_client = Customer.objects.all().filter(q)
    else:
        l_client = Customer.objects.all()
    service = CusEmp.objects.all()
    template = loader.get_template('list.html')
    context = {'iters': l_client, 'service': service, 'page': 'client'}
    return HttpResponse(template.render(context, request))

def del_client(request, client_id):
    flag=0
    if request.session.get('user_id') != client_id:
        messages.error(request,"您没有删除该信息的权限!")
        return client(request)
    s_account = SavingAccount.objects.all()
    for i in s_account:
        for j in i.owners.all():
            if j.id == client_id:
                messages.error(request,'有关联账户，不允许删除!')
                flag=1
    if flag==0:
        c_account = CheckingAccount.objects.all()
        for i in c_account:
            for j in i.owners.all():
                if j.id == client_id:
                    messages.error(request,'有关联账户，不允许删除!')
                    flag=1
    if flag==0:
        loan = Loan.objects.all()
        for i in loan:
            if flag == 0:
                for j in i.customers.all():
                    if j.id == client_id:
                        messages.error(request,'有关联贷款，不允许删除!')
                        flag=1
                        break
    if flag == 0:  
        o = get_object_or_404(Customer, pk=client_id)
        try:
            o.delete()
            messages.info(request, '刪除成功')
        except Error as e:
            messages.error(request, '刪除失敗: ' + str(e))
    return client(request)

def trans_client(request, client_id):
    detail = get_object_or_404(Customer, pk=client_id)
    return HttpResponse(render(request, 'form.html', {'default': detail, 'page': 'client', 'employee': Employee.objects.all(), 'employee': Employee.objects.all()}))

def alter_client(request, client_id=None):
    if request.method != 'POST':
        messages.error(request, '错误的请求方式')
        return redirect('/')
    if client_id:
        # Update
        client = get_object_or_404(Customer, id=client_id)
        client.id = request.POST['id']
        client.name = request.POST['name']
        client.phone = request.POST['phone']
        client.address = request.POST['address']
        client.contact_name = request.POST['contact_name']
        client.contact_phone = request.POST['contact_phone']
        client.contact_email = request.POST['contact_email']
        client.relation = request.POST['relation']
        client.password = request.POST['password']
        service = get_object_or_404(CusEmp,
            cusID=Customer.objects.get(id=client_id))
        service.empID=Employee.objects.get(empname=request.POST['empID'])
        service.servicetype=request.POST['servicetype']
        if client.id=='' or client.name=='' or client.phone=='' or client.address=='' or client.contact_name=='' or client.contact_phone=='' or client.contact_email=='' or client.relation=='' or client.password=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
        if client.name.find("'")!=-1:
            client.delete()
            messages.error(request,"您输入的姓名中包含\" ' \"，该输入无效，请重新输入!")
        client.save()
        service.save()
        return trans_client(request, client_id)
    else:
        # Create
        client = Customer.objects.create(
            pk=request.POST['id'],
            name=request.POST['name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            contact_name=request.POST['contact_name'],
            contact_phone=request.POST['contact_phone'],
            contact_email=request.POST['contact_email'],
            relation=request.POST['relation'],
            password = request.POST['password']
        )
        service = CusEmp.objects.create(
            cusID=Customer.objects.get(id=request.POST['id']),
            empID=Employee.objects.get(empname=request.POST['empID']),
            servicetype=request.POST['servicetype']
        )
        if client.pk=='' or client.name=='' or client.phone=='' or client.address=='' or client.contact_name=='' or client.contact_phone=='' or client.contact_email=='' or client.relation=='' or client.password=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
            client.delete()
            return add_client(request)
        if client.name.find("'")!=-1:
            client.delete()
            messages.error(request,"您输入的姓名中包含\" ' \"，该输入无效，请重新输入!")
            return add_client(request)
        else:
            client_id = client.pk
            return trans_client(request, client_id)

def add_client(request):
    return HttpResponse(render(request, 'form.html', {'page': 'client', 'employee': Employee.objects.all(), 'employee': Employee.objects.all()}))

def s_account(request):
    q = None
    if 'q1' in request.GET:
        q1 = request.GET['q1']
        q = Q(id__icontains=q1)
    if 'q2' in request.GET:
        q2 = request.GET['q2']
        if not q is None:
            q = q & Q(branch__bankname__icontains=q2)
        else:
            q = Q(branch__bankname__icontains=q2)
    if 'q3' in request.GET:
        q3 = request.GET['q3']
        if not q is None:
            q = q & Q(owners__name__icontains=q3)
        else:
            q = Q(owners__name__icontains=q3)
    if not q is None:
        l_account = SavingAccount.objects.filter(q)     
    else:
        l_account = SavingAccount.objects.all()
    template = loader.get_template('list.html')
    context = {'iters': l_account, 'page': 's_account'}
    return HttpResponse(template.render(context, request))

def trans_saccount(request, account_id):
    detail = get_object_or_404(SavingAccount, pk=account_id)
    return HttpResponse(render(request, 'form.html', {'default': detail, 'page': 's_account', 'branches': Branch.objects.all(), 'owners': Customer.objects.all()}))

def add_saccount(request):
    return HttpResponse(render(request, 'form.html', {'page': 's_account', 'branches': Branch.objects.all(), 'owners': Customer.objects.all()}))

def alter_saccount(request, account_id=None):
    if request.method != 'POST':
        messages.error(request, '错误的请求方式')
        return redirect('/')
    if account_id:
        # Update
        account = get_object_or_404(SavingAccount, id=account_id)
        account.branch = Branch.objects.get_or_create(
            id=request.POST['branch_id'])[0]
        for i in request.POST.getlist('owners'):
            a = SavingAccount.objects.all().filter(Q(owners__id__icontains=i))
            for j in a:
                if j.branch == account.branch and j.id != account.id:
                    messages.error(request, '在同一支行建立两个储蓄帐户！')
                    return redirect('/mybank/s_account/')
            account.owners.add(Customer.objects.get(id=i))
        account.left_money = request.POST.get('left_money', 0.0)
        account.creation_time = request.POST['creation_time']
        account.visit_time = request.POST['visit_time']
        account.currency_type = request.POST['currency_type']
        account.interest_rate = request.POST.get('interest_rate', 0.0)
        if account.left_money=='' or account.creation_time=='' or account.visit_time=='' or account.currency_type=='' or account.interest_rate=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
        account.save()
    else:
        # Create
        account = SavingAccount.objects.create(
            branch=Branch.objects.get_or_create(
                id=request.POST['branch_id'])[0],
            left_money=request.POST.get('left_money', 0.0),
            creation_time=request.POST['creation_time'],
            visit_time=request.POST['visit_time'],
            currency_type=request.POST['currency_type'],
            interest_rate=request.POST.get('interest_rate', 0.0)
        )
        for i in request.POST.getlist('owners'):
            a = SavingAccount.objects.all().filter(Q(owners__id__icontains=i))
            for j in a:
                if j.branch == account.branch:
                    o = get_object_or_404(SavingAccount, pk=account.pk)
                    o.delete()
                    messages.error(request, '在同一支行建立两个储蓄帐户！')
                    return redirect('/mybank/s_account/')
            account.owners.add(Customer.objects.get(id=i))
        if account.left_money=='' or account.creation_time=='' or account.visit_time=='' or account.currency_type=='' or account.interest_rate=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
            account.delete()
            return add_saccount(request)
        account_id = account.pk
    return trans_saccount(request, account_id)

def del_saccount(request, account_id):
    o = get_object_or_404(SavingAccount, pk=account_id)
    for i in o.owners.all():
        if request.session.get('user_id') != i.id:
            messages.error(request,"您没有删除该信息的权限!")
            return s_account(request)
    try:
        o.delete()
        messages.info(request, '刪除成功')
    except Error as e:
        messages.error(request, '刪除失敗: ' + str(e))
    return s_account(request)

def c_account(request):
    q = None
    if 'q1' in request.GET:
        q1 = request.GET['q1']
        q = Q(id__icontains=q1)
    if 'q2' in request.GET:
        q2 = request.GET['q2']
        if not q is None:
            q = q & Q(branch__bankname__icontains=q2)
        else:
            q = Q(branch__bankname__icontains=q2)
    if 'q3' in request.GET:
        q3 = request.GET['q3']
        if not q is None:
            q = q & Q(owners__name__icontains=q3)
        else:
            q = Q(owners__name__icontains=q3)
    if not q is None:
        l_account = CheckingAccount.objects.filter(q)     
    else:
        l_account = CheckingAccount.objects.all()
    template = loader.get_template('list.html')
    context = {'iters': l_account, 'page': 'c_account'}
    return HttpResponse(template.render(context, request))

def trans_caccount(request, account_id):
    detail = get_object_or_404(CheckingAccount, pk=account_id)
    return HttpResponse(render(request, 'form.html', {'default': detail, 'page': 'c_account', 'branches': Branch.objects.all(), 'owners': Customer.objects.all()}))

def alter_caccount(request, account_id=None):
    if request.method != 'POST':
        messages.error(request, '错误的请求方式')
        return redirect('/')
    if account_id:
        # Update
        account = get_object_or_404(CheckingAccount, pk=account_id)
        account.branch = Branch.objects.get_or_create(
            id=request.POST['branch_id'])[0]
        for i in request.POST.getlist('owners'):
            a = CheckingAccount.objects.all().filter(Q(owners__id__icontains=i))
            for j in a:
                if j.branch == account.branch and j.id != account.id:
                    o = get_object_or_404(CheckingAccount, pk=account_id)
                    o.delete()
                    messages.error(request, '在同一支行建立两个储蓄帐户！')
                    return redirect('/')
            account.owners.add(Customer.objects.get(id=i))
        account.left_money = request.POST.get('left_money', 0.0)
        account.creation_time = request.POST['creation_time']
        account.visit_time = request.POST['visit_time']
        account.overdraw = request.POST.get('overdraw', 0.0)
        if account.left_money=='' or account.creation_time=='' or account.visit_time=='' or account.overdraw=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
        account.save()
    else:
        # Create
        account = CheckingAccount.objects.create(
            branch=Branch.objects.get_or_create(
                id=request.POST['branch_id'])[0],
            left_money=request.POST.get('left_money', 0.0),
            creation_time=request.POST['creation_time'],
            visit_time=request.POST['visit_time'],
            overdraw=request.POST.get('overdraw', 0.0)
        )
        for i in request.POST.getlist('owners'):
            a = CheckingAccount.objects.all().filter(Q(owners__id__icontains=i))
            for j in a:
                if j.branch == account.branch:
                    o = get_object_or_404(CheckingAccount, pk=account_id)
                    o.delete()
                    messages.error(request, '在同一支行建立两个储蓄帐户！')
                    return redirect('/')
            account.owners.add(Customer.objects.get(id=i))
        if account.left_money=='' or account.creation_time=='' or account.visit_time=='' or account.overdraw=='':
            messages.error(request,"任何字段不许为空，请再次输入!")
            account.delete()
            return add_caccount(request, account_id)
        account_id = account.pk
    return trans_caccount(request, account_id)

def add_caccount(request):
    return HttpResponse(render(request, 'form.html', {'page': 'c_account', 'branches': Branch.objects.all(), 'owners': Customer.objects.all()}))

def del_caccount(request, account_id):
    o = get_object_or_404(CheckingAccount, pk=account_id)
    for i in o.owners.all():
        if request.session.get('user_id') != i.id:
            messages.error(request,"您没有删除该信息的权限!")
            return c_account(request)
    try:
        o.delete()
        messages.info(request, '刪除成功')
    except Error as e:
        messages.error(request, '刪除失敗: ' + str(e))
    return c_account(request)

def loan(request):
    q = None
    if 'q1' in request.GET:
        q1 = request.GET['q1']
        q = Q(id__icontains=q1)
    if 'q2' in request.GET:
        q2 = request.GET['q2']
        if not q is None:
            q = q & Q(branch__bankname__icontains=q2)
        else:
            q = Q(branch__bankname__icontains=q2)
    if 'q3' in request.GET:
        q3 = request.GET['q3']
        if not q is None:
            q = q & Q(customers__name__icontains=q3)
        else:
            q = Q(customers__name__icontains=q3)
    if not q is None:
        l_loan = Loan.objects.filter(q)     
    else:
        l_loan = Loan.objects.all()
    template = loader.get_template('list.html')
    context = {'iters': l_loan, 'page': 'loan',
               'customers': Customer.objects.all()}
    return HttpResponse(template.render(context, request))

def trans_loan(request, loan_id):
    detail = get_object_or_404(Loan, pk=loan_id)
    return HttpResponse(render(request, 'form.html', {'default': detail, 'page': 'loan', 'branches': Branch.objects.all(), 'owners': Customer.objects.all(), 'pays': LoanPay.objects.all()}))

def alter_loan(request, loan_id=None):
    if request.method != 'POST':
        messages.error(request, '错误的请求方式')
        return redirect('/')
    loan = Loan.objects.create(
        branch=Branch.objects.get_or_create(
            id=request.POST['branch_id'])[0],
        amount=request.POST.get('amount', 0.0),
        date=request.POST['date'],
        count=0.0
    )
    for i in request.POST.getlist('customer_id'):
        loan.customers.add(Customer.objects.get(id=i))
    if loan.amount=='' or loan.date=='':
        messages.error(request,"任何字段不许为空，请再次输入!")
        loan.delete()
        return add_loan(request)
    if float(loan.amount)>float(loan.branch.money):
        messages.error(request,'所贷款项超过银行储蓄!')
        o = get_object_or_404(Loan, pk=loan.pk)
        o.delete()
    loan_id = loan.pk
    return trans_loan(request, loan_id)

def add_loan(request):
    return HttpResponse(render(request, 'form.html', {'page': 'loan', 'branches': Branch.objects.all(), 'owners': Customer.objects.all()}))

def del_loan(request, loan_id):
    o = get_object_or_404(Loan, pk=loan_id)
    for i in o.customers.all():
        if request.session.get('user_id') != i.id:
            messages.error(request,"您没有删除该信息的权限!")
            return loan(request)
    try:
        o.delete()
        messages.info(request, '刪除成功')
    except Error as e:
        messages.error(request, '刪除失敗: ' + str(e))
    return loan(request)

def add_loanpay(request, loan_id):
    return HttpResponse(render(request, 'form.html', {'page': 'loanpay', 'loan_id': loan_id}))

def alter_loanpay(request):
    if request.method != 'POST':
        messages.error(request, '错误的请求方式')
        return redirect('/')
    loanpay = LoanPay.objects.create(
        loan=Loan.objects.get(id=request.POST['loan_id']),
        amount=request.POST.get('amount', 0.0),
        date=request.POST['date']
    )
    loanpay.loan.count += decimal.Decimal(loanpay.amount)
    loanpay.loan.save()
    loan_id = loanpay.loan.id
    return trans_loan(request, loan_id)

def change_time(date_time):
    time=TruncMonth(date_time)
    month=time.month
    month=(month-1)//3*3+1
    return datetime.datetime(time.year,month,time.day)

def statistics(request):
    freq = request.GET.get('frequency', 'year')
    if freq not in ['year', 'month', 'season']:
        messages.error(request, '查询失败（频度无效）')
        return redirect('/statistics')

    template = loader.get_template('statistics.html')
    t_start = dateparse.parse_date(request.GET.get('start_date', '2010-06-30'))
    t_end = dateparse.parse_date(request.GET.get('end_date', '2020-06-30'))
    if t_start <= t_end:
        acc = Account.objects.filter(creation_time__range=[t_start, t_end])
        n_acc = acc.aggregate(Count('id')).get('id__count', 0.00)
        m_acc = acc.aggregate(Sum('left_money')).get('left_money__sum', 0.00)
        loa = LoanPay.objects.filter(date__range=[t_start, t_end])
        n_loa = loa.aggregate(Count('id')).get('id__count', 0.00)
        m_loa = loa.aggregate(Sum('amount')).get('amount__sum', 0.00)
    if freq == 'month':
        account = Account.objects.annotate(month=TruncMonth('creation_time')).values('month', 'branch').annotate(m=Sum('left_money'), n=Count('id')).values('month', 'branch', 'm', 'n')
        amount = Loan.objects.annotate(month=TruncMonth('date')).values('month').annotate(m=Sum('amount'), n=Count('id')).values('month', 'branch', 'm', 'n')
        payamount = LoanPay.objects.annotate(month=TruncMonth('date')).values('month').annotate(m=Sum('amount'), n=Count('id')).values('month', 'm', 'n')
    if freq == 'year':
        account = Account.objects.annotate(month=TruncYear('creation_time')).values('month', 'branch').annotate(m=Sum('left_money'), n=Count('id')).values('month', 'branch', 'm', 'n')
        amount = Loan.objects.annotate(month=TruncYear('date')).values('month').annotate(m=Sum('amount'), n=Count('id')).values('month', 'branch', 'm', 'n')
        payamount = LoanPay.objects.annotate(month=TruncYear('date')).values('month').annotate(m=Sum('amount'), n=Count('id')).values('month', 'm', 'n')
    if freq == 'season':
        account = Account.objects.annotate(month=TruncQuarter('creation_time')).values('month', 'branch').annotate(m=Sum('left_money'), n=Count('id')).values('month', 'branch', 'm', 'n')
        amount = Loan.objects.annotate(month=TruncQuarter('date')).values('month').annotate(m=Sum('amount'), n=Count('id')).values('month', 'branch', 'm', 'n')
        payamount = LoanPay.objects.annotate(month=TruncQuarter('date')).values('month').annotate(m=Sum('amount'), n=Count('id')).values('month', 'm', 'n')

    def range_date_in(start, end, step):
        if step == 'year':
            start = datetime.date(start.year, 1, 1)
            while start < end:
                yield (start, datetime.date(start.year, 12, 31))
                start = datetime.date(start.year+1, 1, 1)
        elif step == 'month':
            start = datetime.date(start.year, start.month, 1)
            while start < end:
                y = start.year
                m = start.month
                yield (start, datetime.date(y, m, calendar.monthrange(y, m)[1]))
                if start.month == 12:
                    start = datetime.date(start.year+1, 1, 1)
                else:
                    start = datetime.date(start.year, start.month+1, 1)
        else:
            start = datetime.date(start.year, (start.month-1)//3*3+1, 1)
            while start < end:
                y = start.year
                m = (start.month-1)//3*3+1+2
                yield (start, datetime.date(y, m, calendar.monthrange(y, m)[1]))
                if 10 <= start.month <= 12:
                    start = datetime.date(start.year+1, 1, 1)
                else:
                    start = datetime.date(start.year, start.month+3, 1)

    def get_labels_by_freq(start_date, end_date, freq):
        if freq == 'year':
            return [str(i) for i in range(start_date.year, end_date.year+1)]
        elif freq == 'month':
            res = []
            d = datetime.date(start_date.year, start_date.month, 1)
            while d < end_date:
                res.append(f'{d.year}-{d.month}')
                if d.month == 12:
                    d = datetime.date(d.year+1, 1, 1)
                else:
                    d = datetime.date(d.year, d.month+1, 1)
            return res
        else:  # season
            res = []
            d = datetime.date(start_date.year, (start_date.month-1) // 3 * 3 + 1, 1)
            while d < end_date:
                res.append('%d-%s' % (d.year, ["Q1", "Q2", "Q3", "Q4"][(d.month-1)//3]))
                if 9 < d.month <= 12:
                    d = datetime.date(d.year+1, 1, 1)
                else:
                    d = datetime.date(d.year, d.month+3, 1)
            return res

    def get_account_data(start_date, end_date, freq):
        data = []
        for (start_date, end_date) in range_date_in(start_date, end_date, freq):
            total_leftmoney = Account.objects.filter(creation_time__range=[start_date, end_date]).aggregate(Count('id')).get('id__count', 0.00)
            data.append(total_leftmoney)
        return data


    def get_loan_data(start_date, end_date, freq):
        data = []
        for (start_date, end_date) in range_date_in(start_date, end_date, freq):
            total_loan = Loan.objects.filter(date__range=[start_date, end_date]).aggregate(Count('id')).get('id__count', 0.00)
            data.append(total_loan)
        return data

    def get_loanpay_data(start_date, end_date, freq):
        data = []
        for (start_date, end_date) in range_date_in(start_date, end_date, freq):
            total_loan = LoanPay.objects.filter(date__range=[start_date, end_date]).aggregate(Count('id')).get('id__count', 0.00)
            data.append(total_loan)
        return data

    data = json.dumps({
        'labels': get_labels_by_freq(t_start, t_end, freq),
        'datasets': [{
            'label': '账户',
            'data': get_account_data(t_start, t_end, freq),
            'backgroundColor': ['rgba(205, 38, 38, 0.4)'],
            'borderColor': ['rgba(205, 38, 38, 1)']
        }, {
            'label': '贷款',
            'data': get_loan_data(t_start, t_end, freq),
            'backgroundColor': ['rgba(0, 0, 255, 0.4)'],
            'borderColor': ['rgba(0, 0, 255, 1)']
        }, {
            'label': '贷款支付',
            'data': get_loanpay_data(t_start, t_end, freq),
            'backgroundColor': ['rgba(0, 100, 0, 0.4)'],
            'borderColor': ['rgba(0, 100, 0, 1)']
        }]
    })
    context = {'n_acc': n_acc, 'm_acc': m_acc, 'n_loa': n_loa, 'm_loa': m_loa, 'account': account, 'payamount':payamount, 'amount': amount, 'data': data}
    return HttpResponse(template.render(context, request))
