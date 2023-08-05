from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages as django_messages
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Advertisement, Response, PrivatePage, Newsletter
from .forms import NewsletterForm, AdvertisementForm, UserRegistrationForm, ResponseForm, EmailAuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def send_confirmation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Подтверждение регистрации'
    message = render_to_string('registration_confirmation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Проверка, что пользователь с таким email уже не зарегистрирован
            if not User.objects.filter(email=email).exists():
                user = form.save()  # Сохранение пользователя в базу данных
                user.is_active = False
                user.save()
                send_confirmation_email(request, user)  # Отправляем письмо с подтверждением
                return redirect('confirmation_sent')  # Редирект на страницу с сообщением о подтверждении
            else:
                # Пользователь уже зарегистрирован
                return render(request, 'registration.html', {'error_message': 'Пользователь с таким email уже зарегистрирован.'})
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})

def confirmation_sent(request):
    return render(request, 'confirmation_sent.html')


def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('all_advertisements')
    else:
        return HttpResponse('Ссылка для подтверждения недействительна или устарела.')

def login_user(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = User.objects.get(email=email).username
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('private_page')
                else:
                    messages.error(request, 'Пользователь не активирован.')
            else:
                messages.error(request, 'Неверный email или пароль.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')  # Перенаправление на страницу входа после выхода

# Функция для просмотра приватной страницы пользователя с его объявлениями и откликами
@login_required
def private_page(request):
    user = request.user
    advertisements = Advertisement.objects.filter(user=user)
    responses = Response.objects.filter(advertisement__user=user)
    return render(request, 'private_page.html', {'advertisements': advertisements, 'responses': responses})

# Функция для просмотра новостной рассылки
def view_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    return render(request, 'newsletter.html', {'newsletter': newsletter})

# Функция для отправки новостной рассылки
@login_required
def send_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            recipients = [user.email for user in User.objects.all()]
            send_mail(newsletter.subject, newsletter.content, 'noreply@example.com', recipients)
            return redirect('newsletter_detail', newsletter_id=newsletter.pk)  # Перенаправление на страницу просмотра рассылки
    else:
        form = NewsletterForm()
    return render(request, 'send_newsletter.html', {'form': form})

@login_required
def create_advertisement(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.user = request.user
            advertisement.save()
            return redirect('advertisement_detail', advertisement_id=advertisement.pk)
        else:
            django_messages.error(request, 'Пожалуйста, заполните форму корректно.')
    else:
        form = AdvertisementForm()
    return render(request, 'create_advertisement.html', {'form': form, 'categories': Category.objects.all()})

@login_required
def advertisement_detail(request, advertisement_id):
    advertisement = get_object_or_404(Advertisement, pk=advertisement_id)

    return render(request, 'advertisement_detail.html', {'advertisement': advertisement})

@login_required
def send_response(request, advertisement_id):
    advertisement = get_object_or_404(Advertisement, pk=advertisement_id)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            response = Response.objects.create(user=request.user, advertisement=advertisement, content=content)

            # Отправка электронной почты с оповещением о новом отклике
            recipient_email = advertisement.user.email
            mail_subject = f'Новый отклик на ваше объявление "{advertisement.title}"'
            message = f'Здравствуйте!\nПользователь {request.user.email} отправил отклик на ваше объявление "{advertisement.title}".\n\nС уважением, Администрация'
            email = EmailMessage(mail_subject, message, to=[recipient_email])
            email.send()

            django_messages.success(request, 'Ваш отклик успешно отправлен.')
            return redirect('all_advertisements')  # Перенаправление на страницу со всеми объявлениями
    else:
        form = ResponseForm()

    return render(request, 'send_response.html', {'form': form, 'advertisement': advertisement})


@login_required
def edit_advertisement(request, advertisement_id):
    advertisement = get_object_or_404(Advertisement, pk=advertisement_id)

    # Проверка, что текущий пользователь является автором объявления
    if request.user == advertisement.user:
        if request.method == 'POST':
            advertisement.title = request.POST['title']
            advertisement.content = request.POST['content']
            category_id = request.POST['category']
            advertisement.category = get_object_or_404(Category, pk=category_id)
            advertisement.save()
            return redirect('advertisement_detail', advertisement_id=advertisement.pk)
        else:
            categories = Category.objects.all()
            return render(request, 'edit_advertisement.html', {'advertisement': advertisement, 'categories': categories})
    else:
        # Если пользователь не является автором объявления, перенаправить на детали объявления
        return redirect('advertisement_detail', advertisement_id=advertisement.pk)

def all_advertisements(request):
    if request.user.is_active:
        # Получаем все объявления из базы данных
        advertisements = Advertisement.objects.all()
        return render(request, 'all_advertisements.html', {'advertisements': advertisements})
    else:
        return render(request, 'confirmation_sent.html')


@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, pk=response_id)
    if request.user == response.advertisement.user:
        response.delete()
    return redirect('private_page')

@login_required
def accept_response(request, response_id):
    response = get_object_or_404(Response, pk=response_id)
    if request.user == response.advertisement.user and not response.is_accepted:
        response.is_accepted = True
        response.save()
        # Отправка уведомления пользователю, оставившему отклик
        recipient_email = response.user.email
        mail_subject = f'Ваш отклик на объявление "{response.advertisement.title}" принят'
        message = f'Здравствуйте!\nВаш отклик на объявление "{response.advertisement.title}" был принят автором объявления.\n\nС уважением, Администрация'
        email = EmailMessage(mail_subject, message, to=[recipient_email])
        email.send()
        return redirect('private_page')
    else:
        return HttpResponseForbidden('У вас нет доступа к этой странице.')