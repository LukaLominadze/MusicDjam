#!/usr/bin/env python3
import os
import re
from pathlib import Path
from dotenv import load_dotenv

def env_generate():
    env_sample_content = ''
    with open('.example.env', 'r') as file:
        env_sample_content = file.read()
    env_content = ''
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            env_content = file.read()

    key_values = {}
    _split_key_values = env_content.split('\n')
    while '' in _split_key_values:
        _split_key_values.remove('')

    for kv in _split_key_values:
        pair = kv.split('=', 1)
        key_values[pair[0]] = pair[1]
        
    split_key_values = env_sample_content.split('\n')

    content = ''

    for sample_key_value in split_key_values:
        if sample_key_value == '':
            content += '\n'
            continue
        pair = sample_key_value.split('=', 1)
        if not pair[0] in key_values.keys():
            content += f'{pair[0]}={pair[1]}\n'
        else:
            content += f'{pair[0]}={key_values[pair[0]]}\n'

    with open('.env', 'w') as file:
        file.write(content)


def main():
    env_generate()

    # Establish root directory paths relative to this script
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    env_file = root_dir / ".env"
    
    if not env_file.exists():
        print(f"[-] Operational Error: Base file '.env' not found at: {env_file}")
        print("    Please build your local configuration layer first.")
        return
    
    load_dotenv(dotenv_path=env_file)

    targets = [
        root_dir / "compose.example.yaml",
        root_dir / "DockerScripts/Nginx/conf.d/django.example.conf",
        root_dir / "DockerScripts/Nginx/conf.d/fs-s3.example.conf",
        root_dir / "DockerScripts/Nginx/conf.d/fs-admin.example.conf",
        root_dir / "DockerScripts/Nginx/conf.d/adminer.example.conf",
    ]

    token_pattern = re.compile(r'\$([A-Z0-9_]+)\$')

    for target_path in targets:
        if not target_path.exists():
            print(f"[!] Warning: Target definition missing: {target_path}")
            continue
        
        # Resolve target nomenclature: {name}.example.{ext} -> {name}.{ext}
        output_name = target_path.name.replace(".example.", ".")
        output_path = target_path.parent / output_name

        print(f"[*] Processing template: {target_path.name} -> {output_name}")
        
        with open(target_path, "r", encoding="utf-8") as file:
            content = file.read()

        def replacer(match):
            var_name = match.group(1)
            # Fetch directly out of environment space updated by load_dotenv()
            value = os.getenv(var_name)
            if value is None:
                print(f"    [!] Warning: Template token '${var_name}$' has no matching mapping inside .env")
                return match.group(0)
            return str(value)

        processed_content = token_pattern.sub(replacer, content)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(processed_content)
            
    print("[+] All target infrastructure configuration configurations successfully updated.")

if __name__ == "__main__":
    main()
