"""
CLI command implementations.
Each command handles its specific functionality with proper error handling.
"""

import json
import sys
from typing import Any, Dict

from ..core.youtube import shorten_youtube_url, is_youtube_url
from ..core.downloader import download_video, get_available_qualities, VideoDownloadError
from ..core.transcript import get_transcript, TranscriptError
from ..core.ai import VideoSummarizer, VideoChatBot, AIError


class CommandError(Exception):
    """Raised when command execution fails"""
    pass


def output_result(data: Any, format_type: str = "text") -> None:
    """
    Output command result in the specified format.
    
    Args:
        data: Data to output
        format_type: "text" or "json"
    """
    if format_type == "json":
        if isinstance(data, dict):
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps({"result": data}, indent=2))
    else:
        if isinstance(data, dict) and "error" in data:
            print(f"Error: {data['error']}", file=sys.stderr)
        elif isinstance(data, dict):
            # For structured data, print key information
            if "summary" in data:
                print(data["summary"])
            elif "result" in data:
                print(data["result"])
            else:
                print(str(data))
        else:
            print(str(data))


def handle_error(error: Exception, format_type: str = "text") -> None:
    """
    Handle and output errors consistently.
    
    Args:
        error: Exception that occurred
        format_type: Output format
    """
    error_data = {"error": str(error)}
    output_result(error_data, format_type)
    sys.exit(1)


def cmd_shorten(url: str, format_type: str = "text") -> None:
    """
    Shorten a YouTube URL.
    
    Args:
        url: YouTube URL to shorten
        format_type: Output format
    """
    try:
        if not is_youtube_url(url):
            raise CommandError("Invalid YouTube URL")
        
        result = shorten_youtube_url(url)
        if format_type == "json":
            output_result({"shortened_url": result}, format_type)
        else:
            output_result(result, format_type)
        
    except Exception as e:
        handle_error(e, format_type)


def cmd_download(url: str, output_path: str = None, quality: str = "best", format_type: str = "text") -> None:
    """
    Download a YouTube video.
    
    Args:
        url: YouTube URL to download
        output_path: Directory to save the video (default: XDG Downloads folder)
        quality: Video quality preference
        format_type: Output format
    """
    try:
        if not is_youtube_url(url):
            raise CommandError("Invalid YouTube URL")
        
        filename = download_video(url, output_path, quality)
        result = {
            "status": "success",
            "message": "Download completed",
            "filename": filename
        }
        if format_type == "json":
            output_result(result, format_type)
        else:
            output_result(f"Download completed!\nSaved to: {filename}", format_type)
        
    except (VideoDownloadError, CommandError) as e:
        handle_error(e, format_type)
    except Exception as e:
        handle_error(CommandError(f"Unexpected error: {str(e)}"), format_type)


def cmd_qualities(url: str, format_type: str = "text") -> None:
    """
    List available video qualities.
    
    Args:
        url: YouTube URL
        format_type: Output format
    """
    try:
        if not is_youtube_url(url):
            raise CommandError("Invalid YouTube URL")
        
        qualities = get_available_qualities(url)
        
        if format_type == "json":
            output_result({"qualities": qualities}, format_type)
        else:
            print("Available qualities:")
            for quality in qualities:
                desc = quality.get('description', quality['quality'])
                print(f"  {quality['quality']}: {desc}")
        
    except (VideoDownloadError, CommandError) as e:
        handle_error(e, format_type)
    except Exception as e:
        handle_error(CommandError(f"Unexpected error: {str(e)}"), format_type)


def cmd_transcript(url: str, format_type: str = "text") -> None:
    """
    Get transcript of a YouTube video.
    
    Args:
        url: YouTube URL
        format_type: Output format
    """
    try:
        if not is_youtube_url(url):
            raise CommandError("Invalid YouTube URL")
        
        transcript = get_transcript(url)
        if format_type == "json":
            output_result({"transcript": transcript}, format_type)
        else:
            output_result(transcript, format_type)
        
    except (TranscriptError, CommandError) as e:
        handle_error(e, format_type)
    except Exception as e:
        handle_error(CommandError(f"Unexpected error: {str(e)}"), format_type)


def cmd_summarize(url: str, format_type: str = "text") -> None:
    """
    Summarize a YouTube video.
    
    Args:
        url: YouTube URL
        format_type: Output format
    """
    try:
        if not is_youtube_url(url):
            raise CommandError("Invalid YouTube URL")
        
        summarizer = VideoSummarizer()
        result = summarizer.summarize(url)
        output_result(result, format_type)
        
    except (AIError, CommandError) as e:
        handle_error(e, format_type)
    except Exception as e:
        handle_error(CommandError(f"Unexpected error: {str(e)}"), format_type)


def cmd_chat(url: str, question: str, format_type: str = "text") -> None:
    """
    Chat with an LLM about a YouTube video.
    
    Args:
        url: YouTube URL
        question: Question to ask
        format_type: Output format
    """
    try:
        if not is_youtube_url(url):
            raise CommandError("Invalid YouTube URL")
        
        chatbot = VideoChatBot(url)
        answer = chatbot.ask(question)
        if format_type == "json":
            output_result({"answer": answer}, format_type)
        else:
            output_result(answer, format_type)
        
    except (AIError, CommandError) as e:
        handle_error(e, format_type)
    except Exception as e:
        handle_error(CommandError(f"Unexpected error: {str(e)}"), format_type)