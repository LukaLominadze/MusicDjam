from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

# Create your models here.


class FileMetadata(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    file_type = models.CharField(max_length=45, blank=True)
    fs_id = models.UUIDField(null=True)

    def __str__(self):
        return str(self.id)


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(unique=True)
    profile_picture = models.ForeignKey(FileMetadata, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.username


class Artist(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    cover = models.ForeignKey(FileMetadata, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    cover = models.ForeignKey(FileMetadata, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Music(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    length = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    music_file = models.ForeignKey(FileMetadata, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=70)
    is_public = models.BooleanField(default=False)
    cover = models.ForeignKey(FileMetadata, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Music, related_name='playlists', blank=True)

    def __str__(self):
        return self.title

