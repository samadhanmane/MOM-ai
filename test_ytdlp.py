import yt_dlp

url = "https://youtu.be/rZIREuBgl5g?si=ilTFkNP4iueN7lGA"

options = {
    "format": "bestaudio/best",
    "outtmpl": "downloades/%(title)s.%(ext)s",
    "noplaylist": True,

    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    },

    "quiet": False,
    "no_warnings": False,
}

with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([url])