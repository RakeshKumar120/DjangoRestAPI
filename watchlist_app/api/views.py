# from django.shortcuts import get_object_or_404
from rest_framework.response import Response
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN
# from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import WatchList, StreamPlatform, Review
from .serializers import WatchListSerializer, StreamPlatformSerializer, ReviewSerializer
from .permissions import AdminOrReadOnly, ReviewUserORReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .pagination import WatchListPagination


class UserReview(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]
    # throttle_classes = [ReviewListThrottle, AnonRateThrottle]

    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Review.objects.filter(review_user__username=username)

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        return Review.objects.filter(review_user__username=username)


class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    # throttle_classes = [UserRateThrottle,AnonRateThrottle]
    
    serializer_class = ReviewSerializer  

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Review.objects.filter(watchlist=pk)
    
    
class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    def perform_create(self, serializer):
        pk = self.kwargs.get("pk")
        movie = WatchList.objects.get(pk=pk)
        review_user = self.request.user
        review_queryset = Review.objects.filter(watchlist=movie, review_user=review_user)
        if review_queryset.exists():
            raise ValidationError({"error" : "The Review already exists for the movie"})
        
        if movie.avg_rating == 0:
            movie.avg_rating = serializer.validated_data['rating']
        else:
            movie.avg_rating = (movie.avg_rating + serializer.validated_data['rating']) / 2
        
        movie.number_rating  += 1
        movie.save()
        
        serializer.save(watchlist=movie,review_user=review_user)



class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer  
    permission_classes = [ReviewUserORReadOnly]

    # def perform_update(self, serializer):
    #     pk = self.kwargs.get("pk")
    #     review_queryset = Review.objects.get(pk=pk)

    #     if review_queryset.rating != serializer.validated_data['rating']:
    #         watchlist_queryset = review_queryset.watchlist
    #         current_sum = watchlist_queryset.avg_rating * watchlist_queryset.number_rating
    #         new_sum = current_sum - review_queryset.rating + serializer.validated_data['rating']
    #         new_avg_rating = new_sum / watchlist_queryset.number_rating
    #         watchlist_queryset.avg_rating = new_avg_rating
    #         watchlist_queryset.save()
    #     return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        watchlist_queryset = instance.watchlist
        current_sum = watchlist_queryset.avg_rating * watchlist_queryset.number_rating
        new_sum = current_sum - instance.rating
        watchlist_queryset.number_rating -= 1
        new_avg_rating = new_sum / watchlist_queryset.number_rating
        watchlist_queryset.avg_rating = new_avg_rating
        watchlist_queryset.save()
        return super().perform_destroy(instance)

    

# class ReviewList(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# class ReviewDetail(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)


# class StreamPlatformVS(viewsets.ViewSet):
#     """
#     A simple ViewSet for listing or retrieving users.
#     """
#     def list(self, request):
#         queryset = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamPlatform.objects.all()
#         user = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(user)
#         return Response(serializer.data)


class StreamPlatformVS(viewsets.ModelViewSet):
    permission_classes = [AdminOrReadOnly]
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer  



class StreamPlatformListAV(APIView):
    def get(self, request):
        streams = StreamPlatform.objects.all()
        stream_serializer = StreamPlatformSerializer(streams, many=True, context={'request': request})
        return Response(stream_serializer.data)
    
    def post(self, request):
        stream_serializer = StreamPlatformSerializer(data=request.data)
        if stream_serializer.is_valid():
            stream_serializer.save()
            return Response(stream_serializer.data)
        else:
            return Response(stream_serializer.errors, status=HTTP_400_BAD_REQUEST)
        
class StreamPlatformDetailAV(APIView):
    def get(self, request, pk):
        try:
            stream = StreamPlatform.objects.get(pk=pk)
        except:
            return Response({"error" : "Not Found"}, status=HTTP_404_NOT_FOUND)
        stream_serializer = StreamPlatformSerializer(stream)
        return Response(stream_serializer.data)
    
    def put(self, request, pk):
        try:
            stream = StreamPlatform.objects.get(pk=pk)
        except:
            return Response({"error" : "Not Found"}, status=HTTP_404_NOT_FOUND)
        stream_serializer = StreamPlatformSerializer(stream, request.data)
        if stream_serializer.is_valid():
            stream_serializer.save()
            return Response(stream_serializer.data)
        else:
            return Response(stream_serializer.errors, status=HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        try:
            stream = StreamPlatform.objects.get(pk=pk)
        except:
            return Response({"error" : "Not Found"}, status=HTTP_404_NOT_FOUND)
        name = stream.name
        stream.delete()
        return Response({"message" : f"deleted {name} movie"}, status=HTTP_204_NO_CONTENT)
    


class WatchListFilterVW(generics.ListAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['active']
    ordering_fields = ['avg_rating', 'number_rating']
    pagination_class = WatchListPagination

        

class WatchListAV(APIView):
    permission_classes = [AdminOrReadOnly]
    pagination_class = WatchListPagination
    
    def get(self, request):
        movies = WatchList.objects.all()
        serializer = WatchListSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_403_FORBIDDEN)
        
class WatchDetailAV(APIView):
    permission_classes = [AdminOrReadOnly]

    def get(self, request, pk):
        try:
            movie = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({"Error" : "Not found"} , status=HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            movie = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({"Error" : "Movies not found"} , status=HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movie, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        

    def delete(self, request, pk):
        try:
            movie = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({"Error" : "Movies not found"} , status=HTTP_404_NOT_FOUND)
        name = movie.title
        movie.delete()
        return Response({"message" : f"deleted {name} movie"}, status=HTTP_204_NO_CONTENT)
    
    

# Create your views here

# @api_view(['GET', 'POST'])
# def movie_list(request):
#     if request.method == 'GET':
#         movies = Movie.objects.all()
#         serializer = WatchListSerializer(movies, many=True)
#         return Response(serializer.data)
#     if request.method == 'POST':
#         serializer = WatchListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)


# @api_view(['GET',"PUT",'DELETE'])
# def movie_details(request, pk):
#     try:
#         movie = Movie.objects.get(pk=pk)
#     except Movie.DoesNotExist:
#         return Response({"Error" : "Movies not found"} , status=HTTP_404_NOT_FOUND)
    
#     if request.method == 'GET':
#         serializer = WatchListSerializer(movie)
#         return Response(serializer.data)
    
#     if request.method =="PUT":
#         serializer = WatchListSerializer(movie, request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

#     if request.method == "DELETE":
#         name = movie.name
#         movie.delete()
#         return Response({"error" : f"deleted {name} movie"}, status=HTTP_204_NO_CONTENT)