"""
YouTube Tools - A versatile application for YouTube video processing.
Provides both CLI and GUI interfaces.
"""

__version__ = "1.0.0"
__author__ = "YouTube Tools Contributors"

from .core.youtube import is_youtube_url, shorten_youtube_url
from .core.downloader import download_video
from .core.transcript import get_transcript
from .core.ai import VideoSummarizer, VideoChatBot
