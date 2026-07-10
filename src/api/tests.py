from django.test import TestCase
from .models import Artist, Album, Music
from .repositories import MusicRepository


class MusicRepositoryFilterTest(TestCase):
    def setUp(self):
        self.repo = MusicRepository()
        self.artist_a = Artist.objects.create(name="Artist A")
        self.artist_b = Artist.objects.create(name="Artist B")
        self.album_a = Album.objects.create(title="Album A", artist=self.artist_a)
        self.album_b = Album.objects.create(title="Album B", artist=self.artist_b)
        self.track1 = Music.objects.create(
            title="Love Song", artist=self.artist_a, album=self.album_a, is_public=True
        )
        self.track2 = Music.objects.create(
            title="Love Story", artist=self.artist_b, album=self.album_b, is_public=True
        )
        self.track3 = Music.objects.create(
            title="Private Jam", artist=self.artist_a, album=self.album_a, is_public=False
        )

    def test_no_filters_returns_all(self):
        result = self.repo.list()
        self.assertEqual(result.count(), 3)

    def test_filter_by_artist(self):
        result = self.repo.list({"artist": "Artist A"})
        self.assertEqual(result.count(), 2)
        self.assertIn(self.track1, result)
        self.assertIn(self.track3, result)

    def test_filter_by_album(self):
        result = self.repo.list({"album": "Album B"})
        self.assertEqual(result.count(), 1)
        self.assertIn(self.track2, result)

    def test_filter_by_is_public(self):
        result = self.repo.list({"is_public": False})
        self.assertEqual(result.count(), 1)
        self.assertIn(self.track3, result)

    def test_filter_by_title_icontains(self):
        result = self.repo.list({"title": "love"})
        self.assertEqual(result.count(), 2)
        self.assertIn(self.track1, result)
        self.assertIn(self.track2, result)

    def test_search_cross_field(self):
        result = self.repo.list({"search": "private"})
        self.assertEqual(result.count(), 1)
        self.assertIn(self.track3, result)

    def test_search_matches_artist_name(self):
        result = self.repo.list({"search": "Artist B"})
        self.assertEqual(result.count(), 1)
        self.assertIn(self.track2, result)

    def test_search_matches_album_title(self):
        result = self.repo.list({"search": "Album A"})
        self.assertEqual(result.count(), 2)
        self.assertIn(self.track1, result)
        self.assertIn(self.track3, result)

    def test_combined_filters(self):
        result = self.repo.list({"artist": "Artist A", "is_public": True})
        self.assertEqual(result.count(), 1)
        self.assertIn(self.track1, result)
