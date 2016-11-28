import superkeys

def func1(context):
    pass

FUNCTION_LAYER_ACTIONS = {
    'i': 'UpArrow', 
    'j': 'LeftArrow',
    'k': 'DownArrow',
    'l': 'RightArrow',

    '+LeftShift': 'LeftCtrl + C', 
    '-LeftShift': ('RightCtrl + V', 'Enter'),

    'Enter': func1,
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