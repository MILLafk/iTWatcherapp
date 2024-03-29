import os
# comment out below line to enable tensorflow logging outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import time
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
# from absl import app, flags, logging
# from absl.flags import FLAGS
import tracking.deepsort_tric.core.utils as utils
from tracking.deepsort_tric.core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from tracking.deepsort_tric.core.config import cfg
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

# deep sort imports
from tracking.deepsort_tric.deep_sort import preprocessing, nn_matching
from tracking.deepsort_tric.deep_sort.detection import Detection
from tracking.deepsort_tric.deep_sort.tracker import Tracker
from tracking.deepsort_tric.tools import generate_detections as gdet
import datetime
from collections import Counter, deque
import math

import re
import pytesseract
""""
!python object_tracker.py --video /content/road1.mp4 --output ./outputs/custom3.avi --model yolov4 --dont_show --info
"""



class VehiclesCounting():
    def __init__(self, file_counter_log_name, framework='tf', weights='./checkpoints/yolov4-416',
                size=416, tiny=False, model='yolov4', video='./data/videos/cam0.mp4',
                output=None, output_format='XVID', iou=0.45, score=0.5,
                dont_show=False, info=False,
                detection_line=(0.5,0)):
        '''- cam_name: input your camera name
        - framework: choose your model framework (tf, tflite, trt)
        - weights: path to your .weights
        - size: resize images to
        - tiny: (yolo,yolo-tiny)
        - model: (yolov3,yolov4)
        - video: path to your video or set 0 for webcam or youtube url
        - output: path to your results
        - output_format: codec used in VideoWriter when saving video to file
        - iou: iou threshold
        - score: score threshold
        - dont_show: dont show video output
        - info: show detailed info of tracked objects
        - count: count objects being tracked on screen
        - detection_line: tuple of 2 detection line's parameters (percent_of_height, angle_of_line). 
        (0..1) of height of video frame.
        (0..180) degrees of detect line.
        '''
        self._file_counter_log_name = file_counter_log_name
        self._framework = framework
        self._weights = weights
        self._size = size
        self._tiny = tiny
        self._model = model
        self._video = video
        self._output = output
        self._output_format = output_format
        self._iou = iou
        self._score = score
        self._dont_show = dont_show
        self._info = info
        self._detect_line_position = detection_line[0]
        self._detect_line_angle = detection_line[1]

    def _intersect(self, A, B, C, D):
        return self._ccw(A,C,D) != self._ccw(B, C, D) and self._ccw(A,B,C) != self._ccw(A,B,D)


    def _ccw(self, A,B,C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def _vector_angle(self, midpoint, previous_midpoint):
        x = midpoint[0] - previous_midpoint[0]
        y = midpoint[1] - previous_midpoint[1]
        return math.degrees(math.atan2(y, x))

    '''def recognize_license_plate(self,plate_img):
        # resize image
        plate_img = cv2.resize(plate_img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # convert to grayscale
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        # apply GaussianBlur to smooth image (remove noise)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # apply threshold to get black and white image (binarization)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # apply morphological transformations to remove noise and fill up holes
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresh = cv2.erode(thresh, rect_kernel, iterations=1)
        thresh = cv2.dilate(thresh, rect_kernel, iterations=1)
        
        # apply OCR using Pytesseract
        plate_number = pytesseract.image_to_string(thresh, config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 8 --oem 3')
        
        # return the recognized plate number
        return plate_number.strip()'''
    
    def recognize_color(self, frame, bbox):
        # define color ranges
        color_ranges = {
            #'blue': [(100, 50, 50), (130, 255, 255)],
            #'yellow': [(20, 100, 100), (50, 255, 255)],
            'yellow': [(0, 0, 0), (180, 255, 30)],
            'white': [(0, 0, 200), (180, 25, 255)],
            'red': [(0, 50, 50), (10, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            #'blue': [(120, 50, 50), (160, 255, 255)],
            'blue': [(10, 100, 100), (20, 255, 255)],
            'pink': [(160, 50, 50), (180, 255, 255)]
        }

        # crop the frame to the bounding box region
        x1, y1, x2, y2 = bbox
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        cropped = frame[y1:y2, x1:x2]

        # convert cropped image to HSV color space
        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

        # initialize variables
        max_area = 0
        dominant_color = None

        # iterate over color ranges and find the color with the largest area
        for color, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            area = 0
            for contour in contours:
                area += cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                dominant_color = color

        # get the HSV values of the dominant color
        x, y, w, h = cv2.boundingRect(contours[0]) if contours else (0, 0, 0, 0)
        hsv_values = self.get_hsv_values(cropped, x, y, w, h)

        # write the color and HSV values to a file
        with open('tricycle_colors.txt', 'a') as f:
            f.write(f'{dominant_color}: {hsv_values}\n')

        return dominant_color
    
    def process_frame(self,frame, framework='tflite',model = "yolov4",tiny = False, input_size=416, iou=0.45, score=0.25):
        
        input_shape = tf.constant([input_size, input_size])
        # initialize deep sort
        model_filename = '/home/itwatcher/tricycle/tracking/deepsort_tric/model_data/mars-small128.pb'

        #Definition of the parameters
        max_cosine_distance = 0.4
        nn_budget = None
        encoder = gdet.create_box_encoder(model_filename, batch_size=1)
        nms_max_overlap = 1.0
        show_detections = False
        # calculate cosine distance metric
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
        # initialize tracker
        tracker = Tracker(metric)

        frame_num = 0
        current_date = datetime.datetime.now().date()
        count_dict = {}  # initiate dict for storing counts

        total_counter = 0
        up_count = 0
        down_count = 0

        class_counter = Counter()  # store counts of each detected class
        already_counted = deque(maxlen=50)  # temporary memory for storing counted IDs
        intersect_info = []  # initialise intersection list

        memory = {}
        skip_frames = 20
            
        if framework == 'tflite':
            interpreter = tf.lite.Interpreter(model_path=model)
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            frame_size = frame.shape[:2]
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], image_data)
            interpreter.invoke()
            pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
            if model == 'yolov3' and tiny:
                boxes, pred_conf = filter_boxes(pred[1], pred[0], score_threshold=score, input_shape=input_shape)
            else:
                boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=score, input_shape=input_shape)
        else:
            model = tf.saved_model.load(model)
            infer = model.signatures['serving_default']
            frame_size = frame.shape[:2]
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)
            batch_data = tf.constant(image_data)
            pred_bbox = infer(batch_data)
            for _, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]
        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=iou,
            score_threshold=score
        )
        num_objects = valid_detections.numpy()[0]
        bboxes = boxes.numpy()[0]
        bboxes = bboxes[0:int(num_objects)]
        scores = scores.numpy()[0]
        scores = scores[0:int(num_objects)]
        classes = classes.numpy()[0]
        classes = classes[0:int(num_objects)]
        original_h, original_w, _ = frame.shape
        bboxes = utils.format_boxes(bboxes, original_h, original_w)
        class_names = utils.read_class_names(cfg.YOLO.CLASSES)
        allowed_classes = list(class_names.values())
        names = []
        deleted_indx = []
        for i in range(num_objects):
                class_indx = int(classes[i])
                class_name = class_names[class_indx]
                if class_name not in allowed_classes:
                    deleted_indx.append(i)
                else:
                    names.append(class_name)
        names = np.array(names)
        count = len(names)
        if count:
            cv2.putText(frame, "Objects being tracked: {}".format(count), (5, 35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2)
            print("Objects being tracked: {}".format(count))
            
            # delete detections that are not in allowed_classes
            bboxes = np.delete(bboxes, deleted_indx, axis=0)
            scores = np.delete(scores, deleted_indx, axis=0)

            # encode yolo detections and feed to tracker
            features = encoder(frame, bboxes)
            detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(bboxes, scores, names, features)]

            # run non-maxima supression
            boxs = np.array([d.tlwh for d in detections])
            scores = np.array([d.confidence for d in detections])
            classes = np.array([d.class_name for d in detections])
            indices = preprocessing.non_max_suppression(boxs, classes, nms_max_overlap, scores)
            detections = [detections[i] for i in indices]

            # Call the tracker
            tracker.predict()
            tracker.update(detections)

            # calculate line position and angle
            # (0, pos*y+y'), (x, pos*y-y')
            # y' = tan(angle) * x / 2

            yp = math.tan(self._detect_line_angle*math.pi/180) * frame.shape[1] / 2
            x1 = 0
            y1 = int(self._detect_line_position * frame.shape[0] + yp)
            x2 = int(frame.shape[1])
            y2 = int(self._detect_line_position * frame.shape[0] - yp)

            line = [(x1, y1), (x2, y2)]
            # draw yellow line
            cv2.line(frame, line[0], line[1], (0, 255, 255), 2)

            # update tracks
            for track in tracker.tracks:
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue

                bbox = track.to_tlbr()
                class_name = track.get_class()

                midpoint = track.tlbr_midpoint(bbox)
                origin_midpoint = (midpoint[0], frame.shape[0] - midpoint[1])

                if track.track_id not in memory:
                        memory[track.track_id] = deque(maxlen=2)

                memory[track.track_id].append(midpoint)
                previous_midpoint = memory[track.track_id][0]

                origin_previous_midpoint = (previous_midpoint[0], frame.shape[0] - previous_midpoint[1])
                cv2.line(frame, midpoint, previous_midpoint, (0, 255, 0), 2)

                if self._intersect(midpoint, previous_midpoint, line[0], line[1]) and track.track_id not in already_counted:
                        class_counter[class_name] += 1
                        total_counter += 1


                        # draw red line
                        cv2.line(frame, line[0], line[1], (0, 0, 255), 2)

                        # Set already counted for ID to true.
                        already_counted.append(track.track_id)  

                        intersection_time = datetime.datetime.now() - datetime.timedelta(microseconds=datetime.datetime.now().microsecond)
                        angle = self._vector_angle(origin_midpoint, origin_previous_midpoint)
                        intersect_info.append([class_name, origin_midpoint, angle, intersection_time])

                        if angle > 0:
                            up_count += 1
                        if angle < 0:
                            down_count += 1

                if class_name != class_names[0]:
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255,0,0), 2)
                    cv2.putText(frame, "NOT ALLOWED!", (int(bbox[0]), int(bbox[1])), 0,
                                1.1e-3 * frame.shape[0], (255, 0, 0), 2)
                    
                if class_name == class_names[0]:
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255,255,255), 2)  # WHITE BOX
                    cv2.putText(frame, "ALLOWED " + str(track.track_id), (int(bbox[0]), int(bbox[1])), 0,
                                1.1e-3 * frame.shape[0], (0, 255, 0), 2)


                if show_detections:
                    adc = "%.2f" % (track.adc * 100) + "%"  # Average detection confidence
                    cv2.putText(frame, str(class_name), (int(bbox[0]), int(bbox[3])), 0,
                                    1e-3 * frame.shape[0], (0, 255, 0), 2)
                    cv2.putText(frame, 'ADC: ' + adc, (int(bbox[0]), int(bbox[3] + 2e-2 * frame.shape[1])), 0,
                                    1e-3 * frame.shape[0], (0, 255, 0), 2)


            # if enable info flag then print details about each track
                if self._info:
                    print("Tracker ID: {}, Class: {},  BBox Coords (xmin, ymin, xmax, ymax): {}".format(str(track.track_id), class_name, (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))))

        # Delete memory of old tracks.
                # This needs to be larger than the number of tracked objects in the frame.
            if len(memory) > 50:
                del memory[list(memory)[0]]

                # Draw total count.
            cv2.putText(frame, "Total: {} ({} right, {} left)".format(str(total_counter), str(up_count),
                        str(down_count)), (int(0.05 * frame.shape[1]), int(0.1 * frame.shape[0])), 0,
                        1.5e-3 * frame.shape[0], (0, 255, 255), 2)

            if show_detections:
                track_dict = {}

                for det in detections:
                    bbox = det.to_tlbr()
                    class_name = det.get_class_name()
                    score = "%.2f" % (det.confidence * 100) + "%"
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0), 2)  # BLUE BOX
                    if len(classes) > 0:
                        det_cls = det.cls
                        cv2.putText(frame, str(det_cls) + " " + score, (int(bbox[0]), int(bbox[3])), 0,
                                    1.5e-3 * frame.shape[0], (0, 255, 0), 2)


            # display counts for each class as they appear
            y = 0.2 * frame.shape[0]
            for cls in class_counter:
                class_count = class_counter[cls]
                cv2.putText(frame, str(cls) + " " + str(class_count), (int(0.05 * frame.shape[1]), int(y)), 0,
                            1.5e-3 * frame.shape[0], (0, 255, 255), 2)
                y += 0.05 * frame.shape[0]

                # calculate current minute
            now = datetime.datetime.now()
            rounded_now = now - datetime.timedelta(microseconds=now.microsecond)  # round to nearest second
            current_minute = now.time().minute

            if current_minute == 0 and len(count_dict) > 1:
                count_dict = {}  # reset counts every hour
            else:
                    # write counts to file for every set interval of the hour
                    write_interval = 5
                    if current_minute % write_interval == 0:  # write to file once only every write_interval minutes
                        if current_minute not in count_dict:
                            count_dict[current_minute] = True
                            total_filename = 'Total counts for {}, {}.txt'.format(current_date, self._file_counter_log_name)
                            counts_folder = './counts/'
                            if not os.access(counts_folder + str(current_date) + '/total', os.W_OK):
                                os.makedirs(counts_folder + str(current_date) + '/total')
                            total_count_file = open(counts_folder + str(current_date) + '/total/' + total_filename, 'a')
                            print('{} writing...'.format(rounded_now))
                            print('Writing current total count ({}) and directional counts to file.'.format(total_counter))
                            total_count_file.write('{}, {}, {}, {}, {}\n'.format(str(rounded_now), self._file_counter_log_name,
                                                                                str(total_counter), up_count, down_count))
                            total_count_file.close()

                            # if class exists in class counter, create file and write counts

                            if not os.access(counts_folder + str(current_date) + '/classes', os.W_OK):
                                os.makedirs(counts_folder + str(current_date) + '/classes')
                            for cls in class_counter:
                                class_count = class_counter[cls]
                                print('Writing current {} count ({}) to file.'.format(cls, class_count))
                                class_filename = 'Class counts for {}, {}.txt'.format(current_date, self._file_counter_log_name)
                                class_count_file = open(counts_folder + str(current_date) + '/classes/' + class_filename, 'a')
                                class_count_file.write("{}, {}, {}\n".format(rounded_now, self._file_counter_log_name, str(class_count)))
                                class_count_file.close()

                            # write intersection details
                            if not os.access(counts_folder + str(current_date) + '/intersections', os.W_OK):
                                os.makedirs(counts_folder + str(current_date) + '/intersections')
                            print('Writing intersection details for {}'.format(self._file_counter_log_name))
                            intersection_filename = 'Intersection details for {}, {}.txt'.format(current_date, self._file_counter_log_name)
                            intersection_file = open(counts_folder + str(current_date) + '/intersections/' + intersection_filename, 'a')
                            for i in intersect_info:
                                cls = i[0]

                                midpoint = i[1]
                                x = midpoint[0]
                                y = midpoint[1]

                                angle = i[2]

                                intersect_time = i[3]

                                intersection_file.write("{}, {}, {}, {}, {}, {}\n".format(str(intersect_time), self._file_counter_log_name, cls,
                                                                                        x, y, str(angle)))
                            intersection_file.close()
                            intersect_info = []  # reset list after writing

                            # write restriction details
                            if not os.access(counts_folder + str(current_date) + '/restrictions', os.W_OK):
                                os.makedirs(counts_folder + str(current_date) + '/restrictions')
                            print('Writing restriction details for {}'.format(self._file_counter_log_name))
                            intersection_filename = 'Intersection details for {}, {}.txt'.format(current_date, self._file_counter_log_name)
                            restriction_filename = 'Restriction details for {}, {}.txt'.format(current_date, self._file_counter_log_name)
                            restriction_file = open(counts_folder + str(current_date) + '/restrictions/' + restriction_filename, 'a')

                            text = b'blue_tricycle'
                            with open(r"./counts/"+str(current_date)+"/intersections/"+str(intersection_filename), 'rb') as file_in:
                                 with open(r"./counts/"+str(current_date)+"/restrictions/"+str(restriction_filename), 'wb') as file_out:
                                    file_out.writelines(
                                        filter(lambda line: text not in line, file_in)
                                    ) 
    
    def run(self):
        
        #initialize color map
        cmap = plt.get_cmap('tab20b')
        colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]

        # load configuration for object detector
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        session = InteractiveSession(config=config)
        #STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(FLAGS)
        input_size = self._size
        video_path = self._video

        # load tflite model if flag is set
        if self._framework == 'tflite':
            interpreter = tf.lite.Interpreter(model_path=self._weights)
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            print(input_details)
            print(output_details)
        # otherwise load standard tensorflow saved model
        else:
            saved_model_loaded = tf.saved_model.load(self._weights, tags=[tag_constants.SERVING])
            infer = saved_model_loaded.signatures['serving_default']

        # begin video capture
        try:
            vid = cv2.VideoCapture(int(video_path))
        except:
            vid = cv2.VideoCapture(video_path)

        out = None

        # get video ready to save locally if flag is set
        if self._output:
            # by default VideoCapture returns float instead of int
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(vid.get(cv2.CAP_PROP_FPS))
            codec = cv2.VideoWriter_fourcc(*self._output_format)
            out = cv2.VideoWriter(self._output, codec, fps, (width, height))

        # Get the current timestamp
        start_time = time.time()

 
        while True:
            return_value, frame = vid.read()
            if return_value:
                #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                #Get the timestamp of the current frame
                current_time = time.time()

                # Calculate the delay in milliseconds
                delay = int((current_time - start_time) * 1000)

                print(f"Delay: {delay} ms")

                # Update the start time
                start_time = current_time

            else:
                print('Video has ended or failed, try a different video format!')
                break
            
            self.process_frame()

            result = np.asarray(frame)

            if not self._dont_show:
                cv2.namedWindow(self._file_counter_log_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(self._file_counter_log_name, 640, 480)
                cv2.imshow(self._file_counter_log_name, result)


            # if output flag is set, save video file
            if self._output:
                out.write(result)


            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cv2.destroyAllWindows()
