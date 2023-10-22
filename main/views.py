from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from .forms import SignupForm
from .forms import SessionForm
from .models import Session
from .forms import PrivateSessionForm
from .forms import PhotoForm
from .models import Photo
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files import File
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import json
import io
import pyzipper




def index(request):
    context = {}
    return render(request, 'main/base.html', context)

def home(request):
    context = {}
    return render(request, 'main/home.html', context)

def portfolio(request):
    context = {}
    return render(request, 'main/portfolio.html', context)

def pricing(request):
    context = {}
    return render(request, 'main/pricing.html', context)

def weddingSession(request):
    context = {}
    return render(request, 'main/session/wedding.html', context)
def newbornSession(request):
    context = {}
    return render(request, 'main/session/newborn.html', context)
def familySession(request):
    context = {}
    return render(request, 'main/session/family.html', context)

def profile(request):
    context = {}
    return render(request, 'main/profile.html', context)

def sign_up(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else: form = SignupForm()
    context = {'form':form}
    return render(request, 'registration/sign_up.html', context)

def log_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/home')
    context = {}
    return render(request, 'registration/logout.html', context)



@user_passes_test(lambda user: user.is_superuser)
def control_panel(request):
    context = {}
    return render(request, 'main/control_panel/control_panel.html', context)

@user_passes_test(lambda user: user.is_superuser)
def create_session(request):
    if request.method == 'POST':
        name = request.POST['name']
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save()
            return redirect('view_session', name=name)
    else: form = SessionForm()
    context = {'form':form}
    return render(request, 'main/control_panel/create_session.html', context)




@user_passes_test(lambda user: user.is_superuser)
def delete_sessions(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions}
    return render(request, 'main/control_panel/delete_sessions.html', context)

@user_passes_test(lambda user: user.is_superuser)
def delete_session(request,name):
    session = Session.objects.filter(name=name).delete()
    context = {'session': session}
    return render(request, 'main/session/session_template.html', context)


@user_passes_test(lambda user: user.is_superuser)
def view_sessions(request):
    sessions = Session.objects.all()

    for session in sessions:
        photos = session.photo_set.all()
        photos_size = []
        for photo in photos:
            photos_size.append(photo.image.size / (1024*1024))
        photos_size_in_session = round(sum(photos_size))
        session.photos_size_in_session = photos_size_in_session
    context = {'sessions': sessions}
    return render(request, 'main/control_panel/view_sessions.html', context)


def view_session(request, name):
    session = get_object_or_404(Session, name=name)
    photos = session.photo_set.all()
    photos_size = []
    context = {}
    for photo in photos:
        photos_size.append(photo.image.size/(1024*1024))
    photos_size_in_session = round(sum(photos_size))

    if request.user.is_superuser:
        context = {'session': session, 'photos':photos, 'photos_size_in_session':photos_size_in_session}
        return render(request, 'main/session/private_session.html', context)

    if request.method == 'POST':
        form = PrivateSessionForm(request.POST)
        if form.is_valid():
            entered_password = form.cleaned_data['password']
            if entered_password == session.password:
                context = {'session': session, 'photos':photos}
                return render(request, 'main/session/private_session.html', context)
    
    else:
        form = PrivateSessionForm()
    
    context = {'form': form}
    return render(request, 'main/session/private_session_form.html', context)


@user_passes_test(lambda user: user.is_superuser)
def photos_sessions(request):
    context = {}
    sessions = Session.objects.all()

    if request.method == 'POST':
        if 'clear_session' in request.POST:
            session_id =  request.POST['session']
            dropped_photo = Photo.objects.filter(session_id=session_id)
            for photo in dropped_photo:
                photo.delete()


        if 'delete_session' in request.POST:
            session_id =  request.POST['session']
            dropped_photo = Photo.objects.filter(session_id=session_id)
            for photo in dropped_photo:
                photo.delete()
                
            Session.objects.filter(id=session_id).delete()


        if 'add_images_session' in request.POST:
            form = PhotoForm(request.POST, request.FILES)
            if form.is_valid():
                images = request.FILES.getlist('image')
                image_type = request.POST.get('image_type')
                uploaded_photos = []

                for image in images:
                    uploaded_photos.append('a')
                    print(uploaded_photos)
                    try:
                        img = Image.open(image)
                        if img.format !='JPEG':
                            raise ValidationError("not jpeg")
                        
                        if image_type == 'original':
                            photo = Photo(title=image.name, image=image, session=form.cleaned_data['session'])
                            photo.save()

                        elif image_type == 'resized':
                            create_watermarked_photo(image, form.cleaned_data['session'], request.POST['watermark_opacity'])

                    except Exception as e:
                        form.add_error('image',str(e))

                img_obj = form.instance
                context = {'form': form, 'img_obj': img_obj, 'sessions':sessions,  'uploaded_photos': uploaded_photos}
                return render(request, 'main/control_panel/photos_sessions.html', context)
    else:
        form = PhotoForm()

    photos = Photo.objects.all()
    context = {'sessions': sessions, 'photos': photos}
    return render(request, 'main/control_panel/photos_sessions.html', context)


def update_photo_select(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        photo.selected_to_edit = not photo.selected_to_edit
        photo.save()
        return JsonResponse({'status': 'ok'})
    

def download_photos_zip(request, name):
    session = get_object_or_404(Session, name=name)
    photos = session.photo_set.all()
    zip_buffer = io.BytesIO()
    password = f"{session.password}"

    with pyzipper.AESZipFile(zip_buffer, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zip_file:
        zip_file.setpassword(password.encode())
        for photo in photos:
            zip_file.write(photo.image.path, arcname=photo.image.name)
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename={}'.format(f"{name}_photos.zip")
    return response


import zipfile
def download_photos_folder(request, name):
    session = get_object_or_404(Session, name=name)
    photos = session.photo_set.all()
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for photo in photos:
            with open(photo.image.path, 'rb') as photo_file:
                zip_file.writestr(photo.image.name, photo_file.read())

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={name}_photos.zip'

    return response





def update_photo_select_multiple(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            photo_ids = data.get('photoIds', [])

            for photo_id in photo_ids:
                photo = get_object_or_404(Photo, id=photo_id)
                photo.selected_to_edit = False
                photo.save()
            return JsonResponse({'message': 'Photos updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'message': 'Method not allowed'}, status=405)


def create_watermarked_photo(image, session, watermark_opacity):
    img = Image.open(image)
    img.thumbnail((img.width, img.height))
    text = "moccastudio"
    opacity = int(watermark_opacity)
    grid = 5

    img_width, img_height = img.size
    text_size = img_width // 32
    font = ImageFont.truetype("arial.ttf", text_size)
    text_color = (255, 255, 255, opacity)

    cell_width = img_width // grid
    cell_height = img_height // grid
    for i in range(grid**2):
        row = i // grid
        col = i % grid
        x = col * cell_width + cell_width // 2 - cell_width // 3
        y = row * cell_height + cell_height // 2 

        text_image = Image.new('RGBA', (cell_width, cell_height), (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((cell_width // 2, cell_height // 2), text, fill=text_color, font=font, anchor="mm")
        rotated_text = text_image.rotate(45, expand=True)
        img.paste(rotated_text, (x - cell_width // 2, y - cell_height // 2), rotated_text)

    output_io = BytesIO()
    img.save(output_io, format='JPEG') 
    output_io.seek(0)

    photo = Photo(title=image.name, image=File(output_io, name=image.name), session=session)
    photo.save()