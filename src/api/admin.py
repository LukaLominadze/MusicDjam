from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import FileMetadata, User, Artist, Album, Music, Playlist


@admin.register(FileMetadata)
class FileMetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_type', 'fs_id')
    search_fields = ('id', 'file_type')
    list_filter = ('file_type',)
    readonly_fields = ('id',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cover')
    search_fields = ('name',)
    list_select_related = ('cover',)


class MusicInline(admin.TabularInline):
    model = Music
    extra = 0
    fields = ('title', 'length', 'is_public', 'owner')
    readonly_fields = ('length',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'artist', 'cover')
    list_filter = ('artist',)
    search_fields = ('title', 'artist__name')
    list_select_related = ('artist', 'cover')
    inlines = [MusicInline]


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'artist', 'album', 'owner', 'length', 'is_public')
    list_filter = ('is_public', 'artist', 'album')
    search_fields = ('title', 'artist__name', 'album__title', 'owner__username')
    list_select_related = ('artist', 'album', 'owner', 'music_file')
    raw_id_fields = ('artist', 'album', 'owner', 'music_file')


class PlaylistSongsInline(admin.TabularInline):
    model = Playlist.songs.through
    extra = 0
    verbose_name = 'song'
    verbose_name_plural = 'songs'


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'is_public', 'song_count')
    list_filter = ('is_public', 'owner')
    search_fields = ('title', 'owner__username')
    list_select_related = ('owner', 'cover')
    raw_id_fields = ('owner', 'cover')
    filter_horizontal = ('songs',)

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = 'Songs'
