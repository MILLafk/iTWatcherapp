'''from django.conf import settings
from tracking.extract import (
    frame_extract,
)
import os
import cv2
from django.conf import settings
from tracking.deepsort_tric.object_tracker_cam_color import VehiclesCounting
import datetime
import requests


REQUEST_URL = f"http://{settings.HOST}:8000/"


def process_vid(video_path=None, livestream_url=None, is_live_stream=False, video_stream=None):
    # Tricycle Detection and Tracking
    if video_path:
        # Load the video file
        video_file = video_path

        # Create a folder to store the output frames
        output_folder_path = os.path.join(settings.MEDIA_ROOT, 'tracked_videos')
        os.makedirs(output_folder_path, exist_ok=True)

        # Specify the filename and format of the output video
        output_video_path = os.path.join(output_folder_path, f"tracked_{os.path.basename(video_path)}")

        # Create an instance of the VehiclesCounting class
        vc = VehiclesCounting(file_counter_log_name='vehicle_count.log',
                              framework='tf',
                              weights='/home/itwatcher/tricycle/tracking/deepsort_tric/checkpoints/yolov4-416',
                              size=416,
                              tiny=False,
                              model='yolov4',
                              video=video_file,
                              output=output_video_path,
                              output_format='XVID',
                              iou=0.45,
                              score=0.5,
                              dont_show=False,
                              info=False,
                              detection_line=(0.5, 0))

        # Run the tracking algorithm on the video
        vc.run()

        # Release the video capture object and close any open windows
        #video_file.release()
        cv2.destroyAllWindows()

        # Return the path to the output video
        return {'output_video_path': output_video_path}

    elif livestream_url:
         # Check if the livestream_url is valid
        response = requests.get(livestream_url, auth=('username', 'password'))
        if response.status_code != 200:
            # Handle invalid url    
            return {'error': 'Invalid livestream url'}

        # Create a VideoCapture object using the livestream url
        video_file = cv2.VideoCapture(livestream_url)

       # get the current timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # create a unique output video name using the timestamp
        output_video_path = os.path.join(output_folder_path, f'tracked_livestream_{timestamp}.avi')
        os.makedirs(output_folder_path, exist_ok=True)
        
        # Create an instance of the VehiclesCounting class
        vc = VehiclesCounting(file_counter_log_name='vehicle_count.log',
                              framework='tf',
                              weights='/home/itwatcher/tricycle/tracking/deepsort_tric/checkpoints/yolov4-416',
                              size=416,
                              tiny=False,
                              model='yolov4',
                              #video=stream_path,
                              video=video_file,
                              output=output_video_path,
                              output_format='XVID',
                              iou=0.45,
                              score=0.5,
                              dont_show=False,
                              info=False,
                              detection_line=(0.5, 0))

        # Run the tracking algorithm on the video stream
        vc.run()


        #video_file.release()
        cv2.destroyAllWindows()
        # Return the path to the output video
        return {'output_video_path': output_video_path}

    else:
        raise ValueError('Either video or camera_feed_url must be provided.')'''
