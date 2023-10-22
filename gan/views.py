import subprocess
from django.shortcuts import render
import os
import sys

def gan_control_panel(request):
    return render(request, 'gan/test.html')



def ESRGAN_run(request):
    if request.method == 'POST':
        try:
            script_path = 'gan/programs/ESRGAN/test.py'

            subprocess.run(['pipenv', 'run', 'python', script_path])

            print("wykonano")
            return render(request, 'gan/test.html')
        except Exception as e:
            print("nie udalo sie")
            return render(request, 'main/home.html', {'error_message': str(e)})
        
    return render(request, 'gan/test.html')
