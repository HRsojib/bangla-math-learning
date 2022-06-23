from django.http import HttpResponse
from django.shortcuts import render, redirect
from .froms import handwritingForm


from keras.models import load_model
import pandas as pd
import numpy as np
from PIL import Image,ImageOps
from . import charectersegmentation as cs
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import os
import cv2

from django.conf import settings
MEDIA = settings.MEDIA_ROOT
SEGMENTED_OUTPUT_DIR = MEDIA+'/segmented/'

#helper

def preprocessing(img):
                img=img.astype("uint8")
                img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, img = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY)
                img = img/255
                return img
def value(arr):
                classNo=arr[0]
                if classNo==0:
                    return "0"
                elif classNo==1:
                    return "1"
                elif classNo==2:
                    return "2"
                elif classNo==3:
                    return "3"
                elif classNo==4:
                    return "4"
                elif classNo==5:
                    return "5"
                elif classNo==6:
                    return "6"
                elif classNo==7:
                    return "7"
                elif classNo==8:
                    return "8"
                elif classNo==9:
                    return "9"
                elif classNo==10:
                    return "+"
                elif classNo==11:
                    return "-"
                elif classNo==12:
                    return "/"
                elif classNo==13:
                    return "*"
                elif classNo==14:
                    return "="





# Create your views here.
def index(request):
    return render(request,'index.html')

def guide(request):
    return render(request,'mathguide.html')

def upload(request):
    dir=MEDIA+'/images/'
    for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
    dir = SEGMENTED_OUTPUT_DIR
    for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))  
    if request.method == 'POST':
        form = handwritingForm(request.POST, request.FILES)
        for filename, file in request.FILES.items():
            print(filename, file)
        if form.is_valid():
            form.save()
            img_obj = form.instance            
            INPUT_IMAGE = MEDIA+'/images/'+str(file)
            img = cv2.imread(INPUT_IMAGE)
            try:
                cs.image_segmentation(INPUT_IMAGE)
            except:
                return render(request, 'index.html', {'error' : 'image may not appropriate','form' : form})

            segmented_images = []
            images_name = []
            image_int=[]
            for (root,dirs,files) in os.walk(SEGMENTED_OUTPUT_DIR, topdown=True):
                    images_name=files
            for i in files:
                image_int.append(int(i[0:-4]))
            image_int.sort()
            for f in image_int:
                segmented_images.append(Image.open(SEGMENTED_OUTPUT_DIR +str(f)+'.jpg'))
            model=load_model(MEDIA+'/banglaModel.h5')
            IMG_SIZE=45
            expression =""
            lst = os.listdir(SEGMENTED_OUTPUT_DIR)
            for i in range(len(lst)):
                    filename = SEGMENTED_OUTPUT_DIR +str(i+1)+'.jpg'
                    print(filename)
                    img=cv2.imread(filename)
                    img=np.asarray(img)
                    BLUE = [255,255,255]
                    img= cv2.copyMakeBorder(img.copy(),20,20,20,20,cv2.BORDER_CONSTANT,value=BLUE)
                    
                    img=cv2.resize(img, (IMG_SIZE,IMG_SIZE))
                    img=preprocessing(img)
                    img=img.reshape(1, IMG_SIZE, IMG_SIZE, 1)
                    prediction=model.predict(img)
                    classIndex=np.argmax(prediction,axis=1)
                    expression=expression + value(classIndex)
            exp= expression.split('=')
            vardict=False
            if len(exp) == 2:
                leftexp= eval(exp[0])
                rightexp = eval(exp[1])
                if leftexp == rightexp:
                    vardict=True
            return render(request, 'upload.html', {'expression' : expression,'form' : form,'vardict':vardict,'img':img_obj})
    else:
        form =handwritingForm()
    return render(request, 'upload.html', {'form' : form})
  




