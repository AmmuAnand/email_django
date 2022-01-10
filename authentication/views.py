from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_fun
from django.core.mail import send_mail
from matrimonial import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token
from django.core.mail import EmailMessage
# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        confpass = request.POST['confpass']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists. Please try something else")
            return redirect('home')
        if User.objects.filter(email=email):
            messages.error(request, "Email already exists. Please login")
            return redirect('login')
        if password != confpass:
            messages.error(request, "Password didn't match. Try agian")
            return redirect('home')
        if not username.isalnum():
            messages.error(request,"Username must be alphanumeric")
            return redirect('home')
        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname

        myuser.is_active = False    # for email confirmation


        myuser.save()
        messages.success(request, "your account has been created!. Sent confirmation email to confirm account!")

        # email confirmation code
        subject = "thank you for creating account with us!. "
        message = "hello " + myuser.first_name + "!! \n " + "Welcome to our website \n This email is for the confirmation. \n Please confirm this email address in order to activate it. \n \n Thanking you, \n Team Sciencesoft."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # email when confirmation link
        current_site = get_current_site(request)
        email_subject = "Confirm your account with sciencesoft"

        message2= render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('login')
       
    return render(request, "authentication/signup.html")

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login_fun(request, user)
            fname = user.first_name
            return render(request,"authentication/index.html", {'fname':fname})
        else:
            messages.error(request, "bad credentials")
            return redirect('home')
    return render(request, "authentication/login.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def activate(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')