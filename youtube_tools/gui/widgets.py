"""
Custom GUI widgets and components.
Reusable UI components for the YouTube Tools application.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib


class MessageRow(Adw.ActionRow):
    """Custom row for displaying chat messages"""
    
    def __init__(self, sender: str, message: str):
        super().__init__()
        
        self.set_title(message)
        self.set_subtitle(sender)
        
        if sender == "You":
            self.add_css_class("accent")
        
        # Enable text selection
        self.set_activatable(False)


class StatusDisplay(Gtk.Box):
    """Widget for displaying status messages and loading states"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        self.status_page = Adw.StatusPage()
        self.status_page.set_title("Ready")
        self.status_page.set_description("Enter a YouTube URL and select a tool to get started")
        self.status_page.set_icon_name("video-x-generic-symbolic")
        
        self.append(self.status_page)
        
    def show_ready(self):
        """Show ready state"""
        self.status_page.set_title("Ready")
        self.status_page.set_description("Enter a YouTube URL and select a tool to get started")
        self.status_page.set_icon_name("video-x-generic-symbolic")
        
    def show_loading(self, message: str = "Processing..."):
        """Show loading state"""
        self.status_page.set_title("Working")
        self.status_page.set_description(message)
        self.status_page.set_icon_name("content-loading-symbolic")
        
    def show_error(self, error_message: str):
        """Show error state"""
        self.status_page.set_title("Error")
        self.status_page.set_description(error_message)
        self.status_page.set_icon_name("dialog-error-symbolic")


class ResultsView(Gtk.Box):
    """Container for different result views"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        
        # Text output view
        self.text_scroll = Gtk.ScrolledWindow()
        self.text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_margin_top(12)
        self.text_view.set_margin_bottom(12)
        self.text_view.set_margin_start(12)
        self.text_view.set_margin_end(12)
        
        self.text_scroll.set_child(self.text_view)
        self.stack.add_named(self.text_scroll, "text")
        
        # Chat view
        self.chat_box = self.create_chat_view()
        self.stack.add_named(self.chat_box, "chat")
        
        # Status view
        self.status_display = StatusDisplay()
        self.stack.add_named(self.status_display, "status")
        
        self.append(self.stack)
        
        # Show status by default
        self.show_status()
        
    def create_chat_view(self):
        """Create the chat interface"""
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
        self.chat_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_placeholder_text("Ask about the video...")
        self.chat_entry.set_hexpand(True)
        
        self.chat_send_button = Gtk.Button(label="Send")
        self.chat_send_button.add_css_class("suggested-action")
        
        self.chat_input_box.append(self.chat_entry)
        self.chat_input_box.append(self.chat_send_button)
        chat_box.append(self.chat_input_box)
        
        return chat_box
    
    def show_text(self, text: str):
        """Show text result"""
        buffer = self.text_view.get_buffer()
        buffer.set_text(text)
        self.stack.set_visible_child_name("text")
        
    def show_chat(self):
        """Show chat interface"""
        self.stack.set_visible_child_name("chat")
        
    def show_status(self):
        """Show status page"""
        self.stack.set_visible_child_name("status")
        
    def clear_text(self):
        """Clear text view"""
        buffer = self.text_view.get_buffer()
        buffer.set_text("")
        
    def clear_chat(self):
        """Clear chat history"""
        while True:
            child = self.chat_listbox.get_first_child()
            if child is None:
                break
            self.chat_listbox.remove(child)
            
    def add_chat_message(self, sender: str, message: str):
        """Add a message to chat"""
        row = MessageRow(sender, message)
        self.chat_listbox.append(row)
        
        # Auto-scroll to bottom
        def scroll_to_bottom():
            adjustment = self.chat_listbox.get_parent().get_vadjustment()
            adjustment.set_value(adjustment.get_upper())
            return False
        
        GLib.idle_add(scroll_to_bottom)
        
    def set_chat_enabled(self, enabled: bool):
        """Enable/disable chat input"""
        self.chat_entry.set_sensitive(enabled)
        self.chat_send_button.set_sensitive(enabled)