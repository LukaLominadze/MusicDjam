# MusicDjam / Earpiece

Self-hosted music listening platform.
https://musicdjam.kabada.org — See the hosted version

## Table of Contents
1. [Supported Platforms](#supported-platforms)
2. [Requirements](#requirements)
3. [Quick Start](#quick-start)
4. [Manual Setup](#manual-setup)
5. [S3 Bucket Provisioning](#s3-bucket-provisioning)
6. [Dataset Population](#dataset-population)
7. [License](#license)

## Supported Platforms

Linux (Debian, Ubuntu tested)

## Requirements
- python3
- Docker

## Quick Start

```bash
git clone https://github.com/LukaLominadze/MusicDjam
cd MusicDjam
# Editing .env is recommended before first boot
cp .example.env .env
python3 Scripts/setup.py
```

This sets up everything: venv, dependencies, Docker containers, and SeaweedFS S3 bucket with credentials.
Edit `.env` beforehand to customize domains, ports, volumes, ssl, or database credentials.


Options:

```
--bucket NAME    S3 bucket name (default: value from .env)
--user NAME      SeaweedFS S3 user name (default: alice)
```

## Manual Setup

If you prefer to run each step yourself:

```bash
git clone https://github.com/LukaLominadze/MusicDjam
cd MusicDjam

cp .example.env .env

python3 -m venv venv
source venv/bin/activate

cd src
python3 -m pip install .
cd ..

mkdir -p volumes/fs_admin volumes/fs_filer volumes/fs_master volumes/fs_volume

# run this every time a change is made in .env
python3 Scripts/generate_env.py

# initial run
docker compose up -d --build
```

### S3 bucket provisioning

Once containers are running, create the S3 bucket and user:

```bash
docker compose exec -it fs-master weed shell
# use info from .env
> s3.bucket.create -name my-bucket
> s3.user.provision -name alice -bucket my-bucket -role readwrite
```

Copy the outputted `AccessKey` and `SecretKey` into `.env`:

```
FS_S3_ACCESS_KEY_ID=<access key>
FS_S3_SECRET_ACCESS_KEY=<secret key>
FS_S3_DJANGO_ACCESS_KEY_ID=<access key>
FS_S3_DJANGO_SECRET_ACCESS_KEY=<secret key>
```

Then regenerate configs and restart:

```bash
python3 Scripts/generate_env.py
docker compose up -d
```

## Dataset Population

Optionally, you can retrieve the [FMA](https://github.com/mdeff/fma) dataset.
**This will take a long time.**

```bash
python3 -m pip install -r Scripts/fma_requirements.txt
python3 Scripts/download_fma.py
python3 Scripts/upload_fma.py
```

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
