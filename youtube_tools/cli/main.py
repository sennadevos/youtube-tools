#!/usr/bin/env python3
"""
YouTube Tools CLI Main Entry Point
Handles argument parsing and command routing.
"""

import argparse
import sys
from typing import List, Optional

from .commands import cmd_shorten, cmd_download, cmd_transcript, cmd_summarize, cmd_chat, cmd_qualities


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="youtube-tools",
        description="YouTube Tools - CLI for YouTube video processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  youtube-tools shorten "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  youtube-tools qualities "https://youtu.be/dQw4w9WgXcQ"
  youtube-tools download "https://youtu.be/dQw4w9WgXcQ" --quality 720p
  youtube-tools download "https://youtu.be/dQw4w9WgXcQ" --output-path ./downloads
  youtube-tools transcript "https://youtu.be/dQw4w9WgXcQ" --json
  youtube-tools summarize "https://youtu.be/dQw4w9WgXcQ"
  youtube-tools chat "https://youtu.be/dQw4w9WgXcQ" "What is this video about?"
        """
    )
    
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shorten URL command
    shorten_parser = subparsers.add_parser(
        "shorten", 
        help="Shorten YouTube URL",
        description="Convert a long YouTube URL to its short youtu.be equivalent"
    )
    shorten_parser.add_argument("url", help="YouTube URL to shorten")
    
    # List qualities command
    qualities_parser = subparsers.add_parser(
        "qualities", 
        help="List available video qualities",
        description="Show available video qualities for a YouTube video"
    )
    qualities_parser.add_argument("url", help="YouTube URL")
    
    # Download video command
    download_parser = subparsers.add_parser(
        "download", 
        help="Download YouTube video",
        description="Download a YouTube video in the specified quality"
    )
    download_parser.add_argument("url", help="YouTube URL to download")
    download_parser.add_argument(
        "--output-path", 
        help="Output directory (default: XDG Downloads folder)"
    )
    download_parser.add_argument(
        "--quality", 
        default="best",
        help="Video quality (default: best). Use 'qualities' command to see available options."
    )
    
    # Show transcript command
    transcript_parser = subparsers.add_parser(
        "transcript", 
        help="Get video transcript",
        description="Extract and display the transcript of a YouTube video"
    )
    transcript_parser.add_argument("url", help="YouTube URL")
    
    # Summarize video command
    summarize_parser = subparsers.add_parser(
        "summarize", 
        help="Summarize video content",
        description="Generate an AI-powered summary of a YouTube video"
    )
    summarize_parser.add_argument("url", help="YouTube URL")
    
    # Chat about video command
    chat_parser = subparsers.add_parser(
        "chat", 
        help="Chat with LLM about video",
        description="Ask questions about a YouTube video using AI"
    )
    chat_parser.add_argument("url", help="YouTube URL")
    chat_parser.add_argument("question", help="Question to ask about the video")
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        args: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    output_format = "json" if parsed_args.json else "text"
    
    try:
        if parsed_args.command == "shorten":
            cmd_shorten(parsed_args.url, output_format)
        elif parsed_args.command == "qualities":
            cmd_qualities(parsed_args.url, output_format)
        elif parsed_args.command == "download":
            cmd_download(parsed_args.url, parsed_args.output_path, parsed_args.quality, output_format)
        elif parsed_args.command == "transcript":
            cmd_transcript(parsed_args.url, output_format)
        elif parsed_args.command == "summarize":
            cmd_summarize(parsed_args.url, output_format)
        elif parsed_args.command == "chat":
            cmd_chat(parsed_args.url, parsed_args.question, output_format)
        
        return 0
        
    except KeyboardInterrupt:
        if output_format == "json":
            print('{"error": "Operation cancelled by user"}')
        else:
            print("Operation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        if output_format == "json":
            print(f'{{"error": "Unexpected error: {str(e)}"}}')
        else:
            print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())