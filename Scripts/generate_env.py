#!/usr/bin/env python3
import os
import re
from pathlib import Path
from dotenv import load_dotenv

def main():
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