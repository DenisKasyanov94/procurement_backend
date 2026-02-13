from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_confirmation(order):
    """
    Отправка подтверждения заказа клиенту
    """
    subject = f'Заказ #{order.id} оформлен'
    
    context = {
        'order': order,
        'user': order.user,
        'items': order.ordered_items.all(),
        'total': sum(
            item.quantity * item.product_info.price 
            for item in order.ordered_items.all()
        )
    }
    
    html_message = render_to_string('emails/order_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_admin_notification(order):
    """
    Отправка уведомления администратору о новом заказе
    """
    subject = f'Новый заказ #{order.id}'
    
    context = {
        'order': order,
        'user': order.user,
        'items': order.ordered_items.all(),
        'contact': order.contact,
        'total': sum(
            item.quantity * item.product_info.price 
            for item in order.ordered_items.all()
        )
    }
    
    html_message = render_to_string('emails/admin_notification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        ['admin@procurement.com'],  # Замени на реальный email администратора
        html_message=html_message,
        fail_silently=False,
    )


def send_registration_confirmation(user, token):
    """
    Отправка подтверждения регистрации
    """
    subject = 'Подтверждение регистрации'
    
    context = {
        'user': user,
        'token': token.key
    }
    
    html_message = render_to_string('emails/registration_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

