"""
YouTube transcript extraction functionality.
Handles transcript fetching with language preferences and formatting.
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from typing import List, Optional

from .youtube import get_video_id, is_youtube_url


class TranscriptError(Exception):
    """Raised when transcript extraction fails"""
    pass


def get_transcript(
    url: str,
    languages: List[str] = None,
    prefer_generated: bool = True,
    format_text: bool = True
) -> str:
    """
    Retrieve the transcript of a YouTube video.

    Args:
        url: YouTube video URL
        languages: Preferred language codes in priority order (default: ['en'])
        prefer_generated: If True, prefer auto-generated subtitles
        format_text: If True, format as plain text; otherwise return raw data

    Returns:
        Transcript text or formatted transcript data

    Raises:
        ValueError: If URL is invalid
        TranscriptError: If transcript extraction fails
    """
    if not is_youtube_url(url):
        raise ValueError("Invalid YouTube URL")

    if languages is None:
        languages = ['en']

    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Could not extract video ID from URL")

    try:
        # Use the new API structure
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Try to find transcript based on preference
        transcript = None
        
        if prefer_generated:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except:
                pass
        
        if not transcript:
            try:
                transcript = transcript_list.find_manually_created_transcript(languages)
            except:
                pass
        
        # Fallback to any available transcript
        if not transcript:
            try:
                transcript = transcript_list.find_transcript(languages)
            except:
                pass
        
        if not transcript:
            raise TranscriptError("No transcript available in the requested languages")

        # Fetch the transcript data
        transcript_data = transcript.fetch()
        
        if format_text:
            # Format as plain text
            formatter = TextFormatter()
            return formatter.format_transcript(transcript_data)
        else:
            return transcript_data

    except TranscriptError:
        raise
    except Exception as e:
        raise TranscriptError(f"Failed to retrieve transcript: {str(e)}")


def get_available_transcripts(url: str) -> List[dict]:
    """
    Get information about available transcripts for a video.
    
    Args:
        url: YouTube video URL
        
    Returns:
        List of dictionaries with transcript information
        
    Raises:
        ValueError: If URL is invalid
        TranscriptError: If unable to fetch transcript list
    """
    if not is_youtube_url(url):
        raise ValueError("Invalid YouTube URL")

    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Could not extract video ID from URL")

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        transcripts = []
        for transcript in transcript_list:
            transcripts.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable,
            })
        
        return transcripts
        
    except Exception as e:
        raise TranscriptError(f"Failed to get transcript list: {str(e)}")