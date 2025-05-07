from django.urls import path
from . import views
from .views import edit_room_view
from .views import admin_booking_list
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('contact/', views.contact_view, name='contact'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/hotels/', views.admin_hotel_list, name='admin_hotel_list'),
    path('admin-panel/hotels/add/', views.add_hotel, name='add_hotel'),
    path('admin-panel/hotels/<int:hotel_id>/add-room/', views.add_room_to_hotel, name='add_room_to_hotel'),
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin-panel/hotel/<int:hotel_id>/edit/', views.update_hotel, name='update_hotel'),
    path('admin-panel/hotel/<int:hotel_id>/delete/', views.delete_hotel, name='delete_hotel'),
    path('admin-panel/rooms/', views.room_list, name='room_list'),
    path('admin/rooms/edit/<int:room_id>/', edit_room_view, name='edit_room'),
    path('admin/rooms/delete/<int:room_id>/', views.delete_room_view, name='delete_room'),
    path('admin/bookings/', admin_booking_list, name='admin_booking_list'),
    path('admin/bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('admin/bookings/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('admin/users/edit/<int:user_id>/', views.edit_user_view, name='edit_user'),
    path('admin/users/delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
     path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    
]

    

