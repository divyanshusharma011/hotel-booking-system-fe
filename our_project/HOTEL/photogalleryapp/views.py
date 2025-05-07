from django.shortcuts import render
from .models import Photo

def photo_gallery(request):
    photos = list(Photo.objects.all().order_by('-uploaded_at'))

    # Group photos into chunks of 10
    rows = [photos[i:i+10] for i in range(0, len(photos), 10)]

    return render(request, 'photogalleryapp/gallery.html', {'rows': rows})


def video_quotes_page(request):
    return render(request, 'photogalleryapp/video_quotes.html')
