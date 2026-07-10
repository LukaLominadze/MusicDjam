#!/usr/bin/env python3
import subprocess
import zipfile
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATASETS_DIR = ROOT_DIR / "datasets"

DATASETS_DIR.mkdir(exist_ok=True)

FILES = {
    "fma_metadata.zip": "https://os.unil.cloud.switch.ch/fma/fma_metadata.zip",
    "fma_small.zip": "https://os.unil.cloud.switch.ch/fma/fma_small.zip",
}


def download(name, url):
    dest = DATASETS_DIR / name
    if dest.exists():
        print(f"[=] {name} already exists, skipping download")
        return dest
    print(f"[+] Downloading {name}...")
    result = subprocess.run(
        ["curl", "-LO", "-C", "-", url],
        cwd=str(DATASETS_DIR),
    )
    if result.returncode != 0:
        print(f"[-] Failed to download {name}")
        sys.exit(1)
    return dest


def extract(zip_path):
    print(f"[+] Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(DATASETS_DIR)
    print(f"[+] Deleting {zip_path.name}...")
    zip_path.unlink()


def main():
    for name, url in FILES.items():
        zip_path = download(name, url)
        extract(zip_path)
    print("[+] Done. Dataset ready at:", DATASETS_DIR)


if __name__ == "__main__":
    main()
