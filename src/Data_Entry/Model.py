# Simple data store object definition for use in project intended to help
# learn how to implement GTK+ 3.0 ListStores and add, delete, and edit theur
# contents in a Gtk.TreeView

from gi.repository import Gtk # pylint: disable-msg = E0611

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
# set here. They start out as empty string. The Glade file ensures that the spinbutton
# and adjustment holding its value will lie within the valid range of 1 to 4.
        self.project = ""
        self.status = ""
        self.priority = 1
        self.pointer = None
        self.window.show_all() 
               
    def on_ok_clicked(self, widget): # pylint: disable-msg = W0613
# Read the data the user entered, check it for valid data, and, if so,  store the new
# record in the ListStore 
        self.project = self.project_entry.get_text()
        self.status = self.status_entry.get_text()
        self.priority = int(self.priority_adjustment.get_value())
        row = [self.project, self.status, self.priority]
# Future task: replace error messages to the console with GUI alerts.
        if row[0] == "":
            print("Invalid or incomplete record.")
            return
        elif row[1] == "":
            print("Invalid or incomplete record.")
            return
        elif row[2] == -1:
            print("Invalid or incomplete record.")
            return
        else:
            self.recordsstore.append(row)
        self.window.destroy()
        
    def on_cancel_clicked(self, widget): # pylint: disable-msg = W0613
# If the user decides to cancel creation of the new record, just close the "Add Record"
# dialog without reading or saving any of the data.
        self.window.destroy()