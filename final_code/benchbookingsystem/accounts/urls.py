from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_view, name='login'),
        path('home/', views.home, name='home'),


    path('signup/', views.signup_view, name='signup'),

    path('logout/', views.logout_view, name='logout'),

    path('vendor_1/', views.vendor_1, name='vendor_1'),
    path('vendor_2/', views.vendor_2, name='vendor_2'),
    path('vendor_3/', views.vendor_3, name='vendor_3'),
    path('manager/', views.manager, name='manager'),
    path('manager/users/', views.users_list, name='users_list'),
    path('manager/create-user/', views.create_user, name='create_user'),
    path('manager/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/', views.vendor_users, name='vendor_users'),

]