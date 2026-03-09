from django.urls import path
from . import views

urlpatterns = [

    path("my-bookings/", views.my_bookings, name="my_bookings"),

    path("connect/<int:booking_id>/", views.connect_bench, name="connect_bench"),
        path('monitor/<int:booking_id>/', views.monitor_page, name='monitor_page'),

    path("heartbeat/<int:booking_id>/", views.heartbeat, name="heartbeat"),
    path("disconnect/<int:booking_id>/", views.disconnect_bench, name="disconnect_bench"),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),

]