from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracking.views import (
    VideoUploadViewSet,
    ProcessVideoViewSet,
    CatchAllViewSet,
    LPRViewSet,
    LPRAllViewSet,
    LPRFrontSideViewSet,
    MyView,
    PlateView,
    FrameView,
    MapView,
    CountLogViewSet,
    CountLogListView,
    VehicleLogViewSet,
    VehicleLogListView,
    TricycleCountGraphView,
    VehicleCountGraphView,
    
)

router = DefaultRouter()
router.register("tracking/video", VideoUploadViewSet, basename="tracking-video")
router.register("tracking/tric", ProcessVideoViewSet, basename="tracking-tric")
router.register("tracking/lpr", LPRViewSet, basename="LPR-tric")
router.register("tracking/count-logs", CountLogViewSet, basename="tracking-count")
router.register("tracking/catchall", CatchAllViewSet, basename="tracking-catchall")
router.register("tracking/lpr_all", LPRAllViewSet, basename="LPR-All_Vehicle")
router.register("tracking/lpr_frontside", LPRFrontSideViewSet, basename="LPR-Trike_FrontSide")

urlpatterns = [
    path('', include(router.urls)),
    path('my-url/', MyView.as_view(), name='my-view'),
    path('display_plates/', PlateView.as_view(), name='display_plates'),
    path('view_frame/<int:log_id>/', FrameView.view_frame, name='view_frame'),
    path('view_camera_map/<int:log_id>/', MapView.view_camera_map, name='view_camera_map'),
    path('count_logs/', CountLogListView.as_view(), name='count_log_list'),
    path('vehicle_logs/', VehicleLogListView.as_view(), name='vehicle_log_list'),
    path('tricycle_count_graph/<int:log_id>/', TricycleCountGraphView.as_view(), name='tricycle_count_graph'),
    path('vehicle_count_graph/<int:log_id>/', VehicleCountGraphView.as_view(), name='vehicle_count_graph'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
