# Simple data store object definition for use in project intended to help
# learn how to implement GTK+ 3.0 ListStores and add, delete, and edit theur
# contents in a Gtk.TreeView. This versioni relies upon glade to construct the
# AddRecordDialog.

from gi.repository import Gtk #@UnresolvedImport pylint: disable-msg = E0611


class RecordsStore(Gtk.ListStore):
# Subclass ListStore to add a list of column titles
    
    def __init__(self, columns, names):
        
        Gtk.ListStore.__init__(self, *columns)
        self.names = names
        
def AddRecordDialog(treeview, fields = None):
        
# The UI for the dialog the user completes for each new record is defined in a glade
# file.
    record_dialog  = Gtk.Builder()
    record_dialog.add_from_file("Add_Record.glade")
# This window is a dialog, so no close button.
    record_dialog.window = record_dialog.get_object("add_record_dialog")
    record_dialog.project_entry = record_dialog.get_object("project_entry")
    record_dialog.project_entry.set_text(fields['project'])
    record_dialog.status_entry = record_dialog.get_object("status_entry")
    record_dialog.status_entry.set_text(fields['status'])
    record_dialog.priority_spinbutton = record_dialog.get_object("priority_spinbutton")
    record_dialog.priority_adjustment = record_dialog.get_object("priority_adjustment")
    record_dialog.priority_adjustment.set_value(fields['priority'])
    record_dialog.ok_button = record_dialog.get_object("ok_button")
    record_dialog.cancel_button = record_dialog.get_object("cancel_button")
    record_dialog.connect_signals(record_dialog)
    if fields['focus'] == "project":
        record_dialog.project_entry.grab_focus()
    elif fields['focus'] == "status":
        record_dialog.status_entry.grab_focus()
    elif fields['focus'] == "priority":
        record_dialog.priority_spinbutton.grab_focus()
        
# Placeholder text for the project and status Gtk.Entries can be set in the Glade
# file, but the actual starting values for those fields in the new record need to be
# set here. The Glade file ensures that the SpinButton and adjustment holding
# its value will lie within the valid range of 1 to 4.
#    

    result = record_dialog.window.run()
    if result == Gtk.ResponseType.OK:
        fields['project'] = record_dialog.project_entry.get_text()
        fields['status'] = record_dialog.status_entry.get_text()
        fields['priority'] = int(record_dialog.priority_adjustment.get_value())
# After submitting data to the caller, this dialog's work is done.
        record_dialog.window.destroy()
        return fields
    elif result == Gtk.ResponseType.CANCEL:
        record_dialog.window.destroy()
        return None