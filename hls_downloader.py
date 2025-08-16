import requests
import yt_dlp
import tempfile
import os

HLS_URL = input("Enter HLS .m3u8 URL: ").strip()
HLS_KEY_HEX = input("Enter HLS HEX Key: ").strip()

KEY_FILE = "hls.key"
with open(KEY_FILE, "wb") as f:
    f.write(bytes.fromhex(HLS_KEY_HEX))

def patch_m3u8_recursively(url, visited=None):
    if visited is None:
        visited = set()
    if url in visited:
        return None
    visited.add(url)

    print(f"[+] Fetching: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    lines = resp.text.splitlines()
    base = url.rsplit("/", 1)[0] + "/"
    patched = []

    for line in lines:
        if line.startswith("#EXT-X-KEY"):
            patched.append(f'#EXT-X-KEY:METHOD=AES-128,URI="{os.path.abspath(KEY_FILE)}"')
        elif not line.startswith("#") and line.strip().endswith(".m3u8"):
            sub_url = line if line.startswith("http") else base + line
            sub_file = patch_m3u8_recursively(sub_url, visited)
            if sub_file:
                patched.append(sub_file)
            else:
                patched.append(line)
        else:
            patched.append(line)

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".m3u8")
    tf.write("\n".join(patched).encode())
    tf.close()
    return tf.name

patched_master = patch_m3u8_recursively(HLS_URL)

ydl_opts = {
    "outtmpl": "downloaded_video.%(ext)s",
    "format": "best",
    "extractor_args": {
        "generic": f"hls_aes_key={HLS_KEY_HEX}"
    }
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([patched_master])

print("✅ Done! Video saved as downloaded_video.mp4")
