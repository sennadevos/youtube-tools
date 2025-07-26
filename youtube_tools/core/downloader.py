"""
YouTube video downloader functionality.
Handles video downloading with error handling and quality selection.
Uses pytube as primary method with yt-dlp as fallback.
"""

from pytube import YouTube
from typing import Optional, List, Dict
import os
import subprocess
import tempfile
import yt_dlp

from .youtube import is_youtube_url


class VideoDownloadError(Exception):
    """Raised when video download fails"""
    pass


def get_default_download_path() -> str:
    """
    Get the default download path using XDG directories.
    Falls back to user's home directory if XDG is not available.
    
    Returns:
        Path to the default download directory
    """
    # Try XDG_DOWNLOAD_DIR first
    xdg_download = os.environ.get('XDG_DOWNLOAD_DIR')
    if xdg_download and os.path.isdir(xdg_download):
        return xdg_download
    
    # Try standard Downloads folder in home directory
    home = os.path.expanduser('~')
    downloads_dir = os.path.join(home, 'Downloads')
    if os.path.isdir(downloads_dir):
        return downloads_dir
    
    # Try localized Downloads folder names
    for downloads_name in ['Downloads', 'downloads', 'Descargas', 'Téléchargements', 'Download']:
        downloads_path = os.path.join(home, downloads_name)
        if os.path.isdir(downloads_path):
            return downloads_path
    
    # Fall back to home directory
    return home


def get_available_qualities(url: str) -> List[Dict[str, str]]:
    """
    Get available video qualities for a YouTube video.
    
    Args:
        url: YouTube video URL
        
    Returns:
        List of dictionaries with quality information
        
    Raises:
        ValueError: If URL is invalid
        VideoDownloadError: If unable to fetch quality info
    """
    if not is_youtube_url(url):
        raise ValueError("Invalid YouTube URL")
    
    try:
        # Use yt-dlp to get available formats
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'listformats': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            qualities = []
            seen_qualities = set()
            
            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':  # Has both video and audio
                    height = fmt.get('height')
                    if height and height not in seen_qualities:
                        qualities.append({
                            'quality': f"{height}p",
                            'format_id': fmt.get('format_id', ''),
                            'filesize': fmt.get('filesize'),
                            'ext': fmt.get('ext', 'mp4'),
                            'description': f"{height}p - {fmt.get('ext', 'mp4')}"
                        })
                        seen_qualities.add(height)
            
            # Sort by quality (highest first)
            qualities.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
            
            # Add special options
            qualities.insert(0, {'quality': 'best', 'description': 'Best available quality'})
            qualities.append({'quality': 'worst', 'description': 'Lowest available quality'})
            
            return qualities
            
    except Exception as e:
        raise VideoDownloadError(f"Failed to get available qualities: {str(e)}")


def _download_with_ytdlp(url: str, output_path: str = ".", quality: str = "best") -> str:
    """
    Download video using yt-dlp as fallback method.
    
    Args:
        url: YouTube video URL
        output_path: Directory to save the video
        quality: Video quality preference
        
    Returns:
        Path to the downloaded file
        
    Raises:
        VideoDownloadError: If download fails
    """
    try:
        # Configure format selector based on quality
        if quality == "best":
            format_selector = 'best'
        elif quality == "worst":
            format_selector = 'worst'
        elif quality.endswith('p'):
            # Specific resolution (e.g., "720p")
            height = quality.replace('p', '')
            format_selector = f'best[height<={height}]/best'
        else:
            # Default to best
            format_selector = 'best'
        
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': format_selector,
            'noplaylist': True,
            'no_warnings': True,
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            print(f"Found video (yt-dlp): {title}")
            
            # Download the video
            ydl.download([url])
            
            # Find the downloaded file
            expected_filename = ydl.prepare_filename(info)
            if os.path.exists(expected_filename):
                return expected_filename
            
            # If exact filename doesn't exist, try to find a similar one
            base_name = os.path.splitext(os.path.basename(expected_filename))[0]
            for file in os.listdir(output_path):
                if base_name in file and file.endswith(('.mp4', '.mkv', '.webm')):
                    return os.path.join(output_path, file)
            
            raise VideoDownloadError("Downloaded file not found")
            
    except Exception as e:
        if "Private video" in str(e):
            raise VideoDownloadError("Video is private")
        elif "Video unavailable" in str(e):
            raise VideoDownloadError("Video is unavailable")
        else:
            raise VideoDownloadError(f"yt-dlp download failed: {str(e)}")


def download_video(url: str, output_path: str = None, quality: str = "best") -> str:
    """
    Download a YouTube video.
    
    Args:
        url: YouTube video URL
        output_path: Directory to save the video (default: XDG Downloads folder)
        quality: Quality preference - "best", "worst", or specific resolution like "720p"
        
    Returns:
        Path to the downloaded file
        
    Raises:
        VideoDownloadError: If download fails
        ValueError: If URL is invalid
    """
    if not is_youtube_url(url):
        raise ValueError("Invalid YouTube URL")
    
    # Use XDG Downloads folder as default
    if output_path is None:
        output_path = get_default_download_path()
    
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    
    # First, try yt-dlp (more reliable)
    try:
        print("Attempting download with yt-dlp...")
        print(f"Output path: {output_path}")
        print(f"Quality: {quality}")
        return _download_with_ytdlp(url, output_path, quality)
    except VideoDownloadError as e:
        print(f"yt-dlp failed: {e}")
        print("Falling back to pytube...")
    
    # Fallback to pytube
    try:
        # Initialize YouTube object with better error handling
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=False
        )
        
        # Try to access video info first to check if video is accessible
        try:
            title = yt.title
            print(f"Found video (pytube): {title}")
        except Exception as e:
            raise VideoDownloadError(f"Cannot access video information: {str(e)}")
        
        # Get available streams
        streams = yt.streams
        if not streams:
            raise VideoDownloadError("No streams available for this video")
        
        # Select stream based on quality preference with fallbacks
        stream = None
        
        if quality == "highest":
            # Try progressive streams first (video + audio combined)
            stream = streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            # If no progressive streams, try adaptive video streams
            if not stream:
                stream = streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
                
            # Last resort: any available stream
            if not stream:
                stream = streams.first()
                
        elif quality == "lowest":
            # Try progressive streams first
            stream = streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
            
            # Fallback to any stream
            if not stream:
                stream = streams.filter(file_extension='mp4').first()
                
            # Last resort
            if not stream:
                stream = streams.first()
        else:
            # Try to get specific itag
            stream = streams.get_by_itag(quality)
            if not stream:
                # Fallback to highest quality
                stream = streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if not stream:
                    stream = streams.first()
        
        if not stream:
            raise VideoDownloadError("No suitable stream found")
        
        print(f"Selected stream: {stream.resolution or 'unknown'} - {stream.mime_type}")
        
        # Download the video
        filename = stream.download(output_path=output_path)
        return filename
        
    except VideoDownloadError:
        raise
    except Exception as e:
        # More specific error handling for common issues
        error_msg = str(e).lower()
        if "400" in error_msg or "bad request" in error_msg:
            raise VideoDownloadError("Video may be private, age-restricted, or unavailable. Both pytube and yt-dlp failed.")
        elif "403" in error_msg or "forbidden" in error_msg:
            raise VideoDownloadError("Access denied - video may be private or region-locked")
        elif "404" in error_msg or "not found" in error_msg:
            raise VideoDownloadError("Video not found - it may have been deleted or the URL is incorrect")
        elif "regex" in error_msg or "extract" in error_msg:
            raise VideoDownloadError("Unable to extract video information - YouTube may have changed their format")
        else:
            raise VideoDownloadError(f"Download failed with both methods: {str(e)}")


def get_video_info(url: str) -> dict:
    """
    Get basic information about a YouTube video.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary with video information
        
    Raises:
        ValueError: If URL is invalid
        VideoDownloadError: If unable to fetch video info
    """
    if not is_youtube_url(url):
        raise ValueError("Invalid YouTube URL")
    
    try:
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=False
        )
        
        # Safely get video information with fallbacks
        info = {}
        
        try:
            info["title"] = yt.title or "Unknown"
        except:
            info["title"] = "Unknown"
            
        try:
            info["author"] = yt.author or "Unknown"
        except:
            info["author"] = "Unknown"
            
        try:
            info["description"] = (yt.description or "")[:500]
        except:
            info["description"] = ""
            
        try:
            info["length"] = yt.length or 0
        except:
            info["length"] = 0
            
        try:
            info["views"] = yt.views or 0
        except:
            info["views"] = 0
            
        try:
            info["publish_date"] = yt.publish_date.isoformat() if yt.publish_date else None
        except:
            info["publish_date"] = None
            
        return info
        
    except Exception as e:
        error_msg = str(e).lower()
        if "400" in error_msg or "bad request" in error_msg:
            raise VideoDownloadError("Video may be private, age-restricted, or unavailable")
        elif "403" in error_msg or "forbidden" in error_msg:
            raise VideoDownloadError("Access denied - video may be private or region-locked")
        elif "404" in error_msg or "not found" in error_msg:
            raise VideoDownloadError("Video not found - it may have been deleted or the URL is incorrect")
        else:
            raise VideoDownloadError(f"Failed to get video info: {str(e)}")