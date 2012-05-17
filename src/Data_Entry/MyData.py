# Main program control file for this toy project to demonstrate entry of data records
# into a Gtk.ListStore, display the records and allow the user to edit and delete them.
from ErrorDialog import ErrorCheck
from Model import RecordsStore, AddRecord
#from TaggedColumn import TaggedColumn
from gi.repository import Gtk, Gdk, GObject # pylint: disable-msg = E0611

class MyData:
    
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("Data_Entry.glade")
        self.window = builder.get_object("window")
        self.main_box = builder.get_object("main_box")
        self.textbuffer = builder.get_object("textbuffer")
        self.add_record_button = builder.get_object("add_record_button")
        self.delete_record_button = builder.get_object("delete_record_button")
# The Gtk.TreeView widget to display the data records follows:
        self.treeview = builder.get_object("treeview")
# The following item later holds references to the data records the user has selected
# in the treeview and the Gtk.ListStore from which the data in those records
# were taken.
        self.selection = builder.get_object("treeview-selection")
# Adjustment object to hold the info defining the SpinButton used to enter Priority
# values: current value, minimum, maximum, step, page increment, page size.
        self.adjustment = Gtk.Adjustment(1.0, 1.0, 4.0, 1.0, 4.0, 0.0)
# Make sure that that reference to selected records is empty at program start
        self.treeiter = None
# Empty list to hold list of CellRenderers allocated to the treeview columns.
        self.renderer = list()
# Eventually the following three lines setting up a fixed three-field RecordsStore
# will be replaced with code offering the user the choice of opening an existing
# RecordsStore or creating a new one with a user-determined number and type of 
# data fields (columns).
        self.types = [GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_INT]
        self.names = ["Project", "Status", "Priority"]
# Call constructor of subclassed ListStore that adds list of names of columns in the
# ListStore as another member variable of the ListStore object.
        self.CurrentRecordsStore = RecordsStore(self.types, self.names)
# Call method for constructing the TreeView used to display the data.
        self.construct_view()
        builder.connect_signals(self)
       
        
    def construct_view(self):
# First tell the TreeView from where to get its data to display.
        self.treeview.set_model(self.CurrentRecordsStore)
        
# Create a list of CellRenderers equal to the number of data columns in the ListStore
# so that when data cells get edited, we can detect in which column the cell that
# produced the "edited" signal is found from the "widget" data contained in the
# "edited" signal. In this program, the assignment of CellRenderers to COlumns is
# constant throughout. The "edited" signal emits a "path" value identifying the row
# in which the edited cell can be found.
        for i in range(len(self.names)):
# We want to use a SpinButton to edit the numeric data entered into the Priority
# column, so we check for the data type of the column so we can assign the appropriate
# CellRenderer to it.
            if self.types[i] == GObject.TYPE_INT:
                self.renderer.append(Gtk.CellRendererSpin())
# Attach the CellRendererSpin to the adjustment holding the data defining the
# SpinButton's behavior.                
                self.renderer[i].set_property("adjustment", self.adjustment)
# Glade doesn't handle anything about TreeViewColumns or CellRenderers, so we must
# The Priority column shouldn't expand, so we set that behavior here, too.
                expand = False
# All the other columns receive text and need to expand.
            else:
                self.renderer.append(Gtk.CellRendererText())
                expand = True
                
            self.renderer[i].set_property("editable", True)
            self.renderer[i].connect("edited", self.on_records_edited)
            
            column = Gtk.TreeViewColumn(self.names[i], self.renderer[i], text = i)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_clickable(True)
            column.set_resizable(True)
            column.set_reorderable(True)
# The "clicked" signal will be emitted when this column is clicked on.
            column.connect("clicked", self.on_column_clicked)
# This method identifies the column of the ListStore upon whose values the column in
# the treeview short be sorted.            
            column.set_sort_column_id(i)
            column.set_sort_indicator(True)
            column.set_expand(expand)
# Append the column to the TreeView.
            self.treeview.append_column(column)
            self.treeview.connect("button-press-event", self.on_mouse_button_press_event)
           
    def on_window_destroy(self, widget): # pylint: disable-msg = w0613
        Gtk.main_quit()
    
    def on_add_button_clicked(self, widget): # pylint: disable-msg = W0613
# The class and constructor method for a new data record is found in the Model.py 
# file. We pass the ListStore we're using as a parameter to allow for eventual use
# of multiple ListStores.
        AddRecord(self.CurrentRecordsStore, self.treeview)
                  
    def on_records_edited(self, widget, path, text):
# The "path"parameter emitted with the signal contains the row number of the cell that
# produced the signal.The widget parameter is the CellRenderer that produced the
# "edited" signal. To learn the column number of the cell that produced the signal,
# we look for the widget parameter in the list of all CellRenderers; its place in
# the list gives us the column number of the cell that produced the signal.
        col_num = self.renderer.index(widget)
# The "text" parameter emitted with the "edited" signal is a str representation of 
# the new data the user entered into the edited cell. If the relevant column in the
# ListStore is expecting an int, we need to cast the str as an int. The SpinButton
# used for entry of data in the Priority column ensures that "text" will always be
# a str representation of a double between 1.0 and 4.0, inclusive, so we need only
# cast it as an int - no bounds checking needed here. .               

        if text.isdigit():
         	text = int(text)

# Now submit the new, updated data field to a function that checks it for invalid
# values.If the updated record fails the error check, the on_records_edited method
# returns without changing the existing record; if the error check is passed, the
# updated data field gets written to the appropriate column row and column in the
#ListStore.
        if not ErrorCheck(col_num, text):
         	return
           
        self.CurrentRecordsStore[path][col_num] = text

    def on_delete_button_clicked(self, widget): # pylint: disable-msg = W0613        
# Iterate over a list of pointers to the rows in the TreeView the user has selected 
# and, after checking to see that each pointer actually points to a row of data,
# delete the corresponding data record in the ListStore. This has to be done in two
# steps to ensure that we don't try to delete data using an iter that doesn't point
# to anything.
        for i in [self.CurrentRecordsStore.get_iter(row) for row in self.treeiter]:# pylint: disable-msg = E1103
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

    def on_column_clicked(self, column):
        col_num = self.names.index(column.get_title())    
        column.set_sort_column_id(col_num)
#        self.window.reshow_with_initial_size()
        
# Use button-press-events to get focus on the edited cell.
    def on_mouse_button_press_event(self, treeview, event):
        if event.button == 1:
            x = int(event.x)
            y = int(event.y)
            pathinfo = treeview.get_path_at_pos(x, y)
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.set_cursor(path, col, True)
                treeview.grab_focus()
            return False

        
if __name__=="__main__":
    win = MyData()
    win.window.show_all()
    Gtk.main()

