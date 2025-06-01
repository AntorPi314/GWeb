import os
import re
import sys
import shutil
import json
import pyperclip
import requests
import subprocess

###########################################################################################################
# Get the path of the current script
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
print("Working Directory: " + script_dir + "\n")

ffmpeg_exe = os.path.join(script_dir, "bin", "ffmpeg", "bin", "ffmpeg.exe")
ffprobe_exe = os.path.join(script_dir, "bin", "ffmpeg", "bin", "ffprobe.exe")

seven_zip_path = os.path.join(script_dir, "bin", "7-Zip", "7z.exe")
backupFolder = backupFolder = os.path.join(script_dir, "my-media-backups")
os.makedirs(backupFolder, exist_ok=True)
m3u8_path = os.path.join(script_dir, "htdocs", "m3u8")
os.makedirs(m3u8_path, exist_ok=True)

# Try to read firebase URL from file
firebase_file = os.path.join(script_dir, "bin", "firebase.txt")
firebase = None
if os.path.exists(firebase_file):
    with open(firebase_file, 'r', encoding='utf-8') as f:
        firebase = f.read().strip()
else:
    print("📁 firebase.txt not found.")
    
# Try to read Zip Password from file
zip_file = os.path.join(script_dir, "bin", "zip-password.txt")
zip_password = None
if os.path.exists(zip_file):
    with open(zip_file, 'r', encoding='utf-8') as f:
        zip_password = f.read().strip()
else:
    print("📁 zip-password.txt not found. run setup file to make it.")
    input("Press Enter to exit...")
    exit(1)

# Try to read git username from file
git_username_file = os.path.join(script_dir, "bin", "git-username.txt")
git_username = None
if os.path.exists(git_username_file):
    with open(git_username_file, 'r', encoding='utf-8') as f:
        git_username = f.read().strip()
else:
    print("📁 git-username.txt not found. run setup file to make it.")
    input("Press Enter to exit...")
    exit(1)

###########################################################################################################
# SEGMENT_DURATION = "15"  # Default HLS segment duration (Second)
# Try to read Segment Duration from file
SEGMENT_DURATION_file = os.path.join(script_dir, "bin", "segment-duration.txt")
SEGMENT_DURATION = None
if os.path.exists(SEGMENT_DURATION_file):
    with open(SEGMENT_DURATION_file, 'r', encoding='utf-8') as f:
        SEGMENT_DURATION = f.read().strip()
else:
    print("📁 segment-duration.txt not found. run setup file to make it.")
    input("Press Enter to exit...")
    exit(1)
###########################################################################################################

def wait_for_user_input():
    input("Press Enter to exit...")
    exit(1)
###########################################################################################################
# Define fallback function
def get_valid_folder_path_from_user():
    while True:
        user_input = input("Enter a valid folder path: ").strip()

        # Remove surrounding quotes if any
        if user_input.startswith('"') and user_input.endswith('"'):
            user_input = user_input[1:-1]

        if os.path.exists(user_input) and os.path.isdir(user_input):
            return user_input
        else:
            print("Invalid path. Please try again.")

# Step 1: Check if folder path was passed as argument
if len(sys.argv) >= 2:
    targetFolderPath = sys.argv[1].strip('"')  # Remove quotes
    targetFolderPath = os.path.abspath(targetFolderPath)
    if not os.path.isdir(targetFolderPath):
        print(f"❌ Error: '{targetFolderPath}' is not a valid directory.")
        sys.exit(1)

else:
    # Step 2: Try clipboard path
    try:
        clipboard_path = pyperclip.paste().strip()

        # Remove surrounding quotes
        if clipboard_path.startswith('"') and clipboard_path.endswith('"'):
            clipboard_path = clipboard_path[1:-1]

        if os.path.exists(clipboard_path) and os.path.isdir(clipboard_path):
            targetFolderPath = clipboard_path
        else:
            print("Clipboard does not contain a valid folder path.")
            targetFolderPath = get_valid_folder_path_from_user()
    except Exception as e:
        print(f"Error accessing clipboard: {e}")
        targetFolderPath = get_valid_folder_path_from_user()

print(f"📁 Using folder path: {targetFolderPath}")
###########################################################################################################
lineSpace = []     
Pics_lineSpace = []
Vids_lineSpace = []

def process_media_folders(targetFolderPath):
    # Initialize counters
    pics_folder_counter = 1001
    vids_folder_counter = 1001
    pics_file_counter = 1001
    vids_file_counter = 1001
    
    # Process all folders
    for folder in sorted([f.path for f in os.scandir(targetFolderPath) if f.is_dir()]):
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            continue
            
        # Count images and videos separately
        pics_count = 0
        vids_count = 0
        img_exts = {'.jpg', '.jpeg', '.png'}
        
        # Separate files by type
        image_files = []
        video_files = []
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in img_exts:
                image_files.append(file)
                pics_count += 1
            elif ext == '.mp4':
                video_files.append(file)
                vids_count += 1
        
        # Skip if no media files
        if not (image_files or video_files):
            continue
            
        # Record counts for this folder
        lineSpace.append(f"{pics_count}:{vids_count}")
        if pics_count > 0:
            Pics_lineSpace.append(str(pics_count))
        if vids_count > 0:
            Vids_lineSpace.append(str(vids_count))
        
        # Process images if any exist
        if image_files:
            # Step 1: Rename images to temporary names
            temp_image_files = []
            for i, filename in enumerate(sorted(image_files), start=1):
                old_path = os.path.join(folder, filename)
                ext = os.path.splitext(filename)[1]
                temp_name = f"temp_pic{i}{ext}"
                temp_path = os.path.join(folder, temp_name)
                os.rename(old_path, temp_path)
                temp_image_files.append(temp_name)
            
            # Step 2: Rename folder (only if it's not already being processed as video)
            if not os.path.basename(folder).startswith('Vids'):
                new_folder_name = f"Pics{pics_folder_counter}"
                new_folder_path = os.path.join(targetFolderPath, new_folder_name)
                os.rename(folder, new_folder_path)
                folder = new_folder_path
                pics_folder_counter += 1
            
            # Step 3: Final rename for images with correct numbering
            for temp_name in sorted(temp_image_files):
                old_path = os.path.join(folder, temp_name)
                ext = os.path.splitext(temp_name)[1]
                new_name = f"pic{pics_file_counter}{ext}"
                new_path = os.path.join(folder, new_name)
                os.rename(old_path, new_path)
                pics_file_counter += 1
        
        # Process videos if any exist
        if video_files:
            # Step 1: Rename videos to temporary names
            temp_video_files = []
            for i, filename in enumerate(sorted(video_files), start=1):
                old_path = os.path.join(folder, filename)
                ext = os.path.splitext(filename)[1]
                temp_name = f"temp_vid{i}{ext}"
                temp_path = os.path.join(folder, temp_name)
                os.rename(old_path, temp_path)
                temp_video_files.append(temp_name)
            
            # Step 2: Rename folder (only if it's not already being processed as images)
            if not os.path.basename(folder).startswith('Pics'):
                new_folder_name = f"Vids{vids_folder_counter}"
                new_folder_path = os.path.join(targetFolderPath, new_folder_name)
                os.rename(folder, new_folder_path)
                folder = new_folder_path
                vids_folder_counter += 1
            
            # Step 3: Final rename for videos with correct numbering
            for temp_name in sorted(temp_video_files):
                old_path = os.path.join(folder, temp_name)
                ext = os.path.splitext(temp_name)[1]
                new_name = f"vid{vids_file_counter}{ext}"
                new_path = os.path.join(folder, new_name)
                os.rename(old_path, new_path)
                vids_file_counter += 1
    
    # Move all files to root and clean up
    for f in os.scandir(targetFolderPath):
        if f.is_dir() and (f.name.startswith('Pics') or f.name.startswith('Vids')):
            for file in os.listdir(f.path):
                src = os.path.join(f.path, file)
                dst = os.path.join(targetFolderPath, file)
                shutil.move(src, dst)
            shutil.rmtree(f.path)

process_media_folders(targetFolderPath)
# Print results
print("sub-folders pics:vids array = \"" + ", ".join(lineSpace) + "\"")
print("Continue...")

targetFolderName = os.path.basename(targetFolderPath)
pyperclip.copy(targetFolderName)

CollectionTypeName = re.sub(r'\d+$', '', targetFolderName)

m3u8_json_destination_path = os.path.join(m3u8_path, CollectionTypeName) + "\\"


###########################################################################################################
# URL
firebase_url = f"{firebase}/c/{CollectionTypeName}/{targetFolderName}.json"

# Firebase paths
dropdown_jsonPath = f"{firebase}/dropdown/{CollectionTypeName}.json"
path_jsonPath = f"{firebase}/path/{CollectionTypeName}.json"

# Default JSON values
dropdown_default_json = {
    "label": f"{CollectionTypeName}",
    "random": "1001-1001",
    "selected": False
}
path_default_json = {
    "m3u8": f"https://raw.githubusercontent.com/{git_username}/All/main/m3u8",
    "pics": f"https://github.com/{git_username}/All/releases/download"
}

default_value_vids = f"https://github.com/{git_username}/All/releases/download"
firebase_replace_url = f"{firebase}/pathVids/{CollectionTypeName}.json"

# Fetch from Firebase
response = requests.get(firebase_replace_url)

if response.status_code == 200:
    data = response.json()

    # Case 1: No data (None or empty string), ask user to set value
    if data is None or data == "":
        print("⛔ No data found in Firebase.")
        print(f"➡️ Setting value at: {firebase_replace_url}")
        user_input = input(
            f"Default video path is: {default_value_vids}\n"
            f"Type 'y' to use default -or- Enter a custom path -or- Press Enter to exit:\n>> "
        ).strip()

        if user_input == "":
            sys.exit(1)
        elif user_input.lower() == "y":
            value_to_set = default_value_vids
        else:
            value_to_set = user_input  # custom path entered by user

        # Push value to Firebase
        push_response = requests.put(firebase_replace_url, json=value_to_set)
        if push_response.status_code == 200:
            print("✅ Value set successfully.")
            replace_url = value_to_set  # Continue with the pushed value
        else:
            print(f"❌ Failed to set value. Code: {push_response.status_code}")
            sys.exit(1)

    # Case 2: Valid string already present
    elif isinstance(data, str):
        replace_url = data
        print(f"✅ Valid URL fetched: {replace_url}")

    # Case 3: Unexpected format
    else:
        print("❌ Unexpected data format in Firebase.")
        input(f"🚫 Error: Invalid format found at:\n{firebase_replace_url}\nPress Enter to exit.")
        sys.exit(1)

else:
    print(f"❌ Failed to fetch from Firebase: HTTP {response.status_code}")
    input(f"🚫 Error: Could not reach:\n{firebase_replace_url}\nPress Enter to exit.")
    sys.exit(1)


# Append target folder to the URL
replace_url = f"{replace_url}/{targetFolderName}/"
print(f"🔁 Final Replace URL: {replace_url}")
###########################################################################################################
# Configs
getVideoThumbnailFrom = 0
p_count = 0
json_path = CollectionTypeName                # 📘📘📘📘📘📘📘 (Change if need)
te_duratons = ""
ve_count = 0

targetFolderName_DIR = os.path.join(targetFolderPath, targetFolderName)
VIDS_DIR = os.path.join(targetFolderPath, "Vids")
PICS_DIR = os.path.join(targetFolderPath, "Pics")
M3U8_DIR = os.path.join(targetFolderPath, "Videos")
TRASH_DIR = os.path.join(targetFolderPath, "Trash")


# Check JSON already exists or not
try:
    response = requests.get(firebase_url)
    if response.status_code == 200:
        data = response.json()
        if data is not None:
            print("❌ Data already exists")
            user_input = input("\nType 'dlt' to delete this existing data, or press Enter to exit: \n>> ").strip().lower()
            if user_input == 'dlt':
                try:
                    delete_response = requests.delete(firebase_url)
                    if delete_response.status_code in [200, 204]:
                        print("🗑️ Data deleted successfully.")
                        input("\nPress Enter to exit...")
                        sys.exit()
                    else:
                        print(f"⚠️ Failed to delete data (Status Code: {delete_response.status_code})")
                        input("\nPress Enter to exit...")
                        sys.exit()
                except Exception as e:
                    print(f"⚠️ Error while deleting: {e}")
                    input("\nPress Enter to exit...")
                    sys.exit()
            else:
                print("❌ Exiting...")
                sys.exit()
        else:
            print("✅ Proceeding...")
    else:
        print(f"⚠️ Failed to fetch data (Status Code: {response.status_code})")
except Exception as e:
    print(f"⚠️ An error occurred: {e}")
    input("\nPress Enter to exit...")
    sys.exit()


# Create subfolders
try:
    subfolders = ["Pics", "Vids", targetFolderName, "Trash", "Videos"]
    for folder in subfolders:
        os.makedirs(os.path.join(targetFolderPath, folder), exist_ok=True)
except Exception as e:
    print(f"Error creating subfolders: {e}")
    wait_for_user_input()

# Move and rename images
try:
    p_index = 1001
    for file in os.listdir(targetFolderPath):
        if file.lower().endswith(('.jpeg', '.jpg', '.png')):
            new_name = f"p{p_index}.p"
            shutil.move(os.path.join(targetFolderPath, file), os.path.join(PICS_DIR, new_name))
            p_index += 1

    p_count = p_index - 1001
except Exception as e:
    print(f"Error moving and renaming images: {e}")
    wait_for_user_input()

# Move and rename videos
try:
    v_index = 1001
    for file in os.listdir(targetFolderPath):
        if file.lower().endswith(".mp4"):
            new_name = f"v{v_index}_.mp4"
            shutil.move(os.path.join(targetFolderPath, file), os.path.join(VIDS_DIR, new_name))
            v_index += 1

    ve_count = v_index - 1001
except Exception as e:
    print(f"Error moving and renaming videos: {e}")
    wait_for_user_input()

# Generate thumbnails
try:
    for i in range(1001, 1001 + ve_count):
        input_file = os.path.join(VIDS_DIR, f"v{i}_.mp4")
        temp_output_file = os.path.join(PICS_DIR, f"t{i}.jpg")  # Save as a temporary valid format
        final_output_file = os.path.join(PICS_DIR, f"v{i}.te")  # Rename later

        if os.path.exists(input_file):
            ffmpeg_cmd = [ffmpeg_exe, "-y", "-ss", str(getVideoThumbnailFrom), "-i", input_file, "-vframes", "1", temp_output_file]
            subprocess.run(ffmpeg_cmd, check=True)
            os.rename(temp_output_file, final_output_file)  # Rename to .te
except Exception as e:
    print(f"Error generating thumbnails: {e}")
    wait_for_user_input()

# Get video durations
try:
    durations = []
    for i in range(1001, 1001 + ve_count):
        input_file = os.path.join(VIDS_DIR, f"v{i}_.mp4")
        if os.path.exists(input_file):
            result = subprocess.run(
                [ffmpeg_exe.replace("ffmpeg.exe", "ffprobe.exe"),  # ← use ffprobe instead
                 "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", input_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            duration_str = result.stdout.strip()
            if duration_str:
                duration = float(duration_str)
                minutes, seconds = divmod(int(duration), 60)
                hours, minutes = divmod(minutes, 60)
                if hours > 0:
                    durations.append(f"{hours}:{minutes:02}:{seconds:02}")
                else:
                    durations.append(f"{minutes}:{seconds:02}")
    te_duratons = ", ".join(durations)
except Exception as e:
    print(f"Error getting video durations: {e}")
    wait_for_user_input()


# Move other files to "Trash"
try:
    trash_path = os.path.join(targetFolderPath, "Trash")
    for file in os.listdir(targetFolderPath):
        if file not in subfolders:
            shutil.move(os.path.join(targetFolderPath, file), os.path.join(trash_path, file))
except Exception as e:
    print(f"Error moving files to Trash: {e}")
    wait_for_user_input()

# Create info JSON
try:
    info_json = {
        "p": f"1-{p_count}",
        "te": te_duratons,
        "ve": f"1-{ve_count}"
    }
    
    # Add lineSpace if it exists and is not empty
    if lineSpace:  # This checks if the list is not empty
        info_json["lineSpace"] = ", ".join(lineSpace)
        
except Exception as e:
    print(f"Error creating info JSON: {e}")
    wait_for_user_input()

# Save JSON
try:
    info_json_path = os.path.join(targetFolderPath, targetFolderName, "info.json")
    with open(info_json_path, "w") as f:
        json.dump(info_json, f, indent=4)
except Exception as e:
    print(f"Error saving JSON: {e}")
    wait_for_user_input()

# Push JSON to Firebase
try:
    requests.put(firebase_url, json=info_json)
except Exception as e:
    print(f"Error pushing JSON to Firebase: {e}")
    wait_for_user_input()

print("File Processing complete!")

# Convert to m3u8 format
try:
    keyinfo_path = os.path.join(script_dir, "enc.keyinfo")

    for entry in os.scandir(VIDS_DIR):
        if entry.is_file():
            name, ext = os.path.splitext(entry.name)
            output_file = os.path.join(M3U8_DIR, f"{name}.m3u8")

            # Run FFmpeg command based on presence of enc.keyinfo
            if os.path.exists(keyinfo_path):
                ffmpeg_cmd = [
                    ffmpeg_exe, "-y", "-noautorotate", "-i", entry.path,
                    "-codec:", "copy", "-start_number", "0", "-hls_time", SEGMENT_DURATION,
                    "-hls_list_size", "0", "-hls_key_info_file", keyinfo_path, "-f", "hls", output_file
                ]
                print(f"🔐 Converting with encryption: {entry.name} → {output_file}")
            else:
                ffmpeg_cmd = [
                    ffmpeg_exe, "-y", "-noautorotate", "-i", entry.path,
                    "-codec:", "copy", "-start_number", "0", "-hls_time", SEGMENT_DURATION,
                    "-hls_list_size", "0", "-f", "hls", output_file
                ]
                print(f"🔓 Converting without encryption: {entry.name} → {output_file}")

            try:
                subprocess.run(ffmpeg_cmd, check=True)
                print(f"✔ Successfully converted: {entry.name}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to convert: {entry.name} ({e})")
except Exception as e:
    print(f"Error converting to m3u8 format: {e}")
    wait_for_user_input()

print("✅ All conversions completed.")


# Process each .m3u8 file
try:
    for file_name in os.listdir(M3U8_DIR):
        if file_name.endswith(".m3u8"):
            file_path = os.path.join(M3U8_DIR, file_name)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Replace .ts file references with new URL and .ve extension
            content = re.sub(r"(\n#EXTINF:[0-9.]+,\n)([\w\-]+)\.ts", rf"\1{replace_url}\2.ve", content)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

    print("All .m3u8 files updated successfully!")
except Exception as e:
    print(f"Error processing .m3u8 files: {e}")
    wait_for_user_input()

# Move all .m3u8 files
try:
    for filename in os.listdir(M3U8_DIR):
        if filename.endswith(".ts"):
            os.rename(
                os.path.join(M3U8_DIR, filename),
                os.path.join(M3U8_DIR, filename.replace(".ts", ".ve"))
            )
            
    for filename in os.listdir(M3U8_DIR):
        if filename.endswith(".m3u8"):
            shutil.move(
                os.path.join(M3U8_DIR, filename),
                os.path.join(targetFolderName_DIR, filename)
            )
except Exception as e:
    print(f"Error moving .m3u8 files: {e}")
    wait_for_user_input()

# Move all .m3u8 and json to safe place
try:
    shutil.copytree(targetFolderName_DIR, os.path.join(m3u8_json_destination_path, targetFolderName), dirs_exist_ok=True)
except Exception as e:
    print(f"Error moving .m3u8 and JSON files: {e}")
    wait_for_user_input()
    
# Rename all .m3u8 to .m
for filename in os.listdir(targetFolderName_DIR):
    if filename.endswith(".m3u8"):
        old_path = os.path.join(targetFolderName_DIR, filename)
        new_filename = filename.replace(".m3u8", ".m")
        new_path = os.path.join(targetFolderName_DIR, new_filename)
        os.rename(old_path, new_path)

        
# Create zip file using 7-Zip (All .m3u8 files)
try:
    zip_file_path = os.path.join(M3U8_DIR, "v.zip")

    command = [
        seven_zip_path, "a", "-tzip", zip_file_path, f"{targetFolderName_DIR}\*", f"-p{zip_password}", "-mem=AES256"
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Show success message
    if result.returncode == 0:
        print("Password-protected ZIP created successfully(1)!")
    else:
        print("Error occurred:", result.stderr)

    # Rename .zip to .zo
    new_zip_path = zip_file_path.replace(".zip", ".zo")
    os.rename(zip_file_path, new_zip_path)
except Exception as e:
    print(f"Error creating ZIP file(1): {e}")
    wait_for_user_input()

# Create zip file using 7-Zip (All image)
try:
    zip_file_path = os.path.join(M3U8_DIR, "p.zip")

    command = [
        seven_zip_path, "a", "-tzip", zip_file_path, f"{PICS_DIR}\*", f"-p{zip_password}", "-mem=AES256"
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Show success message
    if result.returncode == 0:
        print("Password-protected ZIP created successfully(2)!")
    else:
        print("Error occurred(2):", result.stderr)

    # Rename .zip to .zo
    new_zip_path = zip_file_path.replace(".zip", ".zo")
    os.rename(zip_file_path, new_zip_path)
except Exception as e:
    print(f"Error creating ZIP file: {e}")
    wait_for_user_input()

# Delete v.zo in PICS_DIR
v_zo_PATH = os.path.join(PICS_DIR, "v.zo")
if os.path.exists(v_zo_PATH):
    os.remove(v_zo_PATH)


# Check if the Trash folder is empty
try:
    if not os.listdir(TRASH_DIR):  # os.listdir() returns an empty list if the folder is empty
        os.rmdir(TRASH_DIR)  # Delete the empty folder
        print("✅ 'Trash' folder is empty and has been deleted.")
    else:
        print("❌ 'Trash' folder is not empty.")
except Exception as e:
    print(f"Error checking Trash folder: {e}")
    wait_for_user_input()
    
    
for file_name in os.listdir(PICS_DIR):
    if file_name.endswith(".p"):
        source_file = os.path.join(PICS_DIR, file_name)
        destination_file = os.path.join(VIDS_DIR, file_name[:-2] + ".jpg")  # Replace .p with .jpg

        # Copy the file with the new extension
        shutil.copy2(source_file, destination_file)
        
        
new_folder_name = os.path.join(targetFolderPath, targetFolderName + "_backup")
if os.path.exists(VIDS_DIR):
    os.rename(VIDS_DIR, new_folder_name)
    

files = [f for f in os.listdir(M3U8_DIR) if os.path.isfile(os.path.join(M3U8_DIR, f))]
files.sort()
if len(files) < 400:
    print("Total files less than 400. Organization skipped.")
else:
    folder_number = 1
    file_count = 0
    folder_path = os.path.join(M3U8_DIR, str(folder_number))
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        shutil.move(os.path.join(M3U8_DIR, file), os.path.join(folder_path, file))
        file_count += 1

        if file_count >= 400:
            folder_number += 1
            folder_path = os.path.join(M3U8_DIR, str(folder_number))
            os.makedirs(folder_path, exist_ok=True)
            file_count = 0

    print("Files have been organized successfully.")


print("Files copied successfully!")

print("✅ All Work completed.")
################################################################################################
# --- Check and push dropdown_jsonPath if needed ---
response_dropdown = requests.get(dropdown_jsonPath)
if response_dropdown.status_code == 200:
    dropdown_data = response_dropdown.json()
    if dropdown_data is None:
        print(f"🟡 No data found at: {dropdown_jsonPath}")
        push = requests.put(dropdown_jsonPath, json=dropdown_default_json)
        if push.status_code == 200:
            print(f"✅ Default dropdown JSON pushed to: {dropdown_jsonPath}")
        else:
            print(f"❌ Failed to push default dropdown JSON. Code: {push.status_code}")
else:
    print(f"❌ Failed to fetch: {dropdown_jsonPath} | Code: {response_dropdown.status_code}")

# --- Check and push path_jsonPath if needed ---
response_path = requests.get(path_jsonPath)
if response_path.status_code == 200:
    path_data = response_path.json()
    if path_data is None:
        print(f"🟡 No data found at: {path_jsonPath}")
        push = requests.put(path_jsonPath, json=path_default_json)
        if push.status_code == 200:
            print(f"✅ Default path JSON pushed to: {path_jsonPath}")
        else:
            print(f"❌ Failed to push default path JSON. Code: {push.status_code}")
else:
    print(f"❌ Failed to fetch: {path_jsonPath} | Code: {response_path.status_code}")
################################################################################################
# if lineSpace is not empty than >> in new_folder_name folder create folder(F1, F2, F3...) and move files for created folder accroding to liSpace array

if lineSpace:
    try:
        print("\nRestoring folder structure based on lineSpace...")
        
        # Get all files from the backup folder and separate them into pics and vids
        backup_files = [f for f in os.listdir(new_folder_name) if os.path.isfile(os.path.join(new_folder_name, f))]
        
        # Sort files with pics first (p*.jpg) then vids (v*_.mp4)
        pic_files = sorted([f for f in backup_files if f.startswith('p') and (f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png'))])
        vid_files = sorted([f for f in backup_files if f.startswith('v') and f.endswith('_.mp4')])
        
        pic_index = 0
        vid_index = 0
        
        # Create folders and move files according to lineSpace
        for i, counts in enumerate(lineSpace, start=1):
            # Parse the pics:vids counts
            try:
                pics_count, vids_count = map(int, counts.split(':'))
            except:
                print(f"❌ Invalid lineSpace format: {counts}")
                continue
                
            folder_name = f"F{i}"
            folder_path = os.path.join(new_folder_name, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Move picture files
            moved_pics = 0
            while moved_pics < pics_count and pic_index < len(pic_files):
                src = os.path.join(new_folder_name, pic_files[pic_index])
                dst = os.path.join(folder_path, pic_files[pic_index])
                shutil.move(src, dst)
                pic_index += 1
                moved_pics += 1
            
            # Move video files
            moved_vids = 0
            while moved_vids < vids_count and vid_index < len(vid_files):
                src = os.path.join(new_folder_name, vid_files[vid_index])
                dst = os.path.join(folder_path, vid_files[vid_index])
                shutil.move(src, dst)
                vid_index += 1
                moved_vids += 1
            
            print(f"Created {folder_name} with {moved_pics} pics and {moved_vids} vids")
            
            if moved_pics < pics_count or moved_vids < vids_count:
                print(f"⚠️ Warning: Not enough files to fill folder {folder_name} (expected {pics_count}p:{vids_count}v, got {moved_pics}p:{moved_vids}v)")
                    
        print("✅ Folder structure restored successfully.")
        
        # Move any remaining files to a special folder
        remaining_files = []
        remaining_files.extend(pic_files[pic_index:])
        remaining_files.extend(vid_files[vid_index:])
        
        if remaining_files:
            remaining_folder = os.path.join(new_folder_name, "Remaining")
            os.makedirs(remaining_folder, exist_ok=True)
            for remaining_file in remaining_files:
                src = os.path.join(new_folder_name, remaining_file)
                dst = os.path.join(remaining_folder, remaining_file)
                shutil.move(src, dst)
            print(f"⚠️ Moved {len(remaining_files)} remaining files to 'Remaining' folder")
            
    except Exception as e:
        print(f"❌ Error restoring folder structure: {e}")
        wait_for_user_input()
################################################################################################
destination_path = os.path.join(backupFolder, os.path.basename(new_folder_name))

if os.path.exists(destination_path):
    print(f"⚠️ Warning: Backup folder already exists at {destination_path}")
    print("Skipping backup to avoid overwriting existing data.")
else:
    try:
        shutil.move(new_folder_name, destination_path)
        print("✅ Backup completed successfully.")
    except Exception as e:
        print(f"❌ Error during backup: {e}")
        
try:
    shutil.rmtree(targetFolderName_DIR)
except Exception as e:
    print(f"❌ Error deleting folder {targetFolderName_DIR}: {e}")
################################################################################################

print("✅ All operations completed successfully")
input("Press Enter to exit...")