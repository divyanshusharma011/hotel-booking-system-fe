from django.contrib import admin
from .models import Hotel, Room
from .models import Booking
from .models import ContactMessage


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

class HotelAdmin(admin.ModelAdmin):
    inlines = [RoomInline]

admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'room',
        'number_of_members',
        'check_in',
        'check_out',
        'payment_method',
        'status',
        'created_at',
    )
    list_filter = ('status', 'payment_method', 'check_in', 'check_out')
    search_fields = ('full_name', 'user__username', )
    ordering = ('-created_at',)


admin.site.register(ContactMessage)

