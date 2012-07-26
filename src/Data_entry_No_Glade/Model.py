'''
Simple data store object definition for use in project intended to help
learn how to implement GTK+ 3.0 ListStores and add, delete, and edit theur
contents in a Gtk.TreeView.
'''
from gi.repository import Gtk #@UnresolvedImport pylint: disable-msg = E0611


class RecordsStore(Gtk.ListStore):
    '''
    Subclass ListStore to add a list of column titles
    '''
    def __init__(self, columns, names):
        
        Gtk.ListStore.__init__(self, *columns)
        self.names = names
        
def AddRecordDialog(recordsstore, fields):
    '''
    Function to get values for a new record. Args point to the current data store and
    provide a way to communicate previous failed attempts at entering the record.
    '''
    
    record_dialog = Gtk.Dialog("Add a New Record", buttons = (Gtk.STOCK_OK, Gtk.ResponseType.OK,\
                                                               Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
    record_dialog.set_modal(True)
    record_dialog.set_destroy_with_parent(True)
    vbox = record_dialog.get_content_area()
    project_label = Gtk.Label("Enter New Project Name:")
    vbox.add(project_label)
    project_entry = Gtk.Entry()
    project_entry.set_text(fields['project'])
    vbox.add(project_entry)
    status_label = Gtk.Label("Enter New Project Status:")
    vbox.add(status_label)
    status_entry = Gtk.Entry()
    status_entry.set_text(fields['status'])
    vbox.add(status_entry)
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    vbox.add(hbox)
    priority_label = Gtk.Label("Enter New Project Priority:")
    hbox.add(priority_label)
    priority_spin = Gtk.SpinButton()
    priority_spin.set_numeric(True)
    priority_spin.set_value(1.0)
    priority_spin.set_digits(0)
    priority_spin.set_increments(1.0, 4.0)
    priority_adjustment = Gtk.Adjustment(1.0, 1.0, 4.0, 1.0, 0.0, 0.0 )
    priority_spin.set_adjustment(priority_adjustment)
    hbox.add(priority_spin)
    '''
    If the "focus" data fields has a value  when this function gets
    called, it means that the user tried at least once before and entered
    an illegal value. That field shows where the user first went wrong and
    puts the cursor and focus on the offending field while maintaining any
    legal values that were supplied to other fields.
    '''
    if fields['focus'] == "project":
        project_entry.grab_focus()
    elif fields['focus'] == "status":
        status_entry.grab_focus()
    elif fields['focus'] == "priority":
        priority_spin.grab_focus()
    '''
    Now we've got the dialog all set up - show the results and wait
    for the user to finish data input.
    '''
    record_dialog.show_all()
    result = record_dialog.run()
    if result == Gtk.ResponseType.OK:
        fields['project'] = project_entry.get_text()
        fields['status'] = status_entry.get_text()
        '''
        Adjustments return floats, but we need an int.
        '''
        fields['priority'] = int(priority_adjustment.get_value())
        '''
        After submitting data to the caller, this dialog's work is done.
        '''
        record_dialog.destroy()
        return fields
    elif result == Gtk.ResponseType.CANCEL:
        '''
        If the user decides to cancel, just close the dialog and go
        back to the main program loop without changing any recorded
        data.
        '''
        record_dialog.destroy()
        return None