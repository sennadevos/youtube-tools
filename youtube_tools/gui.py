#!/usr/bin/env python3
"""
YouTube Tools GTK4 GUI
Modern GTK4 interface for YouTube video processing tools.
"""

import gi
import json
import threading
from typing import Optional

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio

from .cli import cmd_shorten, cmd_download, cmd_transcript, cmd_summarize, cmd_chat
from .url_utils import is_youtube_url


class YouTubeToolsWindow(Adw.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, application):
        super().__init__(application=application)
        self.set_title("YouTube Tools")
        self.set_default_size(800, 600)
        
        # Current video state for chat functionality
        self.current_video_url: Optional[str] = None
        self.chat_backend = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header bar - AdwApplicationWindow handles this automatically
        
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
        self.url_entry.connect("changed", self.on_url_changed)
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
        self.tool_combo.connect("notify::selected", self.on_tool_changed)
        
        tool_group.add(self.tool_combo)
        main_box.append(tool_group)
        
        # Action button
        self.action_button = Gtk.Button(label="Go")
        self.action_button.add_css_class("suggested-action")
        self.action_button.set_sensitive(False)
        self.action_button.connect("clicked", self.on_action_clicked)
        main_box.append(self.action_button)
        
        # Results area
        self.results_stack = Gtk.Stack()
        self.results_stack.set_vexpand(True)
        
        # Text output page (for shorten URL, errors)
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_scroll.set_child(self.text_view)
        self.results_stack.add_named(text_scroll, "text")
        
        # Chat interface page
        chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Chat history
        chat_scroll = Gtk.ScrolledWindow()
        chat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        chat_scroll.set_vexpand(True)
        
        self.chat_listbox = Gtk.ListBox()
        self.chat_listbox.add_css_class("boxed-list")
        chat_scroll.set_child(self.chat_listbox)
        chat_box.append(chat_scroll)
        
        # Chat input
        chat_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_placeholder_text("Ask about the video...")
        self.chat_entry.set_hexpand(True)
        self.chat_entry.connect("activate", self.on_chat_send)
        
        self.chat_send_button = Gtk.Button(label="Send")
        self.chat_send_button.add_css_class("suggested-action")
        self.chat_send_button.connect("clicked", self.on_chat_send)
        
        chat_input_box.append(self.chat_entry)
        chat_input_box.append(self.chat_send_button)
        chat_box.append(chat_input_box)
        
        self.results_stack.add_named(chat_box, "chat")
        
        # Status page
        status_page = Adw.StatusPage()
        status_page.set_title("Ready")
        status_page.set_description("Enter a YouTube URL and select a tool to get started")
        status_page.set_icon_name("video-x-generic-symbolic")
        self.results_stack.add_named(status_page, "status")
        
        main_box.append(self.results_stack)
        
        # Set initial page
        self.results_stack.set_visible_child_name("status")
        
        self.set_content(main_box)
    
    def on_url_changed(self, entry):
        """Handle URL entry changes"""
        url = entry.get_text().strip()
        self.action_button.set_sensitive(bool(url))
    
    def on_tool_changed(self, combo, param):
        """Handle tool selection changes"""
        selected = combo.get_selected()
        if selected == 3:  # Summarize & Chat
            self.results_stack.set_visible_child_name("chat")
        else:
            self.results_stack.set_visible_child_name("text")
    
    def on_action_clicked(self, button):
        """Handle main action button click"""
        url = self.url_entry.get_text().strip()
        if not url:
            return
        
        if not is_youtube_url(url):
            self.show_error("Please enter a valid YouTube URL")
            return
        
        selected_tool = self.tool_combo.get_selected()
        tool_names = ["Shorten URL", "Download Video", "Show Transcript", "Summarize & Chat"]
        
        button.set_sensitive(False)
        button.set_label("Working...")
        
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
                GLib.idle_add(lambda: button.set_sensitive(True))
                GLib.idle_add(lambda: button.set_label("Go"))
        
        thread = threading.Thread(target=run_tool)
        thread.daemon = True
        thread.start()
    
    def handle_shorten(self, url: str):
        """Handle URL shortening"""
        try:
            from .url_utils import shorten_youtube_url
            result = shorten_youtube_url(url)
            GLib.idle_add(self.show_text_result, f"Shortened URL:\n{result}")
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def handle_download(self, url: str):
        """Handle video download"""
        try:
            from .downloader import download_youtube_video
            download_youtube_video(url)
            GLib.idle_add(self.show_text_result, "Download completed successfully!")
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def handle_transcript(self, url: str):
        """Handle transcript fetching"""
        try:
            from .transcript import fetch_youtube_transcript
            transcript = fetch_youtube_transcript(url)
            if transcript:
                GLib.idle_add(self.show_text_result, transcript)
            else:
                GLib.idle_add(self.show_error, "No transcript available for this video")
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def handle_summarize(self, url: str):
        """Handle video summarization and setup chat"""
        try:
            from .video_chat_backend_json import VideoChatBackendJSON
            self.chat_backend = VideoChatBackendJSON(url)
            self.current_video_url = url
            
            summary = self.chat_backend.get_summary()
            GLib.idle_add(self.add_chat_message, "Assistant", summary)
            GLib.idle_add(self.results_stack.set_visible_child_name, "chat")
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def show_text_result(self, text: str):
        """Show text result in the text view"""
        buffer = self.text_view.get_buffer()
        buffer.set_text(text)
        self.results_stack.set_visible_child_name("text")
    
    def show_error(self, error_msg: str):
        """Show error message"""
        buffer = self.text_view.get_buffer()
        buffer.set_text(f"Error: {error_msg}")
        self.results_stack.set_visible_child_name("text")
    
    def add_chat_message(self, sender: str, message: str):
        """Add a message to the chat"""
        row = Adw.ActionRow()
        
        if sender == "You":
            row.set_title(message)
            row.add_css_class("accent")
        else:
            row.set_title(message)
        
        row.set_subtitle(sender)
        self.chat_listbox.append(row)
        
        # Auto-scroll to bottom
        adjustment = self.chat_listbox.get_parent().get_vadjustment()
        adjustment.set_value(adjustment.get_upper())
    
    def on_chat_send(self, widget):
        """Handle chat message sending"""
        if not self.chat_backend:
            return
        
        message = self.chat_entry.get_text().strip()
        if not message:
            return
        
        self.chat_entry.set_text("")
        self.add_chat_message("You", message)
        
        # Disable input while processing
        self.chat_entry.set_sensitive(False)
        self.chat_send_button.set_sensitive(False)
        
        def get_response():
            try:
                response = self.chat_backend.ask(message)
                GLib.idle_add(self.add_chat_message, "Assistant", response)
            except Exception as e:
                GLib.idle_add(self.add_chat_message, "System", f"Error: {str(e)}")
            finally:
                GLib.idle_add(lambda: self.chat_entry.set_sensitive(True))
                GLib.idle_add(lambda: self.chat_send_button.set_sensitive(True))
        
        thread = threading.Thread(target=get_response)
        thread.daemon = True
        thread.start()


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


def main():
    """Main GUI entry point"""
    app = YouTubeToolsApplication()
    return app.run()


if __name__ == "__main__":
    main()