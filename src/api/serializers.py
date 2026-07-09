from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Artist, Album, Music, Playlist

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class AlbumSerializer(serializers.ModelSerializer):
    cover = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'cover']
        read_only_fields = ['id']


class MusicSerializer(serializers.ModelSerializer):
    music_file = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    class Meta:
        model = Music
        fields = ['id', 'title', 'length', 'is_public', 'artist', 'album', 'owner', 'music_file']
        read_only_fields = ['id']


class PlaylistSerializer(serializers.ModelSerializer):
    cover = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    class Meta:
        model = Playlist
        fields = ['id', 'title', 'is_public', 'cover', 'owner', 'songs']
        read_only_fields = ['id']


class ArtistSerializer(serializers.ModelSerializer):
    cover = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    class Meta:
        model = Artist
        fields = ['id', 'name', 'cover']
        read_only_fields = ['id']
