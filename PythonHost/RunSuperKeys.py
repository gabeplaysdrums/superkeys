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
import superkeys
from superkeys import *


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

"""
SUPERKEYS_FILTER_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p)
SUPERKEYS_MAX_CHORD_CODE_COUNT = 8


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
        self.raw_callback_func = SUPERKEYS_FILTER_CALLBACK(self._raw_callback)

        if action is None:
            def action_cancel(context):
                context.cancel()
            action = action_cancel
        elif type(action) is str:
            delim = re.compile(r'\s*,\s*')
            strokes = list(filter(None, delim.split(action)))
            def action_send(context):
                context.cancel()
                context.send(*strokes)
            action = action_send

        self.action = action

    def _raw_callback(self, rawFilterContext):
        print('[python] filter triggered! ' + self.filter_text)
        context = SuperKeysFilterContext(rawFilterContext)
        self.action(context)

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
"""

SUPERKEYS_LAYER_ID_FUNCTION = 1

class SuperKeys_EngineConfig(ctypes.Structure):
    _fields_ = (
        ('fnKey', SuperKeys_KeyStroke),
        ('layerLockIndicator', SuperKeys_KeyStroke),
    )

class SuperKeysEngine:
    def __init__(self, raw_config):
        self.context = superkeys.lib.SuperKeys_CreateEngineContext(ctypes.byref(raw_config));
        #self.filters = dict()

    def __del__(self):
        superkeys.lib.SuperKeys_DestroyEngineContext(self.context)

    """
    def add_filter(self, filter):
        raw_chords, raw_chords_count = filter.make_raw()
        superkeys.lib.SuperKeys_AddFilter(self.context, ctypes.byref(raw_chords), ctypes.c_int(raw_chords_count), filter.raw_callback_func)
    """

    def add_rule(self, layer, filter_stroke, action_list):
        return superkeys.lib.SuperKeys_AddRule(
            self.context,
            layer,
            ctypes.byref(filter_stroke),
            ctypes.byref(action_list.raw_array),
            action_list.raw_count)

    def run(self):
        superkeys.lib.SuperKeys_Run(self.context);


if __name__ == '__main__':
    (options, args) = parse_command_line()
    config = imp.load_source('', args[0])

    superkeys.lib = ctypes.CDLL(os.path.join(SCRIPT_DIR, 'SuperKeys.dll'))

    raw_config = SuperKeys_EngineConfig()
    ActionList.parse_stroke(getattr(config, 'FUNCTION_KEY', 'CapsLock'), raw_config.fnKey, allow_single_direction=False)
    ActionList.parse_stroke(getattr(config, 'LAYER_LOCK_ENABLED_INDICATOR', None), raw_config.layerLockIndicator, allow_single_direction=False)

    engine = SuperKeysEngine(raw_config)

    for filter_text, action in getattr(config, 'FUNCTION_LAYER_ACTIONS', {}).items():
        filter_stroke = SuperKeys_KeyStroke()
        ActionList.parse_stroke(filter_text, filter_stroke)
        action_list = ActionList(action)
        rule_id = engine.add_rule(SUPERKEYS_LAYER_ID_FUNCTION, filter_stroke, action_list)
        if rule_id == 0:
            print('Invalid rule: %s : %s' % (repr(filter_text), repr(action)))

    engine.run()