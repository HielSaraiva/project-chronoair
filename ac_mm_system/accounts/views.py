from django.shortcuts import render, redirect
from django.contrib.auth import login
from accounts.forms import CustomUserCreationForm


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('website:pagina_inicial')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)
