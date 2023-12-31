from django.db import models
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    content = RichTextField()  # Заменим TextField на RichTextField
    file = models.FileField(upload_to='media/', blank=True, null=True)  # Добавим поле для медиа-контента
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Модель для медиа-контента объявления (картинки, видео и другой контент)
#class MediaContent(models.Model):
 #   advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
  #  file = models.FileField(upload_to='media/')

# Модель для откликов на объявления
class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)  # Поле для хранения информации о принятии отклика

    def __str__(self):
        return f'Response #{self.pk} by {self.user.email}'

    class Meta:
        ordering = ['-sent_at']

# Модель для приватной страницы пользователя с его объявлениями и откликами
class PrivatePage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

# Модель для новостных рассылок
class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

# Функция для создания категорий
def create_categories():
    categories = [
        "Танки",
        "Хилы",
        "ДД",
        "Торговцы",
        "Гилдмастеры",
        "Квестгиверы",
        "Кузнецы",
        "Кожевники",
        "Зельевары",
        "Мастера заклинаний",
    ]
    created_count = 0

    for category_name in categories:
        category, created = Category.objects.get_or_create(name=category_name)
        if created:
            created_count += 1

    return created_count

def send_response_notification(sender, instance, **kwargs):
    response = instance
    if response.is_accepted:
        recipient_email = response.user.email
        mail_subject = f'Ваш отклик на объявление "{response.advertisement.title}" принят'
        message = f'Здравствуйте!\nВаш отклик на объявление "{response.advertisement.title}" был принят автором объявления.\n\nС уважением, Администрация'
        email = EmailMessage(mail_subject, message, to=[recipient_email])
        email.send()


post_save.connect(send_response_notification, sender=Response)


User = get_user_model()

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError('Неверный email или пароль')
            else:
                # При успешной аутентификации обновляем cleaned_data
                self.cleaned_data['user'] = user

        return self.cleaned_data

