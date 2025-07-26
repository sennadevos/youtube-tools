from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from .url_utils import get_video_id

def fetch_youtube_transcript(
    url: str,
    languages: list[str] = ['en'],
    prefer_generated: bool = True
) -> str:
    """
    Retrieve the transcript (subtitles) of a YouTube video in text form.

    Args:
        url: YouTube video URL (long or short).
        languages: Preferred language codes in priority order (default: ['en']).
        prefer_generated: If True, prefer auto-generated subtitles; otherwise prefer manual ones.

    Returns:
        A plain-text transcript string, or None if no transcript is available for the given video.
    """
    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    try:
        api = YouTubeTranscriptApi()
        # List all available transcripts
        transcript_list = api.list(video_id)

        # Choose transcript type based on preference
        if prefer_generated:
            transcript = transcript_list.find_generated_transcript(languages)
        else:
            transcript = transcript_list.find_manually_created_transcript(languages)
        # Fallback to any available transcript
        if not transcript:
            transcript = transcript_list.find_transcript(languages)

        fetched = transcript.fetch()
        # Use formatter to remove timestamps and join text
        formatter = TextFormatter()
        return formatter.format_transcript(fetched)

    except Exception as e:
        # TODO - Come up with a more robust way of doing this...
        print(f"Failed to retrieve transcript due to: {e}")
        return None

