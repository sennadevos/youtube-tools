#!/usr/bin/env python3
"""
YouTube Tools GTK4 GUI Main Application
Modern GTK4 interface with Libadwaita styling.
"""

import gi
import threading
from typing import Optional

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from .widgets import ResultsView
from ..core.youtube import is_youtube_url, shorten_youtube_url
from ..core.downloader import download_video, get_available_qualities, get_default_download_path, VideoDownloadError
from ..core.transcript import get_transcript, TranscriptError
from ..core.ai import VideoChatBot, AIError


class YouTubeToolsWindow(Adw.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, application):
        super().__init__(application=application)
        self.set_title("YouTube Tools")
        self.set_default_size(800, 600)
        
        # Application state
        self.current_chatbot: Optional[VideoChatBot] = None
        self.is_processing = False
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # URL input section
        url_group = Adw.PreferencesGroup()
        url_group.set_title("YouTube Video")
        url_group.set_description("Enter a YouTube video URL to get started")
        
        self.url_entry = Adw.EntryRow()
        self.url_entry.set_title("Video URL")
        url_group.add(self.url_entry)
        
        main_box.append(url_group)
        
        # Tool selection
        tool_group = Adw.PreferencesGroup()
        tool_group.set_title("Select Tool")
        
        self.tool_combo = Adw.ComboRow()
        self.tool_combo.set_title("Tool")
        
        # Create string list for tools
        string_list = Gtk.StringList()
        string_list.append("Shorten URL")
        string_list.append("Download Video")
        string_list.append("Show Transcript")
        string_list.append("Summarize & Chat")
        
        self.tool_combo.set_model(string_list)
        self.tool_combo.set_selected(0)
        
        tool_group.add(self.tool_combo)
        main_box.append(tool_group)
        
        # Action button
        self.action_button = Gtk.Button(label="Go")
        self.action_button.add_css_class("suggested-action")
        self.action_button.set_sensitive(False)
        main_box.append(self.action_button)
        
        # Results area
        self.results_view = ResultsView()
        main_box.append(self.results_view)
        
        self.set_content(main_box)
    
    def connect_signals(self):
        """Connect UI signals"""
        self.url_entry.connect("changed", self.on_url_changed)
        self.tool_combo.connect("notify::selected", self.on_tool_changed)
        self.action_button.connect("clicked", self.on_action_clicked)
        
        # Chat signals
        self.results_view.chat_entry.connect("activate", self.on_chat_send)
        self.results_view.chat_send_button.connect("clicked", self.on_chat_send)
    
    def on_url_changed(self, entry):
        """Handle URL entry changes"""
        url = entry.get_text().strip()
        self.action_button.set_sensitive(bool(url) and not self.is_processing)
    
    def on_tool_changed(self, combo, param):
        """Handle tool selection changes"""
        if self.is_processing:
            return
            
        selected = combo.get_selected()
        
        # Clear previous results
        self.results_view.clear_text()
        self.results_view.clear_chat()
        self.current_chatbot = None
        
        # Show appropriate view
        if selected == 3:  # Summarize & Chat
            self.results_view.show_chat()
        else:
            self.results_view.show_status()
    
    def on_action_clicked(self, button):
        """Handle main action button click"""
        url = self.url_entry.get_text().strip()
        if not url or self.is_processing:
            return
        
        if not is_youtube_url(url):
            self.show_error("Please enter a valid YouTube URL")
            return
        
        selected_tool = self.tool_combo.get_selected()
        
        self.set_processing(True)
        
        def run_tool():
            try:
                if selected_tool == 0:  # Shorten URL
                    self.handle_shorten(url)
                elif selected_tool == 1:  # Download Video
                    self.handle_download(url)
                elif selected_tool == 2:  # Show Transcript
                    self.handle_transcript(url)
                elif selected_tool == 3:  # Summarize & Chat
                    self.handle_summarize(url)
            except Exception as e:
                GLib.idle_add(self.show_error, f"Error: {str(e)}")
            finally:
                GLib.idle_add(self.set_processing, False)
        
        thread = threading.Thread(target=run_tool, daemon=True)
        thread.start()
    
    def handle_shorten(self, url: str):
        """Handle URL shortening"""
        try:
            result = shorten_youtube_url(url)
            GLib.idle_add(self.results_view.show_text, f"Shortened URL:\n{result}")
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def handle_download(self, url: str):
        """Handle video download"""
        try:
            # Use default XDG download path and best quality
            filename = download_video(url, output_path=None, quality="best")
            download_path = get_default_download_path()
            GLib.idle_add(self.results_view.show_text, f"Download completed!\nSaved to: {download_path}\nFilename: {filename}")
        except VideoDownloadError as e:
            GLib.idle_add(self.show_error, str(e))
    
    def handle_transcript(self, url: str):
        """Handle transcript fetching"""
        try:
            transcript = get_transcript(url)
            GLib.idle_add(self.results_view.show_text, transcript)
        except TranscriptError as e:
            GLib.idle_add(self.show_error, str(e))
    
    def handle_summarize(self, url: str):
        """Handle video summarization and setup chat"""
        try:
            self.current_chatbot = VideoChatBot(url)
            summary_data = self.current_chatbot.get_summary()
            summary = summary_data["summary"]
            
            GLib.idle_add(self.results_view.show_chat)
            GLib.idle_add(self.results_view.add_chat_message, "Assistant", summary)
        except AIError as e:
            GLib.idle_add(self.show_error, str(e))
    
    def on_chat_send(self, widget):
        """Handle chat message sending"""
        if not self.current_chatbot or self.is_processing:
            return
        
        message = self.results_view.chat_entry.get_text().strip()
        if not message:
            return
        
        self.results_view.chat_entry.set_text("")
        self.results_view.add_chat_message("You", message)
        
        self.results_view.set_chat_enabled(False)
        
        def get_response():
            try:
                response = self.current_chatbot.ask(message)
                GLib.idle_add(self.results_view.add_chat_message, "Assistant", response)
            except AIError as e:
                GLib.idle_add(self.results_view.add_chat_message, "System", f"Error: {str(e)}")
            finally:
                GLib.idle_add(self.results_view.set_chat_enabled, True)
        
        thread = threading.Thread(target=get_response, daemon=True)
        thread.start()
    
    def show_error(self, error_msg: str):
        """Show error message"""
        self.results_view.show_text(f"Error: {error_msg}")
    
    def set_processing(self, processing: bool):
        """Set processing state"""
        self.is_processing = processing
        self.action_button.set_sensitive(not processing and bool(self.url_entry.get_text().strip()))
        self.action_button.set_label("Working..." if processing else "Go")


class YouTubeToolsApplication(Adw.Application):
    """Main application class"""
    
    def __init__(self):
        super().__init__(application_id="com.github.sjdevos.youtube-tools")
        
    def do_activate(self):
        """Called when the application is activated"""
        window = self.props.active_window
        if not window:
            window = YouTubeToolsWindow(self)
        window.present()


def main() -> int:
    """Main GUI entry point"""
    app = YouTubeToolsApplication()
    return app.run()


if __name__ == "__main__":
    main()