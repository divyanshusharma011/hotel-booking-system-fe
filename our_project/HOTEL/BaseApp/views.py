from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404,redirect
from .models import Hotel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.shortcuts import render as dj_render
from .models import Room, Booking
from .forms import BookingForm
from django.contrib import messages
from datetime import date
from .forms import ContactForm
from .models import Hotel
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from .forms import HotelForm
from .forms import RoomForm
from django.contrib.auth.models import User
from BaseApp.models import Room
from .models import Booking
from django.utils import timezone  # Add this import
from django.contrib.auth.forms import UserChangeForm
import requests
from django.conf import settings

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives


FLASK_API_URL = 'http://127.0.0.1:5000/bookings'  # or use settings.FLASK_API_URL

def HomeView(request):
    return render(request, 'home.html', {} )  

def contact(request):
    return render(request, 'contact.html')  


def AboutView(request):
    return render(request,'about.html')

def Facility(request):
    return render(request,'facility.html')

def home(request):
    return render(request, 'home.html')


def Policy(request):
    return render(request, 'policy.html')

def Terms(request):
    return render(request, 'terms.html')

def Maps(request):
    return render(request, 'map.html')

def hotel_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        hotels = Hotel.objects.filter(
            Q(location__icontains=search_query) | Q(name__icontains=search_query)
        )
    else:
        hotels = Hotel.objects.all()

    context = {
        'hotels': hotels,
        'search_query': search_query,
    }
    return render(request, 'hotels/hotel_list.html', context)


def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, 'hotels/hotel_detail.html', {'hotel': hotel})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:  # 👈 redirect admin
                return redirect('admin_dashboard')  # or 'admin_dashboard' if that's the URL name
            return redirect('home')  # 👈 normal user
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

from django.contrib.auth.models import User
from django.template.loader import render_to_string

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                f"/reset_password/{uid}/{token}/"
            )

            subject = 'Password Reset Link'
            message = f'Click the link to reset your password: {reset_link}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('login')
        else:
            messages.error(request, "No account found with that email.")
    
    return render(request, 'forgot_password.html')


from django.contrib.auth.forms import SetPasswordForm

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password has been reset successfully.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'reset_password.html', {'form': form})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('forgot_password')


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')  # or 'admin_dashboard'
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            
            # Directly save the booking in Django
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.save()

            # Optionally, notify the Flask API about the booking if needed
            payload = {
                'user': request.user.username,
                'hotel': room.hotel.name,
                'date': str(check_in),
                'nights': (check_out - check_in).days
            }
            response = requests.post(FLASK_API_URL, json=payload)

            if response.status_code == 201:
                return redirect('booking_success')
            else:
                messages.error(request, f"Failed to notify external system: {response.json().get('message', 'Error')}")
    else:
        form = BookingForm()

    return render(request, 'book_room.html', {'form': form, 'room': room})


def booking_success(request):
    return render(request, 'booking_success.html')

@login_required
def my_bookings(request):
    response = requests.get(f"{FLASK_API_URL}?user={request.user.username}")
    if response.status_code == 200:
        bookings = response.json()
    else:
        bookings = []
        messages.error(request, "Could not fetch your bookings.")

    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    response = requests.put(f"{FLASK_API_URL}/{booking_id}", json={"status": "cancelled"})
    if response.status_code == 200:
        messages.success(request, "Your booking has been cancelled.")
    else:
        messages.error(request, "Cancellation failed.")
    return redirect('my_bookings.html')
  # Update with your actual bookings page URL name

@login_required
def delete_booking(request, booking_id):
    response = requests.delete(f"{FLASK_API_URL}/{booking_id}")
    if response.status_code == 200:
        messages.success(request, "Booking deleted successfully.")
    else:
        messages.error(request, "Could not delete booking.")
    return redirect('my_bookings.html')
  # Adjust URL name as per your project

def contact_view(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form, 'success': success})

@staff_member_required
def admin_dashboard(request):
    try:
        today = timezone.now().date()
        
        total_hotels = Hotel.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        available_rooms = Room.objects.filter(available=True).count()
        
        # CORRECTED: Removed __date lookup for DateFields
        todays_bookings = Booking.objects.filter(
            check_in__lte=today,
            check_out__gte=today
        ).count()

        context = {
            'admin_user': request.user,
            'total_hotels': total_hotels,
            'active_users': active_users,
            'available_rooms': available_rooms,
            'todays_bookings': todays_bookings,
        }
        return render(request, 'admin_panel/dashboard.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'total_hotels': 0,
            'active_users': 0,
            'available_rooms': 0,
            'todays_bookings': 0,
        }
        return render(request, 'admin_panel/dashboard.html', context, status=500)
    
    
@staff_member_required
def admin_hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'admin_panel/hotel_list.html', {'hotels': hotels})

@staff_member_required
def add_hotel(request):
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hotel_list')
    else:
        form = HotelForm()
    return render(request, 'admin_panel/add_hotel.html', {'form': form})


@staff_member_required
def add_room_to_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            messages.success(request, 'Room added successfully!')
            return redirect('admin_hotel_list')
    else:
        form = RoomForm()

    return render(request, 'admin_panel/add_room.html', {'form': form, 'hotel': hotel})



@staff_member_required
def admin_user_list(request):
    users = User.objects.all().order_by('-date_joined')
    print("Fetched Users:", users)  # 👈 Debug print
    return render(request, 'admin_panel/user_list.html', {'users': users})


@staff_member_required
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'admin_panel/user_detail.html', {'user': user})


@staff_member_required
def update_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('admin_hotel_list')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'admin_panel/edit_hotel.html', {'form': form, 'hotel': hotel})

@staff_member_required
def delete_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        hotel.delete()
        messages.success(request, 'Hotel deleted successfully!')
        return redirect('admin_hotel_list')
    return render(request, 'admin_panel/delete_hotel.html', {'hotel': hotel})

@staff_member_required
def room_list(request):
    rooms = Room.objects.select_related('hotel').all()
    return render(request, 'admin_panel/room_list.html', {'rooms': rooms})

@staff_member_required
def edit_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully!')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'admin_panel/edit_room.html', {'form': form, 'room': room})

def delete_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted successfully!')
    return redirect('room_list')  # make sure this is the name of your room list url

def admin_booking_list(request):
    bookings = Booking.objects.select_related('user', 'room').all().order_by('-created_at')
    return render(request, 'admin_panel/booking_list.html', {'bookings': bookings})

def cancel_booking(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = "Cancelled"
        booking.save()
    return redirect('admin_booking_list')  # Or wherever your booking list is

def delete_booking(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.delete()
    return redirect('admin_booking_list')


@staff_member_required
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "You cannot edit a superuser!")
        return redirect('admin_user_list')

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.is_active = bool(request.POST.get('is_active'))
        user.is_staff = bool(request.POST.get('is_staff'))
        user.save()

        messages.success(request, 'User updated successfully!')
        return redirect('admin_user_list')

    return render(request, 'admin_panel/edit_user.html', {'user': user})



@staff_member_required
def delete_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('user_list')

    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "You cannot delete yourself!")
        elif user.is_superuser and not request.user.is_superuser:
            messages.error(request, "You cannot delete a superuser!")
        else:
            user.delete()
            messages.success(request, 'User deleted successfully!')
        return redirect('admin_user_list')

    return render(request, 'admin_panel/delete_user.html', {'user': user})
