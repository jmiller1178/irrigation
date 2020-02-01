from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(name='rabbitmq_host')
def get_rabbitmq_host():
    rabbitmq_host = ''
    if hasattr(settings, 'RABBITMQ_HOST'):
        rabbitmq_host =  settings.RABBITMQ_HOST
    return rabbitmq_host

@register.simple_tag(name='rabbitmq_username')
def get_rabbitmq_username():
    rabbitmq_username = ''
    if hasattr(settings, 'RABBITMQ_USERNAME'):
        rabbitmq_username = settings.RABBITMQ_USERNAME
    return rabbitmq_username

@register.simple_tag(name='rabbitmq_password')
def get_rabbitmq_password():
    rabbitmq_password = ''
    if hasattr(settings, 'RABBITMQ_PASSWORD'):
        rabbitmq_password = settings.RABBITMQ_PASSWORD
    return rabbitmq_password

@register.simple_tag(name='rabbitmq_ws_port')
def get_rabbitmq_ws_port():
    rabbitmq_password = ''
    if hasattr(settings, 'RABBITMQ_WS_PORT'):
        rabbitmq_password = settings.RABBITMQ_WS_PORT
    return rabbitmq_password
