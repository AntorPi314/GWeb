<h1><img src="https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/icon.svg" width="30" style="vertical-align: middle;"/> GWeb - Gallery Web</h1>

A lightweight media-serving web app

Demo: https://antorpi314.github.io/GWeb/Website

## 🌟 Features
- **Organized Media Storage**  
  Easily upload and manage your photos and videos in a clean, structured layout.

- **Encrypted Video Streaming**  
  Videos are **encrypted before upload** and can be securely streamed from anywhere.

- **Password-Protected Website**  
  Full access control with a secure login system to keep your media private.

- **Firebase Realtime Database**  
  Uses a secure Firebase backend to store and sync data in real time.




## ⚙️ Setup Requirements

1. ✅ Firebase Realtime Database  
2. ✅ GitHub Desktop (signed in with your GitHub account)  
3. ✅ VLC Player (Windows) & MX Player Pro (Android)

📦 Python Dependencies
```bash
pip install pyperclip requests cryptography Send2Trash Pillow
```


<h2><img src="https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/youtube.svg" width="30" style="vertical-align: middle;"/> YouTube Tutorial</h2>

- [GWeb Setup Tutorial](https://youtu.be/ElEUCZjwg24)
- [GWeb – How to Play Video from Another PC](https://youtu.be/R2FcvYgmSLw)



## ⌨️ Keyboard & Mouse Shortcuts

| Shortcut                | Action Description                                      |
|-------------------------|----------------------------------------------------------|
| `Alt + S`              | Start / Stop the server                                  |
| `Ctrl + Shift + G`     | Convert your media for upload                            |
| `Ctrl + Shift + Z`     | Revert converted media back to original                  |
| `Ctrl + Shift + M`     | Convert media formats to JPG, PNG, or MP4                |
| `Alt + Mouse-Click`    | Launch the selected video in **VLC Player**              |


## 📸 Screenshots

![Screenshot 1](https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/s1.png)
![Screenshot 1](https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/s1c.png)
![Screenshot 2](https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/s2.jpg)
![Screenshot 3](https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/s3.jpeg)
![Screenshot 4](https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/s4.jpg)


## 📱 Android Local Server Info

To stream videos on Android using GWeb:

1. The HTTP server must start on:  
   **http://127.0.0.1:8080/**

2. Ensure the following files are present in the **root directory**:
   - `enc.key`  http://127.0.0.1:8080/enc.key

3. To play videos, it is required to install:  
   🎬 **[MX Player Pro](https://play.google.com/store/apps/details?id=com.mxtech.videoplayer.pro)**


![Screenshot 5](https://raw.githubusercontent.com/AntorPi314/GWeb/main/Screenshot/s5.png)



## ⚠️ Windows Security Notice

> ⚠️ **Important:**  
> When running the downloaded `.exe` file or starting the local server, **Windows Security** (Defender or SmartScreen) might show a warning.  
> This is a common behavior for `.exe` files from unknown publishers.  
>
> ✅ To continue using GWeb without issues:
> - Click **“More info”** → **“Run anyway”** (for SmartScreen).
> - Or **temporarily disable Windows Defender**.
> - You may also **allow the app through your firewall** if prompted.


## ⚠️ **Warning**  
> Host files on your own server. Do not abuse GitHub. I’m using it strictly for educational purposes.


