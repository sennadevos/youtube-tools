# YouTube Tools

A versatile application that provides both command-line and graphical interfaces for working with YouTube videos. The app allows you to:

- **Shorten YouTube URLs** - Convert long URLs to short youtu.be format
- **Download videos** - Choose from multiple quality options, saves to Downloads folder
- **View video transcripts** - Extract and display video subtitles
- **List video qualities** - See all available download options
- **Summarize videos** - AI-powered summaries using LLM
- **Chat about videos** - Interactive discussions based on video transcripts

## Architecture

This application features a modern, modular architecture with clean separation of concerns:

- **Core (`youtube_tools/core/`)**: Business logic and data processing
  - YouTube URL handling and validation
  - Video downloading with yt-dlp + pytube fallback
  - Transcript extraction with API compatibility
  - AI integration for summarization and chat
  
- **CLI (`youtube_tools/cli/`)**: Command-line interface with JSON output
  - Structured commands with comprehensive help
  - Quality selection and XDG Downloads integration
  - Perfect for automation and scripting
  
- **GUI (`youtube_tools/gui/`)**: Modern GTK4 interface with Libadwaita
  - Clean, responsive design with automatic Downloads folder
  - Integrated chat functionality for video discussions

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
- **Smart Downloads**: Automatically saves to your Downloads folder
- **Clean Interface**: Modern GTK4 design with Libadwaita styling
- **Tool Selection**: Easy switching between different YouTube tools
- **Quality Selection**: Downloads in best available quality by default
- **Chat Integration**: Interactive discussions about video content
- **Auto-clearing**: Interface resets when switching between tools

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
./run.sh --json shorten "https://youtu.be/dQw4w9WgXcQ"
```

**List Available Qualities:**
```bash
./run.sh qualities "https://youtu.be/dQw4w9WgXcQ"
./run.sh --json qualities "https://youtu.be/dQw4w9WgXcQ"
```

**Download Video:**
```bash
# Download to XDG Downloads folder (default)
./run.sh download "https://youtu.be/dQw4w9WgXcQ"

# Choose specific quality
./run.sh download "https://youtu.be/dQw4w9WgXcQ" --quality 720p

# Custom output directory
./run.sh download "https://youtu.be/dQw4w9WgXcQ" --output-path ./downloads

# JSON output with full details
./run.sh --json download "https://youtu.be/dQw4w9WgXcQ" --quality best
```

**Get Transcript:**
```bash
./run.sh transcript "https://youtu.be/dQw4w9WgXcQ"
./run.sh --json transcript "https://youtu.be/dQw4w9WgXcQ"
```

**Summarize Video:**
```bash
./run.sh summarize "https://youtu.be/dQw4w9WgXcQ"
./run.sh --json summarize "https://youtu.be/dQw4w9WgXcQ"
```

**Chat About Video:**
```bash
./run.sh chat "https://youtu.be/dQw4w9WgXcQ" "What is this video about?"
./run.sh --json chat "https://youtu.be/dQw4w9WgXcQ" "Summarize the main points"
```

#### JSON Output

All CLI commands support the `--json` flag for structured output, making it easy to integrate with other applications:

```bash
./run.sh --json summarize "https://youtu.be/dQw4w9WgXcQ"
```

**Quality List Output:**
```json
{
  "qualities": [
    {"quality": "best", "description": "Best available quality"},
    {"quality": "1080p", "description": "1080p - mp4"},
    {"quality": "720p", "description": "720p - mp4"},
    {"quality": "480p", "description": "480p - mp4"},
    {"quality": "worst", "description": "Lowest available quality"}
  ]
}
```

**Download Output:**
```json
{
  "status": "success",
  "message": "Download completed",
  "filename": "/home/user/Downloads/Video Title.mp4"
}
```

**Summarization Output:**
```json
{
  "summary": "This video is about...",
  "title": "Video Title",
  "author": "Channel Name",
  "description": "Video description..."
}
```

## Key Features

### 🎬 **Smart Video Downloads**
- **XDG Integration**: Downloads automatically save to your Downloads folder
- **Quality Selection**: Choose from available qualities (best/worst/720p/480p/etc.)
- **Reliable Downloading**: Uses yt-dlp as primary method with pytube fallback
- **Progress Feedback**: Real-time download progress and completion status

### 📝 **Transcript Processing**  
- **Multi-language Support**: Automatic language detection and fallback
- **Format Options**: Plain text or structured data output
- **API Compatibility**: Updated for latest youtube-transcript-api

### 🤖 **AI-Powered Features**
- **Video Summarization**: Generate concise summaries using OpenAI GPT
- **Interactive Chat**: Ask questions about video content
- **Context-Aware**: Responses based solely on video transcripts

### 🔧 **Developer-Friendly**
- **JSON Output**: All commands support structured data output
- **Modular Architecture**: Clean separation between core, CLI, and GUI
- **Error Handling**: Comprehensive error messages and fallback mechanisms

## Requirements

- Python 3.7+
- GTK4 and Libadwaita (for GUI)
- OpenAI API key (for LLM features)
- Internet connection

## Dependencies

The app relies on several third-party libraries:
- **`yt-dlp`** - Primary YouTube video downloader (reliable and actively maintained)
- **`pytube`** - Fallback YouTube video downloader 
- **`youtube-transcript-api`** - Transcript extraction with multi-language support
- **`openai`** - LLM integration for summarization and chat features
- **`PyGObject`** - GTK4 bindings for the graphical interface

### Download Pipeline
The application uses a robust two-tier download system:
1. **Primary**: yt-dlp (handles YouTube's anti-bot measures effectively)
2. **Fallback**: pytube (for compatibility and redundancy)

## Cleanup

To remove the virtual environment and cache files:
```bash
./cleanup.sh
```

## Important Notes

### 🔑 **API Requirements**
- **OpenAI API key required** for summarization and chat features
- Set via `export OPENAI_API_KEY=your-key-here`

### 🎥 **Video Compatibility** 
- **Transcript availability**: Some videos may not have transcripts due to creator settings
- **Download restrictions**: Private, age-restricted, or region-locked videos may fail
- **URL formats**: Supports both long (`youtube.com/watch?v=`) and short (`youtu.be/`) formats

### 📁 **Download Behavior**
- **Default location**: Uses XDG Downloads directory (typically `~/Downloads`)
- **Quality selection**: Automatically falls back to best available if requested quality unavailable
- **File naming**: Uses video title with safe filename characters

### 🔧 **Troubleshooting**
- **Download failures**: Application automatically tries pytube if yt-dlp fails
- **Transcript errors**: Check if video has captions enabled
- **GUI issues**: Ensure GTK4 and Libadwaita are installed

## License

This project is provided as-is, without any warranty. Feel free to use it as a starting point for your own experiments or applications.

---

*Generated with the help of LLM models.*
