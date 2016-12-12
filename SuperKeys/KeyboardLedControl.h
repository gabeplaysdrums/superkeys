#pragma once

#include <ntddkbd.h>

namespace SuperKeys {
namespace Details {

    class KeyboardLedControl final
    {
    public:
        KeyboardLedControl();
        ~KeyboardLedControl();

        void SetStatus(DWORD enableFlags = 0, DWORD disableFlags = 0);

        void Enable(DWORD flags) { SetStatus(flags, 0); }
        void Disable(DWORD flags) { SetStatus(0, flags); }
    };

}} // SuperKeys::Details