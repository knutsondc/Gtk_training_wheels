# Error Dialogs invoked upon input of invalid data

from gi.repository import Gtk # pylint: disable-msg = E0611

class Error_Dialog:
    
    def __init__(self, msg):
        
        builder = Gtk.Builder()
        builder.add_from_file("Error_Dialog.glade")
# This window is a dialog, so no close button.
        self.window = builder.get_object("dialog")
        self.msg_textview = builder.get_object("textview")
        self.msg_textbuffer = builder.get_object("textbuffer")
        self.ok_button = builder.get_object("button")
        builder.connect_signals(self)
        
        self.msg_textbuffer.set_text(msg)
        self.window.show_all() 
        
    def on_ok_button_clicked(self, widget):
        self.window.destroy()