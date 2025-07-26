from openai import OpenAI

def summarize_text(text: str, model: str = "gpt-4o", max_tokens: int = None) -> str:
    """
    Summarizes the input text using OpenAI's GPT model.

    Args:
        text: The text to summarize.
        model: The model to use (default "gpt-4o").
        max_tokens: Maximum tokens for the summary (default None, no limit).

    Returns:
        The summary string.
    """
    client = OpenAI()

    prompt = (
        "You are a helpful assistant. Please provide a clear, concise summary "
        "of the following video, focusing on the main points and avoiding unnecessary details. "
        "Base your summary only on the transcript below, but refer to it as the video, not as text.\n\n"
        f"Transcript:\n{text}\n\nSummary:"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful summarization assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            top_p=1,
            n=1,
            stop=None,
        )
        # Extract summary from the response
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        return f"Error during summarization: {e}"
