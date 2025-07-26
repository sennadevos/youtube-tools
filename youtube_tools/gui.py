import gi
import threading
import json

from .url_utils import shorten_youtube_url
from .downloader import download_youtube_video
from .transcript import fetch_youtube_transcript
from .video_chat_backend_json import VideoChatBackendJSON

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

class YouTubeToolsGUI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="YouTube Tools")
        self.set_border_width(10)
        self.set_default_size(600, 600)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("YouTube URL")

        self.mode_combo = Gtk.ComboBoxText()
        self.mode_combo.append_text("Shorten URL")
        self.mode_combo.append_text("Download Video")
        self.mode_combo.append_text("Show Transcript")
        self.mode_combo.append_text("Summarize & Chat")
        self.mode_combo.set_active(0)
        self.mode_combo.connect("changed", self.on_mode_changed)

        self.action_btn = Gtk.Button(label="Go")
        self.action_btn.connect("clicked", self.on_action)

        # Chat UI for summarize/chat mode
        # Output for Shorten URL (selectable)
        self.output_entry = Gtk.Entry()
        self.output_entry.set_editable(False)
        self.output_entry.set_visible(False)
        self.clipboard_btn = Gtk.Button(label="Copy to clipboard")
        self.clipboard_btn.set_visible(False)
        self.clipboard_btn.connect("clicked", self.on_copy_clipboard)

        # Chat UI for summarize/chat mode
        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.chat_scroller = Gtk.ScrolledWindow()
        self.chat_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.chat_scroller.set_min_content_height(300)
        self.chat_scroller.add(self.chat_box)
        self.chat_scroller.set_visible(False)

        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_placeholder_text("Ask about the video transcript...")
        self.chat_entry.set_visible(False)
        self.chat_btn = Gtk.Button(label="Send")
        self.chat_btn.connect("clicked", self.on_chat)
        self.chat_btn.set_visible(False)

        chat_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        chat_input_box.pack_start(self.chat_entry, True, True, 0)
        chat_input_box.pack_start(self.chat_btn, False, False, 0)
        chat_input_box.set_visible(False)
        self.chat_input_box = chat_input_box

        # Transcript view
        self.transcript_view = Gtk.TextView()
        self.transcript_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.transcript_view.set_editable(False)
        self.transcript_scroller = Gtk.ScrolledWindow()
        self.transcript_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.transcript_scroller.add(self.transcript_view)
        self.transcript_scroller.set_visible(False)

        # Hide chat and transcript UI elements on startup
        self.chat_scroller.set_visible(False)
        self.chat_input_box.set_visible(False)
        self.chat_entry.set_visible(False)
        self.chat_btn.set_visible(False)
        self.transcript_scroller.set_visible(False)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.pack_start(self.url_entry, False, False, 0)
        self.main_box.pack_start(self.mode_combo, False, False, 0)
        self.main_box.pack_start(self.action_btn, False, False, 0)
        self.main_box.pack_start(self.output_entry, False, False, 0)
        self.main_box.pack_start(self.clipboard_btn, False, False, 0)
        self.main_box.pack_start(self.chat_scroller, True, True, 0)
        self.main_box.pack_start(self.chat_input_box, False, False, 0)
        self.main_box.pack_start(self.transcript_scroller, True, True, 0)
        self.add(self.main_box)

        self.backend = None
        self.transcript = None
        self.chat_history = []

        # Ensure correct initial UI state
        self.update_ui()

        self.backend = None
        self.transcript = None
        self.chat_box.set_halign(Gtk.Align.FILL)  # Ensure chat box fills horizontally
        self.chat_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.chat_scroller.set_min_content_width(300)  # Set a minimum width for better wrapping

    def add_chat_message(self, text, sender="system"):
        import html
        label = Gtk.Label()
        safe_text = html.escape(text)
        label.set_line_wrap(True)  # Enable line wrapping
        if sender == "user":
            label.set_markup(f'<span foreground="blue"><b>You:</b> {safe_text}</span>')
        elif sender == "assistant":
            label.set_markup(f'<span foreground="green"><b>LLM:</b> {safe_text}</span>')
        else:
            label.set_markup(f'<span foreground="gray">{safe_text}</span>')
        label.set_xalign(0)
        self.chat_box.pack_start(label, False, False, 0)
        self.chat_box.show_all()
        self.chat_history.append((sender, text))

    def set_output(self, text):
        self.output_entry.set_text(text)
        self.output_entry.set_visible(True)
        self.clipboard_btn.set_visible(True)
        self.chat_box.foreach(lambda widget: self.chat_box.remove(widget))
        self.chat_scroller.set_visible(False)
        self.chat_input_box.set_visible(False)
        self.chat_entry.set_visible(False)
        self.chat_btn.set_visible(False)
        self.chat_history = []
    def set_transcript(self, text):
        buffer = self.transcript_view.get_buffer()
        buffer.set_text(text)
        self.transcript_scroller.set_visible(True)

    def update_ui(self):
        mode = self.mode_combo.get_active_text()
        if mode == "Shorten URL":
            self.output_entry.set_visible(False)
            self.clipboard_btn.set_visible(False)
            self.chat_scroller.set_visible(False)
            self.chat_input_box.set_visible(False)
            self.chat_entry.set_visible(False)
            self.chat_btn.set_visible(False)
            self.transcript_scroller.set_visible(False)
        elif mode == "Summarize & Chat":
            self.output_entry.set_visible(False)
            self.clipboard_btn.set_visible(False)
            self.chat_scroller.set_visible(True)
            self.chat_input_box.set_visible(True)
            self.chat_entry.set_visible(True)
            self.chat_btn.set_visible(True)
            self.transcript_scroller.set_visible(False)
        elif mode == "Show Transcript":
            self.output_entry.set_visible(False)
            self.clipboard_btn.set_visible(False)
            self.chat_scroller.set_visible(False)
            self.chat_input_box.set_visible(False)
            self.chat_entry.set_visible(False)
            self.chat_btn.set_visible(False)
            self.transcript_scroller.set_visible(True)
        else:
            self.output_entry.set_visible(False)
            self.clipboard_btn.set_visible(False)
            self.chat_scroller.set_visible(False)
            self.chat_input_box.set_visible(False)
            self.chat_entry.set_visible(False)
            self.chat_btn.set_visible(False)
            self.transcript_scroller.set_visible(False)
    def on_mode_changed(self, combo):
        self.update_ui()

    def on_action(self, widget):
        mode = self.mode_combo.get_active_text()
        url = self.url_entry.get_text().strip()
        if mode == "Shorten URL":
            short_url = shorten_youtube_url(url)
            self.output_entry.set_text(short_url)
            self.output_entry.set_visible(True)
            self.clipboard_btn.set_visible(True)
            self.chat_scroller.set_visible(False)
            self.chat_input_box.set_visible(False)
            self.chat_entry.set_visible(False)
            self.chat_btn.set_visible(False)
        elif mode == "Download Video":
            def download():
                try:
                    download_youtube_video(url)
                    self.set_output("Download complete.")
                except Exception as e:
                    self.set_output(f"Download error: {e}")
            threading.Thread(target=download).start()
        elif mode == "Show Transcript":
            def fetch():
                try:
                    transcript = fetch_youtube_transcript(url)
                    self.transcript = transcript
                    self.set_transcript(transcript)
                except Exception as e:
                    self.set_output(f"Transcript error: {e}")
            threading.Thread(target=fetch).start()
        elif mode == "Summarize & Chat":
            def summarize():
                try:
                    self.backend = VideoChatBackendJSON(url)
                    summary_json = self.backend.get_summary_json()
                    summary = json.loads(summary_json)["summary"]
                    self.output_entry.set_visible(False)
                    self.clipboard_btn.set_visible(False)
                    self.chat_box.foreach(lambda widget: self.chat_box.remove(widget))
                    self.chat_scroller.set_visible(True)
                    self.chat_input_box.set_visible(True)
                    self.chat_entry.set_visible(True)
                    self.chat_btn.set_visible(True)
                    self.add_chat_message(summary, sender="assistant")
                except Exception as e:
                    self.set_output(f"Summarize error: {e}")
            threading.Thread(target=summarize).start()
    def on_copy_clipboard(self, widget):
        # Wayland clipboard support using Gtk
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.output_entry.get_text(), -1)

    def on_chat(self, widget):
        question = self.chat_entry.get_text().strip()
        if not self.backend:
            self.set_output("Please summarize the video first.")
            return
        self.add_chat_message(question, sender="user")
        def chat():
            try:
                answer_json = self.backend.ask_json(question)
                answer = json.loads(answer_json)["answer"]
                self.add_chat_message(answer, sender="assistant")
            except Exception as e:
                self.add_chat_message(f"Chat error: {e}", sender="system")
        threading.Thread(target=chat).start()

if __name__ == "__main__":
    win = YouTubeToolsGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
