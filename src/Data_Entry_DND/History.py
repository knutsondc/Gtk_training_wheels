'''
Simple undo/redo system
'''
class Action(object):
    '''
    Describes an action, and a way to revert that action
    '''
 
    def __init__(self, perform, undo):
        '''
        Both perform and undo are in the form (function, [arg1, arg2, ...]).
        '''
        self._perform = perform
        self._undo = undo
 
    def perform(self):
        '''
        The function to perform or redo an action.
        '''
        fun, args = self._perform
        return fun(*args) #pylint: disable-msg=W0142
 
    def undo(self):
        '''
        The function to undo an action,
        '''
        fun, args = self._undo
        return fun(*args) #pylint: disable-msg=W0142
 
 
class History(object):
    '''Maintains a list of actions that can be undone and redone.'''
 
    def __init__(self):
        self._actions = []
        '''List of actions'''#pylint: disable-msg=W0105
        self._last = -1
        '''
        Marker for the next undoable/redoable action in the list
        '''#pylint: disable-msg=W0105
 
    def _push(self, action):
        '''Add an action to the history list'''
        if self._last < len(self._actions) - 1:
            '''
            Erase previously undone actions whenever a new action
            gets added to the list.
            '''#pylint: disable-msg=W0105
            del self._actions[self._last + 1:]
        self._actions.append(action)
        '''
        Actually add the new action to the history list
        '''#pylint: disable-msg=W0105
        self._last += 1
        '''
        Update marker to point to the newly added action
        '''#pylint: disable-msg=W0105
 
    def undo(self):
        '''
        Returns the function needed to undo an action.
        '''
        if self._last < 0:
            '''No actions left to undo '''#pylint: disable-msg=W0105
            return None
        else:
            action = self._actions[self._last]
            '''
            Fetch next undoable action in the history list
            '''#pylint: disable-msg=W0105
            self._last -= 1
            '''
            Move the marker to the next earlier undoable action in the list
            '''#pylint: disable-msg=W0105
            return action.undo()
            '''
            Return the undo function and args to the caller
            '''#pylint: disable-msg=W0105, W0101
 
    def redo(self):
        '''
        Returns the function needed to redo an undone action.
        '''
        if self._last == len(self._actions) - 1:
            '''No undone actions left to redo'''#pylint: disable-msg=W0105
            return None
        else:
            self._last += 1
            '''
            Move marker to the next redoable action in the list
            '''#pylint: disable-msg=W0105
            action = self._actions[self._last]
            return action.perform()
            '''
            Return the perform function and args to the caller
            '''#pylint: disable-msg=W0105, W0101
 
    def add(self, perform, undo):
        """Adds a new action to the history list and then does it.
 
        Both perform and undo are in the form (function, [arg1, arg2, ...]).
 
        """
        action = Action(perform, undo)
        self._push(action)
        return action.perform()