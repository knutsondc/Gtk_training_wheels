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
# The Gtk.TreeView widget to display the data records follows:
        self.list_w = builder.get_object("treeview")
# The following item later holds references to the data records the user has selected
# in the list_w treeview and the Gtk.ListStore from which the data in those records
# were taken.
        self.selection = builder.get_object("treeview-selection")
# Adjustment object to hold the info defining the SpinButton used to enter Priority
# values: current value, minimum, maximum, step, page increment, page size.
        self.adjustment = Gtk.Adjustment(1.0, 1.0, 4.0, 1.0, 4.0, 0.0)
# Make sure that that reference to selected records is empty at program start
        self.treeiter = None
# List of the CellRenderers our TreeView widget will use.
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
# produced the "edited" signal is found from the "widget" data contained in the
# "edited" signal. The "edited" signal emits a "path" value identifying the row in
# which the edited cell can be found.
        for i in range(len(self.names)):
# We want to use a SpinButton to edit the numeric data entered into the Priority
# column, so we check for the data type of the column so we can assign the appropriate
# CellRenderer to it.
            if self.types[i] == type(1):
                self.renderer.append(Gtk. CellRendererSpin())
# Attach the CellRendererSpin to the adjustment holding the data defining the
# SpinButton's behavior.                
                self.renderer[i].set_property("adjustment", self.adjustment)
# Glade doesn't handle anything about TreeViewColumns or CellRenderers, so we must
# connect the CellRenderer to the relevant signal by hand.
                self.renderer[i].connect("edited", self.on_records_edited)
# The Priority column shouldn't expand, so we set that behavior here, too.
                expand = False
# All the other columns receive text and need to expand.
            else:
                self.renderer.append(Gtk.CellRendererText())
                self.renderer[i].connect("edited", self.on_records_edited)
                expand = True
# The remaining steps to configure the columns are common to all.
# By default, TreeView cells aren't editable, so we have to set this property.
            self.renderer[i].set_property("editable", True)
# Create a TreeView Column to hold a data field, give it a name header, attach the
# relevant CellRenderer, and tell the TreeViewColumn from which column of the
# ListStore to read its data.
            column = Gtk.TreeViewColumn(self.names[i], self.renderer[i], text = i)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_expand(expand)
# Finally, append the column to the TreeView.
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
# Once we've found the relevant column, no need to look at the rest.
                break 
# The "text" parameter emitted with the "edited" signal is a str representation of 
# the new data the user entered into the edited cell. If the relevant column in the
# ListStore is expecting an int, we need to cast the str as an int. The SpinButton
# used for entry of data in the Priority column ensures that "text" will always be
# a str representation of a double between 1.0 and 4.0, inclusive, so we need only
# cast it as an int - no bounds checking needed here. .               
        if isinstance(widget, Gtk.CellRendererSpin):
            self.CurrentRecordsStore[path][col_num] = int(text)
# Make sure the adjustment object holding the value for changes to Priority is reset
# to 1.0 after using it.
            self.adjustment.set_value(1.0)
        else:
            self.CurrentRecordsStore[path][col_num] = text
                    
    def on_delete_button_clicked(self, widget): # pylint: disable-msg = W0613
        
# Collect a list of pointers to the rows in the TreeView the user has selected.
        iters = [self.CurrentRecordsStore.get_iter(row) for row in self.treeiter]# pylint: disable-msg = E1103

# Then iterate over the list of pointers and, after checking to see that each pointer
# actually points to a row of data, delete the corresponding data record in the
# ListStore. This has to be done in two steps to ensure that we don't try to delete
# data using an iter that doesn't point to anything.
        for i in iters:
            if i is not None:
                self.CurrentRecordsStore.remove(i) # pylint: disable-msg = E1103
                
# Finally, shrink the window down to only the size needed to display the remaining
# records. The method invoked below hides the window and reopens it to the size
# needed to contain the visible widgets now contained in it, just as when a window
# is initially opened.
        self.window.reshow_with_initial_size()
        
    def on_selection_changed(self, selection):
# The TreeViewSelection contains references to the rows in the TreeView the user has
# selected and the ListStore from which the data contained in those rows was taken.
# Note that this code is for multiple selection.
        self.CurrentRecordsStore, self.treeiter = selection.get_selected_rows()

        
if __name__=="__main__":
    win = My_Data()
    win.window.show_all()
    Gtk.main()

