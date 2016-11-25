#!python
"""
SuperKeys host application
"""

from __future__ import print_function
from optparse import OptionParser
import os
import sys
import ctypes
import imp
import re


def parse_command_line():

    parser = OptionParser(
        usage = '%prog [options]'
    )
    
    # options

    """
    parser.add_option(
        '-o', '--output', dest='output_path', default='output.txt',
        help='output path',
    )
    """
    
    (options, args) = parser.parse_args()

    # args

    if len(args) < 1:
        parser.print_usage()
        sys.exit(1)

    return (options, args)


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SUPERKEYS_FILTER_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_bool)
SUPERKEYS_MAX_CHORD_CODE_COUNT = 8

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
    ('F11',         (87, INTERCEPTION_KEY_DOWN)),
    ('F12',         (88, INTERCEPTION_KEY_DOWN)),
    ('LeftWin',     (91, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('RightWin',    (92, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
))

#REVERSE_KEY_MAP = { v:k for k,v in KEY_MAP.items() }
KEY_MAP = { k.lower():v for k,v in KEY_MAP.items() }

class SUPERKEYS_KEY_STATE(ctypes.Structure):
    _fields_ = (
        ('code', ctypes.c_ushort),
        ('state', ctypes.c_ushort),
    )

class SUPERKEYS_CHORD(ctypes.Structure):
    _fields_ = (
        ('nKeyStates', ctypes.c_ushort),
        ('keyStates', SUPERKEYS_KEY_STATE * SUPERKEYS_MAX_CHORD_CODE_COUNT),
    )


class SuperKeysFilter:
    def __init__(self, filter_text, action):
        self.filter_text = filter_text
        self.action = action
        self.raw_callback_func = SUPERKEYS_FILTER_CALLBACK(self._raw_callback)

    def _raw_callback(self):
        """
        print('[python] recv << code=%d, state=%d' % (code, state));

        if code == 46: # c
            print('[python] ! blocked keystroke')
            return False

        #self._callback()

        return True
        """
        print('[python] filter triggered! ' + self.filter_text)
        return True

    def make_raw(self):
        delim = re.compile(r'\s*,\s*')
        valid = True
        chords_data = []
        for chord_text in filter(None, delim.split(self.filter_text)):
            chord_text = chord_text.strip()
            if not chord_text:
                valid = False
                break
            keyStates = []
            delim = re.compile(r'\s*\+\s*')
            contains_up_stroke = False
            for code_text in filter(None, delim.split(chord_text)):
                code_text = code_text.strip()
                code_text = code_text.lower()
                state_union = 0
                if code_text[0] == '-' and len(code_text) > 1:
                    state_union = INTERCEPTION_KEY_UP
                    code_text = code_text[1:]
                    contains_up_stroke = True
                if not code_text or code_text not in KEY_MAP:
                    valid = False
                    break
                code, state = KEY_MAP[code_text]
                keyStates.append((code, state | state_union))
            if not keyStates or (len(keyStates) > 1 and contains_up_stroke):
                valid = False
            if not valid:
                break
            chords_data.append(keyStates)
        if not valid or not chords_data:
            raise AssertionError('Invalid filter: ' + self.filter_text)

        raw_chords_count = len(chords_data)
        raw_chords = (SUPERKEYS_CHORD * raw_chords_count)()

        for i in range(len(chords_data)):
            raw_chords[i].nKeyStates = ctypes.c_ushort(len(chords_data[i]))
            for j in range(len(chords_data[i])):
                code, state = chords_data[i][j]
                raw_chords[i].keyStates[j].code = ctypes.c_ushort(code)
                raw_chords[i].keyStates[j].state = ctypes.c_ushort(state)

        return raw_chords, raw_chords_count


class SuperKeysEngine:
    def __init__(self):
        self.context = lib.SuperKeys_CreateContext();
        self.filters = dict()

    def __del__(self):
        lib.SuperKeys_DestroyContext(self.context)

    def add_filter(self, filter):
        raw_chords, raw_chords_count = filter.make_raw()
        lib.SuperKeys_AddFilter(self.context, ctypes.byref(raw_chords), ctypes.c_int(raw_chords_count), filter.raw_callback_func)

    def run(self):
        lib.SuperKeys_Run(self.context);


if __name__ == '__main__':
    (options, args) = parse_command_line()
    config = imp.load_source('', args[0])

    global lib
    lib = ctypes.CDLL(os.path.join(SCRIPT_DIR, 'SuperKeys.dll'))

    engine = SuperKeysEngine()

    for filter_text, action in config.SUPERKEYS.items():
        f = SuperKeysFilter(filter_text, action)
        engine.add_filter(f)

    engine.run()