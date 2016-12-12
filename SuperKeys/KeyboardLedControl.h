#pragma once

#include <ntddkbd.h>
#include <wrl/wrappers/corewrappers.h>
#include <thread>

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

        void StartBlink(DWORD flags);
        void StopBlink();

    private:
        Microsoft::WRL::Wrappers::FileHandle m_device;
        Microsoft::WRL::Wrappers::Event m_stopBlinkEvent;
        std::thread m_blinkThread;
    };

}} // SuperKeys::Details