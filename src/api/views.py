import uuid
import boto3
from django.shortcuts import render
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from botocore.exceptions import ClientError
from botocore.config import Config
from .serializers import RegisterSerializer
from .models import FileMetadata

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

    def get_s3_client(self):
        return boto3.client(
            service_name='s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_PUBLIC_STORAGE_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
        )

    @action(detail=False, methods=['put'], url_path='update-profile-picture')
    def update_profile_picture(self, request):
        user = request.user
        content_type = request.data.get('file_type', 'undefined')
        
        if content_type not in ['image/jpeg', 'image/png']:
            return Response({"error": "Unsupported or invalid file type provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        s3_client = self.get_s3_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        if not user.profile_picture:
            metadata = FileMetadata.objects.create(file_type=content_type)
            user.profile_picture = metadata
            user.save()
        else:
            metadata = user.profile_picture
            if metadata.file_type != content_type:
                metadata.file_type = content_type
                metadata.save()

        fs_id = ''
        is_existing = False
        if user.profile_picture.fs_id:
            fs_id = user.profile_picture.fs_id
            is_existing = True
        else:
            fs_id = str(uuid.uuid4())

        s3_key = f'{fs_id}'

        try:
            presigned_post = s3_client.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': s3_key,
                },
                ExpiresIn=600
            )
            
            return Response({
                'upload_url': presigned_post,
                'fs_id': fs_id,
                'requires_completion': not is_existing
            }, status=status.HTTP_200_OK)
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
        
        metadata = user.profile_picture
        metadata.fs_id = fs_id
        metadata.save()

        return Response({'detail', 'Profile picture synchronized'}, status=status.HTTP_200_OK)
