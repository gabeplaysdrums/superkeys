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
    ('LeftCtrl',    (29, INTERCEPTION_KEY_DOWN)),
    ('RightCtrl',   (29, INTERCEPTION_KEY_DOWN | INTERCEPTION_KEY_E0)),
    ('Z',           (44, INTERCEPTION_KEY_DOWN)),
    ('X',           (45, INTERCEPTION_KEY_DOWN)),
    ('C',           (46, INTERCEPTION_KEY_DOWN)),
    ('V',           (47, INTERCEPTION_KEY_DOWN)),
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
            for code_text in filter(None, delim.split(chord_text)):
                code_text = code_text.strip()
                code_text = code_text.lower()
                if not code_text or code_text not in KEY_MAP:
                    valid = False
                    break
                keyState = KEY_MAP[code_text]
                keyStates.append(keyState)
            if not keyStates:
                valid = False
            if not valid:
                break
            chords_data.append(keyStates)
        if not valid or not chords_data:
            raise AssertionError('Invalid filter text: ' + self.filter_text)

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