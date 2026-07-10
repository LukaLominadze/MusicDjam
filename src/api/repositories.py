
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Artist, Album, Music, Playlist
from .serializers import ArtistSerializer, AlbumSerializer, MusicSerializer, PlaylistSerializer

class MusicRepository:
    def list(self, filters=None):
        qs = Music.objects.all()
        if not filters:
            return qs
        if filters.get('artist'):
            qs = qs.filter(artist__name__icontains=filters['artist'])
        if filters.get('artist_id'):
            qs = qs.filter(artist_id=filters['artist_id'])
        if filters.get('album'):
            qs = qs.filter(album__title__icontains=filters['album'])
        if filters.get('album_id'):
            qs = qs.filter(album_id=filters['album_id'])
        if filters.get('playlist_id'):
            qs = qs.filter(playlists__id=filters['playlist_id'])
        if filters.get('owner'):
            qs = qs.filter(owner_id=filters['owner'])
        if filters.get('is_public') is not None:
            qs = qs.filter(is_public=filters['is_public'])
        if filters.get('title'):
            qs = qs.filter(title__icontains=filters['title'])
        if search := filters.get('search'):
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(artist__name__icontains=search) |
                Q(album__title__icontains=search)
            )
        return qs

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
    def list(self, filters=None):
        qs = Playlist.objects.all()
        if not filters:
            return qs
        if filters.get('title'):
            qs = qs.filter(title__icontains=filters['title'])
        if filters.get('is_public') is not None:
            qs = qs.filter(is_public=filters['is_public'])
        if search := filters.get('search'):
            qs = qs.filter(Q(title__icontains=search))
        return qs

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
    def list(self, filters=None):
        qs = Album.objects.all()
        if not filters:
            return qs
        if filters.get('title'):
            qs = qs.filter(title__icontains=filters['title'])
        if filters.get('artist'):
            qs = qs.filter(artist__name__icontains=filters['artist'])
        if search := filters.get('search'):
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(artist__name__icontains=search)
            )
        return qs

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
    def list(self, filters=None):
        qs = Artist.objects.all()
        if not filters:
            return qs
        if filters.get('name'):
            qs = qs.filter(name__icontains=filters['name'])
        if search := filters.get('search'):
            qs = qs.filter(Q(name__icontains=search))
        return qs

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
