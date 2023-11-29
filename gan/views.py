from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
import os
from main.models import Photo, Session
from .models import esrganPhoto, texttoimagePhoto, imagetoimagePhoto
from django.core.files.base import ContentFile


def gan_control_panel_view(request):
    context = {}
    return render(request, 'gan/control_panel/control_panel.html', context)



def esrgan_site_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    esrganPhotos = esrganPhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'esrganPhotos' : esrganPhotos}
    return render(request, 'gan/control_panel/esrgan.html', context)

def delete_all_esrgan_photos(request):
    esrganPhotos = esrganPhoto.objects.all()
    
    for esrgan_photo in esrganPhotos:
        if esrgan_photo.image:
            if os.path.isfile(esrgan_photo.image.path):
                os.remove(esrgan_photo.image.path)

    esrganPhotos.delete()
    return redirect('esrgan_site_view')


def check_if_file_over_100kb(file_path):
    return os.path.getsize(file_path) / 1024 > 100


def ESRGAN_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        photo = get_object_or_404(Photo, id=photo_id)

        if check_if_file_over_100kb(photo.image.path):
              esrgan_photo = run_esrgan_on_image(photo.thumbnail_medium.path)
        else: esrgan_photo = run_esrgan_on_image(photo.image.path)


        return JsonResponse({'changed_image_url': esrgan_photo.image.url})
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
    esrgan_photo = esrganPhoto(title=title)
    esrgan_photo.image.save(title, ContentFile(image_content), save=True)

    return esrgan_photo




def text_to_image_site_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ttiPhotos = texttoimagePhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ttiPhotos' : ttiPhotos}
    return render(request, 'gan/control_panel/text_to_image.html', context)


def TEXTTOIMAGE_run(request):
    if request.method == 'POST':
        text_input = request.POST.get('text_input')
        
        import torch, cv2
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import io
        from diffusers import StableDiffusionPipeline
        import numpy as np

        model_id = "runwayml/stable-diffusion-v1-5"
        #model_id = "stabilityai/stable-diffusion-2-1"
        #pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, revision="fp16")
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        #can comment xformers
        pipe.enable_xformers_memory_efficient_attention()

        pipe = pipe.to('cuda')

        #turning to np array
        image = np.array(pipe(text_input).images[0])

        #fixing colors
        if len(image.shape) == 2:
            _, image_bytes = cv2.imencode('.png', image)
        else:
            _, image_bytes = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        #generating title
        title = '{}.png'.format(text_input)

        #saving
        image_file = InMemoryUploadedFile(io.BytesIO(image_bytes), None, title, 'image/png', len(image_bytes), None)
        new_photo = texttoimagePhoto(prompt=text_input, image=image_file)
        new_photo.save()

        return JsonResponse({'changed_image_url': new_photo.image.url})
    return HttpResponseBadRequest('Invalid request')


def delete_all_tti_photos(request):
    ttiPhotos = texttoimagePhoto.objects.all()
    
    for ttiPhoto in ttiPhotos:
        if ttiPhoto.image:
            if os.path.isfile(ttiPhoto.image.path):
                os.remove(ttiPhoto.image.path)

    ttiPhotos.delete()
    return redirect('text_to_image_site_view')




def image_to_image_site_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ttiPhotos = texttoimagePhoto.objects.all()
    itiPhotos = imagetoimagePhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ttiPhotos' : ttiPhotos, 'itiPhotos' : itiPhotos }
    return render(request, 'gan/control_panel/image_to_image.html', context)


def IMAGETOIMAGE_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        photo_model = request.POST.get('photo_model')

        if photo_model == 'Photo': photo = get_object_or_404(Photo, id=photo_id)
        elif photo_model == 'texttoimagePhoto': photo = get_object_or_404(texttoimagePhoto, id=photo_id)
        elif photo_model == 'imagetoimagePhoto': photo = get_object_or_404(imagetoimagePhoto, id=photo_id)
        else: print("error")


        strength = float(request.POST.get('prompt_strength'))
        text_input = request.POST.get('text_input')
        
        import torch, cv2
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import io
        from diffusers import AutoPipelineForImage2Image
        from diffusers.utils import make_image_grid, load_image
        import numpy as np

        pipe = AutoPipelineForImage2Image.from_pretrained(
            "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, variant="fp16", use_safetensors=None, safety_checker = None
        ).to("cuda")
        pipe.enable_model_cpu_offload()
        pipe.enable_xformers_memory_efficient_attention()

        init_image = load_image(photo.image.path)

        #turning to np array
        image = np.array(pipe(text_input, init_image, strength, guidance_scale=16.0).images[0])

        #fixing colors
        if len(image.shape) == 2:
            _, image_bytes = cv2.imencode('.png', image)
        else:
            _, image_bytes = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        #generating title
        title = '{}.png'.format(text_input)

        #saving
        image_file = InMemoryUploadedFile(io.BytesIO(image_bytes), None, title, 'image/png', len(image_bytes), None)
        new_photo = imagetoimagePhoto(prompt=text_input, image=image_file)
        new_photo.save()

        return JsonResponse({'changed_image_url': new_photo.image.url})
    return HttpResponseBadRequest('Invalid request')


def delete_all_iti_photos(request):
    itiPhotos = imagetoimagePhoto.objects.all()
    
    for itiPhoto in itiPhotos:
        if itiPhoto.image:
            if os.path.isfile(itiPhoto.image.path):
                os.remove(itiPhoto.image.path)

    itiPhotos.delete()
    return redirect('image_to_image_site_view')