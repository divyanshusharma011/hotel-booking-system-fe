from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Booking
from .models import ContactMessage
from .models import Hotel, Room
from .models import UserProfile 

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile  # Import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'gender', 'address']

    def save(self, commit=True):
        # Save the user object first without committing to the database yet
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # If commit is True, save the user object to the database
        if commit:
            user.save()  # Save the user first
            
            # Explicitly create the user profile
            profile = UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                gender=self.cleaned_data['gender'],
                address=self.cleaned_data['address']
            )
        
        return user


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'  # Fixing: should be a string, not a list
        exclude = ['user', 'room','status']  

        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'form-control',
            }),
            'number_of_members': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control',
            }),
            'check_in': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'check_out': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
            }),
        }






class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

        