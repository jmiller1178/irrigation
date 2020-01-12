from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^manually_schedule/', views.manually_schedule, name='manually_schedule'),
    url(r'^create_schedule/', views.create_schedule, name='create_schedule'),
    url(r'^zone_control/(?P<zoneId>\d+)/$', views.zone_control, name='zone_control'),
    url(r'^zone_toggle/(?P<zoneId>\d+)/$', views.zone_toggle, name='zone_toggle'),
    url(r'^rpi_gpio_request_cancel/(?P<id>\d+)/$',  views.rpi_gpio_request_cancel, name='rpi_gpio_request_cancel'),
    url(r'^rpi_gpio_request_cancel_all/', views.rpi_gpio_request_cancel_all, name='rpi_gpio_request_cancel_all'),
    url(r'^m/$', views.mobile_index, name='mobile_index'),
    url(r'^m/mobile_zone_control/(?P<zoneId>\d+)/$', views.mobile_zone_control, name='mobile_zone_control'),
    url(r'^get_schedule/(?P<scheduleId>\d+)/$',  views.get_schedule,  name='get_schedule'), 
    url(r'^enable_system/$', views.enable_system, name='c'),
    url(r'^disable_system/$', views.disable_system, name='disable_system'),
    url(r'^enable_24VAC/$', views.enable_24VAC, name='enable_24VAC'),
    url(r'^disable_24VAC/$', views.enable_24VAC, name='disable_24VAC'),
]
