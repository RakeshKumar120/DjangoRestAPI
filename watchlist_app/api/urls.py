from django.contrib import admin
from django.urls import path, include
# from .api.views import movie_list, movie_details
from rest_framework.routers import DefaultRouter
from .views import WatchDetailAV, WatchListAV, StreamPlatformListAV, StreamPlatformDetailAV, ReviewList, ReviewDetail, ReviewCreate, StreamPlatformVS, WatchListFilterVW, UserReview

from rest_framework.authtoken import views

router = DefaultRouter()
router.register("stream", StreamPlatformVS, basename="streamplatform")

urlpatterns = [
    path('list/', WatchListAV.as_view(), name="movie-list"),
    # path('list2/', WatchListFilterVW.as_view(), name="movie-list"),
    path("<int:pk>/", WatchDetailAV.as_view(), name="movie-detail"),
    # path('stream/', StreamPlatformListAV.as_view(), name="stream-list"),
    # path("stream/<int:pk>", StreamPlatformDetailAV.as_view(), name="stream-details"),
    path("", include(router.urls)),

    path("<int:pk>/reviews/", ReviewList.as_view(), name="review-list"),
    path("<int:pk>/review-create/", ReviewCreate.as_view(), name="review-create"),
    path("review/<int:pk>/", ReviewDetail.as_view(), name="review-detail"),
    path('reviews/', UserReview.as_view(), name='user-review-detail'),
]
