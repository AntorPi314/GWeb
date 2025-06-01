import os
import sys
import shutil
import pyperclip

def wait_and_exit(msg="Press Enter to exit..."):
    input(msg)
    exit(1)

# Get folder path from argument or clipboard
if len(sys.argv) > 1:
    target_folder_path = sys.argv[1].strip('"')
else:
    try:
        target_folder_path = pyperclip.paste().strip()
        if target_folder_path.startswith('"') and target_folder_path.endswith('"'):
            target_folder_path = target_folder_path[1:-1]
    except Exception as e:
        print(f"❌ Error accessing clipboard: {e}")
        wait_and_exit()

# Validate folder path
if not os.path.isdir(target_folder_path):
    print("❌ Invalid folder path!")
    wait_and_exit()

print(f"\n📂 Target folder: {target_folder_path}")

# Define subdirectories
VIDS_DIR = os.path.join(target_folder_path, "Vids")
PICS_DIR = os.path.join(target_folder_path, "Pics")
M3U8_DIR = os.path.join(target_folder_path, "Videos")
TRASH_DIR = os.path.join(target_folder_path, "Trash")
targetFolderName = os.path.basename(target_folder_path)
targetFolderName_DIR = os.path.join(target_folder_path, targetFolderName)

# Convert .p files in Pics to .jpg and move to Vids
if os.path.isdir(PICS_DIR):
    if not os.path.exists(VIDS_DIR):
        os.makedirs(VIDS_DIR)
    for file_name in os.listdir(PICS_DIR):
        if file_name.endswith(".p"):
            src = os.path.join(PICS_DIR, file_name)
            dest = os.path.join(VIDS_DIR, file_name[:-2] + ".jpg")  # Rename .p to .jpg
            try:
                shutil.copy2(src, dest)
            except Exception as e:
                print(f"❌ Error copying {file_name}: {e}")

# Move all files from Vids to target folder
if os.path.isdir(VIDS_DIR):
    for file_name in os.listdir(VIDS_DIR):
        src = os.path.join(VIDS_DIR, file_name)
        dest = os.path.join(target_folder_path, file_name)
        try:
            shutil.move(src, dest)
        except Exception as e:
            print(f"❌ Error moving {file_name}: {e}")
    shutil.rmtree(VIDS_DIR, ignore_errors=True)

# Remove other directories
for folder in [PICS_DIR, M3U8_DIR, TRASH_DIR]:
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)

try:
    shutil.rmtree(targetFolderName_DIR)
except Exception as e:
    print(f"❌ Error deleting folder {targetFolderName_DIR}: {e}")

print("\n✅ Successfully Back Tracked.")
input("Press Enter to exit...")
