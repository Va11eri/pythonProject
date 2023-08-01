from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register_user'),
    path('confirmation_sent/', views.confirmation_sent, name='confirmation_sent'),
    path('confirm_email/<str:uidb64>/<str:token>/', views.confirm_email, name='confirm_email'),
    # URL для создания, просмотра и редактирования объявлений
    path('create_advertisement/', views.create_advertisement, name='create_advertisement'),
    path('advertisement/<int:advertisement_id>/', views.advertisement_detail, name='advertisement_detail'),
    path('advertisement/<int:advertisement_id>/edit/', views.edit_advertisement, name='edit_advertisement'),
    path('advertisement/<int:advertisement_id>/send_response/', views.send_response, name='send_response'),

    # URL для приватной страницы пользователя
    path('private_page/', views.private_page, name='private_page'),

    # URL для просмотра новостной рассылки
    path('newsletter/<int:newsletter_id>/', views.view_newsletter, name='newsletter_detail'),

    # URL для отправки новостной рассылки
    path('send_newsletter/', views.send_newsletter, name='send_newsletter'),
    path('delete_response/<int:response_id>/', views.delete_response, name='delete_response'),
    path('accept_response/<int:response_id>/', views.accept_response, name='accept_response'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

