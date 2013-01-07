''''
Simple method to add to data store for use in project intended to help
learn how to implement GTK+ 3.0 ListStores and add, delete, and edit their
contents in a Gtk.TreeView. This version relies upon glade to construct the
AddRecordDialog.
'''
from gi.repository import Gtk #@UnresolvedImport pylint: disable-msg = E0611
        
def add_record_dialog(fields = None):
    '''
    The UI for the dialog the user completes for each new record is defined in a glade
    file. Function to get values for a new record. The arg provides a way to 
    communicate values used in previous failed attempts at entering the record.
    '''
    record_dialog  = Gtk.Builder()
    record_dialog.add_from_file("Add_Record.glade")
# This window is a dialog, so no close button.
    record_dialog.window = record_dialog.get_object("add_record_dialog")
    record_dialog.project_entry = record_dialog.get_object("project_entry")
    '''
    Set field values to those entered on previous unsuccessful attempts to
    create a record or, if there is no previous valid entry, make the entry
    blank.
    '''#pylint: disable-msg=W0105
    record_dialog.project_entry.set_text(fields['project'])
    record_dialog.context_entry = record_dialog.get_object("context_entry")
    record_dialog.context_entry.set_text(fields['context'])
    record_dialog.priority_spinbutton = record_dialog.get_object(
                                            "priority_spinbutton")
    record_dialog.priority_adjustment = record_dialog.get_object(
                                            "priority_adjustment")
    record_dialog.priority_adjustment.set_value(fields['priority'])
    record_dialog.completed_toggle = record_dialog.get_object("toggle")
    record_dialog.ok_button = record_dialog.get_object("ok_button")
    record_dialog.cancel_button = record_dialog.get_object("cancel_button")
    record_dialog.connect_signals(record_dialog)
    '''
    If some of the data fields already have values when this function gets
    called, it means that the user tried at least once before and entered
    illegal values. This code detects where the user first went wrong and
    puts the cursor and focus on the offending field while maintaining any
    legal values that were supplied to other fields.
    '''#pylint: disable-msg=W0105
    if fields['focus'] == "project":
        record_dialog.project_entry.grab_focus()
    elif fields['focus'] == "context":
        record_dialog.context_entry.grab_focus()
    elif fields['focus'] == "priority":
        record_dialog.priority_spinbutton.grab_focus()
    '''
    Now we've got the dialog all set up - show the results and wait
    for the user to finish data input.
    '''#pylint: disable-msg=W0105
    result = record_dialog.window.run()
    if result == Gtk.ResponseType.OK:
        fields['project'] = record_dialog.project_entry.get_text()
        fields['context'] = record_dialog.context_entry.get_text()
        '''
        The priority_adjustment gives a float value, but we need an int.
        '''#pylint: disable-msg=W0105
        fields['priority'] = int(record_dialog.priority_adjustment.get_value())
        fields['completed'] = record_dialog.completed_toggle.get_active()
        '''
        After submitting data to the caller, this dialog's work is done.
        '''#pylint: disable-msg=W0105
        record_dialog.window.destroy()
        return fields
    elif result == Gtk.ResponseType.CANCEL:
        '''
        If the user decides to cancel, just close the dialog and go
        back to the main program loop without changing any recorded
        data.
        '''#pylint: disable-msg=W0105
        record_dialog.window.destroy()
        return None