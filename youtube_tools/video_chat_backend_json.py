import json
from .transcript import fetch_youtube_transcript
from .summarizer import summarize_text
from .video_chat_llm import VideoChatLLM
from pytube import YouTube

class VideoChatBackendJSON:
    def __init__(self, url: str):
        self.url = url
        # Try to fetch metadata, fallback to empty/defaults if it fails
        try:
            yt = YouTube(url)
            self.metadata = {
                "title": yt.title,
                "creator": yt.author,
                "description": yt.description[:500]  # Limit description length
            }
        except Exception:
            self.metadata = {
                "title": "Unknown",
                "creator": "Unknown",
                "description": "No description available."
            }

        # Fetch transcript
        self.transcript = fetch_youtube_transcript(url)
        if not self.transcript:
            raise ValueError("Transcript not found")

        # Summarize transcript
        try:
            self.summary = summarize_text(self.transcript)
            # Pass transcript and metadata as separate arguments
            self.chat_llm = VideoChatLLM(self.transcript, self.metadata)
        except Exception as e:
            raise ValueError(f"Error processing video: {str(e)}")

    def get_summary(self) -> str:
        return self.summary

    def get_summary_json(self) -> str:
        return json.dumps({
            "summary": self.summary,
            **self.metadata
        })

    def ask(self, question: str) -> str:
        answer = self.chat_llm.ask(question)
        return answer

    def ask_json(self, question: str) -> str:
        answer = self.chat_llm.ask(question)
        return json.dumps({"answer": answer})
