# YouTube Tools (Proof of Concept)

This project is a proof-of-concept application that provides several useful tools for working with YouTube videos. The app allows you to:

- Shorten YouTube URLs
- Download videos in various qualities
- View video transcripts
- Summarize videos using an LLM (Large Language Model)
- Chat with an LLM about the video, based only on its transcript

## About the Code

Most of the code in this project was generated with the help of LLM models (such as GitHub Copilot and GPT). The project demonstrates how AI can be used to quickly build a multi-tool application for YouTube, but it is not a finished product.

**Disclaimer:**
- This app is a proof of concept and not a production-ready application.
- It has not been thoroughly tested and may be unstable or incomplete.
- The code is meant as a starting point for further development and improvement.

## Setup & Usage

1. **Clone the repository**
2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This will create a Python virtual environment and install the required dependencies.

3. **Set your OpenAI API key:**
   You need a valid OpenAI API key for the LLM features. Set the environment variable before running the app:
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```
   Or add it to your shell profile for convenience.

4. **Start the app:**
   ```bash
   ./run.sh
   ```
   This will launch the graphical user interface (GUI) for YouTube Tools.

5. **Cleanup (optional):**
   ```bash
   ./cleanup.sh
   ```
   This will remove the virtual environment and cache files.

## Features

- **Shorten URL:** Enter a YouTube URL and get a shortened version.
- **Download Video:** Download the video in the highest available quality.
- **Show Transcript:** View the transcript of the video (if available).
- **Summarize & Chat:** Get a summary of the video and chat with an LLM about its content, based only on the transcript.

## Notes
- The app relies on several third-party libraries and APIs (OpenAI, pytube, youtube-transcript-api, PyGObject).
- You need a valid OpenAI API key for the LLM features (see above).
- Some YouTube videos may not provide transcripts or metadata due to restrictions.

## License

This project is provided as-is, without any warranty. Feel free to use it as a starting point for your own experiments or applications.

---

*Generated with the help of LLM models.*
