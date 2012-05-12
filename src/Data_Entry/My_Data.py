# Main program control file for this toy project to demonstrate entry of data records
# into a Gtk.ListStore, display the records and allow the user to edit and delete them.

from gi.repository import Gtk # pylint: disable-msg = E0611

import Model

class My_Data:
    
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("Data_Entry.glade")
        self.window = builder.get_object("window")
        self.textbuffer = builder.get_object("textbuffer")
        self.add_record_button = builder.get_object("add_record_button")
        self.delete_record_button = builder.get_object("delete_record_button")
# The widget to display the data records follows:
        self.list_w = builder.get_object("treeview")
# The following item later holds references to the data records the user has selected
# in the list_w treeview and the Gtk.ListStore from which the data in those records
# were taken.
        self.selection = builder.get_object("treeview-selection")
# Make sure that that reference to selected records is empty at program start
        self.adjustment = Gtk.Adjustment(1.0, 1.0, 4.0, 1.0, 4.0, 0.0)
        self.treeiter = None
        self.renderer = []
# Eventually the following three lines setting up a fixed three-field RecordsStore
# will be replaced with code offering the user the choice of opening an existing
# RecordsStore or creating a new one with a user-determined number and type of 
# data fields (columns).
        self.types = [type("string"), type("string"), type(1)]
        self.names = ["Project", "Status", "Priority"]
# Call constructor of subclassed ListStore that adds list of names of columns in the
# ListStore as another member variable of the ListStore object.
        self.CurrentRecordsStore = Model.RecordsStore(self.types, self.names)
# Call method for constructing the TreeView used to display the data.
        self.construct_view()
        builder.connect_signals(self)
        
    def construct_view(self):
# First tell the TreeView from where to get its data to display.
        self.list_w.set_model(self.CurrentRecordsStore)
# Create a list of CellRenderers equal to the number of data columns in the ListStore
# so that when data cells get edited, we can detect in which column the cell that
# produced the "edited" signal is found from the identity of the CellRenderer pointed
#.to by the "widget" data contained in the "edited" signal. The "edited" signal emits
# a "path" value identifying the row in which the edited cell can be found.
        for i in range(len(self.names)):
            if self.types[i] == type(1):
                self.renderer.append(Gtk. CellRendererSpin())                
                self.renderer[i].set_property("adjustment", self.adjustment)
                self.renderer[i].connect("edited", self.on_records_edited)
                expand = False
            else:
                self.renderer.append(Gtk.CellRendererText())
                self.renderer[i].connect("edited", self.on_records_edited)
                expand = True
# By default, TreeView cells aren't editable, so we have to set this property.
            self.renderer[i].set_property("editable", True)
# Glade doesn't handle anything about TreeViewColumns or CellRenderers, so we must
# connect the CellRenderer to the relevant signal by hand.
            
# Create a TreeView Column to hold a data field, give it a name header, attach the
# relevant CellRenderer, and tell the TreeViewColumn from which column of the
#ListStore to read its data.
            column = Gtk.TreeViewColumn(self.names[i], self.renderer[i], text = i)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_expand(expand)
            self.list_w.append_column(column)
           
    def on_window_destroy(self, widget): # pylint: disable-msg = w0613
        Gtk.main_quit()
    
    def on_add_button_clicked(self, widget): # pylint: disable-msg = W0613
# The class and constructor method for a new data record is found in the Model.py 
# file. We pass the ListStore we're using as a parameter to allow for eventual use
# of multiple ListStores.
        Model.AddRecord(self.CurrentRecordsStore, self.list_w)
                  
    def on_records_edited(self, widget, path, text):
# The widget parameter is the CellRenderer that produced the "edited" signal. To
# learn the column number of the cell that produced the signal, we look for the widget
# parameter in the list of all CellRenderers; its place in the list gives us the
# column number of the cell that produced the signal. The "path" parameter emitted
# with the signal contains the row number of the cell that produced the signal.
        for w in self.renderer:
            if self.renderer[self.renderer.index(w)] == widget:
                col_num = self.renderer.index(w)
 
# The "text" parameter emitted with the "edited" signal is a str representation of 
# the new data the user entered into the edited cell. If the relevant column in the
# ListStore is expecting an int, we need to cast the str as an int. Eventually, code
# to check whether the user's input is capable of being cast into the correct data
# type and providing an appropriate response to erroneous input will be inserted
# also..               
        if isinstance(widget, Gtk.CellRendererSpin):
            self.CurrentRecordsStore[path][col_num] = int(text)
# Make sure the adjustment object holding the value for changes to Priority is reset
# to 1.0 after using it.
            self.adjustment.set_value(1.0)
        else:
            self.CurrentRecordsStore[path][col_num] = text
                    
    def on_delete_button_clicked(self, widget): # pylint: disable-msg = W0613
# First collect a list of pointers to the rows in the TreeView the user has selected.
        iters = []
        for row in self.treeiter:
            iters.append(self.CurrentRecordsStore.get_iter(row)) # pylint: disable-msg = E1103
# Then iterate over the list of pointers and, after checking to see that each pointer
# actually points to an actual row of data, delete the corresponding data record in
# the ListStore. This has to be done in two steps to ensure that we don't try to
# delete data using an iter that doesn't point to anything.
        for i in iters:
            if i is not None:
                self.CurrentRecordsStore.remove(i) # # pylint: disable-msg = E1103             
        
    def on_selection_changed(self, selection):
# The TreeViewSelection contains references to the rows in the TreeView the user has
# selected and the ListStore from which the data contained in those rows was taken.
# Note that this code is for multiple selection.
        self.CurrentRecordsStore, self.treeiter = selection.get_selected_rows()

        
if __name__=="__main__":
    win = My_Data()
    win.window.show_all()
    Gtk.main()

