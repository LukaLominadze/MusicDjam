#!/usr/bin/env python3
"""
Automated setup for MusicDjam.

Creates venv, installs dependencies, builds containers, and provisions
the SeaweedFS S3 bucket with credentials written back to .env.

Usage:
    python Scripts/setup.py [--bucket NAME] [--user NAME]
"""
import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"
EXAMPLE_ENV = ROOT_DIR / ".example.env"


def run(cmd, **kwargs):
    """Run a command, stream output, return the CompletedProcess."""
    print(f"\n>>> {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    return subprocess.run(cmd, shell=isinstance(cmd, str), cwd=str(ROOT_DIR), **kwargs)


def run_stream(cmd):
    """Run a command and stream output live."""
    print(f"\n>>> {cmd}")
    proc = subprocess.Popen(
        cmd, shell=True, cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for line in proc.stdout:
        print(line, end="")
    return proc.wait()


def set_env_value(env_path, key, value):
    """Set a key=value pair in an env file, preserving order and comments."""
    lines = env_path.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n")


def get_env_value(env_path, key):
    """Read a single value from an env file."""
    for line in env_path.read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1]
    return None


def main():
    parser = argparse.ArgumentParser(description="Automated MusicDjam setup")
    parser.add_argument("--bucket", default=None, help="S3 bucket name (default: from .env)")
    parser.add_argument("--user", default="alice", help="SeaweedFS S3 user name (default: alice)")
    args = parser.parse_args()

    # ── Step 1: venv + install ────────────────────────────────────────
    print("\n" + "=" * 60)
    print("[1/6] Setting up Python virtual environment")
    print("=" * 60)

    venv_dir = ROOT_DIR / "venv"
    if not venv_dir.exists():
        run_stream(f"{sys.executable} -m venv {venv_dir}")

    if sys.platform == "win32":
        pip = str(venv_dir / "Scripts" / "pip")
        python = str(venv_dir / "Scripts" / "python")
    else:
        pip = str(venv_dir / "bin" / "pip")
        python = str(venv_dir / "bin" / "python")

    run_stream(f"{pip} install --upgrade pip")
    run_stream(f"{pip} install python-dotenv")
    run_stream(f"{pip} install .")

    # ── Step 2: volume directories ───────────────────────────────────
    print("\n" + "=" * 60)
    print("[2/6] Creating volume directories")
    print("=" * 60)

    for d in ("volumes/fs_admin", "volumes/fs_filer", "volumes/fs_master", "volumes/fs_volume"):
        (ROOT_DIR / d).mkdir(parents=True, exist_ok=True)
        print(f"  [+] {d}")

    # ── Step 3: .env ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("[3/6] Preparing .env")
    print("=" * 60)

    if not ENV_FILE.exists():
        import shutil
        shutil.copy2(EXAMPLE_ENV, ENV_FILE)
        print("  [+] Copied .example.env -> .env (edit variables as needed)")
    else:
        print("  [=] .env already exists, keeping current values")

    # Resolve any relative SSL paths to absolute paths (relative to project root)
    ssl_keys = ("SSL_DIR_PATH", "SSL_CERTIFICATE_PUBLIC_KEY_PATH", "SSL_CERTIFICATE_PRIVATE_KEY_PATH")
    for key in ssl_keys:
        val = get_env_value(ENV_FILE, key)
        if val and not os.path.isabs(val):
            abs_path = str((ROOT_DIR / val).resolve())
            set_env_value(ENV_FILE, key, abs_path)
            print(f"  [+] {key}: {val} -> {abs_path}")

    # ── Step 4: generate configs ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("[4/6] Generating infrastructure configs from templates")
    print("=" * 60)

    run_stream(f"{python} Scripts/generate_env.py")

    # ── Step 5: docker compose up ────────────────────────────────────
    print("\n" + "=" * 60)
    print("[5/6] Building and starting containers")
    print("=" * 60)

    run_stream("docker compose up -d --build")

    # ── Step 6: S3 bucket + user ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("[6/6] Provisioning SeaweedFS S3 bucket and user")
    print("=" * 60)

    bucket_name = args.bucket or get_env_value(ENV_FILE, "FS_S3_STORAGE_BUCKET_NAME") or "musicdjam"
    user_name = args.user

    # Check if credentials are already set (not defaults)
    current_key = get_env_value(ENV_FILE, "FS_S3_ACCESS_KEY_ID") or ""
    if current_key and current_key not in ("myaccesskeyid", "djangoaccesskeyid", ""):
        print(f"  [=] S3 credentials already set in .env (key: {current_key[:8]}...)")
        print("  [=] Skipping bucket/user provisioning.")
        print("      To re-provision, reset FS_S3_ACCESS_KEY_ID in .env and re-run.")
    else:
        print(f"  [*] Waiting for SeaweedFS master to be ready...")
        for attempt in range(30):
            result = subprocess.run(
                "docker compose exec -T fs-master wget -q -O /dev/null http://localhost:9333/cluster/status",
                shell=True, cwd=str(ROOT_DIR),
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                break
            time.sleep(2)
        else:
            print("  [-] SeaweedFS master did not become ready in time.")
            sys.exit(1)

        print(f"  [*] Creating bucket: {bucket_name}")
        run_stream(
            f"docker compose exec -T fs-master weed shell -filer= -master=fs-master:9333 "
            f"-c 's3.bucket.create -name {bucket_name}'"
        )

        print(f"  [*] Creating S3 user: {user_name}")
        result = subprocess.run(
            f"docker compose exec -T fs-master weed shell -filer= -master=fs-master:9333 "
            f"-c 's3.user.provision -name {user_name} -bucket {bucket_name} -role readwrite'",
            shell=True, cwd=str(ROOT_DIR),
            capture_output=True, text=True,
        )
        output = result.stdout + result.stderr
        print(output)

        # Parse credentials from output
        # seaweedfs outputs: AccessKey: <key>\nSecretKey: <secret>
        access_match = re.search(r"AccessKey[:\s]+(\S+)", output)
        secret_match = re.search(r"SecretKey[:\s]+(\S+)", output)

        if access_match and secret_match:
            access_key = access_match.group(1)
            secret_key = secret_match.group(1)

            set_env_value(ENV_FILE, "FS_S3_ACCESS_KEY_ID", access_key)
            set_env_value(ENV_FILE, "FS_S3_SECRET_ACCESS_KEY", secret_key)
            set_env_value(ENV_FILE, "FS_S3_DJANGO_ACCESS_KEY_ID", access_key)
            set_env_value(ENV_FILE, "FS_S3_DJANGO_SECRET_ACCESS_KEY", secret_key)

            print(f"\n  [+] Credentials written to .env:")
            print(f"      FS_S3_ACCESS_KEY_ID={access_key}")
            print(f"      FS_S3_DJANGO_ACCESS_KEY_ID={access_key}")
            print(f"      DJANGO_AWS_ACCESS_KEY_ID={access_key}")

            # Re-generate configs and restart so compose picks up new values
            print("\n  [*] Regenerating configs with new credentials...")
            run_stream(f"{python} Scripts/generate_env.py")

            print("  [*] Restarting containers...")
            run_stream("docker compose up -d")
        else:
            print("\n  [-] Could not parse AWS credentials from weed shell output.")
            print("      You may need to set them manually in .env:")
            print("        FS_S3_ACCESS_KEY_ID")
            print("        FS_S3_SECRET_ACCESS_KEY")
            print("        FS_S3_DJANGO_ACCESS_KEY_ID")
            print("        FS_S3_DJANGO_SECRET_ACCESS_KEY")

    # ── Done ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("[+] Setup complete!")
    print("=" * 60)
    print(f"\n  Django:    https://{get_env_value(ENV_FILE, 'DJANGO_DOMAIN')}")
    print(f"  Adminer:   https://{get_env_value(ENV_FILE, 'ADMINER_DOMAIN')}")
    print(f"  FS Admin:  https://{get_env_value(ENV_FILE, 'FS_ADMIN_DOMAIN')}")
    print(f"  FS S3:     https://{get_env_value(ENV_FILE, 'FS_S3_DOMAIN')}")


if __name__ == "__main__":
    main()
