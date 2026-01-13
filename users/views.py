from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from users.forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
def register(request):
    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
         form.save()
         username =form.cleaned_data.get('username')
        messages.success(request,f'your account has been created for {username}!')
        return redirect('login')
           
    else:
     form=UserRegisterForm()
     return render(request,'users/register.html',{'form':form})
    
@login_required
def profile(request):
    return render(request,'users/profile.html')
    

# Create your views here.
