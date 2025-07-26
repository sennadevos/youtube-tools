"""
AI-powered functionality for YouTube videos.
Handles summarization and chat features using OpenAI's API.
"""

from openai import OpenAI
from typing import Optional, Dict, List
import os

from .transcript import get_transcript
from .downloader import get_video_info
from .youtube import is_youtube_url


class AIError(Exception):
    """Raised when AI operations fail"""
    pass


class VideoSummarizer:
    """Handles video summarization using AI"""
    
    def __init__(self, model: str = "gpt-4o", max_tokens: Optional[int] = None):
        """
        Initialize the summarizer.
        
        Args:
            model: OpenAI model to use
            max_tokens: Maximum tokens for responses
        """
        self.model = model
        self.max_tokens = max_tokens
        self.client = OpenAI()
    
    def summarize(self, url: str) -> Dict[str, str]:
        """
        Summarize a YouTube video.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with summary and video metadata
            
        Raises:
            ValueError: If URL is invalid
            AIError: If summarization fails
        """
        if not is_youtube_url(url):
            raise ValueError("Invalid YouTube URL")
        
        try:
            # Get transcript and video info
            transcript = get_transcript(url)
            video_info = get_video_info(url)
            
            # Create summary prompt
            prompt = (
                "You are a helpful assistant. Please provide a clear, concise summary "
                "of the following video, focusing on the main points and avoiding unnecessary details. "
                "Base your summary only on the transcript below, but refer to it as the video, not as text.\n\n"
                f"Transcript:\n{transcript}\n\nSummary:"
            )
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful summarization assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
                top_p=1,
                n=1,
                stop=None,
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "title": video_info.get("title", "Unknown"),
                "author": video_info.get("author", "Unknown"),
                "description": video_info.get("description", "")[:500] if video_info.get("description") else ""
            }
            
        except Exception as e:
            raise AIError(f"Summarization failed: {str(e)}")


class VideoChatBot:
    """Handles chat functionality about YouTube videos"""
    
    def __init__(self, url: str, model: str = "gpt-4o", max_tokens: Optional[int] = None):
        """
        Initialize the chat bot for a specific video.
        
        Args:
            url: YouTube video URL
            model: OpenAI model to use
            max_tokens: Maximum tokens for responses
            
        Raises:
            ValueError: If URL is invalid
            AIError: If initialization fails
        """
        if not is_youtube_url(url):
            raise ValueError("Invalid YouTube URL")
        
        self.url = url
        self.model = model
        self.max_tokens = max_tokens
        self.client = OpenAI()
        
        try:
            self.transcript = get_transcript(url)
            self.video_info = get_video_info(url)
            self.chat_history: List[Dict[str, str]] = []
        except Exception as e:
            raise AIError(f"Failed to initialize chat bot: {str(e)}")
    
    def ask(self, question: str) -> str:
        """
        Ask a question about the video.
        
        Args:
            question: Question to ask about the video
            
        Returns:
            AI response to the question
            
        Raises:
            AIError: If chat fails
        """
        try:
            # Build context with video info and chat history
            system_message = (
                f"You are a helpful assistant that answers questions about a YouTube video. "
                f"The video is titled '{self.video_info.get('title', 'Unknown')}' "
                f"by {self.video_info.get('author', 'Unknown')}. "
                f"Base your answers only on the transcript provided below.\n\n"
                f"Video transcript:\n{self.transcript}"
            )
            
            messages = [{"role": "system", "content": system_message}]
            
            # Add chat history
            for entry in self.chat_history:
                messages.append({"role": "user", "content": entry["question"]})
                messages.append({"role": "assistant", "content": entry["answer"]})
            
            # Add current question
            messages.append({"role": "user", "content": question})
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.3,
                top_p=1,
                n=1,
                stop=None,
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Store in chat history
            self.chat_history.append({
                "question": question,
                "answer": answer
            })
            
            return answer
            
        except Exception as e:
            raise AIError(f"Chat failed: {str(e)}")
    
    def get_summary(self) -> Dict[str, str]:
        """
        Get video summary and metadata.
        
        Returns:
            Dictionary with summary and video metadata
        """
        summarizer = VideoSummarizer(self.model, self.max_tokens)
        return summarizer.summarize(self.url)
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()