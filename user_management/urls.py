from django.urls import path
from . import views


app_name = 'user_management'
urlpatterns = [
    path('', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('my-profile', views.my_profile, name='my_profile'),
    path('record-maintenance', views.record_maintenance, name='record_maintenance'),
    path('logout', views.logout, name='logout'),
    path('approve', views.approve, name='approve'),
    path('reject', views.reject, name='reject'),
    path('approve-member', views.approve_member, name='approve_member'),
    path('paid-maintenance', views.paid_maintenance, name='paid_maintenance')
]
