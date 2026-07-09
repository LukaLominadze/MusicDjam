
from django.shortcuts import get_object_or_404
from .models import Artist, Album, Music, Playlist
from .serializers import ArtistSerializer, AlbumSerializer, MusicSerializer, PlaylistSerializer

class MusicRepository:
    def list(self):
        return Music.objects.all()

    def retrieve(self, pk):
        return get_object_or_404(Music, pk=pk)

    def create(self, data):
        serializer = MusicSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def update(self, music, data):
        serializer = MusicSerializer(music, data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def destroy(self, music):
        music.delete()


class PlaylistRepository:
    def list(self):
        return Playlist.objects.all()

    def retrieve(self, pk):
        return get_object_or_404(Playlist, pk=pk)

    def create(self, data):
        serializer = PlaylistSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def update(self, playlist, data):
        serializer = PlaylistSerializer(playlist, data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def destroy(self, playlist):
        playlist.delete()


class AlbumRepository:
    def list(self):
        return Album.objects.all()

    def retrieve(self, pk):
        return get_object_or_404(Album, pk=pk)

    def create(self, data):
        serializer = AlbumSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def update(self, album, data):
        serializer = AlbumSerializer(album, data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def destroy(self, album):
        album.delete()


class ArtistRepository:
    def list(self):
        return Artist.objects.all()

    def retrieve(self, pk):
        return get_object_or_404(Artist, pk=pk)

    def create(self, data):
        serializer = ArtistSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def update(self, artist, data):
        serializer = ArtistSerializer(artist, data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def destroy(self, artist):
        artist.delete()
