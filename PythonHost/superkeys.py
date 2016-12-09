import ctypes
import re
import types
import traceback
import sys

lib = None

INTERCEPTION_KEY_DOWN             = 0x00
INTERCEPTION_KEY_UP               = 0x01
INTERCEPTION_KEY_E0               = 0x02
INTERCEPTION_KEY_E1               = 0x04
INTERCEPTION_KEY_TERMSRV_SET_LED  = 0x08
INTERCEPTION_KEY_TERMSRV_SHADOW   = 0x10
INTERCEPTION_KEY_TERMSRV_VKPACKET = 0x20

KEY_MAP = dict((
    ('Esc',         (1, INTERCEPTION_KEY_DOWN)),
    ('Escape',      (1, INTERCEPTION_KEY_DOWN)),
    ('1',           (2, INTERCEPTION_KEY_DOWN)),
    ('2',           (3, INTERCEPTION_KEY_DOWN)),
    ('3',           (4, INTERCEPTION_KEY_DOWN)),
    ('4',           (5, INTERCEPTION_KEY_DOWN)),
    ('5',           (6, INTERCEPTION_KEY_DOWN)),
    ('6',           (7, INTERCEPTION_KEY_DOWN)),
    ('7',           (8, INTERCEPTION_KEY_DOWN)),
    ('8',           (9, INTERCEPTION_KEY_DOWN)),
    ('9',           (10, INTERCEPTION_KEY_DOWN)),
    ('0',           (11, INTERCEPTION_KEY_DOWN)),
    ('-',           (12, INTERCEPTION_KEY_DOWN)),
    ('=',           (13, INTERCEPTION_KEY_DOWN)),
    ('Backspace',   (14, INTERCEPTION_KEY_DOWN)),
    ('Tab',         (15, INTERCEPTION_KEY_DOWN)),
    ('Q',           (16, INTERCEPTION_KEY_DOWN)),
    ('W',           (17, INTERCEPTION_KEY_DOWN)),
    ('E',           (18, INTERCEPTION_KEY_DOWN)),
    ('R',           (19, INTERCEPTION_KEY_DOWN)),
    ('T',           (20, INTERCEPTION_KEY_DOWN)),
    ('Y',           (21, INTERCEPTION_KEY_DOWN)),
    ('U',           (22, INTERCEPTION_KEY_DOWN)),
    ('I',           (23, INTERCEPTION_KEY_DOWN)),
    ('O',           (24, INTERCEPTION_KEY_DOWN)),
    ('P',           (25, INTERCEPTION_KEY_DOWN)),
    ('[',           (26, INTERCEPTION_KEY_DOWN)),
    ('{',           (26, INTERCEPTION_KEY_DOWN)),
    (']',           (27, INTERCEPTION_KEY_DOWN)),
    ('}',           (27, INTERCEPTION_KEY_DOWN)),
    ('Enter',       (28, INTERCEPTION_KEY_DOWN)),
    ('NumPadEnter', (28, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('LeftCtrl',    (29, INTERCEPTION_KEY_DOWN)),
    ('RightCtrl',   (29, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('A',           (30, INTERCEPTION_KEY_DOWN)),
    ('S',           (31, INTERCEPTION_KEY_DOWN)),
    ('D',           (32, INTERCEPTION_KEY_DOWN)),
    ('F',           (33, INTERCEPTION_KEY_DOWN)),
    ('G',           (34, INTERCEPTION_KEY_DOWN)),
    ('H',           (35, INTERCEPTION_KEY_DOWN)),
    ('J',           (36, INTERCEPTION_KEY_DOWN)),
    ('K',           (37, INTERCEPTION_KEY_DOWN)),
    ('L',           (38, INTERCEPTION_KEY_DOWN)),
    (';',           (39, INTERCEPTION_KEY_DOWN)),
    (':',           (39, INTERCEPTION_KEY_DOWN)),
    ('\'',          (40, INTERCEPTION_KEY_DOWN)),
    ('"',           (40, INTERCEPTION_KEY_DOWN)),
    ('`',           (41, INTERCEPTION_KEY_DOWN)),
    ('~',           (41, INTERCEPTION_KEY_DOWN)),
    ('LeftShift',   (42, INTERCEPTION_KEY_DOWN)),
    ('\\',          (43, INTERCEPTION_KEY_DOWN)),
    ('|',           (43, INTERCEPTION_KEY_DOWN)),
    ('Z',           (44, INTERCEPTION_KEY_DOWN)),
    ('X',           (45, INTERCEPTION_KEY_DOWN)),
    ('C',           (46, INTERCEPTION_KEY_DOWN)),
    ('V',           (47, INTERCEPTION_KEY_DOWN)),
    ('B',           (48, INTERCEPTION_KEY_DOWN)),
    ('N',           (49, INTERCEPTION_KEY_DOWN)),
    ('M',           (50, INTERCEPTION_KEY_DOWN)),
    (',',           (51, INTERCEPTION_KEY_DOWN)),
    ('<',           (51, INTERCEPTION_KEY_DOWN)),
    ('.',           (52, INTERCEPTION_KEY_DOWN)),
    ('>',           (52, INTERCEPTION_KEY_DOWN)),
    ('/',           (53, INTERCEPTION_KEY_DOWN)),
    ('?',           (53, INTERCEPTION_KEY_DOWN)),
    ('NumPadDivide', (53, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('RightShift',  (54, INTERCEPTION_KEY_DOWN)),
    ('NumPadMultiply', (55, INTERCEPTION_KEY_DOWN)),
    ('LeftAlt',     (56, INTERCEPTION_KEY_DOWN)),
    ('RightAlt',    (56, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('Space',       (57, INTERCEPTION_KEY_DOWN)),
    ('CapsLock',    (58, INTERCEPTION_KEY_DOWN)),
    ('F1',          (59, INTERCEPTION_KEY_DOWN)),
    ('F2',          (60, INTERCEPTION_KEY_DOWN)),
    ('F3',          (61, INTERCEPTION_KEY_DOWN)),
    ('F4',          (62, INTERCEPTION_KEY_DOWN)),
    ('F5',          (63, INTERCEPTION_KEY_DOWN)),
    ('F6',          (64, INTERCEPTION_KEY_DOWN)),
    ('F7',          (65, INTERCEPTION_KEY_DOWN)),
    ('F8',          (66, INTERCEPTION_KEY_DOWN)),
    ('F9',          (67, INTERCEPTION_KEY_DOWN)),
    ('F10',         (68, INTERCEPTION_KEY_DOWN)),
    ('NumLock',     (69, INTERCEPTION_KEY_DOWN)),
    ('ScrollLock',  (70, INTERCEPTION_KEY_DOWN)),
    ('NumPad7',     (71, INTERCEPTION_KEY_DOWN)),
    ('Home',        (71, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPad8',     (72, INTERCEPTION_KEY_DOWN)),
    ('UpArrow',     (72, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPad9',     (73, INTERCEPTION_KEY_DOWN)),
    ('PageUp',      (73, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPadSubtract', (74, INTERCEPTION_KEY_DOWN)),
    ('NumPad4',     (75, INTERCEPTION_KEY_DOWN)),
    ('LeftArrow',   (75, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPad5',     (76, INTERCEPTION_KEY_DOWN)),
    ('NumPad6',     (77, INTERCEPTION_KEY_DOWN)),
    ('RightArrow',  (77, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPadAdd',   (78, INTERCEPTION_KEY_DOWN)),
    ('NumPad1',     (79, INTERCEPTION_KEY_DOWN)),
    ('End',         (79, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPad2',     (80, INTERCEPTION_KEY_DOWN)),
    ('DownArrow',   (80, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPad3',     (81, INTERCEPTION_KEY_DOWN)),
    ('PageDown',    (81, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPad0',     (82, INTERCEPTION_KEY_DOWN)),
    ('Insert',      (82, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('NumPadPeriod', (83, INTERCEPTION_KEY_DOWN)),
    ('Del',         (83, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('F11',         (87, INTERCEPTION_KEY_DOWN)),
    ('F12',         (88, INTERCEPTION_KEY_DOWN)),
    ('LeftWin',     (91, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('RightWin',    (92, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
))

#REVERSE_KEY_MAP = { v:k for k,v in KEY_MAP.items() }
KEY_MAP = { k.lower():v for k,v in KEY_MAP.items() }

"""
class SuperKeysFilterContext:
    def __init__(self, filterContext):
        self._filterContext = filterContext

    def cancel(self):
        lib.SuperKeys_Cancel(self._filterContext)

    def send(self, *strokes):
        valid = True
        chords_data = []
        for chord_text in strokes:
            chord_text = chord_text.strip()
            if not chord_text:
                valid = False
                break
            keyStates = []
            delim = re.compile(r'\s*\+\s*')
            contains_up_stroke = False
            contains_down_stroke = False
            for code_text in filter(None, delim.split(chord_text)):
                code_text = code_text.strip()
                code_text = code_text.lower()
                state_union = 0
                if code_text[0] == '-' and len(code_text) > 1:
                    state_union = INTERCEPTION_KEY_UP
                    code_text = code_text[1:]
                    contains_up_stroke = True
                if code_text[0] == '_' and len(code_text) > 1:
                    state_union = INTERCEPTION_KEY_UP
                    code_text = code_text[1:]
                    contains_down_stroke = True
                if not code_text or code_text not in KEY_MAP:
                    valid = False
                    break
                code, state = KEY_MAP[code_text]
                keyStates.append((code, state | state_union))
            if not keyStates or (len(keyStates) > 1 and (contains_up_stroke or contains_down_stroke)):
                valid = False
            if not valid:
                break
            chords_data.append((keyStates, not contains_down_stroke and not contains_up_stroke))
        if not valid or not chords_data:
            raise AssertionError('Invalid filter: ' + repr(strokes))

        # press each key in the chord down in order, then up in reverse order
        for keyStates, simulate_up_strokes in chords_data:
            for code, state in keyStates:
                print('[python] send >> code: %d, state: %d' % (code, state))
                lib.SuperKeys_Send(self._filterContext, code, state)
            if simulate_up_strokes:
                print('simulating up strokes')
                for code, state in reversed(keyStates):
                    lib.SuperKeys_Send(self._filterContext, code, state | INTERCEPTION_KEY_UP)
                    import time
                    time.sleep(0.001)
"""

SUPERKEYS_ACTION_MAX_STROKE_COUNT = 8

class SuperKeys_KeyStroke(ctypes.Structure):
    _fields_ = (
        ('code', ctypes.c_ushort),
        ('state', ctypes.c_ushort),
        ('mask', ctypes.c_ushort),
    )

SuperKeys_ActionCallback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p)

class SuperKeys_Action(ctypes.Structure):
    _fields_ = (
        ('nStrokes', ctypes.c_ushort),
        ('strokes', SuperKeys_KeyStroke * SUPERKEYS_ACTION_MAX_STROKE_COUNT),
        ('callback', SuperKeys_ActionCallback),
    )

class ActionContext:
    def __init__(self, raw_context):
        self._raw_context = raw_context

    def send(self, *actions):
        for action in actions:
            if not type(action) == str:
                raise ValueError()
            raw_action = SuperKeys_Action()
            ActionList._parse(action, raw_action)
            if not lib.SuperKeys_Send(self._raw_context, raw_action.strokes, raw_action.nStrokes):
                raise ValueError()

class ActionList:
    def __init__(self, value):
        if callable(value):
            self.raw_count = 1
            self.raw_array = (SuperKeys_Action * 1)()
            self.raw_array[0].nStrokes = 0
            self._callback = value;
            self.raw_callback = SuperKeys_ActionCallback(self._callback_wrapper)
            self.raw_array[0].callback = self.raw_callback
        elif type(value) is str:
            self.raw_count = 1
            self.raw_array = (SuperKeys_Action * 1)()
            ActionList._parse(value, self.raw_array[0])
        else: # iterable of str
            self.raw_count = len(value)
            self.raw_array = (SuperKeys_Action * self.raw_count)()
            for i in range(self.raw_count):
                ActionList._parse(value[i], self.raw_array[i])

    _stroke_delim = re.compile(r'\s*\+\s*')

    def _callback_wrapper(self, raw_context):
        context = ActionContext(raw_context)
        try:
            self._callback(context)
        except:
            print("Exception in user code:")
            print('-'*60)
            traceback.print_exc(file=sys.stderr)
            print('-'*60)

    @staticmethod
    def parse_stroke(value, raw_stroke, allow_single_direction=True):
        if not value:
            raw_stroke.code = 0
            raw_stroke.state = 0
            raw_stroke.mask = 0
            return
        raw_stroke.mask = ~0x1
        raw_stroke.state = 0
        if allow_single_direction and (value[0] == '-' or value[0] == '+'):
            raw_stroke.state = (INTERCEPTION_KEY_UP if value[0] == '-' else 0)
            raw_stroke.mask = ~0x0
            value = value[1:]
        code, state = KEY_MAP[value.lower()]
        raw_stroke.code = code
        raw_stroke.state |= state

    @staticmethod
    def _parse(value, raw_action):
        raw_action.callback = SuperKeys_ActionCallback()
        if value[0] == '-' or value[0] == '+':
            raw_action.nStrokes = 1
            ActionList.parse_stroke(value, raw_action.strokes[0])
            return
        raw_action.nStrokes = 0
        for stroke_text in filter(None, ActionList._stroke_delim.split(value)):
            ActionList.parse_stroke(stroke_text, raw_action.strokes[raw_action.nStrokes], allow_single_direction=False)
            raw_action.nStrokes += 1
