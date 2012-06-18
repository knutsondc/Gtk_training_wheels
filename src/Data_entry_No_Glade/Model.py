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
        
def AddRecordDialog(recordsstore, fields = \
                    {'project':'', 'status': '', 'priority': 1.0, 'focus': None }):
        

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
    if fields['focus'] == "project":
        project_entry.grab_focus()
    elif fields['focus'] == "status":
        status_entry.grab_focus()
    elif fields['focus'] == "priority":
        priority_spin.grab_focus()
    record_dialog.show_all()
    result = record_dialog.run()
    if result == Gtk.ResponseType.OK:
        fields['project'] = project_entry.get_text()
        fields['status'] = status_entry.get_text()
        fields['priority'] = int(priority_adjustment.get_value())
        record_dialog.destroy()
        return fields
    elif result == Gtk.ResponseType.CANCEL:
        record_dialog.destroy()
        return None
    