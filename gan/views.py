from django.http import HttpResponse, HttpResponseBadRequest
import subprocess
from django.shortcuts import render
import os
import sys
from django.http import JsonResponse

from main.models import Photo, Session


def gan_control_panel(request):
    context = {}
    sessions = Session.objects.all()
    photos = Photo.objects.all()

    context = {'sessions': sessions, 'photos': photos}

    return render(request, 'gan/test.html', context)





def ESRGAN_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')

        # Uzyskaj obiekt Photo na podstawie sesji i zdjęcia
        photo = Photo.objects.get(id=photo_id)

        changed_image_url = photo.thumbnail_medium.url

        return JsonResponse({'changed_image_url': changed_image_url})
    return HttpResponseBadRequest('Invalid request')


#def ESRGAN_run(request):
#    if request.method == 'POST':
#        try:
#            script_path = 'gan/programs/ESRGAN/test.py'
##            subprocess.run(['pipenv', 'run', 'python', script_path])
#            return render(request, 'gan/test.html')
#        except Exception as e:
#            return render(request, 'main/home.html', {'error_message': str(e)})
#
#    return render(request, 'gan/test.html')
