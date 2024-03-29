from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
import os, io
from main.models import Photo, Session
from .models import esrganPhoto, texttoimagePhoto, imagetoimagePhoto, inpaintPhoto
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import numpy
import base64
from PIL import Image

#views build
#modules_name : 
#   _view - views of modules site
#   _run  - checking post, running script ,returning json
#   _script  - load heavy modules, executing heavy script, returning and saving image
#   _delete_all_photos  - delete all photos from models and databse

def gan_control_panel_view(request):
    context = {}
    return render(request, 'gan/control_panel/control_panel.html', context)


#esrgan
def esrgan_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    esrganPhotos = esrganPhoto.objects.all()
    ttiPhotos = texttoimagePhoto.objects.all()
    itiPhotos = imagetoimagePhoto.objects.all()

    context = {'sessions': sessions,
               'photos': photos,
               'esrganPhotos' : esrganPhotos,
               'ttiPhotos' : ttiPhotos,
               'itiPhotos' : itiPhotos,
              }
    return render(request, 'gan/control_panel/esrgan.html', context)

def esrgan_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        photo_model = request.POST.get('photo_model')

        photo = check_image_model(photo_model, photo_id)
        if photo_model == 'Photo' and check_if_file_over_100kb(photo.image.path):
            esrgan_photo = esrgan_script(photo.image.path)
            #esrgan_photo = esrgan_script(photo.thumbnail_medium.path)
        else: esrgan_photo = esrgan_script(photo.image.path)

        return JsonResponse({'changed_image_url': esrgan_photo.image.url})
    return HttpResponseBadRequest('Invalid request')

def esrgan_script(input_image):
    #modules in function will lag single image, drop to start to transfer lag to overall entire app
    import glob, cv2, torch
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

def esrgan_delete_all_photos(request):
    esrganPhotos = esrganPhoto.objects.all()
    
    for esrgan_photo in esrganPhotos:
        if esrgan_photo.image:
            if os.path.isfile(esrgan_photo.image.path):
                os.remove(esrgan_photo.image.path)

    esrganPhotos.delete()
    return redirect('esrgan_view')


#text to image
def tti_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ttiPhotos = texttoimagePhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ttiPhotos' : ttiPhotos}
    return render(request, 'gan/control_panel/text_to_image.html', context)

def tti_run(request):
    if request.method == 'POST':
        text_input = request.POST.get('text_input')
        seed = int(request.POST.get('seed_input'))
        guidance_scale = float(request.POST.get('guidance_scale_input'))
        steps = int(request.POST.get('steps_input'))
        model = request.POST.get('model_input')

        new_photo = tti_script(text_input, seed, guidance_scale, steps, model)
        return JsonResponse({'changed_image_url': new_photo.image.url})
    return HttpResponseBadRequest('Invalid request')

def tti_script(text_input, seed, guidance_scale, steps, model):
    import torch, cv2

    torch.manual_seed(seed)

    if torch.cuda.is_available(): #gpu usage
        if model == "stabilityai/stable-diffusion-xl-base-1.0":
            from diffusers import StableDiffusionXLPipeline
            pipe = StableDiffusionXLPipeline.from_pretrained(model, torch_dtype=torch.float16)
        elif model == "kandinsky-community/kandinsky-2-2-decoder":
            from diffusers import AutoPipelineForText2Image
            pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float16)
        else: 
            from diffusers import StableDiffusionPipeline
            pipe = StableDiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16)
        pipe.to('cuda')
        pipe.enable_xformers_memory_efficient_attention()

    else: #cpu usage
        if model == "stabilityai/stable-diffusion-xl-base-1.0":
            from diffusers import StableDiffusionXLPipeline
            pipe = StableDiffusionXLPipeline.from_pretrained(model)
        elif model == "kandinsky-community/kandinsky-2-2-decoder":
            from diffusers import AutoPipelineForText2Image
            pipe = AutoPipelineForText2Image.from_pretrained(model)
        else: 
            from diffusers import StableDiffusionPipeline
            pipe = StableDiffusionPipeline.from_pretrained(model)
        pipe.to('cpu')

    #turning to np array
    image = numpy.array(pipe(text_input, guidance_scale=guidance_scale, num_inference_steps = steps).images[0])

    #fixing colors
    if len(image.shape) == 2:  _, image_bytes = cv2.imencode('.png', image)
    else:   _, image_bytes = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
    #generating title
    title = '{}.png'.format(text_input)

    #saving
    image_file = InMemoryUploadedFile(io.BytesIO(image_bytes), None, title, 'image/png', len(image_bytes), None)


    new_photo = texttoimagePhoto(prompt=text_input, image=image_file)
    new_photo.save()
    return new_photo

def tti_delete_all_photos(request):
    ttiPhotos = texttoimagePhoto.objects.all()
    
    for ttiPhoto in ttiPhotos:
        if ttiPhoto.image:
            if os.path.isfile(ttiPhoto.image.path):
                os.remove(ttiPhoto.image.path)

    ttiPhotos.delete()
    return redirect('tti_view')


#image to image
def iti_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ttiPhotos = texttoimagePhoto.objects.all()
    itiPhotos = imagetoimagePhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ttiPhotos' : ttiPhotos, 'itiPhotos' : itiPhotos }
    return render(request, 'gan/control_panel/image_to_image.html', context)

def iti_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        photo_model = request.POST.get('photo_model')
        photo = check_image_model(photo_model, photo_id)
        is_composition = request.POST.get('is_composition')

        seed = int(request.POST.get('seed_input'))
        guidance_scale = float(request.POST.get('guidance_scale_input'))
        strength_scale = float(request.POST.get('strength_scale_input'))
        text_input = request.POST.get('text_input')
        model = request.POST.get('model_input')

        new_photo = iti_script(photo, seed, guidance_scale, strength_scale, text_input, model, is_composition)
        
        return JsonResponse({'changed_image_url': new_photo.image.url})
    return HttpResponseBadRequest('Invalid request')

def iti_script(photo, seed, guidance_scale, strength_scale, text_input, model, IsComposition):
        import torch, cv2
        from diffusers.utils import load_image, make_image_grid
        from diffusers import AutoPipelineForImage2Image

        torch.manual_seed(seed)

        if torch.cuda.is_available(): #gpu usage
            pipe = AutoPipelineForImage2Image.from_pretrained(model, torch_dtype=torch.float16, use_safetensors=None, safety_checker = None)
            pipe.to('cuda')
            pipe.enable_model_cpu_offload()
            pipe.enable_xformers_memory_efficient_attention()

        else: #cpu usage
            pipe = AutoPipelineForImage2Image.from_pretrained(model)
            pipe.to('cpu')


        #loading image
        
        try:
            init_image = load_image(photo.thumbnail_medium.path)
        except AttributeError:
            init_image = load_image(photo.image.path)

        #turning to np array
        if not IsComposition:
            generated_image = pipe(
                                    prompt = text_input,
                                    image = init_image,
                                    strength = strength_scale,
                                    guidance_scale=guidance_scale,
                                  ).images[0]
            
            image = numpy.array(generated_image)
        else:
            rows = cols = 5
            strength_range = (0.0, 1.0)
            guidance_scale_range = (0.0, 20.0)

            strength_tab = []
            guidance_tab = []
            print(strength_tab)
            print(guidance_tab)

            images = []
            for row in range(rows):
                for col in range(cols):
                    strength = round(strength_range[0] + col * ((strength_range[1] - strength_range[0]) / (cols - 1)), 2)
                    guidance_scale = round(guidance_scale_range[0] + row * ((guidance_scale_range[1] - guidance_scale_range[0]) / (rows - 1)), 2)

                    img = pipe(prompt=text_input, image=init_image, strength=strength, guidance_scale=guidance_scale).images[0]
                    images.append(img)

                    strength_tab.append(strength)
                    guidance_tab.append(guidance_scale)

            grid = make_image_grid(images, rows=rows, cols=cols)
            image = numpy.array(grid)

            strength_scale = strength_tab
            guidance_scale = guidance_tab
            print("strenght")
            print(strength_scale)
            print(strength_tab)

            print("guidance")
            print(guidance_scale)
            print(guidance_tab)


        #fixing colors
        if len(image.shape) == 2: _, image_bytes = cv2.imencode('.png', image)
        else: _, image_bytes = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        

        #generating title
        title = '{}.png'.format(text_input)


        #saving
        image_file = InMemoryUploadedFile(io.BytesIO(image_bytes), None, title, 'image/png', len(image_bytes), None)

        new_photo = imagetoimagePhoto(prompt=text_input, image=image_file, model_used=model, strength=strength_scale , guidance=guidance_scale)
        new_photo.save()
        return new_photo

def iti_delete_all_photos(request):
    itiPhotos = imagetoimagePhoto.objects.all()
    
    for itiPhoto in itiPhotos:
        if itiPhoto.image:
            if os.path.isfile(itiPhoto.image.path):
                os.remove(itiPhoto.image.path)

    itiPhotos.delete()
    return redirect('iti_view')


#inpaint
def inpaint_view(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    ttiPhotos = texttoimagePhoto.objects.all()
    itiPhotos = imagetoimagePhoto.objects.all()
    inpaintPhotos = inpaintPhoto.objects.all()

    context = {'sessions': sessions, 'photos': photos, 'ttiPhotos' : ttiPhotos, 'itiPhotos' : itiPhotos, 'inpaintPhotos' : inpaintPhotos }
    return render(request, 'gan/control_panel/inpaint.html', context)

def inpaint_run(request):
    if request.method == 'POST':
        text_input = request.POST.get('text_input')
        seed = int(request.POST.get('seed_input'))
        guidance_scale = float(request.POST.get('guidance_scale_input'))
        strength_scale = float(request.POST.get('strength_scale_input'))

        model = request.POST.get('model_input')
        mask_data_url = request.POST.get('maskUrl')
        is_composition = request.POST.get('is_composition')

        photo_id = request.POST.get('photo_id')
        photo_model = request.POST.get('photo_model')
        photo = check_image_model(photo_model, photo_id)


        new_photo = inpaint_script(photo,mask_data_url,text_input,seed, guidance_scale, strength_scale, model, is_composition)

        return JsonResponse({'changed_image_url': new_photo.image.url})
    return HttpResponseBadRequest('Invalid request')

def inpaint_script(photo,mask_data_url,text_input,seed, guidance_scale, strength_scale, model, IsComposition):
        import torch, cv2
        from diffusers.utils import load_image, make_image_grid
        from diffusers import AutoPipelineForInpainting

        #process mask
        _, encoded_data = mask_data_url.split(',', 1)
        image_data = base64.b64decode(encoded_data)
        image_io = io.BytesIO(image_data)
        masked_image = Image.open(image_io)

        
        torch.manual_seed(seed)

        if torch.cuda.is_available(): #gpu usage
            if model == "diffusers/stable-diffusion-xl-1.0-inpainting-0.1":
                pipe = AutoPipelineForInpainting.from_pretrained(model, torch_dtype=torch.float16 , variant="fp16", use_safetensors=None, safety_checker = None)
            elif model == "kandinsky-community/kandinsky-2-2-decoder-inpaint":
                pipe = AutoPipelineForInpainting.from_pretrained(model, torch_dtype=torch.float16 , variant="fp16", use_safetensors=None, safety_checker = None)
            else: 
                pipe = AutoPipelineForInpainting.from_pretrained(model, torch_dtype=torch.float16 , variant="fp16", use_safetensors=None, safety_checker = None)
            pipe.enable_xformers_memory_efficient_attention()
            pipe.to('cuda')
        else: #cpu usage
            if model == "diffusers/stable-diffusion-xl-1.0-inpainting-0.1":
                pipe = AutoPipelineForInpainting.from_pretrained(model, use_safetensors=None, safety_checker = None)
            elif model == "kandinsky-community/kandinsky-2-2-decoder-inpaint":
                pipe = AutoPipelineForInpainting.from_pretrained(model, use_safetensors=None, safety_checker = None)
            else: 
                pipe = AutoPipelineForInpainting.from_pretrained(model, use_safetensors=None, safety_checker = None)
            pipe.to('cup')


        #loading image and mask
        try:
            init_image = load_image(photo.thumbnail_medium.path)
        except AttributeError:
            init_image = load_image(photo.image.path)

        mask_image = load_image(masked_image)




                #turning to np array
        if not IsComposition:
            generated_image = pipe(
                                    prompt = text_input,
                                    image = init_image,
                                    mask_image=mask_image,
                                    guidance_scale=guidance_scale,
                                    strength=strength_scale
                                  ).images[0]
            
            image = numpy.array(generated_image)
        else:
            #not working with xl
            rows = cols = 5
            strength_range = (0.2, 1.0)
            guidance_scale_range = (0.0, 20.0)

            strength_tab = []
            guidance_tab = []

            images = []
            for row in range(rows):
                for col in range(cols):
                    strength = round(strength_range[0] + col * ((strength_range[1] - strength_range[0]) / (cols - 1)), 2)
                    guidance_scale = round(guidance_scale_range[0] + row * ((guidance_scale_range[1] - guidance_scale_range[0]) / (rows - 1)), 2)

                    img = pipe(prompt=text_input, image=init_image, mask_image=mask_image, guidance=guidance_scale, strength=strength).images[0]
                    images.append(img)

                    strength_tab.append(strength)
                    guidance_tab.append(guidance_scale)

            grid = make_image_grid(images, rows=rows, cols=cols)
            image = numpy.array(grid)

            strength_scale = strength_tab
            guidance_scale = guidance_tab


        #fix steps
        #image = numpy.array(pipe(prompt=text_input, image=init_image, mask_image=mask_image, guidance_scale=guidance_scale).images[0])


        #fixing colors
        if len(image.shape) == 2: _, image_bytes = cv2.imencode('.png', image)
        else: _, image_bytes = cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        

        #generating title
        title = '{}.png'.format(text_input)


        #saving
        image_file = InMemoryUploadedFile(io.BytesIO(image_bytes), None, title, 'image/png', len(image_bytes), None)
        new_photo = inpaintPhoto(prompt=text_input, image=image_file, model_used=model,guidance=guidance_scale, strength=strength_scale)
        new_photo.save()
        return new_photo

def inpaint_delete_all_photos(request):
    itiPhotos = imagetoimagePhoto.objects.all()
    
    for itiPhoto in itiPhotos:
        if itiPhoto.image:
            if os.path.isfile(itiPhoto.image.path):
                os.remove(itiPhoto.image.path)

    itiPhotos.delete()
    return redirect('iti_view')


#assistance function
def check_image_model(photo_model, photo_id):
    if photo_model == 'Photo': photo = get_object_or_404(Photo, id=photo_id)
    elif photo_model == 'texttoimagePhoto': photo = get_object_or_404(texttoimagePhoto, id=photo_id)
    elif photo_model == 'imagetoimagePhoto': photo = get_object_or_404(imagetoimagePhoto, id=photo_id)
    return photo

def check_if_file_over_100kb(file_path):
    return os.path.getsize(file_path) / 1024 > 100
