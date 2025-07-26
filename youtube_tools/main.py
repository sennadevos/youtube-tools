import json
from .video_chat_backend_json import VideoChatBackendJSON

def main():
    from .gui import YouTubeToolsGUI
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    win = YouTubeToolsGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()