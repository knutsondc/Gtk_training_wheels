# Main program control file for this toy project to demonstrate entry of data 
# records into a Gtk.ListStore, display the records and allow the user to edit
# and delete them. This version does not rely upon glade at all.

#from Model import RecordsStore, AddRecordDialog
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
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.window.add(box)
        win_lab = Gtk.Label("Gtk Data Entry and Display Demo - Unsaved Data File.")
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
        new_menu_item.connect("activate", self.on_new_menu_item_activated)
        filemenu.add(new_menu_item)
        open_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-open")
        open_menu_item.set_use_stock(True)
        open_menu_item.set_always_show_image(True)
        open_menu_item.connect("activate", self.on_open_menu_item_activated)
        filemenu.add(open_menu_item)
        save_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-save")
        save_menu_item.set_use_stock(True)
        save_menu_item.set_always_show_image(True)
        save_menu_item.connect("activate", self.on_save_menu_item_activated)
        filemenu.add(save_menu_item)
        save_as_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-save-as")
        save_as_menu_item.set_use_stock(True)
        save_as_menu_item.set_always_show_image(True)
        save_as_menu_item.connect("activate", self.on_save_as_menu_item_activated)
        filemenu.add(save_as_menu_item)
        menu_separator_item = Gtk.SeparatorMenuItem()
        filemenu.add(menu_separator_item)
        quit_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-quit")
        quit_menu_item.set_use_stock(True)
        quit_menu_item.set_always_show_image(True)
        quit_menu_item.connect("activate", self.on_quit_menu_item_activated)
        filemenu.add(quit_menu_item)
        
        edit_menu_item = Gtk.MenuItem.new_with_mnemonic('_Edit')
        edit_menu_item.show()
        menu_bar.add(edit_menu_item)
        editmenu = Gtk.Menu()
        edit_menu_item.set_submenu(editmenu)
        cut_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-cut")
        cut_menu_item.set_use_stock(True)
        cut_menu_item.set_always_show_image(True)
        cut_menu_item.connect("activate", self.on_cut_menu_item_activated)
        editmenu.add(cut_menu_item)
        copy_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-copy")
        copy_menu_item.set_use_stock(True)
        copy_menu_item.set_always_show_image(True)
        copy_menu_item.connect("activate", self.on_copy_menu_item_activated)
        editmenu.add(copy_menu_item)
        paste_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-paste")
        paste_menu_item.set_use_stock(True)
        paste_menu_item.set_always_show_image(True)
        paste_menu_item.connect("activate", self.on_paste_menu_item_activated)
        editmenu.add(paste_menu_item)
        delete_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-delete")
        delete_menu_item.set_use_stock(True)
        delete_menu_item.set_always_show_image(True)
        delete_menu_item.connect("activate", self.on_delete_menu_item_activated)
        editmenu.add(delete_menu_item)
        
        help_menu_item = Gtk.MenuItem.new_with_mnemonic('_Help')
        help_menu_item.show()
        menu_bar.add(help_menu_item)
        helpmenu = Gtk.Menu()
        help_menu_item.set_submenu(helpmenu)
        about_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-about")
        about_menu_item.set_use_stock(True)
        about_menu_item.set_always_show_image(True)
        about_menu_item.connect("activate", self.on_about_menu_item_activated)
        helpmenu.add(about_menu_item)
        instructions_menu_item = Gtk.ImageMenuItem.new_with_mnemonic("gtk-info")
        instructions_menu_item.set_use_stock(True)
        instructions_menu_item.set_always_show_image(True)
        instructions_menu_item.connect("activate", self.on_instructions_menu_item_activated)
        helpmenu.add(instructions_menu_item)

    def on_new_menu_item_activated(self, widget):
        return
    
    def on_open_menu_item_activated(self, widget):
        return
    
    def on_save_menu_item_activated(self, widget):
        return
    
    def on_save_as_menu_item_activated(self, widget):
        return
    
    def on_quit_menu_item_activated(self, widget):
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
    
    def on_cut_menu_item_activated(self, widget):
        return
    
    def on_copy_menu_item_activated(self, widget):
        return
    
    def on_paste_menu_item_activated(self, widget):
        return
    
    def on_delete_menu_item_activated(self, widget):
        return
    
    def on_about_menu_item_activated(self, widget):
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
    
    def on_instructions_menu_item_activated(self, widget):
        instructions = "To start, either open a data file or create " + 
        "one by clicking the 'Add Record' button.\n" + 
        "All record fields are mandatory; Priority must be between 1 and 4, inclusive.\n" + 
        "Select records with the mouse and click 'Delete Records'to remove them.\n" +  
        "Double click on data fields to edit them; hit Enter or Tab to save."
        
        msg = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, \
                                Gtk.MessageType.INFO, Gtk.ButtonsType.OK,\
                                 instructions)
        msg.set_title("Program Instructions")
        msg.run()
        msg.hide()
        
if __name__ == "__main__":
    win = MyData()
    win.window.show_all()
    Gtk.main()
        
        
        
        
        
        
        
        
        
        