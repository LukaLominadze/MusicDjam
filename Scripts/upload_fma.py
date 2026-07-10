#!/usr/bin/env python3
"""
Upload FMA dataset to database and object storage.

Reads metadata from FMA CSV files, uploads audio/image files to S3,
and creates corresponding database records.

Usage:
    python Scripts/upload_fma.py [--dry-run] [--skip-images] [--skip-audio]
"""
import os
import sys
import csv
import uuid
import argparse
import urllib.request
import ssl
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATASETS_DIR = ROOT_DIR / "datasets"
FMA_SMALL_DIR = DATASETS_DIR / "fma_small"
METADATA_DIR = DATASETS_DIR / "fma_metadata"

sys.path.insert(0, str(ROOT_DIR / "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musicdjam.settings")
os.environ["MIGRATE"] = "1"

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

if os.getenv("POSTGRES_PORT"):
    os.environ["POSTGRES_PORT"] = os.getenv("POSTGRES_PORT")

import django
django.setup()

import boto3
from botocore.config import Config as BotoConfig
from api.models import FileMetadata, Artist, Album, Music

S3_ENDPOINT = os.getenv("AWS_PUBLIC_STORAGE_URL", f"https://{os.getenv('FS_S3_DOMAIN')}:{os.getenv('FS_S3_PORT')}")
S3_ACCESS_KEY = os.getenv("FS_S3_DJANGO_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("FS_S3_DJANGO_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("FS_S3_STORAGE_BUCKET_NAME")
S3_REGION = os.getenv("FS_S3_REGION_NAME", "us-east-1")

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def get_s3_client():
    return boto3.client(
        service_name="s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        endpoint_url=S3_ENDPOINT,
        region_name=S3_REGION,
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


def s3_upload(client, file_path, key):
    content_type_map = {
        ".mp3": "audio/mpeg",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    ext = Path(file_path).suffix.lower()
    extra = {}
    if ext in content_type_map:
        extra["ContentType"] = content_type_map[ext]
    client.upload_file(str(file_path), S3_BUCKET, key, ExtraArgs=extra)


def download_url(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"    [!] Failed to download {url}: {e}")
        return False


def parse_duration(s):
    try:
        parts = s.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except (ValueError, IndexError):
        pass
    return 0


def read_csv_file(name):
    with open(METADATA_DIR / name, "r", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def get_mp3_ids():
    ids = set()
    for d in FMA_SMALL_DIR.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix == ".mp3":
                    ids.add(int(f.stem))
    return ids


def mp3_path(track_id):
    padded = str(track_id).zfill(6)
    return FMA_SMALL_DIR / padded[:3] / f"{padded}.mp3"


def create_metadata(file_type):
    return FileMetadata.objects.create(file_type=file_type)


def set_fs_id(metadata, fs_id):
    metadata.fs_id = fs_id
    metadata.save(update_fields=["fs_id"])


def upload_image(s3_client, url, record, field_name, tmp_prefix):
    ext = ".jpg"
    if ".png" in url:
        ext = ".png"
    tmp = Path(f"/tmp/{tmp_prefix}{ext}")
    try:
        if not download_url(url, tmp):
            return False
        fs_id = str(uuid.uuid4())
        s3_upload(s3_client, tmp, fs_id)
        meta = create_metadata(f"image/{'jpeg' if ext == '.jpg' else 'png'}")
        set_fs_id(meta, fs_id)
        setattr(record, field_name, meta)
        record.save(update_fields=[field_name])
        return True
    except Exception as e:
        print(f"    [!] Image upload failed for {tmp_prefix}: {e}")
        return False
    finally:
        tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Upload FMA dataset")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--skip-audio", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("FMA Dataset Upload")
    print("=" * 60)

    print("\n[1/5] Scanning fma_small...")
    mp3_ids = get_mp3_ids()
    print(f"  {len(mp3_ids)} tracks found")

    print("\n[2/5] Reading CSV metadata...")
    raw_tracks = read_csv_file("raw_tracks.csv")
    raw_artists = read_csv_file("raw_artists.csv")
    raw_albums = read_csv_file("raw_albums.csv")

    tracks = [t for t in raw_tracks if int(t["track_id"]) in mp3_ids]
    artists_map = {a["artist_id"]: a for a in raw_artists}
    albums_map = {a["album_id"]: a for a in raw_albums}

    artist_ids_needed = set(t["artist_id"] for t in tracks)
    album_ids_needed = set(t["album_id"] for t in tracks)
    artists_list = [artists_map[i] for i in artist_ids_needed if i in artists_map]
    albums_list = [albums_map[i] for i in album_ids_needed if i in albums_map]

    print(f"  {len(tracks)} tracks, {len(artists_list)} artists, {len(albums_list)} albums")

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    print("\n[3/5] Connecting to S3...")
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"  Bucket '{S3_BUCKET}' accessible")
    except Exception as e:
        print(f"  [-] S3 error: {e}")
        sys.exit(1)

    print("\n[4/5] Checking existing data...")
    existing_artists = set(Artist.objects.values_list("id", flat=True))
    existing_albums = set(Album.objects.values_list("id", flat=True))
    existing_music = set(Music.objects.values_list("id", flat=True))
    print(f"  DB: {len(existing_artists)} artists, {len(existing_albums)} albums, {len(existing_music)} music")

    print("\n[5/5] Uploading...")
    stats = {"artists": 0, "albums": 0, "tracks": 0, "images": 0, "audio": 0}
    errs = {"artists": 0, "albums": 0, "tracks": 0, "images": 0, "audio": 0}

    artist_id_map = {}
    print(f"\n  --- Artists ({len(artists_list)}) ---")
    for i, a in enumerate(artists_list):
        aid = a["artist_id"]
        name = (a["artist_name"] or f"Artist {aid}")[:100]
        try:
            obj = Artist.objects.create(name=name)
            artist_id_map[aid] = obj.id
            stats["artists"] += 1
        except Exception as e:
            print(f"    [!] Artist {aid}: {e}")
            errs["artists"] += 1
            continue

        if not args.skip_images and a.get("artist_image_file"):
            if upload_image(s3, a["artist_image_file"], obj, "cover", f"artist_{aid}"):
                stats["images"] += 1
            else:
                errs["images"] += 1

        if (i + 1) % 200 == 0:
            print(f"    {i + 1}/{len(artists_list)} artists...")

    print(f"  Artists: {stats['artists']} ok, {errs['artists']} err")

    album_id_map = {}
    print(f"\n  --- Albums ({len(albums_list)}) ---")
    for i, alb in enumerate(albums_list):
        alb_id = alb["album_id"]
        title = (alb["album_title"] or f"Album {alb_id}")[:100]
        fma_artist = next((t["artist_id"] for t in tracks if t["album_id"] == alb_id), None)
        django_artist = artist_id_map.get(fma_artist)

        try:
            obj = Album.objects.create(title=title, artist_id=django_artist)
            album_id_map[alb_id] = obj.id
            stats["albums"] += 1
        except Exception as e:
            print(f"    [!] Album {alb_id}: {e}")
            errs["albums"] += 1
            continue

        if not args.skip_images and alb.get("album_image_file"):
            if upload_image(s3, alb["album_image_file"], obj, "cover", f"album_{alb_id}"):
                stats["images"] += 1
            else:
                errs["images"] += 1

        if (i + 1) % 200 == 0:
            print(f"    {i + 1}/{len(albums_list)} albums...")

    print(f"  Albums: {stats['albums']} ok, {errs['albums']} err")

    print(f"\n  --- Tracks ({len(tracks)}) ---")
    for i, t in enumerate(tracks):
        tid = int(t["track_id"])
        title = (t["track_title"] or f"Track {tid}")[:100]
        duration = parse_duration(t.get("track_duration", ""))

        try:
            obj = Music.objects.create(
                title=title,
                length=duration,
                is_public=True,
                artist_id=artist_id_map.get(t["artist_id"]),
                album_id=album_id_map.get(t["album_id"]),
            )
            stats["tracks"] += 1
        except Exception as e:
            print(f"    [!] Track {tid}: {e}")
            errs["tracks"] += 1
            continue

        if not args.skip_audio:
            p = mp3_path(tid)
            if p.exists():
                fs_id = str(uuid.uuid4())
                try:
                    s3_upload(s3, p, fs_id)
                    meta = create_metadata("audio/mpeg")
                    set_fs_id(meta, fs_id)
                    obj.music_file = meta
                    obj.save(update_fields=["music_file"])
                    stats["audio"] += 1
                except Exception as e:
                    print(f"    [!] Audio {tid}: {e}")
                    errs["audio"] += 1

        if (i + 1) % 500 == 0:
            print(f"    {i + 1}/{len(tracks)} tracks...")

    print(f"  Tracks: {stats['tracks']} ok, {errs['tracks']} err")

    print("\n" + "=" * 60)
    print("Done!")
    print(f"  Artists:  {stats['artists']} created")
    print(f"  Albums:   {stats['albums']} created")
    print(f"  Tracks:   {stats['tracks']} created")
    print(f"  Images:   {stats['images']} uploaded")
    print(f"  Audio:    {stats['audio']} uploaded")
    if any(errs.values()):
        print(f"  Errors:   {sum(errs.values())}")
    print("=" * 60)


if __name__ == "__main__":
    main()
