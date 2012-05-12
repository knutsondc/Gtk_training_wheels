# Simple data store object definition for use in project intended to help
# learn how to implement GTK+ 3.0 ListStores and add, delete, and edit theur
# contents in a Gtk.TreeView

from gi.repository import Gtk # pylint: disable-msg = E0611
import Error_Dialog

class RecordsStore(Gtk.ListStore):
# Subclass ListStore to add a list of column titles
    
    def __init__(self, columns, names):
        
        Gtk.ListStore.__init__(self, *columns)
        self.names = names
        
class AddRecord():
    
    def __init__(self, recordsstore, list_w):
# The recordsstore parameter is the ListStore the new record will go into.
        self.recordsstore = recordsstore
        self.list_w = list_w
# The UI for the dialog the user completes for each new record is defined in a glade
# file.
        builder = Gtk.Builder()
        builder.add_from_file("Add_Record.glade")
# This window is a dialog, so no close button.
        self.window = builder.get_object("add_record_dialog")
        self.msg_textview = builder.get_object("msg_textview")
        self.msg_textbuffer = builder.get_object("msg_textbuffer")
        self.project_entry = builder.get_object("project_entry")
        self.status_entry = builder.get_object("status_entry")
        self.priority_textview = builder.get_object("priority_textview")
        self.priority_spinbutton = builder.get_object("priority_spinbutton")
        self.priority_adjustment = builder.get_object("priority_adjustment")
        self.ok_button = builder.get_object("ok_button")
        self.cancel_button = builder.get_object("cancel_button")
        builder.connect_signals(self)
# The placeholder text for the project and status Gtk.Entries is set in the Glade
# file, but the actual starting values for those fields in the new record need to be
# set here. The Glade file ensures that the spinbutton and adjustment holding
# its value will lie within the valid range of 1 to 4.
        self.project = None
        self.status = None
        self.priority = None
        self.pointer = None
        self.window.show_all() 
               
    def on_ok_clicked(self, widget): # pylint: disable-msg = W0613
# Read the data the user entered, check it for valid data, and, if so,  store the new
# record in the ListStore 
        self.project = self.project_entry.get_text()
        self.status = self.status_entry.get_text()
        self.priority = int(self.priority_adjustment.get_value())
        row = [self.project, self.status, self.priority]
# Alert the user to invalid data with GUI alerts from Error_Dialog.py
        if len(row[0]) < 1:
            Error_Dialog.Error_Dialog("Invalid or incomplete Project name.")
            return
        elif len(row[1]) < 1:
            Error_Dialog.Error_Dialog("Invalid or incomplete Status description.")
            return
# The SpinButton used for the Priority field should prevent entry of out-of-bounds
# values here, but check anyway for the sake of completeness.
        elif (row[2] < 1 or row[2] > 4):
            Error_Dialog.Error_Dialog("Invalid or incomplete Priority value.")
            return
        else:
            self.recordsstore.append(row)
# After storing valid data, this window's work is done.
        self.window.destroy()
        
    def on_cancel_clicked(self, widget): # pylint: disable-msg = W0613
# If the user decides to cancel creation of the new record, just close the "Add Record"
# dialog without reading or saving any of the data.
        self.window.destroy()