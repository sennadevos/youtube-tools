from openai import OpenAI
import json

class VideoChatLLM:
    def __init__(self, transcript: str, metadata: dict, model: str = "gpt-4o"):
        self.transcript = transcript
        self.metadata = metadata
        self.model = model
        self.client = OpenAI()
        self.system_prompt = (
            "You are a helpful assistant. You can only answer questions based on the transcript and metadata provided. "
            "Do NOT use any outside knowledge. If the answer is not in the transcript or metadata, reply: 'Sorry, I can't answer that based on the video.'"
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Metadata: {json.dumps(self.metadata)}"},
            {"role": "user", "content": f"Transcript: {self.transcript}"}
        ]

    def ask(self, question: str, max_tokens: int = 200) -> str:
        self.messages.append({"role": "user", "content": question})
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=max_tokens,
                temperature=0.2,
                top_p=1,
                n=1,
                stop=None,
            )
            answer = response.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return f"Error during chat: {e}"
