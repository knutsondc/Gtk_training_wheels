# Error Dialogs invoked upon input of invalid data

from gi.repository import Gtk # pylint: disable-msg = E0611

class ErrorDialog:
    
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
        
def Error_Check(self, row):

    if len(row[0]) < 1:
        ErrorDialog("Invalid or incomplete Project name.")
        return False
    elif len(row[1]) < 1:
        ErrorDialog("Invalid or incomplete Status description.")
        return False
# The SpinButton used for the Priority field should prevent entry of out-of-bounds
# values here, but check anyway for the sake of completeness.
    elif (not isinstance(row[2], int) or row[2] < 1 or row[2] > 4):
        ErrorDialog("Invalid or incomplete Priority value.")
        return False
        
    else:
        return True