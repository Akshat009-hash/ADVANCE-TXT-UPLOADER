import re
import subprocess
import os
from pyrogram import Client, filters

# ====== CONFIG ======
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Regex to detect m3u8 + HLS_KEY
HLS_REGEX = re.compile(r"(.+index\.m3u8)HLS_KEY=([a-zA-Z0-9]+)")

@Client.on_message(filters.text & filters.private)
async def hls_handler(client, message):
    text = message.text.strip()
    match = HLS_REGEX.match(text)
    
    if not match:
        return
    
    m3u8_url = match.group(1)
    hls_key = match.group(2)
    
    video_path = os.path.join(DOWNLOAD_DIR, "video.mp4")

    await message.reply_text("🚀 Downloading started...")

    try:
        cmd = [
            "yt-dlp",
            "--allow-unplayable-formats",
            "--decryption-key", hls_key,
            "-o", video_path,
            m3u8_url
        ]
        subprocess.run(cmd, check=True)

        await message.reply_text("✅ Download complete! Uploading...")

        await client.send_video(
            chat_id=message.chat.id,
            video=video_path,
            caption="🎬 Uploaded via Advance Uploader"
        )

        os.remove(video_path)

    except Exception as e:
        await message.reply_text(f"❌ Download failed: {str(e)}")
