from django.urls import path
from . import views


app_name = 'chat'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),

    path('api/username-check/', views.username_check, name='username_check'),
    path('api/search-users/', views.search_users, name='search_users'),
    path('api/personal-room/', views.get_personal_room, name='get_personal_room'),
    path('api/send-message/', views.send_message, name='send_message'),

    path('ws-test/', views.ws_test, name='ws_test'),
]
