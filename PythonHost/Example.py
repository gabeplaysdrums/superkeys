import superkeys

FUNCTION_KEY = 'RightWin'

# Use a status light on the keyboard to indicate that a layer lock is enabled. 
# Possible values are CapsLock, ScrollLock, NumLock
# The key you use as the indicator will no longer be usable as a rule target 
# (e.g. you cannot specify rule 'x': 'CapsLock' in layer actions if CapsLock is the indicator key)
LAYER_LOCK_ENABLED_INDICATOR = 'ScrollLock'

import time

def func1(context):
    context.send('h', 'e', 'l', 'l', 'o', 'Space')
    for c in 'world':
        context.send(c)
        time.sleep(0.5)
    raise AssertionError()

def type_down(context):
    context.send('d', 'o', 'w', 'n', 'Space')

def type_up(context):
    context.send('u', 'p', 'Space')

FUNCTION_LAYER_ACTIONS = {
    'i': 'UpArrow', 
    'j': 'LeftArrow',
    'k': 'DownArrow',
    'l': 'RightArrow',
    "'": 'End',
    ';': 'Home',
    'g': 'LeftCtrl + RightArrow',
    'h': 'LeftCtrl + LeftArrow',
    'Backspace': 'LeftCtrl + Backspace',

    # trigger when LeftShift state changes to down (does not re-trigger on key repeat)
    #'+LeftShift': 'LeftCtrl + C', 
    # trigger when LeftShift state changes to up
    #'-LeftShift': ('End', 'Enter', 'LeftCtrl + V'),

    #'+CapsLock': func1,
    #'a': ('x', 'CapsLock'),
    'RightShift': 'LeftCtrl+LeftAlt+Tab',
    'LeftShift': 'LeftShift',
    'LeftCtrl': 'LeftCtrl',
    'LeftWin': 'LeftWin',
    #'c': 'LeftCtrl + c',
    #'v': 'LeftCtrl + v',
    'n': 'PageDown',
    'p': 'PageUp',

    #'d': 'd',

    '5': 'F5',

    # callback actions should be triggered on down transition except in special circumstances
    '+Enter': func1,

    # Invoke callback when z state changes to down (does not trigger on key repeat)
    '+z': type_down,
    # Invoke callback when z state changes to up
    '-z': type_up,

    # Invoke callback on every x key down stroke
    'x': type_down,
}

"""
window_nav_enabled = False
desktop_nav_enabled = False
nav_enabled = False

def start_window_navigation(context):
    context.cancel()
    global window_nav_enabled
    window_nav_enabled = True
    global nav_enabled
    nav_enabled = True
    context.send('LeftCtrl+LeftAlt+Tab')

def start_desktop_navigation(context):
    context.cancel()
    global desktop_nav_enabled
    desktop_nav_enabled = True
    global nav_enabled
    nav_enabled = True
    context.send('LeftWin+Tab', 'Tab')

def make_navigation_function(stroke):
    def f(context):
        global nav_enabled
        if nav_enabled:
            print('stroke: ' + stroke)
            context.cancel()
            context.send(stroke)
    return f

def toggle_navigation(context):
    global nav_enabled
    nav_enabled = not nav_enabled
    context.cancel()

def stop_window_navigation(context):
    global window_nav_enabled
    global desktop_nav_enabled
    global nav_enabled
    if window_nav_enabled or desktop_nav_enabled:
        nav_enabled = False
    window_nav_enabled = False
    desktop_nav_enabled = False

SUPERKEYS = {
    #'LeftCtrl + C': None,
    #'LeftCtrl + V': None,
    #'LeftCtrl, LeftWin': None,
    ##'RightWin': 'Alt + F4',
    #'z': None,
    #'x': None,
    #'c': None,
    #'LeftCtrl+LeftShift+Esc': None,
    ##'-LeftShift': None,
    #'LeftShift+RightShift': None,
    'LeftShift+Backspace': 'LeftAlt+F4',
    'LeftShift+RightShift': start_window_navigation,
    'J': make_navigation_function('LeftArrow'),
    'K': make_navigation_function('DownArrow'),
    'L': make_navigation_function('RightArrow'),
    'I': make_navigation_function('UpArrow'),
    'Space': stop_window_navigation,
    'Return': stop_window_navigation,
    'LeftShift+Space': toggle_navigation,
    'RightWin': start_desktop_navigation,
}
"""