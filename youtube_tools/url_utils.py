import re
from urllib.parse import urlparse, parse_qs

def is_youtube_url(url: str) -> bool:
    """
    Check if the URL is a valid YouTube video URL.
    Supports both long and short formats.
    """
    patterns = [
        r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
    ]
    return any(re.match(pattern, url) for pattern in patterns)

def shorten_youtube_url(url: str) -> str:
    """
    Convert a long YouTube video URL to its short youtu.be version.
    If already short or invalid, return as is.
    """
    if not is_youtube_url(url):
        return url

    parsed = urlparse(url)

    # Long format: extract video ID from the 'v' query parameter
    if 'youtube.com' in parsed.netloc and '/watch' in parsed.path:
        query = parse_qs(parsed.query)
        video_id = query.get('v', [None])[0]
        if video_id:
            return f"https://youtu.be/{video_id}"
    
    return url  # Already short or unrecognized format

def get_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL (long or short form).
    """
    parsed = urlparse(url)
    if 'youtube.com' in parsed.netloc:
        return parse_qs(parsed.query).get('v', [None])[0]
    elif 'youtu.be' in parsed.netloc:
        return parsed.path.lstrip('/')
    return None

