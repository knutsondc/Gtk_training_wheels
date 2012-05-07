# Simple practice exercise placing static data into a GtK.ListStore
# and displaying it in a Gtk.TreeView widget using Glade and
# Gtk.Builder.

from gi.repository import Gtk  # pylint: disable-msg = E0611

class HelloGtk():
    
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("Hello World.glade")
        self.window = builder.get_object("window")
        self.textbuffer = builder.get_object("textbuffer")
        self.button = builder.get_object("button")
# The ListStore is defined and linked to the TreeView in the Glade file, 
# so no express reference to the ListStore is needed in the Python source.
        self.list_w = builder.get_object("treeview")
# The callbacks for each widget's signals are specified in the glade file,
# so all the connections can be made in a single method call when using
# Gtk.Builder. 
        builder.connect_signals(self)
        
# One could simply connect the window's "destroy" signal directly
# to Gtk.main_quit(), but sending it here allows insertion of additional
# code (confirmation dialogs, clean up, etc.) before actually bailing. 
# Glade's default treatment of Gtk.Window widgets sets things up this way.
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
# For some reason, window.show() works here in the Glade version, but in the 
# version coded "by hand" window.show() will display the window only, leaving
# all the child and descendant widgets invisible!
    win.window.show_all()
    Gtk.main()
        