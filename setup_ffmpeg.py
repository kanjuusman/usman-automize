"""ffmpeg (video engine) download karke bin/ folder mein rakhta hai. INSTALL.bat isay khud chalata hai."""
import os
import shutil
import sys
import zipfile

import requests

APP_DIR = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(APP_DIR, "bin")
URLS = [
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    "https://github.com/GyanD/codexffmpeg/releases/download/7.1.1/ffmpeg-7.1.1-essentials_build.zip",
]


def _have_both():
    for name in ("ffmpeg",):  # ffprobe zaroori nahi
        exe = name + (".exe" if sys.platform == "win32" else "")
        if not (os.path.isfile(os.path.join(BIN, exe)) or shutil.which(name)):
            return False
    return True


def main(print=print):
    try:  # zip mein ffmpeg.exe.xz (chhota) - pehle use kholo
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from core.util import _unpack_xz
        _unpack_xz(os.path.join(BIN, "ffmpeg.exe"))
    except Exception:
        pass
    if _have_both():
        print("ffmpeg pehle se mojood hai. ✔")
        return True
    if sys.platform != "win32":
        if shutil.which("ffmpeg"):
            print("ffmpeg system par mojood hai. ✔")
        else:
            print("Apne system par ffmpeg install karein (jaise: sudo apt install ffmpeg).")
        return _have_both()
    os.makedirs(BIN, exist_ok=True)
    zpath = os.path.join(BIN, "ffmpeg.zip")
    for url in URLS:
        try:
            print(f"ffmpeg download ho raha hai (~100 MB, thora waqt lagega)...\n{url}")
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                got = 0
                with open(zpath, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
                        got += len(chunk)
                        if total and got % (10 << 20) < (1 << 20):
                            print(f"  download: {got * 100 // total}%")
            with zipfile.ZipFile(zpath) as z:
                for name in z.namelist():
                    base = os.path.basename(name)
                    if base in ("ffmpeg.exe", "ffprobe.exe"):
                        with z.open(name) as src, open(os.path.join(BIN, base), "wb") as dst:
                            shutil.copyfileobj(src, dst)
            os.remove(zpath)
            if os.path.isfile(os.path.join(BIN, "ffmpeg.exe")):
                print("ffmpeg install ho gaya. ✔")
                return True
        except Exception as e:
            print(f"\n  Yeh link nahi chala: {e}")
    print("\n❌ ffmpeg download nahi hua. Doosra tareeqa: CMD mein likhein:\n   winget install Gyan.FFmpeg\n"
          "phir computer restart karein.")
    return False


if __name__ == "__main__":
    main()
