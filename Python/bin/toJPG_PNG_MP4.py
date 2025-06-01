import os
import sys
import pyperclip
import subprocess
from send2trash import send2trash
from PIL import Image

# Get script directory and ffmpeg path
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
ffmpeg_exe = os.path.join(script_dir, "bin", "ffmpeg", "bin", "ffmpeg.exe")

print("== Converting to JPG, PNG, MP4 ==")

# Get folder path from argument or clipboard
if len(sys.argv) > 1:
    targetFolderPath = sys.argv[1].strip('"')
else:
    try:
        targetFolderPath = pyperclip.paste().strip()
        if targetFolderPath.startswith('"') and targetFolderPath.endswith('"'):
            targetFolderPath = targetFolderPath[1:-1]
    except Exception as e:
        print(f"Error accessing clipboard: {e}")
        input("Press Enter to exit...")
        exit()

# Validate folder path
if not os.path.isdir(targetFolderPath):
    print("❌ Invalid folder path!")
    input("Press Enter to exit...")
    exit()

print(f"\n📂 Target folder: {targetFolderPath}")

# Extensions
video_extensions = ['.avi', '.mov', '.wmv', '.mkv', '.mts', '.m2ts', '.flv', '.3gp', '.webm', '.divx', '.ts']
image_extensions = ['.bmp', '.tiff', '.tif', '.webp', '.heic']
keep_image_extensions = ['.jpg', '.jpeg', '.png']

# Process files
for root, dirs, files in os.walk(targetFolderPath):
    for filename in files:
        file_path = os.path.join(root, filename)
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        # 🎥 VIDEO PROCESSING
        if ext == ".mp4":
            print(f"Skipping MP4 file: {file_path}")
            continue

        if ext in video_extensions:
            new_filepath = os.path.join(root, f"{name}.mp4")
            print(f"\nConverting video: {file_path} -> {new_filepath}")
            command = [ffmpeg_exe, '-i', file_path, '-c:v', 'copy', '-c:a', 'copy', new_filepath]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0 and os.path.isfile(new_filepath):
                print(f"✅ Success. Moving original video to Recycle Bin: {file_path}")
                send2trash(file_path)
            else:
                print(f"❌ Failed to convert video: {file_path}")
                print(result.stderr.decode('utf-8'))
            continue

        # 🎞️ GIF TO MP4
        if ext == '.gif':
            new_filepath = os.path.join(root, f"{name}.mp4")
            print(f"\nConverting GIF to MP4: {file_path} -> {new_filepath}")
            command = [ffmpeg_exe, '-i', file_path, '-movflags', '+faststart', '-pix_fmt', 'yuv420p', new_filepath]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0 and os.path.isfile(new_filepath):
                print(f"✅ Success. Moving original GIF to Recycle Bin: {file_path}")
                send2trash(file_path)
            else:
                print(f"❌ Failed to convert GIF: {file_path}")
                print(result.stderr.decode('utf-8'))
            continue

        # 🖼️ IMAGE PROCESSING
        if ext in keep_image_extensions:
            print(f"Keeping image: {file_path}")
            continue

        if ext in image_extensions:
            new_filepath = os.path.join(root, f"{name}.jpg")
            try:
                with Image.open(file_path) as img:
                    rgb_image = img.convert("RGB")
                    rgb_image.save(new_filepath, "JPEG")
                print(f"🖼️ Converted image to JPG: {file_path} -> {new_filepath}")
                send2trash(file_path)
            except Exception as e:
                print(f"❌ Failed to convert image: {file_path} — {e}")

print("\n✅ All conversions complete.")
input("Press Enter to exit...")