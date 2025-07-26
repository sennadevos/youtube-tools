#!/usr/bin/env python3
"""
YouTube Tools CLI Backend
Provides command-line interface for YouTube video processing tools.
"""

import argparse
import json
import sys
from typing import Optional

from .url_utils import shorten_youtube_url, is_youtube_url
from .downloader import download_youtube_video
from .transcript import fetch_youtube_transcript
from .video_chat_backend_json import VideoChatBackendJSON


def cmd_shorten(url: str, output_format: str = "text") -> None:
    """Shorten a YouTube URL"""
    if not is_youtube_url(url):
        result = {"error": "Invalid YouTube URL"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)
    
    shortened = shorten_youtube_url(url)
    
    if output_format == "json":
        print(json.dumps({"shortened_url": shortened}))
    else:
        print(shortened)


def cmd_download(url: str, output_path: str = ".", output_format: str = "text") -> None:
    """Download a YouTube video"""
    if not is_youtube_url(url):
        result = {"error": "Invalid YouTube URL"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)
    
    try:
        download_youtube_video(url, output_path)
        result = {"status": "success", "message": "Download completed"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print("Download completed")
    except Exception as e:
        result = {"error": str(e)}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


def cmd_transcript(url: str, output_format: str = "text") -> None:
    """Get transcript of a YouTube video"""
    if not is_youtube_url(url):
        result = {"error": "Invalid YouTube URL"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)
    
    try:
        transcript = fetch_youtube_transcript(url)
        if transcript is None:
            result = {"error": "No transcript available for this video"}
            if output_format == "json":
                print(json.dumps(result))
            else:
                print(f"Error: {result['error']}")
            sys.exit(1)
        
        if output_format == "json":
            print(json.dumps({"transcript": transcript}))
        else:
            print(transcript)
    except Exception as e:
        result = {"error": str(e)}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


def cmd_summarize(url: str, output_format: str = "text") -> None:
    """Summarize a YouTube video"""
    if not is_youtube_url(url):
        result = {"error": "Invalid YouTube URL"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)
    
    try:
        backend = VideoChatBackendJSON(url)
        if output_format == "json":
            print(backend.get_summary_json())
        else:
            print(backend.get_summary())
    except Exception as e:
        result = {"error": str(e)}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


def cmd_chat(url: str, question: str, output_format: str = "text") -> None:
    """Chat with an LLM about a YouTube video"""
    if not is_youtube_url(url):
        result = {"error": "Invalid YouTube URL"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)
    
    try:
        backend = VideoChatBackendJSON(url)
        if output_format == "json":
            print(backend.ask_json(question))
        else:
            print(backend.ask(question))
    except Exception as e:
        result = {"error": str(e)}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="YouTube Tools - CLI for YouTube video processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  youtube-tools shorten "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  youtube-tools download "https://youtu.be/dQw4w9WgXcQ" --output-path ./downloads
  youtube-tools transcript "https://youtu.be/dQw4w9WgXcQ" --json
  youtube-tools summarize "https://youtu.be/dQw4w9WgXcQ"
  youtube-tools chat "https://youtu.be/dQw4w9WgXcQ" "What is this video about?"
        """
    )
    
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shorten URL command
    shorten_parser = subparsers.add_parser("shorten", help="Shorten YouTube URL")
    shorten_parser.add_argument("url", help="YouTube URL to shorten")
    
    # Download video command
    download_parser = subparsers.add_parser("download", help="Download YouTube video")
    download_parser.add_argument("url", help="YouTube URL to download")
    download_parser.add_argument("--output-path", default=".", help="Output directory (default: current directory)")
    
    # Show transcript command
    transcript_parser = subparsers.add_parser("transcript", help="Get video transcript")
    transcript_parser.add_argument("url", help="YouTube URL")
    
    # Summarize video command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize video content")
    summarize_parser.add_argument("url", help="YouTube URL")
    
    # Chat about video command
    chat_parser = subparsers.add_parser("chat", help="Chat with LLM about video")
    chat_parser.add_argument("url", help="YouTube URL")
    chat_parser.add_argument("question", help="Question to ask about the video")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    output_format = "json" if args.json else "text"
    
    try:
        if args.command == "shorten":
            cmd_shorten(args.url, output_format)
        elif args.command == "download":
            cmd_download(args.url, args.output_path, output_format)
        elif args.command == "transcript":
            cmd_transcript(args.url, output_format)
        elif args.command == "summarize":
            cmd_summarize(args.url, output_format)
        elif args.command == "chat":
            cmd_chat(args.url, args.question, output_format)
    except KeyboardInterrupt:
        result = {"error": "Operation cancelled by user"}
        if output_format == "json":
            print(json.dumps(result))
        else:
            print("Operation cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()