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
    cover_has_file = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'cover', 'cover_has_file']
        read_only_fields = ['id']

    def get_cover_has_file(self, obj):
        return obj.cover is not None and obj.cover.fs_id is not None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.artist_id:
            data['artist'] = {'id': instance.artist_id, 'name': instance.artist.name}
        return data


class MusicSerializer(serializers.ModelSerializer):
    music_file = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    has_file = serializers.SerializerMethodField()

    class Meta:
        model = Music
        fields = ['id', 'title', 'length', 'is_public', 'artist', 'album', 'owner', 'music_file', 'has_file']
        read_only_fields = ['id']

    def get_has_file(self, obj):
        return obj.music_file is not None and obj.music_file.fs_id is not None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.artist_id:
            data['artist'] = {
                'id': instance.artist_id,
                'name': instance.artist.name,
                'cover_has_file': instance.artist.cover is not None and instance.artist.cover.fs_id is not None,
            }
        if instance.album_id:
            data['album'] = {'id': instance.album_id, 'title': instance.album.title}
        return data


class PlaylistSerializer(serializers.ModelSerializer):
    cover = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    song_count = serializers.SerializerMethodField()
    cover_has_file = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'title', 'is_public', 'cover', 'owner', 'songs', 'song_count', 'cover_has_file']
        read_only_fields = ['id', 'owner']

    def get_song_count(self, obj):
        return obj.songs.count()

    def get_cover_has_file(self, obj):
        return obj.cover is not None and obj.cover.fs_id is not None


class UserSearchSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture_url']
        read_only_fields = ['id']

    def get_profile_picture_url(self, obj):
        from .services import FileMetadataService
        try:
            service = FileMetadataService()
            return service.get_download_url(obj.profile_picture)
        except Exception:
            return None


class ArtistSerializer(serializers.ModelSerializer):
    cover = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    cover_has_file = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'cover', 'cover_has_file']
        read_only_fields = ['id']

    def get_cover_has_file(self, obj):
        return obj.cover is not None and obj.cover.fs_id is not None
