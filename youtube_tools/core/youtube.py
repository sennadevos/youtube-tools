"""
YouTube-related utilities and core functionality.
Handles URL validation, video ID extraction, and basic YouTube operations.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional


def is_youtube_url(url: str) -> bool:
    """
    Check if the URL is a valid YouTube video URL.
    Supports both long and short formats.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if the URL is a valid YouTube video URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
        
    patterns = [
        r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def get_video_id(url: str) -> Optional[str]:
    """
    Extract the video ID from a YouTube URL (long or short form).
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID string if found, None otherwise
    """
    if not is_youtube_url(url):
        return None
        
    parsed = urlparse(url)
    
    if 'youtube.com' in parsed.netloc:
        query_params = parse_qs(parsed.query)
        return query_params.get('v', [None])[0]
    elif 'youtu.be' in parsed.netloc:
        return parsed.path.lstrip('/')
    
    return None


def shorten_youtube_url(url: str) -> str:
    """
    Convert a long YouTube video URL to its short youtu.be version.
    If already short or invalid, return as is.
    
    Args:
        url: YouTube video URL to shorten
        
    Returns:
        Shortened URL or original URL if already short/invalid
    """
    if not is_youtube_url(url):
        return url

    video_id = get_video_id(url)
    if video_id:
        return f"https://youtu.be/{video_id}"
    
    return url