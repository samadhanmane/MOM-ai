import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)

#downloading yt video in .wav format
def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        # Android client currently works with format 18
        "format": "18",

        "outtmpl": output_path,

        "noplaylist": True,

        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        "quiet": False,
        "no_warnings": False,

        "retries": 10,
        "fragment_retries": 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        # This is the ACTUAL downloaded MP4 path
        downloaded_path = ydl.prepare_filename(info)

    print(f"Downloaded: {downloaded_path}")

    # MP4 → 16kHz mono WAV
    wav_path = convert_to_wav(downloaded_path)

    # Delete MP4 after extracting audio
    os.remove(downloaded_path)

    return wav_path

#converting files audio settings to 16khz and monoaudio so both side gives same audio (best setting for whisper ai)
def convert_to_wav(input_path : str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz and monoaudio
    audio.export(output_path, format="wav")
    return output_path




#chunking the audio files
def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list :
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 # total number of miliseconds of a file

    chunks = []
    #chunking loop starts
    for i,start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format = "wav")

        chunks.append(chunk_path)

    return chunks

#input taking and combining all functions together 
def process_input(source : str)-> str:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL, Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected Local File. Converting to WAV..")
        wav_path = convert_to_wav(source)

    print("Chunking Audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready - {len(chunks)} chunk(s) created. ")
    return chunks



    