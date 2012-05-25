# Main program control file for this toy project to demonstrate entry of data 
# records into a Gtk.ListStore, display the records and allow the user to edit
# and delete them. This version does not rely upon glade at all.

from Model import RecordsStore, AddRecordDialog
import os
import shelve
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject #pylint: disable-msg = E0611

class MyData:
    
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("Unsaved Data File")
        self.window.set_resizable(True)
        self.window.set_position(Gtk.WindowPosition.MOUSE)
        self.window.set_accept_focus(True)
        self.window.connect("delete-event", self.on_window_delete)
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.window.add(box)
        win_lab = Gtk.Label("Gtk Data Entry and Display Demo.")
        box.pack_start(win_lab, False, True, 0)
        
        menu_bar = Gtk.MenuBar()
        box.pack_start(menu_bar, False, False, 0)
        menu_bar.set_pack_direction(Gtk.PackDirection.LTR)
        menu_bar.set_visible(True)
        
        file_menu_item = Gtk.MenuItem.new_with_mnemonic("_File")
        file_menu_item.show()
        menu_bar.add(file_menu_item)
        filemenu = Gtk.Menu()
        file_menu_item.set_submenu(filemenu)
        new_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-new")
        new_menu_item.set_use_stock(True)
        new_menu_item.set_always_show_image(True)
        new_menu_item.connect("activate", self.on_new_menu_item_activate)
        filemenu.add(new_menu_item)
        open_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-open")
        open_menu_item.set_use_stock(True)
        open_menu_item.set_always_show_image(True)
        open_menu_item.connect("activate", self.on_open_menu_item_activate)
        filemenu.add(open_menu_item)
        save_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-save")
        save_menu_item.set_use_stock(True)
        save_menu_item.set_always_show_image(True)
        save_menu_item.connect("activate", self.on_save_menu_item_activate)
        filemenu.add(save_menu_item)
        save_as_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-save-as")
        save_as_menu_item.set_use_stock(True)
        save_as_menu_item.set_always_show_image(True)
        save_as_menu_item.connect("activate", self.on_save_as_menu_item_activate)
        filemenu.add(save_as_menu_item)
        menu_separator_item = Gtk.SeparatorMenuItem()
        filemenu.add(menu_separator_item)
        quit_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-quit")
        quit_menu_item.set_use_stock(True)
        quit_menu_item.set_always_show_image(True)
        quit_menu_item.connect("activate", self.on_quit_menu_item_activate)
        filemenu.add(quit_menu_item)
        
        edit_menu_item = Gtk.MenuItem.new_with_mnemonic('_Edit')
        edit_menu_item.show()
        menu_bar.add(edit_menu_item)
        editmenu = Gtk.Menu()
        edit_menu_item.set_submenu(editmenu)
        cut_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-cut")
        cut_menu_item.set_use_stock(True)
        cut_menu_item.set_always_show_image(True)
        cut_menu_item.connect("activate", self.on_cut_menu_item_activate)
        editmenu.add(cut_menu_item)
        copy_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-copy")
        copy_menu_item.set_use_stock(True)
        copy_menu_item.set_always_show_image(True)
        copy_menu_item.connect("activate", self.on_copy_menu_item_activate)
        editmenu.add(copy_menu_item)
        paste_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-paste")
        paste_menu_item.set_use_stock(True)
        paste_menu_item.set_always_show_image(True)
        paste_menu_item.connect("activate", self.on_paste_menu_item_activate)
        editmenu.add(paste_menu_item)
        delete_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-delete")
        delete_menu_item.set_use_stock(True)
        delete_menu_item.set_always_show_image(True)
        delete_menu_item.connect("activate", self.on_delete_menu_item_activate)
        editmenu.add(delete_menu_item)
        
        help_menu_item = Gtk.MenuItem.new_with_mnemonic('_Help')
        help_menu_item.show()
        menu_bar.add(help_menu_item)
        helpmenu = Gtk.Menu()
        help_menu_item.set_submenu(helpmenu)
        about_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-about")
        about_menu_item.set_use_stock(True)
        about_menu_item.set_always_show_image(True)
        about_menu_item.connect("activate", self.on_about_menu_item_activate)
        helpmenu.add(about_menu_item)
        instructions_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-info")
        instructions_menu_item.set_use_stock(True)
        instructions_menu_item.set_always_show_image(True)
        instructions_menu_item.connect("activate", self.on_instructions_menu_item_activate)
        helpmenu.add(instructions_menu_item)
        
        self.treeview = Gtk.TreeView()
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.selection.connect("changed", self.on_selection_changed)
        
        self.adjustment = Gtk.Adjustment(1.0, 1.0, 4.0, 1.0, 4.0, 0.0)
        
        self.treeiter = None
        types = [GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_INT]
        names = ["Project", "Status", "Priority"]
        self.CurrentRecordsStore = RecordsStore(types, names)
        self.treeview.set_model(self.CurrentRecordsStore)
        box.pack_start(self.treeview, True, True, 0)
        
        button_box = Gtk.Box(homogeneous = True, orientation = Gtk.Orientation.HORIZONTAL)
        box.pack_start(button_box, False, False, 0)
        add_record_button = Gtk.Button("_Add Record")
        add_record_button.set_use_underline(True)
        add_record_button.set_focus_on_click(True)
        add_record_button.set_can_focus(True)
        add_record_button.set_can_default(True)
#        add_record_button.set_has_default(True)
        add_record_button.set_receives_default(True)
        add_record_button.connect("clicked", self.on_add_button_clicked)
        button_box.pack_start(add_record_button, False, False, 0)
        
        delete_record_button = Gtk.Button("_Delete Record(s)")
        delete_record_button.set_use_underline(True)
        delete_record_button.connect("clicked", self.on_delete_button_clicked)
        button_box.pack_start(delete_record_button, False, False, 0)
        
        renderer = list()
        
# Create a list of CellRenderers equal to the number of data columns in the
# ListStore so that when data cells get edited, we can detect in which column
# the cell that produced the "edited" signal is found from the "widget" data 
# contained in the "edited" signal. In this program, the assignment of 
# CellRenderers to Columns is constant throughout. The "edited" signal emits 
# a "path" value identifying the row in which the edited cell can be found.

        for i in range(len(names)):
            
# We want to use a SpinButton to edit the numeric data entered into the Priority
# column, so we check for the data type of the column so we can assign the 
# appropriate CellRenderer to it.
            if types[i] == GObject.TYPE_INT:
                renderer.append(Gtk.CellRendererSpin())
                
# Attach the CellRendererSpin to the adjustment holding the data defining the
# SpinButton's behavior.
                
                renderer[i].set_property("adjustment", self.adjustment)
                
# Glade doesn't handle anything about TreeViewColumns or CellRenderers, so we 
# must.The Priority column shouldn't expand, so we set that behavior here, too.
                expand = False
                
# All the other columns receive text and need to expand.
            else:
                renderer.append(Gtk.CellRendererText())
                expand = True
                
            renderer[i].set_property("editable", True)
            renderer[i].connect("edited", self.on_records_edited)
            
# Permanently associate this CellRenderer with the column it's assigned to, 
# which matches the column number in the ListStore. This makes retrieving the 
# CellRenderer from signal and event messages much easier and ensures that any
# reordering of columns in the TreeView will not interfere. the GObject.set_data
# and .get_data methods may be dropped from the next version of PyGtk/PyGObject,
# though, so watch for whatever facility is offered to replace that part of the
# API.           
            
            
            column = Gtk.TreeViewColumn(names[i], renderer[i], text = i)
            renderer[i].set_data("column_obj", column)
            renderer[i].set_data("column_number", i)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_clickable(True)
            column.set_resizable(True)
            column.set_reorderable(True)
            
# These methods identify the column of the ListStore upon whose values the column
# in the treeview should be sorted and that a sort indicator showing sort order
# should be attached to the header when clicked to sort on that column's values.
# No need to have our own handler for the "column clicked" signal - Gtk apparently
# takes care of things behind the scenes.          
            column.set_sort_column_id(i)
            column.set_sort_indicator(True)
            column.set_expand(expand)
            
# Append the column to the TreeView.
            self.treeview.append_column(column)

# Catching the mouse button presses speeds cell selection - no need to click
# once to select the treeview and another couple times to start editing the
# content of a cell. 
            self.treeview.connect("button-press-event", \
                                  self.on_mouse_button_press_event)

# Empty list to hold list of CellRenderers allocated to the treeview columns.
        renderer = list()
        self.disk_file = None
        
        
        
    def on_window_delete(self, widget, event): # pylint: disable-msg = w0613
# Throw up a dialog asking if the user really wants to quit.
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                                Gtk.MessageType.QUESTION, \
                                Gtk.ButtonsType.OK_CANCEL, \
                                "Are you SURE you want to quit?")
        msg.format_secondary_text("We were having SO much fun......")
        response = msg.run()
        if response == Gtk.ResponseType.OK:
# Before quitting, check to see if we have a disk file open; if so, close it and
# only then quit.
            if self.disk_file is not None:
                shelve.Shelf.close(self.disk_file)
            Gtk.main_quit()
        elif response == Gtk.ResponseType.CANCEL:
# If the user doesn't want to quit, just go back to where we were.
            msg.destroy()
            return True
        
    def on_add_button_clicked(self, widget, \
                              fields = {'project':'', 'status': '', \
                                        'priority': 1.0, 'focus': None }): \
                                        # pylint: disable-msg = W0613
                                        
# We pass the ListStore we're using as a parameter to allow for eventual use
# of multiple ListStores.
        
        record = AddRecordDialog(self.CurrentRecordsStore, fields)
# If the user clicked "Cancel" in the Add Record dialog, just do nothing and
# go back to where we were.
        if record == None:
            return
# Check the proposed new record to see if the data are valid - non-empty strings
# for the "Project and Status columns and an integer between 1 and 4 for Priority.
# If there are errors, we again call the Add Record dialog, but with the values,
# if any, the user supplied as the default values and the cursor set in the first
# data entry field that caused the error check to fail.

        elif self.ErrorCheck(0, record['project']):
            record['focus'] = 'project'
            self.on_add_button_clicked(widget, record)
            
        elif self.ErrorCheck(1, record['status']):
            record['focus'] = 'status'
            self.on_add_button_clicked(widget, record)
        
        elif self.ErrorCheck(2, record['priority']):
            record['focus'] = 'priority'
            self.on_add_button_clicked(widget, record)            
        else:
# If the data are valid, append them to the ListStore and, if a disk file is
# open for this ListStore, save the new record to that, too. We're not 
# concerned with sorting and order in these data stores here - just add the
# new record to the end.
            row = [record['project'], record['status'], record['priority']]
            self.CurrentRecordsStore.append(row) # pylint: disable-msg = E1103
            if self.disk_file is not None:
                self.disk_file["store"].append(row)
            record['project'] = ''
            record['status'] = ''
            record['priority'] = 1.0
            record['focus'] = None
            
    def on_records_edited(self, widget, path, text):
        
# The "path"parameter emitted with the signal contains the cell's row number 
# that produced the signal.The widget parameter is the CellRenderer that
# produced the "edited" signal; its column number is carried in the "column
# number" key we associated with it earlier with the set_data() method. We 
# could get the column number from the widget's place in the list of renderers,
# but the approach taken here is more generalized.

        col_num = widget.get_data("column_number")

# The "text" parameter emitted with the "edited" signal is a str representation of 
# the new data the user entered into the edited cell. If the relevant column in the
# ListStore is expecting an int, we need to cast the str as an int. The SpinButton
# used for entry of data in the Priority column ensures that "text" will always be
# a str representation of a double between 1.0 and 4.0, inclusive, so we need only
# cast it as an int - no bounds checking needed here. .               


        if text.isdigit():
            text = int(text)

# Now submit the new, updated data field to a function that checks it for
# invalid values.If the updated record fails the error check, the 
# on_records_edited method returns without changing the existing record; if
# the error check is passed, the updated data field gets written to the
# appropriate row and column in the ListStore. Strangely, using this method's
# path parameter here crashes the program - Python complains it points to a
# StructMeta instead of a Gtk.TreePath. The first element of the
# TreeviewSelection (we're using multiple select here) points to the row
# that's been selected, so we can use that instead. When the CellRenderers
# were created, the column object to which each was attached was associated
# with that CellRenderer using set_data(). We use Get_data now to find the
# column we need. Note that  set_data and get_data may be removed from Gtk
# in the future and replaced with the ability to set_attr and get_attr.


        if self.ErrorCheck(col_num, text):         
            self.treeview.set_cursor_on_cell(self.treeiter[0], \
                                             widget.get_data("column_obj"), \
                                             widget, True)
            self.treeview.grab_focus()
            return

# To store the edited data, we can use the path variable to specify the row for the
# ListStore, but NOT for the shelve disk file! For that, we need an integer index.
# The path actually is nothing but a row number, but it is <type: TreePath>, not an
# int and cannot be used directly. It also cannot be cast directly as an int, but it
# CAN be cast as a str and only THEN cast as the int that's needed. There must be a 
# better way.... We sync() the shelve file immediately, just to make sure all new
# data is written to disk.     
        self.CurrentRecordsStore[path][col_num] = text
        if self.disk_file is not None:
            self.disk_file["store"][int(str(path))][col_num] = text
            self.disk_file.sync()
            
    def on_delete_button_clicked(self, widget): # pylint: disable-msg = W0613
              
# Iterate over a list of pointers to the rows in the TreeView the user has
# selected and, after checking to see that each pointer actually points to a
# row of data, delete the corresponding data record in the ListStore. This has
# to be done in two steps to ensure that we don't try to delete data using an
# iter that doesn't point to anything. We can directly use the TreePath rows
# that the selection's constituent iters point to, but we must perform a
# two-part cast on them to obtain the integer indices needed to deal with any
# shelve disk file that's open. Again, we sync() the disk file immediately to
# ensure all deletions are completed on the disk file.
        for i in [self.CurrentRecordsStore.get_iter(row)\
                   for row in self.treeiter]:# pylint: disable-msg = E1103
            if i is not None:
                self.CurrentRecordsStore.remove(i) # pylint: disable-msg = E1103
                if self.disk_file is not None:
                    del self.disk_file['store'][int(str(row))]
                    self.disk_file.sync()
                
# Shrink the window down to only the size needed to display the remaining
# records. The method invoked below hides the window and reopens it to the size
# needed to contain the visible widgets now contained in it, just as when a
# window is initially opened.
        
        self.window.reshow_with_initial_size()
        
    def on_selection_changed(self, selection):
        
# The TreeViewSelection contains references to the rows in the TreeView the
# user has selected and the ListStore from which the data contained in those
# rows was taken. Note that this code is for multiple selection.
        self.CurrentRecordsStore, self.treeiter = self.selection.get_selected_rows()


    def on_mouse_button_press_event(self, treeview, event):

# Button 1 is the left mouse button (for righties, anyway!) and event.type
# 5 is a 2ButtonPress event, aka a double-click. From the coordinates of the
# button press, we can get the cell's row and TreeViewColumn. We stored the
# CellRendererText for the column TreeViewColumn data field and now retrieve
# it so we can focus the treeview cursor on an individual cell.

        if (event.type == 5) and (event.button == 1):
            x = int(event.x)
            y = int(event.y)
            pathinfo = treeview.get_path_at_pos(x, y)
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.set_cursor_on_cell(path, col, \
                                            col.get_data("column_number"), True)
                treeview.grab_focus()
            return [path, col, col.get_data("column_number"), False]
    
    def on_new_menu_item_activate(self, widget):
# Go back to where we were when the program first opened: close and open
# disk files and wipe the ListStore (and, consequently, the TreeView, clean.
# Change the disk_file to None so we won't try to write to alcose file!
# Change the window title to reflect we're now working on unsaved data.
        if self.disk_file is not None:
            shelve.Shelf.close(self.disk_file)
            self.disk_file = None
        self.CurrentRecordsStore.clear() # pylint: disable-msg: E1103
        self.window.reshow_with_initial_size()
        self.window.set_title("Unsaved Data File")            
    
    def on_open_menu_item_activate(self, Widget):
# First, open a FileChooser dialog in OPEN mode.
        dialog = Gtk.FileChooserDialog("Open File", self.window, \
                                       Gtk.FileChooserAction.OPEN, \
                                       (Gtk.STOCK_CANCEL, \
                                        Gtk.ResponseType.CANCEL, \
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_modal(True)
        dialog.set_local_only(True)
        dat_filter = Gtk.FileFilter()
        dat_filter.set_name(".dat files")
        dat_filter.add_pattern("*.dat")
        dialog.add_filter(dat_filter)
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All files")
        all_filter.add_pattern("*.*")
        dialog.add_filter(all_filter)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
# Before opening a file, close and file we presently have open and wipe
# the ListStore..
            if self.disk_file is not None:
                shelve.Shelf.close(self.disk_file)
                self.CurrentRecordsStore.clear()
            self.disk_file = shelve.open(dialog.get_filename(), writeback = True)
# First, retrieve the 'names' element of the CurrentDataStore
            self.CurrentRecordsStore.names = self.disk_file["names"]
# Now read the record data row-by-row into the CurrentDataStor's 'store' section
            for row in self.disk_file["store"]:
                self.CurrentRecordsStore.append(row) #pylint:disable-msg = E1103
                self.disk_file.sync()
# Change the window title to reflect the file we're now using.
            self.window.set_title(os.path.basename(dialog.get_filename()))
            self.window.reshow_with_initial_size()
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
    
    def on_save_menu_item_activate(self, widget):
# If we have a file open already, just update it.
        if self.disk_file:
            self.disk_file.sync()
        else:
            dialog = Gtk.FileChooserDialog("Save File", self.window, \
                                       Gtk.FileChooserAction.SAVE, \
                                       (Gtk.STOCK_CANCEL, \
                                        Gtk.ResponseType.CANCEL, \
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
            dialog.set_modal(True)
            dialog.set_local_only(True)
            dat_filter = Gtk.FileFilter()
            dat_filter.set_name(".dat files")
            dat_filter.add_pattern("*.dat")
            dialog.add_filter(dat_filter)
            all_filter = Gtk.FileFilter()
            all_filter.set_name("All files")
            all_filter.add_pattern("*.*")
            dialog.add_filter(all_filter)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
# In creating a new disk file, we need only append each row in the
# CurrentRecordsStore to the newly-created 'store' key in the shelve file.
# We're not concerned about ordering and sorting the data stores.
                self.disk_file = shelve.open(dialog.get_filename(),\
                                             writeback = True)
                self.disk_file["names"] = self.CurrentRecordsStore.names
                self.disk_file["store"] = []
                for row in self.CurrentRecordsStore:
                    self.disk_file["store"].append(row[:])
                self.disk_file.sync()
# We're now using a file, so the window title should reflect that.
                self.window.set_title(os.path.basename(dialog.get_filename()))
                dialog.destroy()
            elif response == Gtk.ResponseType.CANCEL:
                dialog.destroy()
        
    def on_save_as_menu_item_activate(self, widget):
        
        dialog = Gtk.FileChooserDialog("Save File As", self.window, \
                                       Gtk.FileChooserAction.SAVE, \
                                       (Gtk.STOCK_CANCEL, \
                                        Gtk.ResponseType.CANCEL, \
                                        Gtk.STOCK_SAVE_AS, Gtk.ResponseType.OK))
        dialog.set_modal(True)
        dialog.set_local_only(True)
        dialog.set_do_overwrite_confirmation(True)
        dat_filter = Gtk.FileFilter()
        dat_filter.set_name(".dat files")
        dat_filter.add_pattern("*.dat")
        dialog.add_filter(dat_filter)
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All files")
        all_filter.add_pattern("*.*")
        dialog.add_filter(all_filter)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
# In creating a new disk file, we need only append each row in the
# CurrentRecordsStore to the newly-created 'store' key in the shelve file.
# We're not concerned about ordering and sorting the data stores.
            self.disk_file = shelve.open(dialog.get_filename(),\
                                        writeback = True)
            self.disk_file["names"] = self.CurrentRecordsStore.names
            self.disk_file["store"] = []
            for row in self.CurrentRecordsStore:
                self.disk_file["store"].append(row[:])
            self.disk_file.sync()
# We're now using a file, so the window title should reflect that.
            self.window.set_title(os.path.basename(dialog.get_filename()))
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
    
    def on_quit_menu_item_activate(self, widget):
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.QUESTION, 
                                Gtk.ButtonsType.OK_CANCEL, 
                                "Are you SURE you want to quit?")
        msg.format_secondary_text("We were having SO much fun......")
        response = msg.run()
        if response == Gtk.ResponseType.OK:
#           if self.disk_file is not None:
# Close any disk file we have open.
#               shelve.Shelf.close(self.disk_file)
            Gtk.main_quit()
        elif response == Gtk.ResponseType.CANCEL:
            msg.destroy()
            return
    
    def on_cut_menu_item_activate(self, widget):
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK, \
                                "Development Update")
        msg.format_secondary_text\
            ("Sorry - Edit menu 'Cut' not yet implemented.")
        msg.run()
        msg.destroy()
    
    def on_copy_menu_item_activate(self, widget):
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK, \
                                "Development Update")
        msg.format_secondary_text\
            ("Sorry - Edit menu 'Copy' not yet implemented.")
        msg.run()
        msg.destroy()
    
    def on_paste_menu_item_activate(self, widget):
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
                                "Development Update")
        msg.format_secondary_text\
            ("Sorry - Edit menu 'Paste' not yet implemented.")
        msg.run()
        msg.destroy()
    
    def on_delete_menu_item_activate(self, widget):
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
                                "Development Update")
        msg.format_secondary_text\
            ("Sorry - Edit menu 'Delete' not yet implemented.")
        msg.run()
        msg.destroy()
    
    def on_about_menu_item_activate(self, widget):
        authors = ["Darron C. Knutson", None]
        copyright_notice = "Copyright 2012, Darron C. Knutson"
        msg = Gtk.AboutDialog()
        msg.set_title("About This Program")
        msg.set_logo(GdkPixbuf.Pixbuf.new_from_file("training_wheels.jpg"))
        msg.set_program_name("Gtk Training Wheels\nData Entry Demo")
        msg.set_version(".001 ... barely!")
        msg.set_copyright(copyright_notice)
        msg.set_comments("A learning experience....\nThanks to Jens C. Knutson for all his help and inspiration.")
        msg.set_license_type(Gtk.License.GPL_3_0)
        msg.set_wrap_license(True)
        msg.set_website("http://www.dknutsonlaw.com")
        msg.set_website_label("www.dknutsonlaw.com")
        msg.set_authors(authors)
        msg.run()
        msg.destroy()
        return
    
    def on_instructions_menu_item_activate(self, widget):
        instructions = "To start, either open a data file or create " + \
        "one by clicking the 'Add Record' button.\n" + \
        "All record fields are mandatory; Priority must be between 1 and 4, inclusive.\n" +\
        "Select records with the mouse and click 'Delete Records'to remove them.\n" +  \
        "Double click on data fields to edit them; hit Enter or Tab to save."
        
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK,\
                                 instructions)
        msg.set_title("Program Instructions")
        msg.run()
        msg.hide()
        
    def ErrorCheck(self, col_num, text):
        if ((col_num == 0) and (len(text) < 1)):
            msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, \
                                    "Invalid or incomplete Project name.")
            msg.set_title("Project Entry Error!")
            msg.run()
            msg.destroy()
            return True
        elif ((col_num == 1) and (len(text) < 1)):
            msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                              Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, \
                              "Invalid or incomplete Status description.")
            msg.set_title("Status Entry Error!")
            msg.run()
            msg.destroy()
            return True
        
# The SpinButton used for the Priority field should prevent entry of
# out-of-bounds values here, but check anyway for the sake of completeness.

        elif (col_num == 2) and ((not isinstance(text, int)) or\
                                  ((text < 1) or (text > 4))):
            msg = Gtk.MessageDialog\
                (self.window, Gtk.DialogFlags.MODAL, \
                Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, \
                "Priority value must be an integer between 1 and 4.")
            msg.set_title("Priority Entry Error!")
            msg.run()
            msg.destroy()
            return True
        else:
            return False
        
if __name__ == "__main__":
    win = MyData()
    win.window.show_all()
    Gtk.main()
        
        
        
        
        
        
        
        
        
        