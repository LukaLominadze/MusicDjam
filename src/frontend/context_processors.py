from api.services import FileMetadataService


def profile_picture(request):
    if request.user.is_authenticated:
        try:
            service = FileMetadataService()
            url = service.get_download_url(request.user.profile_picture)
            return {'nav_profile_picture_url': url}
        except Exception:
            pass
    return {'nav_profile_picture_url': None}
