from django.db import models
from django.contrib.auth.models import User
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()

    def __str__(self):
        return self.user.username



class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='hotel_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)  # ✅ Added

    def __str__(self):
        return f"{self.room_type} - {self.hotel.name}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100, default="Guest")
    number_of_members = models.PositiveIntegerField(default=1)
    check_in = models.DateField()
    check_out = models.DateField()

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('paypal', 'PayPal'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='cash'
    )

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')

    created_at = models.DateTimeField(auto_now_add=True)

    def is_cancellable(self):
        return self.check_in > date.today() and self.status == 'confirmed'

    def __str__(self):
        return f"{self.full_name} - {self.room} ({self.check_in} to {self.check_out})"

    class Meta:
        db_table = 'booking_model' 



class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"






