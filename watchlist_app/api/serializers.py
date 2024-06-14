from rest_framework import serializers
from ..models import WatchList, StreamPlatform, Review


class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        # fields = "__all__"
        exclude = ("watchlist",)


class WatchListSerializer(serializers.ModelSerializer):
    # reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = WatchList
        fields = "__all__"


class StreamPlatformSerializer(serializers.ModelSerializer):
    watch_list = WatchListSerializer(many=True, read_only=True)
    # watch_list = serializers.StringRelatedField(many=True, read_only=True)
    # watch_list = serializers.HyperlinkedRelatedField(many=True,read_only=True,view_name='movie-details')

    class Meta:
        model = StreamPlatform
        fields = "__all__"


    