import uuid
import boto3
from django.conf import settings
from botocore.config import Config
from .models import FileMetadata


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            service_name='s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_PUBLIC_STORAGE_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
        )

    def generate_download_url(self, fs_id, expires_in=600):
        return self.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': str(fs_id),
            },
            ExpiresIn=expires_in
        )

    def generate_upload_url(self, fs_id, expires_in=600):
        return self.client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': str(fs_id),
            },
            ExpiresIn=expires_in
        )


class FileMetadataService:
    def __init__(self):
        self.s3 = S3Service()

    def get_or_create_metadata(self, existing_metadata, file_type):
        if existing_metadata is None:
            metadata = FileMetadata.objects.create(file_type=file_type)
        else:
            metadata = existing_metadata
            if metadata.file_type != file_type:
                metadata.file_type = file_type
                metadata.save()
        return metadata

    def get_download_url(self, metadata):
        if metadata is None or metadata.fs_id is None:
            return None
        return self.s3.generate_download_url(metadata.fs_id)

    def initiate_upload(self, metadata):
        if metadata.fs_id:
            fs_id = metadata.fs_id
            requires_completion = False
        else:
            fs_id = str(uuid.uuid4())
            requires_completion = True

        upload_url = self.s3.generate_upload_url(fs_id)

        return {
            'upload_url': upload_url,
            'fs_id': str(fs_id),
            'requires_completion': requires_completion,
        }

    def complete_upload(self, metadata, fs_id):
        if metadata.fs_id == fs_id:
            return
        metadata.fs_id = fs_id
        metadata.save()
