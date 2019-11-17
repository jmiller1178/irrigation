from django.conf.urls import url
from sprinklesmart import views

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
]
