# YouTube Tools

A versatile application that provides both command-line and graphical interfaces for working with YouTube videos. The app allows you to:

- Shorten YouTube URLs
- Download videos in various qualities
- View video transcripts
- Summarize videos using an LLM (Large Language Model)
- Chat with an LLM about the video, based only on its transcript

## Architecture

This application is built with a clean separation between backend and frontend:

- **Backend**: A robust CLI tool that can output structured JSON, making it perfect for integration with other applications
- **Frontend**: A modern GTK4 graphical interface built with Libadwaita for an intuitive user experience

## Setup & Installation

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

## Usage

### Graphical Interface (GTK4)

Launch the modern GTK4 GUI:
```bash
./run.sh
```

The GUI features:
- Large URL input field
- Tool selection dropdown
- Clean, responsive interface
- Integrated chat functionality for video discussions

### Command Line Interface

Use the CLI for automation, scripting, or integration with other tools:

```bash
# Launch GUI (no arguments)
./run.sh

# Use CLI (with arguments)
./run.sh <command> [options]

# Or use the CLI directly
./youtube-tools-cli <command> [options]
```

#### CLI Commands

**Shorten URL:**
```bash
./run.sh shorten "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
./run.sh shorten "https://youtu.be/dQw4w9WgXcQ" --json
```

**Download Video:**
```bash
./run.sh download "https://youtu.be/dQw4w9WgXcQ"
./run.sh download "https://youtu.be/dQw4w9WgXcQ" --output-path ./downloads --json
```

**Get Transcript:**
```bash
./run.sh transcript "https://youtu.be/dQw4w9WgXcQ"
./run.sh transcript "https://youtu.be/dQw4w9WgXcQ" --json
```

**Summarize Video:**
```bash
./run.sh summarize "https://youtu.be/dQw4w9WgXcQ"
./run.sh summarize "https://youtu.be/dQw4w9WgXcQ" --json
```

**Chat About Video:**
```bash
./run.sh chat "https://youtu.be/dQw4w9WgXcQ" "What is this video about?"
./run.sh chat "https://youtu.be/dQw4w9WgXcQ" "Summarize the main points" --json
```

#### JSON Output

All CLI commands support the `--json` flag for structured output, making it easy to integrate with other applications:

```bash
./run.sh summarize "https://youtu.be/dQw4w9WgXcQ" --json
```

Output:
```json
{
  "summary": "This video is about...",
  "title": "Video Title",
  "creator": "Channel Name",
  "description": "Video description..."
}
```

## Features

- **Shorten URL:** Convert long YouTube URLs to their short youtu.be equivalents
- **Download Video:** Download videos in the highest available quality
- **Show Transcript:** Extract and display video transcripts (when available)
- **Summarize & Chat:** Get AI-powered summaries and have conversations about video content

## Requirements

- Python 3.7+
- GTK4 and Libadwaita (for GUI)
- OpenAI API key (for LLM features)
- Internet connection

## Dependencies

The app relies on several third-party libraries:
- `pytube` - YouTube video downloading
- `youtube-transcript-api` - Transcript extraction
- `openai` - LLM integration
- `PyGObject` - GTK4 bindings

## Cleanup

To remove the virtual environment and cache files:
```bash
./cleanup.sh
```

## Notes

- You need a valid OpenAI API key for summarization and chat features
- Some YouTube videos may not provide transcripts due to restrictions
- The application handles both long and short YouTube URL formats

## License

This project is provided as-is, without any warranty. Feel free to use it as a starting point for your own experiments or applications.

---

*Generated with the help of LLM models.*
