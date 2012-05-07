# Simple practice exercise placing static data into a GtK.ListStore
# and displaying it in a Gtk.TreeView widget without using Glade
# and Gtk.Builder. Properties of the widgets all set "by hand" to
# make output look the same as the Glade/Gtk.Builder version.

from gi.repository import Gtk  # pylint: disable-msg = E0611

class HelloGtk():
    
    def __init__(self):
        self.window = Gtk.Window(title="Hello GTK+ World!")
# The "destroy" signal will be caught and close the window when the
# user clicks on the "close" widget, but there's no guarantee that
# the program itself will terminate unless we connect the "destroy"
# signal to a callback that calls Gtk.Main_quit().
        self.window.connect("destroy", self.on_window_destroy)
# A Gtk.Window can itself hold only one Gtk widget, so we add a 
# Gtk.Container widget, a Gtk.Box, that can hold multiple widgets.
        self.box = Gtk.Box()
        self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.box.set_visible(True)
        self.box.set_can_focus(False)
        self.window.add(self.box)
# The remaining widgets get added by packing them into the Gtk.Box
# that we previously added to the Gtk.Window. 
        self.textview = Gtk.TextView()
# Set up a Gtk.TextBuffer to hold the content of the Gtk.TextView.
# We could just use the implicit TextBuffer that comes with the
# TextView by calling self.textview.get_buffer(), but to replicate
# the Glade version and demonstrate the linking of TextBuffer and
# TextView, we instantiate our own, named TextBuffer and stuff the
# text content into it.
        greeting = "This branch built without glade.\nWhere's the ListView?"
        self.textbuffer = Gtk.TextBuffer()
        self.textbuffer.set_text(greeting)
# Tell the TextView to use the TextBuffer we just set up.
        self.textview.set_buffer(self.textbuffer)
# Change content by manipulating the TextBuffer, but change format
# by calling the TextView's methods.
        self.textview.set_justification(Gtk.Justification.CENTER)
        self.textview.set_visible(True)
        self.textview.set_can_focus(True)
        self.box.pack_start(self.textview, False, True, 0)
# Without using glade and Gtk.Builder, we must explicitly define and populate
# the ListStore and expressly link the TreeView to it. Gtk style data types
# such as "gchararray" and "gint" (quotation marks necessary!) can be  used
# here, but we use ordinary Python types to prove it can be done - Glade
# apparently will not let one use the ordinary Python types to define a
# Gtk.ListStore.
        self.store = Gtk.ListStore(str, str, int)
        stored_data = (["Learn GTK", "Pending", 1],
                       ["Learn Android", "Pending", 2],
                       ["Review Django", "Waiting", 3],
                       ["Review Python", "Waiting", 4])
        for row in stored_data:
            self.store.append(row)
# Having created the data model, we now set up the view to display data using
# a Gtk.TreeView that is linked to the model data in parameter passed to 
# the constructor. We could have done the linking by calling the
# Gtk.TreeView.set_store() method later.
        self.list_w = Gtk.TreeView(self.store)
        self.list_w.set_visible(True)
        self.list_w.set_can_focus(True)
        self.list_w.set_reorderable(True)
        self.list_w.set_grid_lines(Gtk.TreeViewGridLines.BOTH) 
        self.box.pack_start(self.list_w, True, True, 1)
        self.button = Gtk.Button(label="Click Me!")
# Create a Gtk.Button widget to invoke the only "action" this program takes,
# displaying the data store and changing the message presented in the TextView.
        self.button.set_visible(True)
        self.button.set_can_focus(True)
        self.button.set_receives_default(True)
        self.button.set_use_action_appearance(False)
# Connect the button's "clicked" signal to the callback function that
# does the work.
        self.button.connect("clicked", self.on_button_clicked)
        self.box.pack_start(self.button, False, True, 2)
        
# One could simply connect the window's "destroy" signal directly
# to Gtk.main_quit(), but sending it here allows insertion of additional
# code (confirmation dialogs, clean up, etc.) before actually bailing. 
# Glade's default treatment of Gtk.Window widgets sets things up this way
# and it gets copied here.
    def on_window_destroy(self, widget): # pylint: disable-msg = w0613
        Gtk.main_quit()

    def on_button_clicked(self, widget): # pylint: disable-msg = W0613
# The data has been displayed, so change the message in the TextView to tell
# the user that nothing more will happen, so he might as well exit the program.
# Instead of changing the contents of the TextBuffer, we could have set up a 
# second TextBuffer holding this new message and connected it to the TextView
# by calling self.textview.set_buffer() with the new TextBuffer as the argument.
        close_msg = "Hello Listview!\nPlease Close The Application Now."
        self.textbuffer.set_text(close_msg)
# The button's function has been completed; it can do nothing more, so to avoid
# confusing the user, we hide the button.
        self.button.hide()
# Finally, call the method that actually displays the data.
        self.display_list()
        
    def display_list(self):
# The TreeView widget will display nothing until columns get added to it. This
# must be cone by hand by specifying column titles, the manner of displaying the
# data in each column, and the column in the data store from which each column
# should take the data to be displayed. After each column gets created, it gets
# appended to the TreeView.
        titles = ["Project", "Status", "Priority"]
# We're dealing with text only here, so the renderer for each column is the one
# used for text. Different renderers are needed for different types of data, such
# as images.
        renderer = Gtk.CellRendererText()
        for title in titles:
            column = Gtk.TreeViewColumn(title, renderer, text=titles.index(title))
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            self.list_w.append_column(column)
        
if __name__ == "__main__":
    win = HelloGtk()
# Be sure to use window.show_all() here! Window.show() will display the window
# only, leaving all the child and descendant widgets invisible! For some reason, 
# window.show() works in the Gladew/Gtk.Builder version. 
    win.window.show_all()
    Gtk.main()
        