# Simple data store object definition for use in project intended to help
# learn how to implement GTK+ 3.0 ListStores and add, delete, and edit theur
# contents in a Gtk.TreeView.

from gi.repository import Gtk # pylint: disable-msg = E0611


class RecordsStore(Gtk.ListStore):
# Subclass ListStore to add a list of column titles
    
    def __init__(self, columns, names):
        
        Gtk.ListStore.__init__(self, *columns)
        self.names = names
        
