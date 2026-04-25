# setup.py - Run this when setting up the project for the first time 
import secrets 
import os
from pathlib import Path

def setup_jwt_secret():
    env_file = Path(".env")

    if not env_file.exists():
        print(".env file not found")
        return
    
    # Read .env file 
    with open(env_file, "r") as f:
        lines = f.readlines()

    # Check if SECRET_KEY exists
    modified = False
    for i, line in enumerate(lines):
        if line.startswith("SECRET_KEY="):
            # Check if it's empty or default 
            value = line.split("=", 1)[1].strip()
            if not value or value == "your-super-secret-key-change-this":
                # Generate new secret 
                new_secret = secrets.token_urlsafe(32)
                lines[i] = f"SECRET_KEY={new_secret}\n"
                modified = True
                print(f"Updated SECRET_KEY with new secure key")
                break

    if modified:
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        print("Secret saved in .env")
    else:
        print("SECRET_KEY already has value")

if __name__ == "__main__":
    setup_jwt_secret()

