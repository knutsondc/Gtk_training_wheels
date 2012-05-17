'''
Created on May 16, 2012

@author: dck
'''
# Subclass extending the Gtk.TreeViewColumn class

from gi.repository import Gtk # pylint: disable-msg = E0611

class TaggedColumn(Gtk.TreeViewColumn):

    def __init__(self, title, renderer, col_num, **kwargs):
    
        Gtk.TreeViewColumn(TaggedColumn, self).__init__(title, renderer, **kwargs)
        self.title = title
        self.renderer = renderer
        self.col_num = col_num

        