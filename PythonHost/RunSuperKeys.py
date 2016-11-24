#!python
"""
SuperKeys host application
"""

from __future__ import print_function
from optparse import OptionParser
import os
import sys
import ctypes


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

    """
    if len(args) < 1:
        parser.print_usage()
        sys.exit(1)
    """

    return (options, args)


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SUPERKEYS_KEYSTROKE_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_uint16, ctypes.c_uint16)

class SuperKeysEngine:
    def __init__(self):
        self.context = lib.SuperKeys_CreateContext();

    def __del__(self):
        lib.SuperKeys_DestroyContext(self.context)

    def run(self):
        self.callback_func = SUPERKEYS_KEYSTROKE_CALLBACK(self._callback)
        lib.SuperKeys_Run(self.context, self.callback_func);

    def _callback(self, code, state):
        print('[python] recv << code=%d, state=%d' % (code, state));

        if code == 46: # c
            print('[python] ! blocked keystroke')
            return False

        return True

if __name__ == '__main__':
    (options, args) = parse_command_line()

    global lib
    lib = ctypes.CDLL(os.path.join(SCRIPT_DIR, 'SuperKeys.dll'))

    engine = SuperKeysEngine()
    engine.run()