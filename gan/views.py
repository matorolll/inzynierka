from django.http import JsonResponse, HttpResponseBadRequest
import subprocess
from django.shortcuts import render, get_object_or_404
import os
import sys
from main.models import Photo, Session
from gan.programs.ESRGAN.RRDBNet_arch import RRDBNet #it might lag
import os.path as osp
import glob
import cv2
import numpy as np
import torch
from .models import ganPhoto
from django.core.files import File

def gan_control_panel(request):
    sessions = Session.objects.all()
    photos = Photo.objects.all()
    context = {'sessions': sessions, 'photos': photos}
    return render(request, 'gan/test.html', context)




def ESRGAN_run(request):
    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        photo = get_object_or_404(Photo, id=photo_id)

        input_image_path = photo.thumbnail_medium.path
        output_image_path = 'media/gan_photos/{}_rlt.png'.format(photo_id)
        run_esrgan_on_image(input_image_path, output_image_path)



        changed_image_name = 'media/programs/ESRGAN/results/{}_rlt.png'.format(photo_id)
        with open(output_image_path, 'rb') as image_file:
            gan_photo = ganPhoto(title=changed_image_name, image=File(image_file))
            gan_photo.save()

        changed_image_url = gan_photo.image.url


        return JsonResponse({'changed_image_url': changed_image_url})
    return HttpResponseBadRequest('Invalid request')






def run_esrgan_on_image(input_image_path, output_image_path):
    model_path = 'gan/programs/ESRGAN/models/RRDB_ESRGAN_x4.pth'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = RRDBNet(3, 3, 64, 23, gc=32)
    model.load_state_dict(torch.load(model_path, map_location=device), strict=True)
    model.eval()
    model = model.to(device)

    # Read input image
    img = cv2.imread(input_image_path, cv2.IMREAD_COLOR)
    img = img * 1.0 / 255
    img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
    img_LR = img.unsqueeze(0)
    img_LR = img_LR.to(device)

    with torch.no_grad():
        output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()

    output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
    output = (output * 255.0).round()
    cv2.imwrite(output_image_path, output)





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
