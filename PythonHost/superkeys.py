import ctypes
import re

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
    ('Return',      (28, INTERCEPTION_KEY_DOWN)),
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
    ('RightShift',  (54, INTERCEPTION_KEY_DOWN)),
    ('LeftAlt',     (56, INTERCEPTION_KEY_DOWN)),
    ('RightAlt',    (56, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('Space',       (57, INTERCEPTION_KEY_DOWN)),
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
    ('UpArrow',     (72, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('LeftArrow',   (75, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('RightArrow',  (77, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('DownArrow',   (80, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('F11',         (87, INTERCEPTION_KEY_DOWN)),
    ('F12',         (88, INTERCEPTION_KEY_DOWN)),
    ('LeftWin',     (91, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('RightWin',    (92, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
))

#REVERSE_KEY_MAP = { v:k for k,v in KEY_MAP.items() }
KEY_MAP = { k.lower():v for k,v in KEY_MAP.items() }

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
