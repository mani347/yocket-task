from django.shortcuts import render
from base64 import b64encode
from .models import Users, MaintenanceTxns
from django.db.models import Q
from django.core.files.storage import default_storage
from project import settings
import os
from datetime import datetime


def login(request):
    if request.method == 'POST':
        email = request.POST.get('inputEmail')
        password = request.POST.get('inputPassword')
        hashed_pwd = b64encode(password.encode('utf-8'))
        users = Users.objects.filter(email=email, password=hashed_pwd)
        if len(users) <= 0:
            return render(request, 'user_management/login.html', {'context': {'message': 'Invalid Email or Password.'}})
        if users[0].is_approved == 0:
            return render(request, 'user_management/login.html', {'context': {'message': 'Approval Pending. Please contact secretary.'}})
        request.session['user_id'] = users[0].pk
        request.session['is_committee_member'] = users[0].is_committee_member
        return dashboard(request)
    if 'user_id' in request.session:
        return dashboard(request)
    return render(request, 'user_management/login.html', {})


def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('inputEmail')
        phone = request.POST.get('phone')
        password = request.POST.get('inputPassword')
        cpassword = request.POST.get('confirmPassword')
        print(request.FILES)
        message = ''
        if password != cpassword:
            message = 'Password and Confirm Password not matched.'
        elif len(phone) != 10:
            message = 'Enter valid Phone.'
        if message == '':
            users = Users.objects.filter(Q(email=email) | Q(phone=phone))
            if len(users) > 0:
                message = "Email or Phone already registered."
        if message != '':
            context = {'context': {'fname': first_name, 'lname': last_name, 'email': email, 'phone': phone,
                                   'message': message}}
            return render(request, 'user_management/signup.html', context)

        hashed_pwd = b64encode(password.encode('utf-8'))
        new_user = Users(first_name=first_name, last_name=last_name, email=email, phone=phone, password=hashed_pwd,
                         image='')
        new_user.save()
        if len(request.FILES) > 0:
            image = request.FILES.get('image')
            default_storage.save(image.name, image)
            init_url = settings.BASE_DIR + default_storage.url(image.name)
            new_file_name = '/media/profile_images/' + str(new_user.pk) + "_" + str(datetime.now()) + "_" + str(image.name)
            new_url = settings.BASE_DIR + new_file_name
            os.rename(init_url, new_url)
            new_user.image = new_file_name
            new_user.save()
        message = 'You Registered Successfully.'
        return render(request, 'user_management/login.html', {'context': {'message': message}})
    context = {}
    return render(request, 'user_management/signup.html', context)


def dashboard(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    member = Users.objects.get(pk=request.session['user_id'])
    if member.is_committee_member == 0:
        maintenance = MaintenanceTxns.objects.filter(user__pk=request.session['user_id'])
        maintenance_list = []
        for main in maintenance:
            d = dict()
            d['amount'] = main.amount
            d['date'] = main.date
            maintenance_list.append(d)
        context = {'context': {'maintenance_list': maintenance_list, 'is_committee_member': request.session['is_committee_member']}}
        return render(request, 'user_management/dashboard.html', context)
    users = Users.objects.filter(is_committee_member=0)
    final_user_contest = []
    for user in users:
        user_context = dict()
        user_context['user_id'] = user.pk
        user_context['email'] = user.email
        user_context['fname'] = user.first_name
        user_context['lname'] = user.last_name
        user_context['image'] = user.image
        user_context['phone'] = user.phone
        user_context['is_committee_member'] = user.is_committee_member
        user_context['is_approved'] = user.is_approved
        final_user_contest.append(user_context)
    context = {'context': {'users': final_user_contest, 'is_committee_member': request.session['is_committee_member']}}
    return render(request, 'user_management/dashboard.html', context)


def my_profile(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    user = Users.objects.get(pk=request.session['user_id'])
    user_context = dict()
    user_context['email'] = user.email
    user_context['fname'] = user.first_name
    user_context['lname'] = user.last_name
    user_context['image'] = user.image
    user_context['phone'] = user.phone
    context = {'context': {'user': user_context, 'is_committee_member': request.session['is_committee_member']}}
    return render(request, 'user_management/my_profile.html', context)


def logout(request):
    try:
        del request.session['user_id']
        del request.session['is_committee_member']
    except Exception as e:
        pass
    return render(request, 'user_management/login.html', {})


def record_maintenance(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    if request.method == 'POST':
        mobile = request.POST.get('phone')
        email = request.POST.get('email')
        amount = request.POST.get('amount')
        if mobile == '' and email == '':
            context = {'context': {'amount': amount, 'message': 'Please Enter Email or Mobile', 'is_committee_member': request.session['is_committee_member']}}
            return render(request, 'user_management/record_maintenance.html', context)
        message = ''
        if email != '' and mobile != '':
            users = Users.objects.filter(email=email, phone=mobile)
            if len(users) <= 0:
                message = 'Email and Mobile does not exists.'
        elif email != '':
            users = Users.objects.filter(email=email)
            if len(users) <= 0:
                message = 'Email does not exists.'
        else:
            users = Users.objects.filter(phone=mobile)
            if len(users) <= 0:
                message = 'Mobile does not exists.'
        if message != '':
            context = {'context': {'email': email, 'phone': mobile, 'amount': amount, 'message': message, 'is_committee_member': request.session['is_committee_member']}}
            return render(request, 'user_management/record_maintenance.html', context)
        user = users[0]
        if message == '' and user.is_approved == 0:
            message = 'User Approval Pending'

        if message != '':
            context = {'context': {'email': email, 'phone': mobile, 'amount': amount, 'message': message, 'is_committee_member': request.session['is_committee_member']}}
            return render(request, 'user_management/record_maintenance.html', context)
        new_rec = MaintenanceTxns(user=user, amount=amount, date=datetime.now().date())
        new_rec.save()
        message = 'Maintenance Recorded Successfully for ' + str(user.first_name) + ' ' + str(user.last_name)
        context = {'context': {'message': message, 'is_committee_member': request.session['is_committee_member']}}
        return render(request, 'user_management/record_maintenance.html', context)
    context = {'context': {'is_committee_member': request.session['is_committee_member']}}
    return render(request, 'user_management/record_maintenance.html', context)


def approve(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    user_id = request.GET.get('id')
    Users.objects.filter(pk=user_id).update(is_approved=1)
    return dashboard(request)


def reject(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    user_id = request.GET.get('id')
    Users.objects.filter(pk=user_id).update(is_approved=0, is_committee_member=0)
    return dashboard(request)


def approve_member(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    user_id = request.GET.get('id')
    Users.objects.filter(pk=user_id).update(is_approved=1, is_committee_member=1)
    return dashboard(request)


def paid_maintenance(request):
    if 'user_id' not in request.session:
        return render(request, 'user_management/login.html', {})
    maintenance = MaintenanceTxns.objects.filter(user__pk=request.session['user_id'])
    print(maintenance)
    maintenance_list = []
    for main in maintenance:
        d = dict()
        d['amount'] = main.amount
        d['date'] = main.date
        maintenance_list.append(d)
    context = {'context': {'maintenance_list': maintenance_list, 'is_committee_member': request.session['is_committee_member']}}
    return render(request, 'user_management/paid_maintenance.html', context)
