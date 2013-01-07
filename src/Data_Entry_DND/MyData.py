'''
Main file for demo Gtk data entry, display and edit program,
'''
from Model import add_record_dialog   #@UnresolvedImport
from History import History         #@UnresolvedImport
import os
import shelve
from gi.repository import Gtk       #@UnresolvedImport pylint: disable-msg=E0611
from gi.repository import Gdk       #@UnresolvedImport pylint: disable-msg=E0611
from gi.repository import GdkPixbuf #@UnresolvedImport pylint: disable-msg=E0611
from gi.repository import GObject   #@UnresolvedImport pylint: disable-msg=E0611
from gi.repository import Pango     #@UnresolvedImport pylint: disable-msg=E0611

PROJECT = 0
CONTEXT = 1
PRIORITY = 2
COMPLETED = 3

class MyData:
    """ 
    Main program class - defines elements of the principal 
    program window. Most elements set up in glade.
    """    
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("Data_Entry.glade")
        '''
        Nearly all of the UI elements and their signal connections are defined
        in the Data_Entry.glade file.        
        '''#pylint: disable-msg=W0105
        self.window = builder.get_object("window")
        self.window.set_title("Unsaved Data")
        '''
        Set up treeview to display unsorted data model. Unsorted
        views can be dragged and dropped to change their order.
        Once a view has been sorted, drag'n drop is no longer
        possible, so we have a separate model using a TreeModelSort
        to present a sortable view.
        '''#pylint: disable-msg=W0105
        self.scroller = builder.get_object("scroller")
        '''
        Present the data inside a window with scroll bars.
        Program starts with the unsorted view active - the 
        Glade file makes treeview_dnd scroller's child widget.
        A toggle button allows us to swap in the sortable view.
        '''#pylint: disable-msg=W0105
        self.treeview_dnd = builder.get_object("treeview_dnd")
        project_column = builder.get_object("ProjectColumn")
        project_renderer = builder.get_object("ProjectCellRendererText")
        '''
        Associate each renderer (cell) with its column and column number
        and treeview for ease of use in signal handling.
        '''#pylint: disable-msg=W0105
        project_renderer.column_obj = project_column
        project_renderer.column_number = PROJECT
        project_renderer.tv = self.treeview_dnd
        project_column.tv = self.treeview_dnd
        project_column.set_cell_data_func(project_renderer,
                                           _format_func, 
                                           func_data = None)
        project_column.connect("notify::width", self.on_column_width_changed)
        '''
        Listen to notifications of column width changes to synchronize
        appearance of sorted and unsorted views.
        '''#pylint: disable-msg=W0105
        context_column = builder.get_object("ContextColumn")
        context_renderer = builder.get_object("ContextCellRendererText")
        context_renderer.column_obj = context_column
        context_renderer.column_number = CONTEXT
        context_renderer.tv = self.treeview_dnd
        context_column.set_cell_data_func(context_renderer, 
                                          _format_func, 
                                          func_data = None)
        context_column.tv = self.treeview_dnd
        context_column.connect("notify::width", self.on_column_width_changed)
        priority_column = builder.get_object("PriorityColumn")
        priority_renderer = builder.get_object("PriorityCellRendererSpin")
        priority_renderer.column_obj = priority_column
        priority_renderer.column_number = PRIORITY
        priority_renderer.tv = self.treeview_dnd
        priority_column.set_cell_data_func(priority_renderer, 
                                           _format_func, 
                                           func_data = None)
        priority_column.tv = self.treeview_dnd
        priority_column.connect("notify::width", 
                                self.on_column_width_changed)      
        completed_column = builder.get_object("CompletedColumn")
        completed_renderer = builder.get_object("CompletedCellRendererToggle")
        completed_renderer.column_obj = completed_column
        completed_renderer.column_number = COMPLETED
        completed_renderer.tv = self.treeview_dnd
        completed_column.tv = self.treeview_dnd
        completed_column.connect("notify::width", self.on_column_width_changed)
        '''
        The following item later holds references to the data records the user  
        has selected in the treeview and, by extension, the Gtk.ListStore from 
        which the data in those records were taken.
        '''#pylint: disable-msg=W0105
#        self.selection = builder.get_object("treeview-selection")
        '''
        The ListStore used for in-memory storage and display of the data.
        '''#pylint: disable-msg=W0105
        self.CurrentRecordsStore = builder.get_object("CurrentRecordsStore")
        self.CurrentRecordsStore.names = ["Project", 
                                          "Context", 
                                          "Priority", 
                                          "Completed?"]     
        self.paths_selected = None
        '''
        Reference to list of records selected at any given time. This is 
        generated by the on_selection_changed method, which detects which
        selection (from the sorted or unsorted treeview) was used and converts
        the path references from the sorted view to those needed to manipulate
        the underlying unsorted data model.
        '''#pylint: disable-msg=W0105    
        self.treeview_sort = builder.get_object("treeview_sort")
        '''
        This view presents the records sorted, courtesy of a TreeModelSort.
        '''#pylint: disable-msg=W0105
        project_column_sorted = builder.get_object("ProjectColumnSorted")
        project_sorted_renderer = builder.get_object(
                        "ProjectSortedCellRendererText")
        project_sorted_renderer.column_obj = project_column_sorted
        project_sorted_renderer.column_number = PROJECT
        project_sorted_renderer.tv = self.treeview_sort
        project_column_sorted.set_cell_data_func(project_sorted_renderer, 
                                                 _format_func, 
                                                 func_data = None)
        project_column_sorted.tv = self.treeview_sort
        project_column_sorted.connect("notify::width", 
                                      self.on_column_width_changed)
        context_column_sorted = builder.get_object("ContextColumnSorted")
        context_sorted_renderer = builder.get_object(
                        "ContextSortedCellRendererText")
        context_sorted_renderer.column_obj = context_column_sorted
        context_sorted_renderer.column_number = CONTEXT
        context_sorted_renderer.tv = self.treeview_sort
        context_column_sorted.set_cell_data_func(context_sorted_renderer, 
                                                 _format_func, 
                                                 func_data = None)
        context_column_sorted.tv = self.treeview_sort
        context_column_sorted.connect("notify::width", 
                                      self.on_column_width_changed)
        priority_column_sorted = builder.get_object("PriorityColumnSorted")
        priority_sorted_renderer = builder.get_object(
                        "PrioritySortedCellRendererSpin")
        priority_sorted_renderer.column_obj = priority_column_sorted
        priority_sorted_renderer.column_number = PRIORITY
        priority_sorted_renderer.tv = self.treeview_sort
        priority_column_sorted.set_cell_data_func(priority_sorted_renderer, 
                                                  _format_func, 
                                                  func_data = None)
        priority_column_sorted.tv = self.treeview_sort
        priority_column_sorted.connect("notify::width", 
                                       self.on_column_width_changed)
        completed_column_sorted = builder.get_object("CompletedColumnSorted")
        completed_sorted_renderer = builder.get_object(
                        "CompletedSortedCellRendererToggle")
        completed_sorted_renderer.column_obj = completed_column_sorted
        completed_sorted_renderer.column_number = COMPLETED
        completed_sorted_renderer.tv = self.treeview_sort
        completed_column_sorted.tv = self.treeview_sort
        completed_column_sorted.connect("notify::width", 
                                        self.on_column_width_changed)
        self.sorted_selection = builder.get_object("treeview_sort_selection")
        self.CurrentRecordsStoreSorted = builder.get_object(
                                    "CurrentRecordsStoreSorted")
        
        self.disk_file = None
        '''
        No disk storage of records at program start.
        '''#pylint: disable-msg=W0105
        self.validate_retry = False
        '''
        Flag indicating whether an edit is a retry after an attempt
        to enter invalid data.
        '''#pylint: disable-msg=W0105
        self.invalid_text_for_retry = ""
        '''
        Initialize variable to hold the invalid text attempted to be 
        entered in an earlier unsuccessful edit.
        '''#pylint: disable-msg=W0105
        builder.connect_signals(self)

        targets =   [('MY_TREE_MODEL_ROW', Gtk.TargetFlags.SAME_WIDGET, 1),
                     ('text/plain', Gtk.TargetFlags.SAME_WIDGET, 2),
                     ('TEXT', Gtk.TargetFlags.SAME_WIDGET, 3),
                     ('STRING', Gtk.TargetFlags.SAME_WIDGET, 4)]
        '''
        Targets for drag and drop. Probably redundant, given the use 
        of add_text_targets methods used below.
        '''#pylint: disable-msg=W0105
        self.treeview_dnd.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, 
                                                   targets, 
                                                   Gdk.DragAction.DEFAULT|
                                                   Gdk.DragAction.MOVE)
        self.treeview_dnd.enable_model_drag_dest(targets, Gdk.DragAction.MOVE)
        '''
        Make the unsorted treeview a source and destination for drag and drop.
        '''#pylint: disable-msg=W0105
        self.treeview_dnd.drag_dest_add_text_targets()
        self.treeview_dnd.drag_source_add_text_targets()
        '''
        The previous two methods add text formats compatible with 
        Gtk.SelectionData to the target list for the unsorted treeview. 
        These are the targets that actually get used; as of now, drag 
        and drop won't work without these two methods.
        '''#pylint: disable-msg=W0105
        self.history = History()
        '''
        Add a stack for storing actions that can be undone and redone.
        '''#pylint: disable-msg=W0105    
    def on_window_delete(self, widget, event): # pylint: disable-msg = w0613
        '''
        When the user clicks the 'close window' gadget.
        First check for unsaved data and ask if it should be saved.
        '''
        if not self.disk_file and len(self.CurrentRecordsStore) > 0:
            plural = True if len(self.CurrentRecordsStore) > 1 else False          
            self.save_unsaved(plural)    
        '''
        Throw up a dialog asking if the user really wants to quit.
        '''#pylint: disable-msg=W0105
        msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.QUESTION, 
                                Gtk.ButtonsType.OK_CANCEL, 
                                "Are you SURE you want to quit?")
        msg.format_secondary_text("We were having SO much fun......")
        msg.set_title("Exit Program?")
        response = msg.run()
        if response == Gtk.ResponseType.OK:
            '''
            Before quitting, check to see if we have a disk file open;
            if so, close it and only then quit.
            '''#pylint: disable-msg=W0105
            if self.disk_file:
                shelve.Shelf.close(self.disk_file)
            Gtk.main_quit()
        elif response == Gtk.ResponseType.CANCEL:
            '''
            If the user changes mind and doesn't want to quit, just go back
            to where we were.
            '''#pylint: disable-msg=W0105
            msg.destroy()
            return True

    def on_add_button_clicked(self, widget, fields = None):
        '''
        Method for adding records.
        '''
        if not fields:
            '''
            fields holds any valid values entered in any earlier
            unsuccessful effort to add a new record. Not included
            as a parameter to avoid using the same object in all
            record creations and the side-effects to which that
            could lead. 
            '''#pylint: disable-msg=W0105
            fields = {'project':'',
                      'context': '',
                      'priority': 1.0,
                      'focus': None,
                      'completed': False }
        
        record = add_record_dialog(fields)
        
        if record == None:
            '''
            If the user clicked "Cancel" in the Add Record dialog, just do nothing and
            go back to where we were.
            '''#pylint: disable-msg=W0105
            return
            '''
            Check the proposed new record to see if the data are valid;
            a non-empty string for Project, a string beginning with "@"
            and having at least one additional character for Context, 
            and an integer between 1 and 4 for Priority. If there are  
            errors, we again call the Add Record dialog, but with the  
            values the user supplied as the defaults and the cursor set 
            in the first dataentry field that caused the error check to 
            fail.
            '''#pylint: disable-msg=W0105, W0101
        elif _error_check(PROJECT, record['project']):
            record['focus'] = 'project'
            self.on_add_button_clicked(widget, record)
            
        elif _error_check(CONTEXT, record['context']):
            record['focus'] = 'context'
            self.on_add_button_clicked(widget, record)
        
        elif _error_check(PRIORITY, record['priority']):
            record['focus'] = 'priority'
            self.on_add_button_clicked(widget, record)            
        else:
            '''
            If the data are valid, append them to the ListStore. If a disk
            file is open for this ListStore, the callback for the row_inserted
            signal will add the record to the disk file, so we needn't do that
            here. We're not concerned with sorting and order in the data stores
            here - just add the new record to the end.
            '''#pylint: disable-msg=W0105
            row = [record[x] for x in ['project', 
                                       'context', 
                                       'priority', 
                                       'completed']]
            '''
            Next two functions are the "do" and "undo" for adding a record 
            that get added to the undo/redo history stack.
            '''#pylint: disable-msg=W0105
            perform = (self.CurrentRecordsStore.append, [row])
            revert = (_delete_row, 
                      [self.CurrentRecordsStore, len(self.CurrentRecordsStore)])
            '''
            Normally, the row number to be deleted would be one less than 
            the length of the ListStore to delete the last record because, 
            like lists, ListStore elements are numbered from 0. Here, however, 
            the record hasn't yet been added to the ListStore when we set up 
            our revert function, so the length of the ListStore now is one 
            record shorter than it will be when our revert function gets 
            called. Thus, the row number argument for our revert function 
            must be made one greater than we'd normally use, i.e., the length 
            of the ListStore,not that length minus one.
            '''#pylint: disable-msg=W0105
            self.history.add(perform, revert)
    
    def validation_on_editing_started(self, cell, cell_editable, row):
        '''
        This method gives us access to the Gtk.Entry used by a CellRendererText
        for editing its contents so we can set up the Entry with the invalid
        data the user tried to enter when the program restarts editing after an
        unsuccessful attempt to edit a cell's contents.
        '''
        if self.validate_retry:
            cell.tv.grab_focus()
            if cell.tv.get_model().get_column_type(cell.column_number) == GObject.TYPE_INT:
                self.invalid_text_for_retry = str(self.invalid_text_for_retry)
            cell_editable.set_text(self.invalid_text_for_retry)
            '''
            Reset flag and invalid text variables to their defaults now that 
            we've set up the Gtk.Entry
            '''#pylint: disable-msg=W0105
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
        member tuple of paths, so we subscript the selection to get the path
        parameter needed to obtain the iterator required to fetch the pre-
        existing data for this cell from the model. We don't need to deal with 
        conversions for cells in the sorted tv because the on_selection_changed 
        method takes care of that.
        '''#pylint: disable-msg=W0105
        cell.set_property("text", 
                          self.CurrentRecordsStore.get_value(my_iter, 
                                                            cell.column_number))
        '''
        We associated the number of the column in which each cellrenderer 
        fell with the cellrenderer because of calls like the one immediately
        above.
        '''#pylint: disable-msg=W0105    
    def validation_on_edited(self, cell, path, text):       
        '''        
        The "path" parameter emitted with the signal contains a str reference to
        the row number of the cell that produced the signal.The cell parameter
        is the CellRenderer that produced the "edited" signal; its column number
        is carried in the "column number" key we associated with it earlier. We
        could get the column number from the cell's place in the list of renderers,
        but the approach taken here is more generalized.
        
        The "text" parameter emitted with the "edited" signal is a str representation
        of the new data the user entered into the edited cell. The SpinButton used
        for entry of data in the Priority column ensures that "text" will always be
        a str representation of a double between 1.0 and 4.0, inclusive, so we need to
        cast it as an int do the ListStore will accept it. Bounds checking is still
        needed here also because the user could enter an invalid Priority value from
        the keyboard.
        '''
        if (text.isdigit() and cell.column_number == PRIORITY):
            '''
            Check that this is the Priority Column before casting to an int because the
            Project Column can take numeric values that must be in str format.
            '''#pylint: disable-msg=W0105
            text = int(text)
            '''
            Now submit the new, updated data field to a function that checks it 
            for invalid values.If the updated record fails the error check, the 
            on_records_edited method returns without changing the existing 
            record; if the error check is passed, the updated data field gets 
            written to the appropriate row and column in the ListStore. This  
            method's path parameter is a str representation of a Gtk.TreePath, 
            so we must use that to get a 'real' TreePath object with the "from 
            string" version of the Gtk.TreePath constructor. When the 
            CellRenderers were created, the column object to which each was 
            attached was associated with that CellRenderer. We use that 
            association now to find the column we need.
            '''#pylint: disable-msg=W0105
        if _error_check(cell.column_number, text):
            self.invalid_text_for_retry = text
            self.validate_retry = True
            GObject.idle_add(_restart_edit, cell.tv, path, cell.column_obj)
            '''
            This is a bit of a hack to get around a long-standing bug in Gtk.
            The set_cursor method called in restart_edit destroys the Gtk.Entry
            in which editing had been occurring and causes an "edited" signal
            to be emitted. Without the delay caused by wrapping the set_cursor
            method in the restart_edit method embedded in a call to 
            GObject.idle_add(), however, the "edited" signal gets sent before
            the Entry gets destroyed, breaking the CellRenderer and its 
            connection to the underlying model's data. See www.gtkforums.com/
            viewtopic.php?t=4619 from December 2009! One can click again on the 
            cell and enter a value, but the cell will thereafter ALWAYS display 
            ONLY that value, even when rows or columns get shuffled. 
            GObject.idle_add() makes the call to set_cursor() asynchronously 
            issue from the main loop's thread rather than synchronously, as 
            before.
            '''#pylint: disable-msg=W0105
        else: 
            if cell.tv == self.treeview_sort:
                '''
                Paths to the sorted tv's model must be converted to paths for the "real,"
                unsorted model. Python can accept str representations of a path as Gtk.ListStore
                indices, so no cast to int required, unlike the ordinary Python lists used
                in the shelved disk file.
                '''#pylint: disable-msg=W0105
                path = self.CurrentRecordsStoreSorted.convert_path_to_child_path(
                                Gtk.TreePath.new_from_string(path)).to_string()
            old_text = self.CurrentRecordsStore[path][cell.column_number]
            '''
            The pre-edit text is saved to use in an "undo" and then the "do"
            and "undo" of the edit are pushed onto the undo/redo stack
            '''#pylint: disable-msg=W0105
            perform = (_enter_edit, 
                       [self.CurrentRecordsStore, path, cell, text])
            revert = (_enter_edit, 
                      [self.CurrentRecordsStore, path, cell, old_text])
            self.history.add(perform, revert)

    def on_completed_toggled(self, cell, path):
        '''
        What to do if the user clicks a box in the "Completed?" column. Params sent
        with the "toggled" signal generated by the CellRendererToggle are a
        reference to the CellRendererToggle and a str representation of the path to
        the relevant entry in the ListStore.
        '''
        if cell.tv == self.treeview_sort:
            '''
            Cells in the sorted view need to have path variables converted to paths
            pointing to the same cell in the underlying, unsorted model, in string
            format, not Gtk.TreePath.
            '''#pylint: disable-msg=W0105
            path = self.CurrentRecordsStoreSorted.convert_path_to_child_path(
                                Gtk.TreePath.new_from_string(path)).to_string()
        '''
        The "do" and "undo" actions pushed onto the history stack here are the same:
        Reverse the value stored at the appropriate location in the ListStore. The
        display updates automatically. Note the use of the column_number association
        in the toggle_completed method. 
        '''#pylint: disable-msg=W0105
        perform = (_toggle_cell, [self.CurrentRecordsStore, cell, path])
        revert = (_toggle_cell, [self.CurrentRecordsStore, cell, path])
        self.history.add(perform, revert)                
        
    def on_delete_button_clicked(self, widget):#pylint: disable-msg=W0613
        '''When the use hits the "Delete Records" button '''      
        if not self.paths_selected:
            '''
            No records selected for deletion - do nothing.
            '''#pylint: disable-msg=W0105
            return
        '''
        Two methods for performing multiple deletions have been tried here.
        The first, which has now been commented out, goes as follows:
        Iterate over the list of rows (paths) in the TreeView the user has
        selected, collect a list of TreeRowReferences that will point to
        those rows even after other rows have been deleted from ListStore.
        Check to see if each TreeRowReference still points to a valid row and
        then use the TreeRowReferences to derive the current path of each
        record selected and then delete the corresponding record from the 
        ListStore. If the deletion is made from the sorted TreeView, the 
        "on_selection_changed" method translates those paths to paths to the
        underlying unsorted ListStore. Note that the _delete_row() function
        uses path numbers, not iters, for deleting rows because the iters we
        get when this method first runs may no longer be valid when later
        performing repeated undos and redos, but the path numbers will.
        This forces use of a "stub" _delete_row() function because the
        undo/redo stack expects to receive a function or method call and args,
        but not a statement (such as del) and args.
        
        Note that Gtk.TreePath.get_indices() returns a TUPLE of numbers
        describing the path. Here this should be a single element tuple,
        but we need a simple integer as an index, so we take the single
        ELEMENT of the tuple as our index, not the tuple itself.     
        '''#pylint: disable-msg=W0105
#        for row in [Gtk.TreeRowReference.new(self.CurrentRecordsStore, path) 
#                    for path in self.paths_selected]:
#            if row.get_path():
#                '''check if the RowReference still points to a valid Path '''
#                row_number = row.get_path().get_indices()[0]
#                record = self.CurrentRecordsStore.get_iter(row.get_path())
#                data = [self.CurrentRecordsStore.get_value(record, i) 
#                    for i in range(self.CurrentRecordsStore.get_n_columns())]
#                perform = (_delete_row, [self.CurrentRecordsStore, row_number])
#                revert = (self.CurrentRecordsStore.insert, [row_number, data])
#                self.history.add(perform, revert)
        '''
        The method currently used is similar, but uses iters instead of
        TreeRowReferences.
        '''#pylint: disable-msg=W0105
        for record in [self.CurrentRecordsStore.get_iter(row) 
                       for row in self.paths_selected]:#pylint:disable-msg=E1103
            if record:
                '''
                For each record selected for deletion, first check to see if the iter pointing to
                the record is still valid.
                '''#pylint: disable-msg=W0105
                row_number = int(self.CurrentRecordsStore.get_path(
                                                record).to_string())
                '''
                Get the row number of the record to be deleted for use in "undo"
                '''#pylint: disable-msg=W0105
                data = [self.CurrentRecordsStore.get_value(record, i) 
                        for i in range(self.CurrentRecordsStore.get_n_columns()
                                                                             )]
                '''
                Save the data from each record to be deleted so the deletion 
                can be reverted, if desired. 
                '''#pylint: disable-msg=W0105
                perform = (_delete_row, [self.CurrentRecordsStore, row_number])
                '''
                Perform the deletion
                '''#pylint: disable-msg=W0105
                revert = (self.CurrentRecordsStore.insert, [row_number, data])
                '''
                Provide the function needed to undo the deletion.
                '''#pylint: disable-msg=W0105
                self.history.add(perform, revert)
                '''
                Push the deletion and its reversion onto the undo/redo history 
                stack.
                '''#pylint: disable-msg=W0105
        '''
        The callbacks for the signals generated by row insertion and
        deletion will cause the ListStore's changed state to be written
        to disk and keep the disk file and ListStore consistent. Note
        that the one-to-one relationship between the disk file version
        of the ListStore and the ListStore itself and their simple two-
        dimensional layout means we could use the TreePaths we derive
        from the RowReferences, after converting them to simple integers,
        as indices to the disk_file['store'] data structure that could
        be used here to delete individual records from the disk file.
        The TreePaths contain a str representation of the row number in
        the ListStore of the records they point to. We would have to
        modify the disk file before the ListStore because otherwise the
        RowReferences would get out of sync with the disk file representation
        of the ListStore - the one-to-one relationship would be broken --
        and the program either would delete the wrong record or (more
        likely) crash trying to delete a non-existent row of the
        disk_file['store'] pointed to by an outdated TreePath.
        '''  #pylint: disable-msg=W0105  
    def drag_data_get(self, tv, context, selection, target_id, time):
        '''
        How to get data for dragging and dropping a record.
        '''
        path = self.paths_selected[0]
        '''
        Drag and drop affects only single rows, so we just take the single 
        element of the instance variable that holds the contents of the 
        treeview selection. As noted above, the treeview selection object 
        is set to multiple mode, so a tuple is returned, not a simple value.
        
        First, construct a byte string data object containing the path 
        number of the row to be moved to use as the drag and drop data.
        The actual copying of the row to be moved takes place in the 
        drag_data_received() method - we need only communicate to 
        drag_data_received() the number of the row to be copied from 
        the liststore.
        '''#pylint: disable-msg=W0105
        data = bytes(path.to_string(), "utf-8")
        selection.set(selection.get_target(), 8, data)
        '''
        Finally, set the selection data object to the drag and drop data 
        we've prepared.
        '''#pylint: disable-msg=W0105             
    def drag_data_received(self, tv, context, x, y, selection,  info, time):
        '''
        What to do when a dragged row gets dropped.
        '''
        model = tv.get_model()
        path_string = selection.get_data().decode("utf-8")
        '''
        The Gtk.SelectionData object we packed in drag_data_get gets decoded
        and unpacked into its original form here.
        '''#pylint: disable-msg=W0105
        old_path_number = int(path_string)
        old_path = Gtk.TreePath.new_from_string(path_string)
        '''
        Use the path the treeview row to be moved originally had to track
        where drag and drop data comes from and perform drag and drop and 
        undo/redo.
        '''#pylint: disable-msg=W0105
        drop_info = tv.get_dest_row_at_pos(x, y)
        '''
        If the data are dropped inside existing treeview rows, find where 
        the drop occurred and move the data in the model accordingly; if 
        there's no drop_info, move the data to the end of the model.
        '''#pylint: disable-msg=W0105
        if drop_info:
            target_path, position = drop_info
            target = int(target_path.to_string())
            '''
            Now move the data according to where its representation was 
            dropped and keep track of changes as they're made so 
            undo/redo becomes possible. The moved row isn't part of the 
            DnD data, only the path number pointing to it. The move is 
            made here directly on the liststore by the move_row() method.
            '''#pylint: disable-msg=W0105
            if (position == Gtk.TreeViewDropPosition.BEFORE
                or position == Gtk.TreeViewDropPosition.INTO_OR_BEFORE):                
                '''
                A "before" drop means the new path is always equal to the target value when
                doing the initial move. The ordinal position of the row to be moved and the
                target row in a reversion must be adjusted depending upon which direction the
                original move was in the treeview because of the effect of temporarily inserting
                an additional row and then deleting it.  
                '''  #pylint: disable-msg=W0105             
                perform = (_move_row, [model, old_path, target])
                if(old_path_number < target):
                    revert_path = Gtk.TreePath.new_from_string(str(target-1)) 
                    revert = (_move_row, 
                              [model, revert_path, old_path_number])
                else:
                    revert_path = Gtk.TreePath.new_from_string(str(target))
                    revert = (_move_row, 
                              [model, 
                               revert_path, 
                               old_path_number+1])               
            else:
                '''
                An "after" drop means the position of the new path must be one greater than the
                target for the initial move; the path for a reversion must back out that increment
                if the original row number was less than the new row number. The target for a 
                reversion move must be one greater than the original row number in that case to
                account for the insertion of a row.
                '''#pylint: disable-msg=W0105                
                perform = (_move_row, [model, old_path, target+1])
                if(old_path_number < target):
                    revert_path = Gtk.TreePath.new_from_string(str(target))
                    revert = (_move_row, 
                              [model, 
                               revert_path, 
                               old_path_number])                  
                else:
                    revert_path = Gtk.TreePath.new_from_string(str(target+1))
                    revert = (_move_row, 
                              [model, 
                               revert_path, 
                               old_path_number+1])                      
        else:
            target = len(model)
            revert_path = Gtk.TreePath.new_from_string(str(target-1))
            '''
            The revert path must be one less than the length of the model 
            to correct for the earlier insertion of a new row.
            ''' #pylint: disable-msg=W0105          
            perform = (_move_row, [model, old_path, target])
            revert = (_move_row, [model, revert_path, old_path_number])
        self.history.add(perform, revert)
#    Lines calling upon the DragContext to delete a moved row are commented out
#    because we delete a moved row by hand to more easily accommodate undo/redo
#        if context.get_actions() == Gdk.DragAction.MOVE|Gdk.DragAction.DEFAULT:
#            '''
#            Tell the context in which the drag and drop occurred that the data 
#            in the row that's been moved can be deleted from the row it 
#            originally was in.
#            '''
#            context.finish(True, True, time)
        return   
    
    def on_row_inserted(self, model, path, my_iter):
        '''
        This and the following two methods implement the scheme of keeping the disk
        file and ListStore synchronized by updating the disk_file when the ListStore
        signals a row insertion, change, or deletion. We need listen only to row events
        on the unsorted store because the TreeModelSort guarantees that the sorted
        view will automatically update with the underlying ListStore. Hence, we needn't
        listen for rows-reordered signals, because the ListStore will never be sorted,
        only the TreeModelSort.
        '''
        if self.disk_file:
            '''
            Disk storage is done by shelving a list of lists - disk_file['store']. The path
            parameter tells us where in the list of lists to insert the list representing
            the row that was inserted in the ListStore. This works because the ListStore
            and the disk_file are always in a one-to-one relationship so that the path value
            not only represents the row number in the ListStore, it also works as the index
            for that row in self.disk_file['store']. We construct a list to be inserted into
            the disk file from the values found in the corresponding row of the ListStore.
            '''#pylint: disable-msg=W0105
            row = [model.get_value(my_iter, i) 
                   for i in range(model.get_n_columns())]
            self.disk_file['store'].insert(int(path.to_string()), row)
                        
    def on_row_deleted(self, model, path):
        '''Update the disk file when a record gets deleted. '''
        if self.disk_file:
            '''
            The one-to-one relationship between disk_file and ListStore allows us
            to use the path parameter as an index to the list to be deleted from
            the disk file list of lists when a record is deleted.
            '''#pylint: disable-msg=W0105
            del self.disk_file['store'][int(path.to_string())]
            
    def on_row_changed(self, model, path, my_iter, data = None):
        '''Update the disk file when a record gets edited. '''
        if self.disk_file:
            '''
            Rather than update only the field that's actually been edited, it's much
            easier just to resave the entire record (row). Again, the updated record
            is put into the form of a list constructed from the values found in the
            corresponding row of the ListStore and then written to disk.
            '''#pylint: disable-msg=W0105
            row = [model.get_value(my_iter, i) 
                   for i in range(model.get_n_columns())]
            self.disk_file['store'][int(path.to_string())] = row

    def on_selection_changed(self, selection):        
        '''
        The TreeViewSelection contains references to the rows in the TreeView the
        user has selected and the ListStore from which the data contained in those
        rows was taken. Note that this code is for multiple selection. Records 
        selected from either tv are stored in a single instance variable available
        to all this class' methods; only one tv is active at any time, so only one
        instance variable is required.
        '''
        model, paths_selected = selection.get_selected_rows()
        self.paths_selected = paths_selected if model == self.CurrentRecordsStore \
          else [self.CurrentRecordsStoreSorted.convert_path_to_child_path(path) 
                  for path in paths_selected] 
        '''
        Paths pointing to entries in the sorted tv need to be converted to paths
        pointing to the "real," unsorted data store before they can be acted 
        upon.
        '''#pylint: disable-msg=W0105       
    def on_new_menu_item_activate(self, widget):       
        '''
        Go back to where we were when the program first opened: close and open
        disk files and wipe the ListStore (and, consequently, the TreeView, clean.
        Change the disk_file to None so we won't try to write to a closed file!
        Change the window title to reflect we're now working on unsaved data.
        '''
        if self.disk_file:
            shelve.Shelf.close(self.disk_file)
            self.disk_file = None
        elif len(self.CurrentRecordsStore) > 1:
            self.save_unsaved(plural = True)
        elif len(self.CurrentRecordsStore) > 0:
            self.save_unsaved(plural = False)
        self.CurrentRecordsStore.clear() #pylint: disable-msg=E1103
        self.history = History()
        '''
        Clear undo/redo history from prior operations.
        '''#pylint: disable-msg=W0105
        self.window.reshow_with_initial_size()
        self.window.set_title("Unsaved Data File")            
    
    def on_open_menu_item_activate(self, widget):
        '''
        Open an existing file. First, check to see if there's unsaved data
        and ask the user if he wants to save it.
        '''
        if not self.disk_file and len(self.CurrentRecordsStore) > 0:
            if len(self.CurrentRecordsStore) > 1:
                self.save_unsaved(True)
            else:
                self.save_unsaved(False)
                
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
            try:
                if self.disk_file:
                    shelve.Shelf.close(self.disk_file)
                    self.disk_file = None
                    self.window.set_title("Unsaved Data")
                    '''
                    Before opening a file, close any file we presently have open
                    and wipe the ListStore.
                    '''#pylint: disable-msg=W0105
                self.CurrentRecordsStore.clear()
                self.history = History()
                '''
                Clear undo/redo stack from prior operations
                '''#pylint: disable-msg=W0105
                self.disk_file = shelve.open(dialog.get_filename(),
                                          writeback = True)
                '''
                First, retrieve the 'names' element of the CurrentDataStore
                '''#pylint: disable-msg=W0105
                self.CurrentRecordsStore.names = self.disk_file["names"]
                '''
                Now read the record data row-by-row into the CurrentDataStore.
                Block row_inserted until we're done so we don't rewrite into 
                the disk file and duplicate every row inserted into the 
                ListStore from the disk file.
                '''#pylint: disable-msg=W0105
                GObject.GObject.handler_block_by_func(
                        self.CurrentRecordsStore, self.on_row_inserted)
                for row in self.disk_file["store"]:
                    self.CurrentRecordsStore.append(row)#pylint:disable-msg=E1103
                    self.disk_file.sync()
                GObject.GObject.handler_unblock_by_func(
                    self.CurrentRecordsStore, self.on_row_inserted)
                '''
                Change the window title to reflect the file we're now using.
                '''#pylint: disable-msg=W0105
                self.window.set_title(os.path.basename(dialog.get_filename()))
                
                self.window.reshow_with_initial_size()
            except IOError as inst:
                msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                   "Couldn't open file {0}: {1} error.".format( 
                                   dialog.get_filename(), type(inst)))
                msg.format_secondary_text(inst)
                msg.set_title("File Open Error!")
                msg.run()
                msg.destroy()            
            dialog.destroy()
            self.window.reshow_with_initial_size()
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
                In creating a new disk file, we need only append each row in the
                CurrentRecordsStore to the newly-created 'store' key in the shelve
                file. We're not concerned about ordering and sorting the data stores.
                '''#pylint: disable-msg=W0105
                try:
                    self.disk_file = shelve.open(dialog.get_filename(),
                                                 writeback = True)
                    self.disk_file["names"] = self.CurrentRecordsStore.names
                    self.disk_file["store"] = []
                    for row in self.CurrentRecordsStore:
                        self.disk_file["store"].append(row[:])
                        self.disk_file.sync()
                    '''
                    We're now using a file, so the window title should reflect that.
                    '''#pylint: disable-msg=W0105
                    self.window.set_title(os.path.basename(
                                        dialog.get_filename()))
                    dialog.destroy()
                except IOError as inst:
                    msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                                            Gtk.MessageType.ERROR, 
                                            Gtk.ButtonsType.OK,
                                            "Couldn't save file {0}: {1} error.".format( 
                                            dialog.get_filename(),type(inst)))
                    msg.format_secondary_text(inst)
                    msg.set_title("Error Saving File!")
                    msg.run()
                    msg.destroy()
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
            In creating a new disk file, we need only append each row in the
            CurrentRecordsStore to the newly-created 'store' key in the shelve
            file. We're not concerned about ordering and sorting the data stores.
            '''#pylint: disable-msg=W0105
            try:
                self.disk_file = shelve.open(dialog.get_filename(),
                                             writeback = True)
                self.disk_file["names"] = self.CurrentRecordsStore.names
                self.disk_file["store"] = []
                for row in self.CurrentRecordsStore:
                    self.disk_file["store"].append(row[:])
                self.disk_file.sync()
                '''
                We're now using a file, so the window title should reflect that.
                '''#pylint: disable-msg=W0105
                self.window.set_title(os.path.basename(dialog.get_filename()))
            except IOError as inst:
                msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                                        Gtk.MessageType.ERROR, 
                                        Gtk.ButtonsType.OK,
                                        "Couldn't save file {0}: {1} error.".format( 
                                        dialog.get_filename(),type(inst)))
                msg.format_secondary_text(inst)
                msg.set_title("Error Saving File!")
                msg.run()
                msg.destroy()
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
                
    def on_quit_menu_item_activate(self, widget):
        '''
        Exit the program?
        '''
        self.on_window_delete(widget, None)
        
    def on_undo_menu_item_activate(self, widget):
        '''
        Retrieve an "undo" function and data from the history stack.
        '''
        self.history.undo()
        
    def on_redo_menu_item_activate(self, widget):
        '''
        Retrieve a "do" function and data from the history stack.
        '''
        self.history.redo()
        
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
        msg.set_version(".01 ... barely!")
        msg.set_copyright(copyright_notice)
        msg.set_comments("A learning experience....\n"
                         "Thanks to Jens C. Knutson"
                         " for all his help and inspiration.")
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
        instructions =  '''To start, open a data file or create one by clicking 'Add Record.' All record fields are mandatory; Priority must be between 1 and 4, inclusive, and Context must start with @ and have at least one additional character.
        
Select records with the mouse and click 'Delete Records' to remove them.
        
Double click on data fields to edit them; hit Enter or Tab or click another cell in the chart to save the edited record. Hit Esc or click outside the chart to cancel edits and retrieve the old data.
        
Click on the 'Drag and Drop?' button to switch between a view of the records that can be rearranged by dragging and dropping records and a view that can be sorted in either direction on any field by clicking on the column headers.
        
Use the 'Save' or 'Save As' menuitems to save your entries to a file.
        
Use the Edit Menu or shortcut keys to undo/redo entry or deletion of a record, edits of a record, or any reordering of records done through "Drag and Drop.'''
        msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
                                instructions)
        msg.set_title("Program Instructions")
        msg.run()
        msg.hide()
               
    def save_unsaved(self, plural):
        '''
        Ask user if he'd like to save unsaved data before taking a step that
        will purge unsaved records.
        '''
        txt1 = "You have unsaved data records." if plural else "You have an unsaved data record."
        txt2 = "Do you wish to save them?" if plural else "Do you wish to save it?"

        msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, 
                                Gtk.MessageType.QUESTION, 
                                Gtk.ButtonsType.OK_CANCEL, 
                                txt1)
        msg.format_secondary_text(txt2)
        msg.set_title("Save Unsaved Data?")
        response = msg.run()
        if response == Gtk.ResponseType.OK:
            '''
            If the user chooses to save, call the Save method,
            '''#pylint: disable-msg=W0105
            self.on_save_menu_item_activate(msg)
            msg.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            '''
            If the user chooses not to save, just destroy the Dialog
            and proceed with the task the user originally asked for.
            '''#pylint: disable-msg=W0105
            msg.destroy()
            
    def on_dnd_toggle_button_toggled(self, widget):
        '''
        Toggle the 'Drag'n Drop?' button to switch between unsorted, 
        drag'n drop mode to sorted but no drag'n drop. First check
        what mode we're in now, then swap the treeview contained
        in the scrollable window.
        '''
        if self.scroller.get_child() == self.treeview_dnd:
            self.scroller.remove(self.treeview_dnd)
            self.scroller.add(self.treeview_sort)
        else:
            self.scroller.remove(self.treeview_sort)
            self.scroller.add(self.treeview_dnd)
            
    def on_columns_changed(self, tv, data = None):
        '''
        This method keeps the columns of the sorted and unsorted treeviews
        in the same order when the user changes column order in either
        treeview.
        '''
        other_tv = self.treeview_sort if tv == self.treeview_dnd else self.treeview_dnd
        '''
        First detect which view got its columns rearranged.
        '''#pylint: disable-msg=W0105
        GObject.GObject.handler_block_by_func(tv, self.on_columns_changed)
        GObject.GObject.handler_block_by_func(other_tv, self.on_columns_changed)
        '''
        Block this handler from responding to columns-changed events until it's 
        done processing the change the user made so the changes it makes to the
        "other_tv" columns don't themselves generate attempts to rearrange the
        columns in tv.
        ''' #pylint: disable-msg=W0105   
        for i in range(len(tv.get_columns())-1):
            '''
            Simple sort algorithm using only method available to move existing columns: for
            each column but the last in the changed tv (leader), find the following column
            (follower) and then make the other_tv insert its column with the same title as
            follower after its column with the same title as leader. 
            '''#pylint: disable-msg=W0105
            leader = tv.get_columns()[i].get_title()
            follower = tv.get_columns()[i+1].get_title()
            leader2 = _get_column_by_title(leader, other_tv)
            other_tv.move_column_after(
                _get_column_by_title(follower, other_tv), leader2)
               
        GObject.GObject.handler_unblock_by_func(tv, self.on_columns_changed)
        GObject.GObject.handler_unblock_by_func(
                    other_tv, self.on_columns_changed)
        '''
        Unblock this handler now that its work is done so that it can respond 
        to new column rearrangements.
        '''#pylint: disable-msg=W0105
    def on_column_width_changed(self, col, width):
        '''
        Keep widths of columns the same in both sorted and unsorted views.
        '''
        other_tv = self.treeview_sort if col.tv == self.treeview_dnd else self.treeview_dnd
        '''
        First determine which view had a column width change.
        ''' #pylint: disable-msg=W0105       
        other_col = _get_column_by_title(col.get_title(), other_tv)
        '''
        Find the same column in the other view as the one that's had a 
        width change.
        '''#pylint: disable-msg=W0105
        GObject.GObject.handler_block_by_func(col, self.on_column_width_changed)
        GObject.GObject.handler_block_by_func(other_col, 
                                              self.on_column_width_changed)
        '''
        Disable this method until we're done processing this width change so 
        that the change in the "slave" column doesn't itself invoke this 
        method and make us chase our tails.
        '''#pylint: disable-msg=W0105
        other_col.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        other_col.set_fixed_width(col.get_width())
        '''
        Change sizing of "slave" column to FIXED so we can set it to the
        width of the column that had its width changed by the user.
        '''#pylint: disable-msg=W0105
        GObject.GObject.handler_unblock_by_func(col, 
                                                self.on_column_width_changed)
        GObject.GObject.handler_unblock_by_func(other_col, 
                                                self.on_column_width_changed)

        other_col.set_resizable(True)
        '''
        "Completed?" and "Priority" are fixed width and not resizable
        at program start. A reduction in another column's width can expand
        them, however, if they're the last column in the view because
        Gtk always expands the last column to take up all "extra" room
        in the view. If the user switches the view while one of these
        columns is expanded, its new size will become "fixed" and the
        user will not be able to reduce that width unless the column is
        made resizable. This is a kludgy solution that should be improved.
        '''#pylint: disable-msg=W0105
        return

def _restart_edit(tv, path, col):
    '''
    See comment above call to ErrorCheck in validation_on_edited()
    method. The set_cursor() method causes the treeview to emit the
    "editing-started" signal
    '''#pylint: disable-msg=W0105
    tv.set_cursor(Gtk.TreePath.new_from_string(path), col, True)
    return False
    '''
    Return False so that this method called from idle_add() won't 
    go on running forever.
    '''#pylint: disable-msg=W0105, W0101        

def _error_check(col_num, text):
    '''
    Check proposed input for invalid data. Return True if there's an error,
    False if everything's good.
    '''
    if col_num == PROJECT:
        '''
        If column calls for a string, it cannot be empty
        '''#pylint: disable-msg=W0105
        if not text:
            msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                            "Invalid or incomplete Project entry.\n"  + \
                            "Project Field cannot be blank.")
            msg.set_title("Project Entry Error!")
            msg.run()
            msg.destroy()
            return True
        else:
            return False
    elif col_num == CONTEXT:
        if (len(text) < 2 or not text.startswith('@')):
            msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                            "Invalid or incomplete Context entry.\n" + \
                            "Entry must be at least two characters starting with @")
            msg.set_title("Context Entry Error!")
            msg.run()
            msg.destroy()
            return True
        else:
            return False
            
    elif col_num == PRIORITY:            
        '''
        If column calls for a number, it must be between 1 and 4. The
        Spinbutton and its adjustment should guarantee compliance, but
        we check here because the user could enter an invalid value from
        the keyboard.
        '''#pylint: disable-msg=W0105
        if ((not isinstance(text, int)) or ((text < 1) or (text > 4))):
            msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                "Priority value must be an integer between 1 and 4.")
            msg.set_title("Priority Entry Error!")
            msg.run()
            msg.destroy()
            return True
        else:
            return False
    else:
        msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                            "Unknown Data Entry Error.")
        msg.set_title("Unknown Data Entry Error!")
        msg.run()
        msg.destroy()
        return True

def _enter_edit(liststore, path, cell, text):
    '''
    Function for final entry of edits or undo of edits to specific cells.
    '''
    liststore[path][cell.column_number] = text
    
def _toggle_cell(liststore, cell, path):
    '''
    The "do" and "undo" function for the toggle of the "Completed" column.
    '''
    liststore[path][cell.column_number] = not liststore[path][cell.column_number]

def _delete_row(liststore, row):
    '''
    The function to "do" the deletion of a record.
    '''
    del liststore[row]
    return

def _move_row(model, path, position):
    '''
    Copy liststore data from source row (path arg) to target row position (position arg) and
    then delete the source row - i.e., move the row from source to destination. This is used
    both for drag and drop and to undo DnD.
    '''
    my_iter = model.get_iter(path)
    ''' First copy the data from the source row '''#pylint: disable-msg=W0105
    row = [model.get_value(my_iter, i) for i in range(model.get_n_columns())]
    model.insert(position, row)
    '''
    Insert the data to the target (new) position
    '''#pylint: disable-msg=W0105
    model.remove(my_iter)
    '''
    Finally, delete the source row to complete the move.
    '''#pylint: disable-msg=W0105
            
def _get_column_by_title(title, tv):
    '''
    Given the title of a column in a treeview, return the column object 
    '''
    for column in tv.get_columns():
        if column.get_title() != title:
            continue
        return column
                        
def _format_func(column, cell, model, my_iter, data = None):
    '''
    Function to format cell contents depending upon Priority
    and Completed values.
    '''
    cell.set_property("font", "Sans 12")
    '''
    This font displays clear differences between UltraHeavy,
    Normal, and UltraLight font weights. Check the Priority
    value for each record; 1s get rendered in UltraHeavy, 2s
    and 3s in Normal and 4s in UltraLight weight script.
    '''#pylint: disable-msg=W0105
    if (model.get_value(my_iter, PRIORITY) == 1):
        cell.set_property("weight", Pango.Weight.ULTRAHEAVY)
    elif (model.get_value(my_iter, PRIORITY) == 4):
        cell.set_property("weight", Pango.Weight.ULTRALIGHT)
    else:
        cell.set_property("weight", Pango.Weight.NORMAL)
    if (model.get_value(my_iter, COMPLETED) == True):
        '''
        Records marked Completed (column 3 == True) get strikethrough rendered.
        '''#pylint: disable-msg=W0105
        cell.set_property("strikethrough", True)
    else:
        cell.set_property("strikethrough", False)

if __name__ == "__main__":
    win = MyData()
    win.window.show_all()
    Gtk.main()