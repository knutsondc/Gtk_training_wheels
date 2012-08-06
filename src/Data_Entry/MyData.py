""" 
Main program control file for this toy project to demonstrate entry of data 
records into a Gtk.ListStore, display the records and allow the user to edit
and delete them. This version relies upon a glade .xml file for several major
user interface windows and dialogs.
"""

from Model import RecordsStore, AddRecordDialog #@UnresolvedImport
import os
import shelve
from gi.repository import Gtk       #@UnresolvedImport pylint: disable-msg=E0611
from gi.repository import GdkPixbuf #@UnresolvedImport pylint: disable-msg=E0611
from gi.repository import GObject   #@UnresolvedImport pylint: disable-msg=E0611

class MyData:
    """ 
    Main program class - defines elements of the principal 
    program window. Most elements set up in glade.
    """ 
    
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("Data_Entry.glade")
        self.window = builder.get_object("window")
        self.window.set_title("Unsaved Data File")
        '''
        Nearly all of the UI elements and their signal connections are defined
        in the MyData.glade file, but the Gtk.TreeView widget to display the data
        records is not. It follows here:
        '''
        self.treeview = builder.get_object("treeview")
        '''
        The following item later holds references to the data records the user has 
        selected in the treeview and, by extension, the Gtk.ListStore from which
        the data in those records were taken.
        '''
        self.selection = builder.get_object("treeview-selection")
        '''
        Make sure that the reference to selected records is empty at program start
        '''
        self.paths_selected = None
        '''
        No disk storage of records at program start.
        '''
        self.disk_file = None        
        
        builder.connect_signals(self)
        '''
        Eventually the following three lines setting up a fixed three-field 
        RecordsStore will be replaced with code offering the user the choice of
        opening an existing RecordsStore or creating a new one with a user-set
        number and type of data fields (columns).
        '''
        types = [GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_INT]
        names = ["Project", "Status", "Priority"]
        self.CurrentRecordsStore = RecordsStore(types, names)
        '''
        Tell the TreeView from where to get its data to display.
        '''
        self.treeview.set_model(self.CurrentRecordsStore)

        self.renderer = list()
        '''
        Create a list of CellRenderers equal to the number of data columns in the
        ListStore so that when data cells get edited, we can detect in which column
        the cell that produced the "edited" signal is found from the "widget" data 
        contained in the "edited" signal. In this program, the assignment of 
        CellRenderers to Columns is constant throughout. The "edited" signal emits 
        a "path" value identifying the row in which the edited cell can be found.
        '''
        for i in range(len(names)):
            '''
            We want to use a SpinButton to edit the numeric data entered
            into the Priority column, so we check for the data type of
            the column so we can assign the appropriate CellRenderer to it.
            '''    
            if types[i] == GObject.TYPE_INT:
                self.renderer.append(Gtk.CellRendererSpin())
                '''
                Attach the CellRendererSpin to the adjustment holding the
                data defining the SpinButton's behavior. Adjustment object
                holds the info defining the SpinButton used to enter
                'Priority' values: current value, minimum, maximum, step,
                page increment, and page size.
                '''
                self.renderer[i].set_property("adjustment", 
                                         Gtk.Adjustment(1.0, 1.0, 4.0, 1.0, 4.0, 0.0))
                
                '''
                Glade doesn't handle anything about TreeViewColumns or
                CellRenderers, so we must.The Priority column shouldn't
                expand, so we set that behavior here, too.
                '''
                expand = False
            else:
                self.renderer.append(Gtk.CellRendererText())
                '''All the other columns receive text and need to expand.'''
                expand = True
                
            self.renderer[i].set_property("editable", True)
            self.renderer[i].connect("editing-started", self.validation_on_editing_started)
            self.renderer[i].connect("editing-canceled", self.validation_on_editing_cancelled)
            self.renderer[i].connect("edited", self.validation_on_edited)
            column = Gtk.TreeViewColumn(names[i], self.renderer[i], text = i)

            '''
            Permanently associate this CellRenderer with the column it's
            assigned to, which matches the column number in the ListStore.
            This makes retrieving the CellRenderer from signal and event
            messages much easier and ensures that any reordering of columns
            in the TreeView will not interfere. the GObject.set_data and
            .get_data methods may be dropped from the next version of
            PyGtk/PyGObject, though, so watch for whatever facility is
            offered to replace that part of the API.    
            '''
            self.renderer[i].set_data("column_obj", column)
            self.renderer[i].set_data("column_number", i)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_clickable(True)
            column.set_resizable(True)
            column.set_reorderable(True)
            '''
            These methods identify the column of the ListStore upon whose
            values the column in the treeview should be sorted and that a
            sort indicator showing sort order should be attached to the 
            header when clicked to sort on that column's values. No need to
            have our own handler for the "column clicked" signal - Gtk
            apparently takes care of things behind the scenes. 
            '''
            column.set_sort_column_id(i)
            column.set_sort_indicator(True)
            column.set_expand(expand)
            
            '''Append the column to the TreeView so it will be displayed.'''
            self.treeview.append_column(column)
            '''
            Catching the mouse button presses speeds cell selection - no
            need to click once to select the treeview and another couple
            times to start editing the content of a cell. 
            '''
            self.disk_file = None
            self.validate_retry = False
            '''
            Flag indicating whether an edit is a retry after an attempt
            to enter invalid data.
            '''
            self.invalid_text_for_retry = ""
            '''
            Initialize variable to hold the invalid text attempted to be 
            entered in an earlier unsuccessful edit.
            '''
           
    def on_window_delete(self, widget, event): # pylint: disable-msg = w0613
        """When the user clicks the 'close window' gadget. """
        '''
        First check for unsaved data and ask if it should be saved.
        '''
        if not self.disk_file:
            if len(self.CurrentRecordsStore) > 1:
                self.save_unsaved(plural = True)
            elif len(self.CurrentRecordsStore) > 0:
                self.save_unsaved(plural = False)
        
        '''Throw up a dialog asking if the user really wants to quit.'''
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.QUESTION, 
                                Gtk.ButtonsType.OK_CANCEL, 
                                "Are you SURE you want to quit?")
        msg.format_secondary_text("We were having SO much fun......")
        response = msg.run()
        if response == Gtk.ResponseType.OK:
            '''
            Before quitting, check to see if we have a disk file open;
            if so, close it and only then quit.
            '''
            if self.disk_file:
                shelve.Shelf.close(self.disk_file)
            Gtk.main_quit()
        elif response == Gtk.ResponseType.CANCEL:
            '''
            If the user changes mind and doesn't want to quit, just go back
            to where we were.
            '''
            msg.destroy()
            return True
    
    def on_add_button_clicked(self, widget, fields = None):
        '''
        Method for adding records. We pass the ListStore we're using as
        a parameter to allow for eventual use of multiple ListStores. The
        fields param holds valid values the user enters in incomplete, invalid
        entries for use in subsequent passes through this method.
        ''' 
        if not fields:
            fields = {'project':'',
                      'status': '', 
                      'priority': 1.0,
                      'focus': None }
        
        record = AddRecordDialog(self.CurrentRecordsStore, fields)
        
        if record == None:
            '''
            If the user clicked "Cancel" in the Add Record dialog, just do
            nothing and go back to where we were.
            '''
            return
            '''
            Check the proposed new record to see if the data are
            valid - non-empty strings for the Project and Status columns
            and an integer from 1 to 4 for Priority. If there are errors,
            we again call the Add Record dialog, but with the values, if
            any, the user supplied as the default values and the cursor
            set in the first data entry field that caused the error check
            to fail.
            '''
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
            '''
            If the data are valid, append them to the ListStore and,
            if a disk file is open for this ListStore, save the new
            record to that, too. We're not concerned with sorting and
            order in these data stores here - just add the new record
            to the end.
            '''
            row = [record['project'], record['status'], record['priority']]
            self.CurrentRecordsStore.append(row) # pylint: disable-msg = E1103
            if self.disk_file:
                self.disk_file["store"].append(row)
                
# The commented out method below caught Tab key presses and made sure they got
# handled the same as Enter key strokes. Now not necessary as the restart_editing()
# method fixed the problem with Tab entries and mouse clicks outside a cell getting
# edited.

#    def on_keypress_event(self, widget, event, data = None):
#        if Gdk.keyval_name(event.keyval) == 'Tab':
#            widget.activate()
#            return True
                            
# The commented out method below is a simple function to use with a renderer's set_data_func() method
# to display the bare data in the ListStore/model.

#    def validation_on_cell_data(self, column, cell_renderer, tree_model, my_iter, user_data = None):
#        value = tree_model.get_value(my_iter, cell_renderer.get_data("column_number"))
#        cell_renderer.set_property("text", value)
                  
    def validation_on_editing_started(self, cell, cell_editable, row):
        '''
        This method gives us access to the Gtk.Entry used by a CellRendererText
        for editing its contents so we can set up the Entry with the invalid
        data the user tried to enter when the program restarts editing after an
        unsuccessful attempt to edit a cell's contents.
        '''
#        cell_editable.connect("key-press-event", self.on_keypress_event)
        if self.validate_retry:
            self.treeview.grab_focus()
            self.edit_entry = cell_editable
            if self.CurrentRecordsStore.get_column_type(cell.get_data("column_number")) == GObject.TYPE_INT:
                self.invalid_text_for_retry = str(self.invalid_text_for_retry)
            self.edit_entry.set_text(self.invalid_text_for_retry)
            self.validate_retry = False
            self.invalid_text_for_retry = ""

    def validation_on_editing_cancelled(self, cell, data = None):
        '''
        Should the user cancel editing by hitting Esc or clicking outside the
        treeview, this method will restore the cell's value to what it was before
        the editing began.
        '''
        my_iter = self.CurrentRecordsStore.get_iter(self.paths_selected[0])
        '''
        The treeview's selection mode is set to MULTIPLE, but if we're editing a
        cell, only a single row will have been selected. This gives us a single-
        member list of paths. so we subscript the selection to get the path
        parameter needed to obtain the iterator required to fetch the preexisting
        data for this cell from the model.
        '''
        col_num = cell.get_data("column_number")
        cell.set_property("text", self.CurrentRecordsStore.get_value(my_iter, col_num))
              
    def validation_on_edited(self, cell, path, text):       
        '''        
        The "path" parameter emitted with the signal contains a str reference to
        the row number of the cell that produced the signal.The widget parameter
        is the CellRenderer that produced the "edited" signal; its column number
        is carried in the "column number" key we associated with it earlier with
        the set_data() method. We could get the column number from the widget's
        place in the list of renderers, but the approach taken here is more
        generalized.
        '''
        col_num = cell.get_data("column_number")
        '''
        The "text" parameter emitted with the "edited" signal is a str representation
        of the new data the user entered into the edited cell. If the relevant column 
        in the ListStore is expecting an int, we need to cast the str as an int. The
        SpinButton used for entry of data in the Priority column ensures that "text"
        will always be a str representation of a double between 1.0 and 4.0,
        inclusive, so we need only cast it as an int - no bounds checking needed
        here.
        '''
        if text.isdigit():
            text = int(text)
            '''
            Now submit the new, updated data field to a function that checks it for
            invalid values.If the updated record fails the error check, the 
            on_records_edited method returns without changing the existing record; if
            the error check is passed, the updated data field gets written to the
            appropriate row and column in the ListStore. This method's path 
            parameter is a str representation of a Gtk.TreePath, so we must use
            that to get a 'real' TreePath object with the "from string" version of
            the Gtk.TreePath constructor. When the CellRenderers were created, the
            column object to which each was attached was associated with that
            CellRenderer using set_data(). We use Get_data now to find the
            column we need. Note that  set_data and get_data may be removed from Gtk
            in the future and replaced with the ability to set_attr and get_attr.
            '''
        if self.ErrorCheck(col_num, text):
            self.invalid_text_for_retry = text
            self.validate_retry = True
            GObject.idle_add(self.restart_edit, path, cell.get_data("column_obj"))
            '''
            This is a bit of a hack to get around a long-standing bug in Gtk.
            The set_cursor method called in restart_edit destroys the Gtk.Entry
            in which editing had been occurring and causes an "edited" signal
            to be emitted. Without the delay caused by wrapping the set_cursor
            method in the restart_edit method embedded in a call to 
            GObject.idle_add(), however, the "edited" signal gets sent before
            the Entry gets destroyed, breaking the CellRenderer and its connection
            to the underlying model's data. See www.gtkforums.com/viewtopic.php?t=4619
            from December 2009! One can click again on the cell and enter a value,
            but the cell will thereafter ALWAYS display ONLY that value, even when
            rows or columns get shuffled. GObject.idle_add() makes the call to
            set_cursor() asynchronously issue from the main loop's thread rather than
            synchronously, as before.
            '''
#            self.treeview.set_cursor(Gtk.TreePath.new_from_string(path),
#                                             cell.get_data("column_obj"),
#                                             True)         
        else:
            '''
        To store the edited data, we can use the path variable to specify the row 
        for the ListStore, but NOT for the shelve disk file! For that, we need an
        integer index. Here, the path actually is nothing but a row number, but it
        is a str, not an int and cannot be used directly. It can be cast as the int 
        that's needed. We sync() the shelve file immediately, just to make sure all 
        new data is written safely to disk.
            '''
            self.CurrentRecordsStore[path][col_num] = text
            if self.disk_file:
                self.disk_file["store"][int(path)][col_num] = text
                self.disk_file.sync()
            
    def restart_edit(self, path, col):
        '''
        See comment above call to ErrorCheck in validation_on_edited()
        method.
        '''
        self.treeview.set_cursor(Gtk.TreePath.new_from_string(path),
                                             col,
                                             True)
        return False
        '''
        Return False so that this method won't go on running forever.
        '''    
    def on_delete_button_clicked(self, widget): # pylint: disable-msg = W0613
        
        '''
        Iterate over the list of rows (paths) in the TreeView the user has
        selected, collect a list of TreeRowReferences that will point to
        those rows even after other rows have been deleted from ListStore.
        Check to see if each TreeRowReference still points to a valid row and
        then use the TreeRowReferences to derive the current path of each
        record selected and use that to derive the current row number of
        each record selected for use as the index to delete the disk file
        copy (if any) of the selected record and then delete the corres-
        ponding record from the ListStore. Again, we sync() the
        disk file immediately to ensure all deletions are written to the
        disk file.
        
        Note that this could be done with iters on the ListStore - see
        commented out code below -- but the disk file can be done practically
        only using rows and paths. We'd have to convert the iters back to
        paths, so why not just use paths in the first place?
        '''
        for row in [Gtk.TreeRowReference.new(self.CurrentRecordsStore, path)
                    for path in self.paths_selected]:
            if row.get_path():
                '''check if the RowReference still points to a valid Path '''
                if self.disk_file:
                    del self.disk_file['store'][row.get_path().get_indices()[0]]
                    '''
                    The one-to-one relationship between the disk file version
                    of the ListStore and the ListStore itself and their simple
                    two-dimensional layout means we can use the TreePaths we
                    derive from the RowReferences, after converting them to
                    simple integers, as indices to the disk_file['store'] data
                    structure. The TreePaths contain a str representation of the
                    row number in the ListStore of the records they point to.
                    We have to modify the disk file first because otherwise the
                    RowReferences would get out of sync with the disk file
                    representation of the ListStore - the one-to-one
                    relationship gets broken -- and the program either would 
                    delete the wrong record or (more likely) crash trying to
                    delete a non-existent row of the disk_File['store'] pointed
                    to by an outdated TreePath..
                    
                    Note that Gtk.TreePath.get_indices() returns a LIST of
                    numbers describing the path. Here this should be a single 
                    element list, but we need a simple integer as an index, so
                    we take the single ELEMENT of the list as our index, not 
                    the list itself.
                    '''
                    self.disk_file.sync()
                    '''
                    Now that the record has been deleted from the disk_file,
                    we can delete the record from the disk_store and restore
                    the one-to-one relationship between the ListStore and the
                    disk_file representation of it in disk_file['store'].
                    '''
                del self.CurrentRecordsStore[row.get_path().get_indices()[0]]
        '''
        Delete method using iters on the ListStore:
               
        for i in [self.CurrentRecordsStore.get_iter(row)
         for row in self.paths_selected]: #pylint: disable-msg = E1103
            if i:
                if self.disk_file:                    
                    del self.disk_file["store"
                        ][self.CurrentRecordsStore.get_path(i).get_indices(
                        )[0]]
                    self.disk_file.sync()
                self.CurrentRecordsStore.remove(i) #pylint: disable-msg=E1103
        '''
        '''
        Shrink the window down to only the size needed to display the remaining
        records. The method invoked below hides the window and reopens it to the
        size needed to contain the visible widgets now contained in it, just as
        when a window is initially opened.
        '''
        
        self.window.reshow_with_initial_size()
        
    def on_selection_changed(self, selection):        
        '''
        The TreeViewSelection contains references to the rows in the TreeView the
        user has selected and the ListStore from which the data contained in those
        rows was taken. Note that this code is for multiple selection.
        '''
        self.CurrentRecordsStore, self.paths_selected = \
         self.selection.get_selected_rows()
                
    def on_new_menu_item_activate(self, widget):
        '''
        Go back to where we were when the program first opened: close any open
        disk files; otherwise check for unsaved data,  ask user if he wishes
        to save it, and save to disk if he does. Then wipe the ListStore (and,
        consequently, the TreeView, clean. Change the disk_file to None so we
        won't try to write to a closed file! Change the window title to reflect
        we're now working on unsaved data.
        '''
        if self.disk_file:
            shelve.Shelf.close(self.disk_file)
            self.disk_file = None
        elif len(self.CurrentRecordsStore) > 1:
            self.save_unsaved(plural = True)
        elif len(self.CurrentRecordsStore) > 0:
            self.save_unsaved(plural = False)
        self.CurrentRecordsStore.clear() # pylint: disable-msg=E1103
        self.window.reshow_with_initial_size()
        self.window.set_title("Unsaved Data File")            

    def on_open_menu_item_activate(self, widget):
        '''
        Open an existing file. First, check for unsaved data.
        '''
        if not self.disk_file:
            if len(self.CurrentRecordsStore) > 1:
                self.save_unsaved(plural = True)
            elif len(self.CurrentRecordsStore) > 0:
                self.save_unsaved(plural = False)
        dialog = Gtk.FileChooserDialog("Open File", self.window, 
                                       Gtk.FileChooserAction.OPEN, 
                                       (Gtk.STOCK_CANCEL, 
                                        Gtk.ResponseType.CANCEL, 
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
            '''
            Before opening a file, close any file we presently have open
            and wipe the ListStore..
            '''
            if self.disk_file:
                shelve.Shelf.close(self.disk_file)
                self.CurrentRecordsStore.clear() #pylint: disable-msg = E1103
            self.disk_file = shelve.open(dialog.get_filename(), writeback = True)
            '''First, retrieve the 'names' element of the CurrentDataStore'''
            self.CurrentRecordsStore.names = self.disk_file["names"]
            '''
            Now read the record data row-by-row into the CurrentDataStore's
            'store' section
            '''
            for row in self.disk_file["store"]:
                self.CurrentRecordsStore.append(row) #pylint:disable-msg = E1103
                self.disk_file.sync()
            '''Change the window title to reflect the file we're now using.'''
            self.window.set_title(os.path.basename(dialog.get_filename()))
            self.window.reshow_with_initial_size()
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def on_save_menu_item_activate(self, widget):
        '''
        If we have a file open already, just update it.
        '''
        if self.disk_file:
            self.disk_file.sync()
        else:
            dialog = Gtk.FileChooserDialog("Save File", self.window, 
                                       Gtk.FileChooserAction.SAVE, 
                                       (Gtk.STOCK_CANCEL, 
                                        Gtk.ResponseType.CANCEL, 
                                        Gtk.STOCK_SAVE, 
                                        Gtk.ResponseType.OK))
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
                '''
                In creating a new disk file, we need only append each row 
                in the CurrentRecordsStore to the newly-created 'store' key
                in the shelve file.We're not concerned about ordering and
                sorting the data stores.
                '''
                self.disk_file = shelve.open(dialog.get_filename(), 
                                             writeback = True)
                self.disk_file["names"] = self.CurrentRecordsStore.names
                self.disk_file["store"] = []
                for row in self.CurrentRecordsStore:
                    self.disk_file["store"].append(row[:])
                self.disk_file.sync()
                '''We're now using a file, so the window title should reflect that.'''
                self.window.set_title(os.path.basename(dialog.get_filename()))
                dialog.destroy()
            elif response == Gtk.ResponseType.CANCEL:
                dialog.destroy()
        
    def on_save_as_menu_item_activate(self, widget):
        '''
        Save an existing file under a different name.
        '''
        
        dialog = Gtk.FileChooserDialog("Save File As", self.window, 
                                       Gtk.FileChooserAction.SAVE, 
                                       (Gtk.STOCK_CANCEL, 
                                        Gtk.ResponseType.CANCEL, 
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
            '''
            In creating a new disk file, we need only append each row
            in the CurrentRecordsStore to the newly-created 'store' 
            key in the shelve file. We're not concerned about ordering
            and sorting the data stores.
            '''
            self.disk_file = shelve.open(dialog.get_filename(), 
                                        writeback = True)
            self.disk_file["names"] = self.CurrentRecordsStore.names
            self.disk_file["store"] = []
            for row in self.CurrentRecordsStore:
                self.disk_file["store"].append(row[:])
            self.disk_file.sync()
            '''We're now using a file, so the window title should reflect that.'''
            self.window.set_title(os.path.basename(dialog.get_filename()))
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
                
    def on_quit_menu_item_activate(self, widget):
        '''
        Exit the program?
        '''
        self.on_window_delete(widget, None)
    '''
    Edit menu removed - the Gnome Desktop clipboard already supplies all the
    intended functions.
    '''
        
    def on_about_menu_item_activate(self, widget):
        '''
        Tell the user about the program using Gtk's built-in "About" Dialog.
        '''
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
        msg.hide()
        return
        
    def on_instructions_menu_item_activate(self, widget):
        '''
        Tell the user how to use the program.
        '''
        instructions = "To start, either open a data file or create one" + \
        " by clicking 'Add Record.'\n All record fields are mandatory;" + \
        "Priority must be between 1 and 4,\ninclusive. Select records" + \
        " with the mouse and click 'Delete Records'\nor select the " + \
        "'Delete' menu item to remove them. Double click on\ndata fields" + \
        " to edit them; hit Enter or Tab to save the edited record.\nUse" + \
        " the 'Save' or 'Save As' menuitems to save your entries to a file."
        
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
                                instructions)
        msg.set_title("Program Instructions")
        msg.run()
        msg.hide()
        
    def ErrorCheck(self, col_num, text):
        '''
        Check proposed input for invalid data. Return True if there's an error,
        False if everything's good.
        '''
        if self.CurrentRecordsStore.get_column_type( #pylint: disable-msg=E1103
                col_num) == GObject.TYPE_STRING:
            '''If column calls for a string, it cannot be empty '''
            if not text:
                msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL,
                                Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                "Invalid or incomplete %s entry." % 
                                self.CurrentRecordsStore.names[col_num])
                msg.set_title("%s Entry Error!" % self.CurrentRecordsStore.names[col_num])
                msg.run()
                msg.destroy()
                return True
            else:
                return False
        elif self.CurrentRecordsStore.get_column_type(#pylint: disable-msg=E1103
                col_num) == GObject.TYPE_INT:
            '''
            If column calls for a number, it must be between 1 and 4. The
            Spinbutton and its adjustment should guarantee compliance, but
            we check here for the sake of completeness.
            '''
            if ((not isinstance(text, int)) or ((text < 1) or (text > 4))):
                msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                    "Priority value must be an integer between 1 and 4.")
                msg.set_title("Priority Entry Error!")
                msg.run()
                msg.destroy()
                return True
            else:
                return False
        else:
            msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL,
                                Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                "Unknown Data Type Entered.")
            msg.set_title("Unknown Data Type Error!")
            msg.run()
            msg.destroy()
            return True
        
    def save_unsaved(self, plural):
        '''
        Ask user if he'd like to save unsaved data before taking a step that
        will purge unsaved records.
        '''
        if plural:
            txt1 = "You have unsaved data records."
            txt2 = "Do you wish to save them?"
        else:
            txt1 = "You have an unsaved data record."
            txt2 = "Do you wish to save it?"
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.QUESTION, 
                                Gtk.ButtonsType.OK_CANCEL, 
                                txt1)
        msg.format_secondary_text(txt2)
        response = msg.run()
        if response == Gtk.ResponseType.OK:
            '''
            If the user chooses to save, call the Save method,
            '''
            self.on_save_menu_item_activate()
            msg.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            '''
            If the user chooses not to save, just destroy the Dialog
            and proceed with the task the user originally asked for.
            '''
            msg.destroy()
if __name__ == "__main__":
    win = MyData()
    win.window.show_all()
    Gtk.main()
