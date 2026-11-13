# Usman Automize — One-Click Video Tool v0 (PC)

Topic in, captioned MP4 video out. Free tools only.

## What it does

1. Take a topic, style (documentary / cartoon / news) and a target length.
2. Write a script and check the word count.
3. Make a voiceover with free Edge TTS (British male) or use a bundled MP3.
4. Build scene-matched visuals with burned-in captions, sound effects and
   background music under the voice.
5. Render a real 1080p MP4 with FFmpeg and write an upload package
   (description, keywords, thumbnail text).

## Run it (Windows)

1. Install Python 3.12 (tick **Add python.exe to PATH**).
2. Double-click `INSTALL.bat` (first time only — installs packages + FFmpeg).
3. Double-click `START.bat` — the tool opens in your browser at
   `http://localhost:4100`.
4. Enter a topic, pick a style and length, press **Run All Agents**.
5. The finished video is in `output/`.

## Files

- `server.py` — local web server (Python standard library only)
- `usman_automize.py` — the 20-agent pipeline + FFmpeg render
- `web/` — the tool's interface (same design as the web version)
- `script.txt` / `title.txt` — the included test topic (Kansas, 500 words)
- `sfx/` — free sound effects (not included in this upload: binary files)
- `voiceover-kansas.mp3` — bundled Kansas voiceover (not included here)

## Manual gates in v0 (not automated)

- **AI images / video:** the tool writes per-scene image and video prompts.
  Generate the media with a free tool (e.g. FLUX) and drop the files into
  `images/`. Unlimited AI video is not free and is not automated.
- **YouTube upload:** the tool prepares the full upload package, but you
  upload the MP4 yourself in YouTube Studio. Auto-upload needs your Google
  login and is not part of v0.
- **Voice:** Edge TTS is free and needs internet the first time a new
  voiceover is made. The bundled voiceover works offline.

## Sound rule

The first 3 seconds play real ambient sound only (no voiceover). After that,
ambient sound stays low under the voice for the whole video.
