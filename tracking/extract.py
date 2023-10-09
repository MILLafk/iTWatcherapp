'''import os
import cv2
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from tracking.models import Image, Frame, Target, Video
from tracking.deepsort_tric import object_tracker
from tracking.deepsort_tric.object_tracker import VehiclesCounting
from tracking.models import Video
from .serializers import VideoSerializers

import numpy as np
import tensorflow as tf


def frame_extract(video_instance):
    images = []
    video_file = os.path.join(settings.MEDIA_ROOT, str(video_instance.file))
    cap = cv2.VideoCapture(video_file)
    frame_no = 1
    while True:
        # reading frame from the video source
        ret, frame = cap.read()
        if ret:
            if frame_no % 50 == 9:
                frame = cv2.resize(frame, (960, 540))
                _, buffer = cv2.imencode(".jpg", frame)
                content = ContentFile(BytesIO(buffer).getvalue())
                image_data = {"user": video_instance.user, "video": video_instance}
                image = Image.objects.create(**image_data)
                image.file.save(
                    f"tric{video_instance.id}_{image.id}.jpg", content, save=True
                )
                images.append(image.id)
                print(f"Extracted image id: {image.id}")
            frame_no += 1
        else:
            break
    cap.release()
    return images'''

