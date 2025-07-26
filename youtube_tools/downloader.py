from pytube import YouTube

def download_youtube_video(url: str, output_path: str = "."):
    """
    Download the YouTube video at the highest available resolution.
    Downloads to the specified output path (default is current directory).
    """
    try:
        yt = YouTube(url)  # Create YouTube object
        stream = yt.streams.get_highest_resolution()  # Select best quality
        print(f"Downloading: {yt.title}")
        stream.download(output_path=output_path)  # Start download
        print("Download complete.")
    except Exception as e:
        print(f"Error: {e}")  # Print error message if something goes wrong

