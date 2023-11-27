from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
import os
from main.models import Photo, Session
from .models import ganPhoto
from django.core.files.base import ContentFile


def gan_control_panel_view(request):
    context = {}
    return render(request, 'gan/control_panel/control_panel.html', context)



def esrgan_site_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ganPhotos = ganPhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ganPhotos' : ganPhotos}
    return render(request, 'gan/control_panel/esrgan.html', context)

def delete_all_gan_photos(request):
    ganPhotos = ganPhoto.objects.all()
    
    for gan_photo in ganPhotos:
        if gan_photo.image:
            if os.path.isfile(gan_photo.image.path):
                os.remove(gan_photo.image.path)

    ganPhotos.delete()
    return redirect('esrgan_site_view')


def check_if_file_over_100kb(file_path):
    return os.path.getsize(file_path) / 1024 > 100


def ESRGAN_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        photo = get_object_or_404(Photo, id=photo_id)

        if check_if_file_over_100kb(photo.image.path):
              gan_photo = run_esrgan_on_image(photo.thumbnail_medium.path)
        else: gan_photo = run_esrgan_on_image(photo.image.path)


        return JsonResponse({'changed_image_url': gan_photo.image.url})
    return HttpResponseBadRequest('Invalid request')


def run_esrgan_on_image(input_image):
    #modules in function will lag single image, drop to start to transfer lag to overall entire app
    import glob, cv2, torch, numpy
    from gan.programs.ESRGAN.RRDBNet_arch import RRDBNet #it might lag 

    model_path = 'gan/programs/ESRGAN/models/RRDB_ESRGAN_x4.pth'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = RRDBNet(3, 3, 64, 23, gc=32)
    model.load_state_dict(torch.load(model_path, map_location=device), strict=True)
    model.eval()
    model = model.to(device)

    img = cv2.imread(input_image, cv2.IMREAD_COLOR)
    img = img * 1.0 / 255
    img = torch.from_numpy(numpy.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
    img_LR = img.unsqueeze(0)
    img_LR = img_LR.to(device)

    with torch.no_grad():
        output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()

    output = numpy.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
    output = (output * 255.0).round()

    input_filename, input_file_extension = os.path.splitext(os.path.basename(input_image))
    title = '{}_esrgan.png'.format(input_filename)
    image_content = cv2.imencode('.png', output)[1].tobytes()
    gan_photo = ganPhoto(title=title)
    gan_photo.image.save(title, ContentFile(image_content), save=True)

    return gan_photo




def text_to_image_site_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ganPhotos = ganPhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ganPhotos' : ganPhotos}
    return render(request, 'gan/control_panel/text_to_image.html', context)


def TEXTTOIMAGE_run(request):
    if request.method == 'POST':
        text_input = request.POST.get('text_input')
        return JsonResponse({'changed_text': text_input})
    return HttpResponseBadRequest('Invalid request')