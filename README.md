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
7. [Architecture & Services](#architecture--services)
8. [License](#license)

## Supported Platforms

Linux (Debian, Ubuntu tested)

## Requirements
- python3
- Docker
- gettext (msgfmt)

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

If you have css missing on your Django site, you can run this:
```
cd src
env $(cat ../.env | xargs) python3 manage.py collectstatic --noinput
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
python3 manage.py compilemessages
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

If you have css missing on your Django site, you can run this:
```
cd src
env $(cat ../.env | xargs) python3 manage.py collectstatic --noinput
```

## Dataset Population

Optionally, you can retrieve the [FMA](https://github.com/mdeff/fma) dataset.
**This will take a long time.**

```bash
python3 -m pip install -r Scripts/fma_requirements.txt
python3 Scripts/download_fma.py
python3 Scripts/upload_fma.py
```

## Architecture & Services

```
                    ┌────────────────┐
                    │   User/Client  │
                    └───────┬────────┘
                            │
                            ▼
                  ┌────────────────┐
                  │      Nginx     │
                  └───────┬──┬─────┘
                          │  │
             ┌────────────┘  └────────────┐
             │ (Web Traffic)              │ (Direct Media Streams)
             ▼                            ▼
   ┌──────────────────┐          ┌──────────────────┐
   │    src (Django)  │◄────────►│  fs-s3 / Filer  │
   └─────────┬────────┘          └──────────────────┘
             │
             ▼
   ┌──────────────────┐
   │  db (PostgreSQL) │
   └──────────────────┘
```

### Component Interactions
* **User ↔ Nginx:** All incoming requests (HTTP/HTTPS) hit the Nginx reverse proxy first. Nginx handles SSL termination (if configured) and acts as the secure gateway to internal services.
* **Nginx ↔ Django (`src`):** Nginx forwards frontend page views, playlist mutations, and API endpoint traffic straight to the underlying Django application server.
* **Nginx ↔ S3 Subsystem (`fs-s3`):** High-performance multimedia streams bypass the Django backend completely. Nginx proxies these data chunks directly from the SeaweedFS S3 gateway to offload heavy file I/O operations.
* **Django ↔ PostgreSQL (`db`):** Persistent relational data (such as user profiles, playlist relations, and track metadata) is structured and queried here.
* **Django ↔ S3 Subsystem:** The Django application interacts with the SeaweedFS internal endpoint using standard S3 API protocols to write uploaded music files, analyze metadata, and store cover art.

| Service / Container Name | Role & Purpose |
| :--- | :--- |
| **`nginx`** | The edge reverse proxy. Ingests all client traffic, offloads SSL termination, and maps domain routes to the backend applications. |
| **`src`** | The core application engine. Runs the Django framework, serving the HTML frontend templates, handling the REST API, and managing database migrations. |
| **`db`** | PostgreSQL relational database holding all application state, user accounts, and track metadata. |
| **`adminer`** | A lightweight database management tool providing a secure web user interface to inspect, query, and manage the PostgreSQL database. |
| **`fs-master,volume,filer`** | The core of object storage. |
| **`fs-s3`** | An Amazon S3-compatible API gateway exposed by SeaweedFS, allowing Django and client clients to interact with the file system using standard S3 client libraries. |
| **`fs-admin`** | The administrative web interface for SeaweedFS, allowing server operators to monitor cluster health, volume distribution, and storage metrics visually. |

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
