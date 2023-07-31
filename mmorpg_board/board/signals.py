from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Response

User = get_user_model()

# Сигнал для отправки электронной почты при создании отклика на объявление
@receiver(post_save, sender=Response)
def send_response_email(sender, instance, created, **kwargs):
    if created:
        advertisement = instance.advertisement
        recipient_email = advertisement.user.email
        mail_subject = f'Новый отклик на ваше объявление "{advertisement.title}"'
        message = f'Здравствуйте!\nПользователь {instance.user.email} отправил отклик на ваше объявление "{advertisement.title}".\n\nС уважением, Администрация'
        send_mail(mail_subject, message, 'noreply@example.com', [recipient_email])