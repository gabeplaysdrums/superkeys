#include "stdafx.h"
#include "KeyboardLedControl.h"

#include <windows.h>
#include <winioctl.h>
#include <assert.h>

#pragma comment(linker, "/subsystem:windows")

namespace SuperKeys {
namespace Details {

    KeyboardLedControl::KeyboardLedControl()
    {
        DefineDosDevice(DDD_RAW_TARGET_PATH, L"Keybd", L"\\Device\\KeyboardClass0");
        m_device.Attach(CreateFile(L"\\\\.\\Keybd", GENERIC_WRITE, 0, 0, OPEN_EXISTING, 0, 0));
        assert(m_device.IsValid());
        m_stopBlinkEvent.Attach(CreateEvent(nullptr, /*bManualReset=*/ TRUE, /*bInitialState=*/ FALSE, nullptr));
        assert(m_stopBlinkEvent.IsValid());
    }

    KeyboardLedControl::~KeyboardLedControl()
    {
        DefineDosDevice(DDD_REMOVE_DEFINITION, L"Keybd", 0);
        StopBlink();
    }

    void KeyboardLedControl::SetStatus(DWORD enableFlags, DWORD disableFlags)
    {
        KEYBOARD_INDICATOR_PARAMETERS params;
        DWORD bytesReturned;

        DeviceIoControl(m_device.Get(), IOCTL_KEYBOARD_QUERY_INDICATORS, 0, 0, &params, sizeof(params), &bytesReturned, 0);
        assert(bytesReturned == sizeof(params));

        // clear all led status bits
        params.LedFlags &= ~disableFlags;
        // set status bits we care about
        params.LedFlags |= enableFlags;

        DeviceIoControl(m_device.Get(), IOCTL_KEYBOARD_SET_INDICATORS, &params, sizeof(params), 0, 0, &bytesReturned, 0);
        assert(bytesReturned == sizeof(params));
    }

    void KeyboardLedControl::StartBlink(DWORD flags)
    {
        StopBlink();

        ResetEvent(m_stopBlinkEvent.Get());

        m_blinkThread = std::thread([this, flags]() {

            const DWORD blinkIntervalMillis = 500;
            
            while (true)
            {
                Enable(flags);

                if (WaitForSingleObject(m_stopBlinkEvent.Get(), blinkIntervalMillis) != WAIT_TIMEOUT)
                {
                    break;
                }
                
                Disable(flags);
                
                if (WaitForSingleObject(m_stopBlinkEvent.Get(), blinkIntervalMillis) != WAIT_TIMEOUT)
                {
                    break;
                }
            }

            Disable(flags);
        });
    }

    void KeyboardLedControl::StopBlink()
    {
        SetEvent(m_stopBlinkEvent.Get());

        if (m_blinkThread.joinable())
        {
            m_blinkThread.join();
        }
    }

}}