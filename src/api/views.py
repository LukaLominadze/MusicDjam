from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .repositories import ArtistRepository, AlbumRepository, MusicRepository, PlaylistRepository
from .serializers import RegisterSerializer, ArtistSerializer, AlbumSerializer, MusicSerializer, PlaylistSerializer
from .models import User, Artist, Album, Music, Playlist
from .services import FileMetadataService

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered succesfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response({'error': 'User Id missing!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(username=username)
        if not user:
            return Response({'error': 'User with username not found!'}, status=status.HTTP_404_NOT_FOUND)

        service = FileMetadataService()
        download_url = service.get_download_url(user.profile_picture)

        if download_url is None:
            return Response({'error': 'User does not have a profile picture'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'download_url': download_url}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['put'], url_path='update-profile-picture')
    def update_profile_picture(self, request):
        user = request.user
        content_type = request.data.get('file_type', 'undefined')

        if content_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/avif', 'image/tiff', 'image/bmp', 'image/svg+xml']:
            return Response({"error": "Unsupported or invalid file type provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        service = FileMetadataService()
        metadata = service.get_or_create_metadata(user.profile_picture, content_type)
        user.profile_picture = metadata
        user.save()

        try:
            result = service.initiate_upload(metadata)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['put'], url_path='complete-update-profile-pic')
    def complete_update_profile_pic(self, request):
        user = request.user
        fs_id = request.data.get('fs_id')

        if not fs_id:
            return Response({'error': 'fs_id required!'}, status=status.HTTP_400_BAD_REQUEST)

        if user.profile_picture and user.profile_picture.fs_id == fs_id:
            return Response({'detail': 'Profile picture synchronized'}, status=status.HTTP_200_OK)

        service = FileMetadataService()
        service.complete_upload(user.profile_picture, fs_id)

        return Response({'detail': 'Profile picture synchronized'}, status=status.HTTP_200_OK)


class MusicViewSet(viewsets.ModelViewSet):
    queryset = Music.objects.all()
    serializer_class = MusicSerializer
    repository = MusicRepository()

    def get_permissions(self):
        return [IsAuthenticated()]

    def list(self, request):
        filters = {
            k: request.query_params.get(k)
            for k in ('artist', 'album', 'owner', 'is_public', 'title', 'search')
            if request.query_params.get(k)
        }
        if 'is_public' in filters:
            filters['is_public'] = filters['is_public'].lower() == 'true'
        music_list = self.repository.list(filters)
        serializer = self.get_serializer(music_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        music = self.repository.retrieve(pk)
        serializer = self.get_serializer(music)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        music = self.repository.create(serializer.validated_data)
        out_serializer = self.get_serializer(music)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        music = self.repository.retrieve(pk)
        if request.user != music.owner and not request.user.is_staff:
            return Response({'error': 'You do not have permission to update this music'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(music, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_music = self.repository.update(music, serializer.validated_data)
        out_serializer = self.get_serializer(updated_music)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        music = self.repository.retrieve(pk)
        if request.user != music.owner and not request.user.is_staff:
            return Response({'error': 'You do not have permission to delete this music'}, status=status.HTTP_403_FORBIDDEN)
        self.repository.destroy(music)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        music = self.repository.retrieve(pk)
        service = FileMetadataService()
        download_url = service.get_download_url(music.music_file)

        if download_url is None:
            return Response({'error': 'No music file available'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'download_url': download_url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='upload')
    def upload(self, request, pk=None):
        music = self.repository.retrieve(pk)
        content_type = request.data.get('file_type', 'undefined')

        if content_type not in ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/ogg']:
            return Response({"error": "Unsupported or invalid file type provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        service = FileMetadataService()
        metadata = service.get_or_create_metadata(music.music_file, content_type)
        music.music_file = metadata
        music.save()

        try:
            result = service.initiate_upload(metadata)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['put'], url_path='complete-upload')
    def complete_upload(self, request, pk=None):
        music = self.repository.retrieve(pk)
        fs_id = request.data.get('fs_id')

        if not fs_id:
            return Response({'error': 'fs_id required!'}, status=status.HTTP_400_BAD_REQUEST)

        if music.music_file and music.music_file.fs_id == fs_id:
            return Response({'detail': 'Music file synchronized'}, status=status.HTTP_200_OK)

        service = FileMetadataService()
        service.complete_upload(music.music_file, fs_id)

        return Response({'detail': 'Music file synchronized'}, status=status.HTTP_200_OK)


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    repository = PlaylistRepository()

    def get_permissions(self):
        return [IsAuthenticated()]

    def list(self, request):
        playlists = self.repository.list()
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        playlist = self.repository.retrieve(pk)
        serializer = self.get_serializer(playlist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        playlist = self.repository.create(serializer.validated_data)
        out_serializer = self.get_serializer(playlist)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        playlist = self.repository.retrieve(pk)
        if request.user != playlist.owner and not request.user.is_staff:
            return Response({'error': 'You do not have permission to update this playlist'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(playlist, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_playlist = self.repository.update(playlist, serializer.validated_data)
        out_serializer = self.get_serializer(updated_playlist)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        playlist = self.repository.retrieve(pk)
        if request.user != playlist.owner and not request.user.is_staff:
            return Response({'error': 'You do not have permission to delete this playlist'}, status=status.HTTP_403_FORBIDDEN)
        self.repository.destroy(playlist)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='download-cover')
    def download_cover(self, request, pk=None):
        playlist = self.repository.retrieve(pk)
        service = FileMetadataService()
        download_url = service.get_download_url(playlist.cover)

        if download_url is None:
            return Response({'error': 'No cover image available'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'download_url': download_url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='upload-cover')
    def upload_cover(self, request, pk=None):
        playlist = self.repository.retrieve(pk)
        content_type = request.data.get('file_type', 'undefined')

        if content_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/avif', 'image/tiff', 'image/bmp', 'image/svg+xml']:
            return Response({"error": "Unsupported or invalid file type provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        service = FileMetadataService()
        metadata = service.get_or_create_metadata(playlist.cover, content_type)
        playlist.cover = metadata
        playlist.save()

        try:
            result = service.initiate_upload(metadata)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['put'], url_path='complete-upload-cover')
    def complete_upload_cover(self, request, pk=None):
        playlist = self.repository.retrieve(pk)
        fs_id = request.data.get('fs_id')

        if not fs_id:
            return Response({'error': 'fs_id required!'}, status=status.HTTP_400_BAD_REQUEST)

        if playlist.cover and playlist.cover.fs_id == fs_id:
            return Response({'detail': 'Cover image synchronized'}, status=status.HTTP_200_OK)

        service = FileMetadataService()
        service.complete_upload(playlist.cover, fs_id)

        return Response({'detail': 'Cover image synchronized'}, status=status.HTTP_200_OK)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    repository = AlbumRepository()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request):
        albums = self.repository.list()
        serializer = self.get_serializer(albums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        album = self.repository.retrieve(pk)
        serializer = self.get_serializer(album)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        album = self.repository.create(serializer.validated_data)
        out_serializer = self.get_serializer(album)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        album = self.repository.retrieve(pk)
        serializer = self.get_serializer(album, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_album = self.repository.update(album, serializer.validated_data)
        out_serializer = self.get_serializer(updated_album)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        album = self.repository.retrieve(pk)
        self.repository.destroy(album)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    repository = ArtistRepository()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request):
        artists = self.repository.list()
        serializer = self.get_serializer(artists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        artist = self.repository.retrieve(pk)
        serializer = self.get_serializer(artist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        artist = self.repository.create(serializer.validated_data)
        out_serializer = self.get_serializer(artist)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        artist = self.repository.retrieve(pk)
        serializer = self.get_serializer(artist, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_artist = self.repository.update(artist, serializer.validated_data)
        out_serializer = self.get_serializer(updated_artist)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        artist = self.repository.retrieve(pk)
        self.repository.destroy(artist)
        return Response(status=status.HTTP_204_NO_CONTENT)
