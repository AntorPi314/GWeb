import base64
import os
import sys
import shutil
import requests
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

# ---------------- Encryption / Decryption ----------------

def encrypt(plain_text: str, key: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    aes_key = kdf.derive(key.encode())
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(iv, plain_text.encode(), None)
    combined = salt + iv + ciphertext
    return base64.b64encode(combined).decode()

def decrypt(encrypted_text: str, key: str) -> str:
    combined = base64.b64decode(encrypted_text)
    salt = combined[:16]
    iv = combined[16:28]
    ciphertext = combined[28:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    aes_key = kdf.derive(key.encode())
    aesgcm = AESGCM(aes_key)
    decrypted = aesgcm.decrypt(iv, ciphertext, None)
    return decrypted.decode()

# ---------------- Push JSON to Firebase ----------------

def check_and_push(url, default_data, name):
    print(f"\n🔍 Checking {name}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data is not None:
                print(f"✔ {name} already exists. Delete it if you want to remake it.")
                
                
            else:
                print(f"✅ {name} is empty. Proceeding to push...")
                push = requests.put(url, json=default_data)
                if push.status_code == 200:
                    print(f"✅ {name} pushed successfully.")
                else:
                    print(f"❌ Failed to push {name}. Status: {push.status_code}")
                    input("\nPress Enter to exit...")
                    sys.exit()
        else:
            print(f"⚠️ Failed to fetch {name} (Status Code: {response.status_code})")
            input("\nPress Enter to exit...")
            sys.exit()
    except Exception as e:
        print(f"⚠️ Error occurred while checking {name}: {e}")
        input("\nPress Enter to exit...")
        sys.exit()

# ---------------- Main Script ----------------

def main():
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    bin_path = os.path.join(script_dir, "bin")
    os.makedirs(bin_path, exist_ok=True)
    print("Working Directory: " + script_dir + "\n")
    
    # === Firebase Information ===
    print("== Firebase Information ==")
    firebase_path = os.path.join(script_dir, "bin", "firebase.txt")
    if os.path.exists(firebase_path):
        print("📁 firebase.txt already exists. Delete it if you want to remake it.")
        with open(firebase_path, 'r', encoding='utf-8') as f:
            firebase = f.read().strip()
    else:
        print("\n🔐 Your Firebase Realtime Database must be PUBLIC (read/write)")
        firebase = input("📥 Enter your Firebase URL:(Example: https://your-url-path.firebaseio.com)\n>> ").strip()
        with open(firebase_path, 'w', encoding='utf-8') as f:
            f.write(firebase)
        print("✅ Firebase URL saved.")

    # === index.html generation ===
    print("\n\n== Gallery Web HTML Maker ==")
    destination_path = os.path.join(script_dir, "htdocs", "index.html")
    if os.path.exists(destination_path):
        print("📁 index.html already exists. Delete it if you want to remake it.")
        skip_making = True
    else:
        skip_making = False

    if not skip_making:
        key = input("🔑 Enter a new passcode: ")
        encrypted_data = encrypt(firebase, key)
        source_path = os.path.join(script_dir, "bin", "website")
        if not os.path.exists(source_path):
            print(f"❌ Error: {source_path} not found.")
            input("\nPress Enter to exit...")
            return
        shutil.copyfile(source_path, destination_path)
        with open(destination_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        updated_content = html_content.replace("ABC-DEF-GHI-JKL-MNO-PQR-STU-VWX-YZ", encrypted_data)
        with open(destination_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("✅ index.html created and updated.")

    # === Github Username ===
    print("\n\n== Github Username ==")
    git_username_path = os.path.join(script_dir, "bin", "git-username.txt")
    if os.path.exists(git_username_path):
        print("📁 git-username.txt already exists. Delete it if you want to remake it.")
        with open(git_username_path, 'r', encoding='utf-8') as f:
            git_username = f.read().strip()
    else:
        git_username = input("📥 Enter your Github username:\n>> ").strip()
        with open(git_username_path, 'w', encoding='utf-8') as f:
            f.write(git_username)
        print("✅ Github Username saved.")
        
        
    # === Github README.md ===
    print("\n\n== Github README.md ==")
    git_README_path = os.path.join(script_dir, "htdocs", "README.md")
    if os.path.exists(git_README_path):
        print("📁 README.md already exists. Delete it if you want to remake it.")
        with open(git_README_path, 'r', encoding='utf-8') as f:
            git_README = f.read().strip()
    else:
        README_data = f"<h1>GWeb - Gallery Web</h1>\n\nhttps://{git_README}.github.io/All"
        with open(git_README_path, 'w', encoding='utf-8') as f:
            f.write(README_data)
        print("✅ Github README.md saved.")


    # === Zip Password File ===
    print("\n\n== Zip Password ==")
    zip_pass = os.path.join(script_dir, "bin", "zip-password.txt")
    if not os.path.exists(zip_pass):
        with open(zip_pass, 'w', encoding='utf-8') as f:
            f.write("@1234")
        print("✅ zip-password.txt created. Default password is >> '@1234'")
    else:
        print("📁 zip-password.txt already exists. Delete it if you want to remake it.")

    # === Segment Duration ===
    print("\n\n== Segment Duration ==")
    SEGMENT_DURATION_file = os.path.join(script_dir, "bin", "segment-duration.txt")
    if not os.path.exists(SEGMENT_DURATION_file):
        with open(SEGMENT_DURATION_file, 'w', encoding='utf-8') as f:
            f.write("15")
        print("✅ segment-duration.txt created. Default password is >> '15' Second")
    else:
        print("📁 segment-duration.txt already exists. Delete it if you want to remake it.")
        
        
    # === Git Ignore ===
    print("\n\n== Git Ignore ==")
    gitignore_file = os.path.join(script_dir, ".gitignore")
    gitignore_file_2 = os.path.join(script_dir, "htdocs", ".gitignore")
    save_data = "**/enc.key\n**/firebase.txt\n**/zip-password.txt\n**/enc.keyinfo"
    if not os.path.exists(gitignore_file):
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(save_data)
        print("✅ .gitignore (1) created.")
    else:
        print("📁 .gitignore (1) already exists. Delete it if you want to remake it.")
        
    if not os.path.exists(gitignore_file_2):
        with open(gitignore_file_2, 'w', encoding='utf-8') as f:
            f.write(save_data)
        print("✅ .gitignore (2) created.")
    else:
        print("📁 .gitignore (2) already exists. Delete it if you want to remake it.")


    # === enc.key File ===
    print("\n\n== enc.key File ==")
    enc_key = os.path.join(script_dir, "htdocs", "enc.key")
    if not os.path.exists(enc_key):
        with open(enc_key, 'w', encoding='utf-8') as f:
            f.write("A000-000-000-000")
        print("✅ enc.key created. Default key is >> 'A000-000-000-000'")
    else:
        print("📁 enc.key already exists. Delete it if you want to remake it.")

    # === enc.keyinfo File ===
    print("\n\n== enc.keyinfo File ==")
    enc_info = os.path.join(script_dir, "enc.keyinfo")
    if not os.path.exists(enc_info):
        with open(enc_info, 'w', encoding='utf-8') as f:
            f.write("http://127.0.0.1:8080/enc.key\nhtdocs\enc.key")
        print("✅ enc.keyinfo created.")
    else:
        print("📁 enc.keyinfo already exists. Delete it if you want to remake it.")

    # === Firebase Database 1st Push Check ===
    print("\n\n== Firebase Database 1st Push Check ==")
    CollectionTypeName = "All"
    dropdown_jsonPath = f"{firebase}/dropdown/All.json"
    path_jsonPath = f"{firebase}/path/All.json"
    pathVids_jsonPath = f"{firebase}/pathVids/All.json"

    dropdown_default_json = {
        "label": f"{CollectionTypeName}",
        "random": "1001-1001",
        "selected": True
    }
    path_default_json = {
        "m3u8": f"https://raw.githubusercontent.com/{git_username}/All/main/m3u8",
        "pics": f"https://github.com/{git_username}/All/releases/download"
    }
    pathVids_data = f"https://github.com/{git_username}/All/releases/download"

    check_and_push(dropdown_jsonPath, dropdown_default_json, "dropdown/All.json")
    check_and_push(path_jsonPath, path_default_json, "path/All.json")
    check_and_push(pathVids_jsonPath, pathVids_data, "pathVids/All.json")

    
    # === Reset Options ===
    print("\n\n== Reset Option ==")
    user_input = input("\nType 'reset' to delete existing data and reset, or press Enter to exit: \n>> ").strip().lower()

    if user_input == "reset":
        print("\n🧹 Resetting data...")

        # Files and folders to delete
        paths_to_delete = [
            firebase_path,
            git_username_path,
            zip_pass,
            SEGMENT_DURATION_file,
            gitignore_file,
            gitignore_file_2,
            destination_path,
            enc_key,
            enc_info
        ]

        for path in paths_to_delete:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"🗑 Deleted: {path}")
            except Exception as e:
                print(f"⚠️ Could not delete {path}: {e}")

        print("\n🔁 Restarting script...\n")
        main()  # Restart the script from beginning
    else:
        print("\n👋 Exiting script. Goodbye!")
        

if __name__ == "__main__":
    main()
