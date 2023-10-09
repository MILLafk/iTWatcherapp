from getpass import getpass
import subprocess
import os

PYTHON_VERSION = 3.7

ALGORITHM = 'yolov7' # set the algorithm, such as 'yolov7'
ALGORITHM_VERSION = 'tiny' # set the algorithm version, such as 'tiny'
WEIGHTS = 'license-plate-recognition:experiment-2:best' # set the weights tag, such as 'license-plates:experiment-1:best'

OCR_MODEL_SIZE = 'large' # set the OCR model size, possible values are 'small', 'medium' and 'large'
OCR_MODEL_TYPE = 'printed' # set the OCR model type if using OCR_MODEL_SIZE = 'large', possible values are 'str', 'printed' and 'handwritten'
OCR_MODEL_ACCURACY = 'best' # set the OCR model accuracy if using OCR_MODEL_SIZE = 'large', possible values are 'base', 'medium' and 'best'
OCR_CLASSES = ['license-plate'] # set the class names that the OCR model should read from, such as ['license-plate']

INPUT_VIDEO = '/home/itwatcher/tricycle_copy/tracking/deepsort_tric/data/videos/samp.MOV'
OUTPUT_VIDEO = '/home/itwatcher/tricycle_copy/output.mp4'

def run(command):
  p  = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  while True:
      output = p.stdout.readline()
      if output == '' and p.poll() is not None:
          break
      if output:
          print(output.strip())

def python(script):
  p = subprocess.Popen(f'python{PYTHON_VERSION} -c "{script}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  while True:
      output = p.stdout.readline()
      if output == '' and p.poll() is not None:
          break
      if output:
          print(output.strip())

def login():
  username = input('[theos] username: ')
  password = getpass('[theos] password: ')
  run(f'theos login -u {username} -p {password}')

def set_project():
  key = getpass('[theos] project key: ')
  run(f'theos set-project {key}')

def install_algorithm(algorithm, version, weights):
  run(f'theos install {algorithm} --version {version} --weights {weights}')

INSTALL = f'sudo apt install tesseract-ocr && wget https://bootstrap.pypa.io/get-pip.py && python{PYTHON_VERSION} get-pip.py && python{PYTHON_VERSION} -m pip install --upgrade pip && python{PYTHON_VERSION} -m pip install theos-ai[ocr]==0.0.28'
SETUP = 'theos setup --version v1 --subfield object-detection'
SCRIPT = f'''
from theos.computer_vision.object_detection.utils import draw
from theos.computer_vision import ocr
from theos.client import Client
from tqdm import tqdm
import torch
import json
import time
import cv2
import os

if torch.cuda.is_available():
  torch.cuda.empty_cache()

ALGORITHM = '{ALGORITHM}'
ALGORITHM_VERSION = '{ALGORITHM_VERSION}'
WEIGHTS = '{WEIGHTS}'

OCR_MODEL_SIZE = '{OCR_MODEL_SIZE}'
OCR_MODEL_TYPE = '{OCR_MODEL_TYPE}'
OCR_MODEL_ACCURACY = '{OCR_MODEL_ACCURACY}'
OCR_CLASSES = {OCR_CLASSES}

INPUT_VIDEO = '{INPUT_VIDEO}'
OUTPUT_VIDEO = '{OUTPUT_VIDEO}'
client = Client(inputs='.', outputs='.')
yolov7 = client.get(ALGORITHM, version=ALGORITHM_VERSION)
yolov7.load_weights(WEIGHTS)
yolov7.to_gpu()

if OCR_MODEL_TYPE and OCR_MODEL_ACCURACY: 
  ocr_model = ocr.load(size=OCR_MODEL_SIZE, model_type=OCR_MODEL_TYPE, accuracy=OCR_MODEL_ACCURACY)
else:
  ocr_model = ocr.load(size=OCR_MODEL_SIZE)


if OCR_MODEL_SIZE == 'large':
  ocr_model.to_gpu()

video = cv2.VideoCapture(INPUT_VIDEO)
width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video.get(cv2.CAP_PROP_FPS))
frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
output = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))

if video.isOpened() == False:
	print('[!] error opening the video')

print('detecting video...')
print()
pbar = tqdm(total=frames_count, unit=' frames', dynamic_ncols=True, position=0, leave=True)
skip_frames = 3
processed_frame = 0
total_frames = 0
total_processing_time = 0
total_delay = 0

while video.isOpened():
    ret, frame = video.read()
    if ret == True:
      total_frames += 1
      if total_frames % skip_frames == 0:
        start_time = time.time()
        detections = yolov7.detect(frame)
        detections = ocr_model.read(frame, detections=detections, classes=OCR_CLASSES)
        detected_frame = draw(frame, detections, alpha=0.15)
        output.write(detected_frame)
        processed_frame +=1
        end_time = time.time()
        processing_time = (end_time - start_time)*1000
        total_processing_time += processing_time
        delay = (time.time() - start_time)*1000
        total_delay += delay
        
      pbar.update(1)
    else:
        break

average_processing_time = total_processing_time / total_frames
average_delay = total_delay / total_frames

print(\n'Average Processing Time: ', average_processing_time,'ms')
print('Average Processing Delay: ', average_delay,'ms')

pbar.close()
print()
video.release()
output.release()
yolov7.unload()
client.close()
'''

#run(INSTALL)
#run(SETUP)
#login()
#set_project()
#install_algorithm(ALGORITHM, ALGORITHM_VERSION, WEIGHTS)
#python(SCRIPT)