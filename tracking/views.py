from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.views import View
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status
from rest_framework.response import Response
from tracking.serializers import (
    VideoSerializers,
    ProcessVideoSerializers,
    LPRSerializers,
    CountLogSerializer,
    VehicleLogSerializer,
)
from tracking.models import Video, PlateLog, CountLog, VehicleLog
from tracking.process import process_vid
from tracking.process_lpr import process_frontside
from tracking.process_all import process_all
from tracking.process_lpr_all import process_alllpr
#from tracking.process_frontside import process_frontside

# Define your Django Rest Framework view
from rest_framework.response import Response
import matplotlib.pyplot as plt
import io
import base64

# Create your views here.
class MyView(View):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        videos = Video.objects.filter(user=request.user)
        context = {'users': users, 'videos': videos}
        return render(request, 'index.html', context)

class CountLogViewSet(viewsets.ModelViewSet):
    queryset = CountLog.objects.all()
    serializer_class = CountLogSerializer

class VehicleLogViewSet(viewsets.ModelViewSet):
    queryset = VehicleLog.objects.all()
    serializer_class = VehicleLogSerializer
       
# Create your views here.
class VideoUploadViewSet(viewsets.ModelViewSet):
    """
    Uploads a File
    """

    queryset = Video.objects.all()
    serializer_class = VideoSerializers
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProcessVideoViewSet(viewsets.ViewSet):
    """
    Perform tricycle Detection in Videos
    """

    serializer_class = ProcessVideoSerializers

    def create(self, request):
        serializer = ProcessVideoSerializers(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            video_path = data.get("video")
            livestream_url = data.get("camera_feed_url")

            if video_path:
                context = process_vid(video_path=video_path)
            elif livestream_url:
                stream_path = livestream_url
                #stream_file = cv2.VideoCapture(stream_path)
                context = process_vid(livestream_url=livestream_url, video_stream=stream_path)
            else:
                return Response({"error": "Either video or camera_feed_url must be provided"}, status=status.HTTP_400_BAD_REQUEST)

             # Return the path to the output video
            return Response({'output_video_path': context['output_video_path']}, status=status.HTTP_200_OK)

        # Return validation errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CatchAllViewSet(viewsets.ViewSet):
    """
    Perform tricycle Detection in Videos
    """

    serializer_class = ProcessVideoSerializers

    def create(self, request):
        serializer = ProcessVideoSerializers(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            video_path = data.get("video")
            livestream_url = data.get("camera_feed_url")

            if video_path:
                context = process_all(video_path=video_path)
            elif livestream_url:
                stream_path = livestream_url
                #stream_file = cv2.VideoCapture(stream_path)
                context = process_all(livestream_url=livestream_url, video_stream=stream_path)
            else:
                return Response({"error": "Either video or camera_feed_url must be provided"}, status=status.HTTP_400_BAD_REQUEST)

             # Return the path to the output video
            return Response({'output_video_path': context['output_video_path']}, status=status.HTTP_200_OK)

        # Return validation errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LPRViewSet(viewsets.ViewSet):
    """
    Perform tricycle Detection in Videos
    """

    serializer_class = LPRSerializers

    def create(self, request):
        serializer = ProcessVideoSerializers(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            video_path = data.get("video")
            livestream_url = data.get("camera_feed_url")

            if video_path:
                context = process_frontside(video_path=video_path)   
            elif livestream_url:
                stream_path = livestream_url
                context = process_frontside(livestream_url=livestream_url, video_stream=stream_path)
            else:
                return Response({"error": "Either video or camera_feed_url must be provided"}, status=status.HTTP_400_BAD_REQUEST)

             # Return the path to the output video
            return Response({'output_video_path': context['output_video_path']}, status=status.HTTP_200_OK)

        # Return validation errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LPRAllViewSet(viewsets.ViewSet):
    """
    Perform tricycle Detection in Videos
    """

    serializer_class = LPRSerializers

    def create(self, request):
        serializer = ProcessVideoSerializers(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            video_path = data.get("video")
            livestream_url = data.get("camera_feed_url")

            if video_path:
                context = process_alllpr(video_path=video_path)
            elif livestream_url:
                stream_path = livestream_url
                #stream_file = cv2.VideoCapture(stream_path)
                context = process_alllpr(livestream_url=livestream_url, video_stream=stream_path)
            else:
                return Response({"error": "Either video or camera_feed_url must be provided"}, status=status.HTTP_400_BAD_REQUEST)

             # Return the path to the output video
            return Response({'output_video_path': context['output_video_path']}, status=status.HTTP_200_OK)

        # Return validation errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

class LPRFrontSideViewSet(viewsets.ViewSet):
    """
    Perform tricycle Detection in Videos
    """

    serializer_class = LPRSerializers

    def create(self, request):
        serializer = ProcessVideoSerializers(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            video_path = data.get("video")
            livestream_url = data.get("camera_feed_url")

            if video_path:
                context = process_frontside(video_path=video_path)
            elif livestream_url:
                stream_path = livestream_url
                #stream_file = cv2.VideoCapture(stream_path)
                context = process_frontside(livestream_url=livestream_url, video_stream=stream_path)
            else:
                return Response({"error": "Either video or camera_feed_url must be provided"}, status=status.HTTP_400_BAD_REQUEST)

             # Return the path to the output video
            return Response({'output_video_path': context['output_video_path']}, status=status.HTTP_200_OK)

        # Return validation errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
class PlateView(View):

    def get(self, request):
        plate_logs = PlateLog.objects.all()
        context = {
            'plate_logs': plate_logs,
        }
        return render(request, '/home/ubuntu/iTWatcherapp/tracking/display_plates.html', context)
    def post(self, request):
        # Handle POST requests if needed
        pass
    
class FrameView(View):

    def view_frame(request, log_id):
        # Retrieve the PlateLog instance based on the log_id
        plate_log = PlateLog.objects.get(id=log_id)
        context = {
            'plate_log': plate_log,
        }
        return render(request, '/home/ubuntu/iTWatcherapp/tracking/view_frame.html', context)
    
class MapView(View):

    def view_camera_map(request, log_id):
        plate_log = PlateLog.objects.get(id=log_id)
        context = {
            'plate_log': plate_log,
        }
        return render(request, '/home/ubuntu/iTWatcherapp/tracking/view_camera_map.html', context)

class CountLogListView(View):

    template_name = 'count_log_list.html'

    def get(self, request, *args, **kwargs):
        count_logs = CountLog.objects.all()
        context = {'count_logs': count_logs}
        return render(request, self.template_name, context)
            
class VehicleLogListView(View):

    template_name = 'vehicle_log_list.html'

    def get(self, request, *args, **kwargs):
        vehicle_logs = VehicleLog.objects.all()
        context = {'vehicle_logs': vehicle_logs}
        return render(request, self.template_name, context)

class TricycleCountGraphView(View):
    template_name = 'tricycle_count_graph.html'  # Path to your template

    def get(self, request, log_id):
        # Retrieve the log entry based on log_id
        log = CountLog.objects.get(id=log_id)  # Adjust this based on your model

        # Extract class names and counts from the log
        class_names = list(log.class_counts.keys())
        class_counts = list(log.class_counts.values())

        # Generate the bar graph
        bar_figure = plt.figure(figsize=(6, 4))
        plt.bar(class_names, class_counts)
        plt.xlabel('Class')
        plt.ylabel('Count')
        plt.title('Bar Graph')
        bar_buffer = io.BytesIO()
        plt.savefig(bar_buffer, format='png')
        plt.close(bar_figure)

        # Generate the pie chart
        pie_figure = plt.figure(figsize=(6, 4))
        plt.pie(class_counts, labels=class_names, autopct='%1.1f%%')
        plt.title('Pie Chart')
        pie_buffer = io.BytesIO()
        plt.savefig(pie_buffer, format='png')
        plt.close(pie_figure)

        # Generate the line graph
        line_figure = plt.figure(figsize=(6, 4))
        plt.plot(class_names, class_counts, marker='o')
        plt.xlabel('Class')
        plt.ylabel('Count')
        plt.title('Line Graph')
        line_buffer = io.BytesIO()
        plt.savefig(line_buffer, format='png')
        plt.close(line_figure)

        # Convert the buffer data to base64 for embedding in the HTML
        bar_graph_data = base64.b64encode(bar_buffer.getvalue()).decode()
        pie_graph_data = base64.b64encode(pie_buffer.getvalue()).decode()
        line_graph_data = base64.b64encode(line_buffer.getvalue()).decode()

        context = {
            'bar_graph_data': bar_graph_data,
            'pie_graph_data': pie_graph_data,
            'line_graph_data': line_graph_data,
            'log_id': log_id,
        }

        return render(request, self.template_name, context)

class VehicleCountGraphView(View):
    template_name = 'vehicle_count_graph.html'  # Path to your template

    def get(self, request, log_date):
        # Retrieve the log entry based on log_id
        #log = VehicleLog.objects.get(id=log_id)  # Adjust this based on your model
        logs = VehicleLog.objects.filter(timestamp__date=log_date)

        # Extract class names and counts from the log
        #class_names = list(log.class_counts.keys())
        #class_counts = list(log.class_counts.values())
        # Extract vehicle types and counts from the logs
        class_names = list(set(log.vehicle_type for log in logs))
        class_counts = [logs.filter(vehicle_type=vehicle_type).count() for vehicle_type in class_names]

        # Generate the bar graph
        bar_figure = plt.figure(figsize=(8, 6))
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Add more colors if needed
        #plt.bar(class_names, class_counts)
        # Calculate cumulative counts for each vehicle type
        cumulative_counts = [0] * len(class_names)
        for i, count in enumerate(class_counts):
            plt.bar(log_date, count, bottom=cumulative_counts, color=colors[i], label=class_names[i])
            cumulative_counts[i] += count

        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.title('Bar Graph for {log_date}')
        bar_buffer = io.BytesIO()
        plt.savefig(bar_buffer, format='png')
        plt.close(bar_figure)

        # Generate the pie chart
        pie_figure = plt.figure(figsize=(6, 4))
        plt.pie(class_counts, labels=class_names, autopct='%1.1f%%')
        plt.title('Pie Chart')
        pie_buffer = io.BytesIO()
        plt.savefig(pie_buffer, format='png')
        plt.close(pie_figure)

        # Generate the line graph
        line_figure = plt.figure(figsize=(6, 4))
        plt.plot(class_names, class_counts, marker='o')
        plt.xlabel('Class')
        plt.ylabel('Count')
        plt.title('Line Graph')
        line_buffer = io.BytesIO()
        plt.savefig(line_buffer, format='png')
        plt.close(line_figure)

        # Convert the buffer data to base64 for embedding in the HTML
        bar_graph_data = base64.b64encode(bar_buffer.getvalue()).decode()
        pie_graph_data = base64.b64encode(pie_buffer.getvalue()).decode()
        line_graph_data = base64.b64encode(line_buffer.getvalue()).decode()

        context = {
            'bar_graph_data': bar_graph_data,
            'pie_graph_data': pie_graph_data,
            'line_graph_data': line_graph_data,
            'log_date': log_date,
            
        }

        return render(request, self.template_name, context)

