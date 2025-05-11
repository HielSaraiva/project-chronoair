from django.shortcuts import render, redirect
from django.contrib.auth import login
from accounts.forms import CustomUserCreationForm
from django.contrib.auth.views import PasswordResetView
from django.core.mail import EmailMultiAlternatives


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


class CustomPasswordResetView(PasswordResetView):
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        # Render the email subject and body
        subject = self.render_to_string(subject_template_name, context)
        body = self.render_to_string(email_template_name, context)
        html_body = self.render_to_string(
            html_email_template_name, context) if html_email_template_name else None

        # Create the email message
        email_message = EmailMultiAlternatives(
            subject, body, from_email, [to_email])
        if html_body:
            email_message.attach_alternative(html_body, "text/html")

        # Send the email
        email_message.send()
