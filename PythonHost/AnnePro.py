from superkeys import *

FUNCTION_KEY = 'RightShift'

# Use a status light on the keyboard to indicate that a layer lock or function layer select is enabled. 
# Possible values are CapsLock, ScrollLock, NumLock
# The key you use as the indicator will no longer be usable as a rule target 
# (e.g. you cannot specify rule 'x': 'CapsLock' in layer actions if CapsLock is the indicator key)
INDICATOR_KEY = 'CapsLock'

# Choose a modifier to key to enable function layer selection
# MODIFIER + FN + FN will enable layer selection mode
# While in layer selection mode:
#   FN will reset the current function layer to the default (FUNCTION_LAYER_ACTIONS).
#   'key' will set the current function layer to the one defined for 'key'.
#   If no function layer is defined for 'key', the action is cancelled and the current is unchanged.
FUNCTION_SELECT_MODIFIER_KEY = 'LeftShift'

DEFAULT_FUNCTION_LAYER_ACTIONS = {
    'i': 'UpArrow', 
    'j': 'LeftArrow',
    'k': 'DownArrow',
    'l': 'RightArrow',
    ';': 'PageUp',
    '"': 'PageDown',
    '[': 'Home',
    ']': 'End',

    '1': 'F1',
    '2': 'F2',
    '3': 'F3',
    '4': 'F4',
    '5': 'F5',
    '6': 'F6',
    '7': 'F7',
    '8': 'F8',
    '9': 'F9',
    '0': 'F10',
    '-': 'F11',
    '=': 'F12',
}