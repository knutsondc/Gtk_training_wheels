# Simple data store object definition for use in project intended to help
# learn how to implement GTK+ 3.0 ListStores and add, delete, and edit theur
# contents in a Gtk.TreeView

from gi.repository import Gtk

class RecordsStore(Gtk.ListStore):
    
    def __init__(self, columns, names):
        
        Gtk.ListStore__init__(self, *columns)
        self.names = names