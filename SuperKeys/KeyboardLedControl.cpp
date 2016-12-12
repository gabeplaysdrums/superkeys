#include "stdafx.h"
#include "KeyboardLedControl.h"

#include <windows.h>
#include <winioctl.h>

#pragma comment(linker, "/subsystem:windows")

namespace SuperKeys {
namespace Details {

    KeyboardLedControl::KeyboardLedControl()
    {
    }

    KeyboardLedControl::~KeyboardLedControl()
    {
    }

    void KeyboardLedControl::SetStatus(DWORD enableFlags, DWORD disableFlags)
    {
        HANDLE hKeybd;
        KEYBOARD_INDICATOR_PARAMETERS buffer;
        DWORD retlen;

        DefineDosDevice(DDD_RAW_TARGET_PATH, L"Keybd", L"\\Device\\KeyboardClass0");
        hKeybd = CreateFile(L"\\\\.\\Keybd", GENERIC_WRITE, 0, 0, OPEN_EXISTING, 0, 0);

        DeviceIoControl(hKeybd, IOCTL_KEYBOARD_QUERY_INDICATORS, 0, 0, &buffer, sizeof(buffer), &retlen, 0);

        // clear all led status bits
        buffer.LedFlags &= ~disableFlags;
        // set status bits we care about
        buffer.LedFlags |= enableFlags;

        DeviceIoControl(hKeybd, IOCTL_KEYBOARD_SET_INDICATORS, &buffer, sizeof(buffer), 0, 0, &retlen, 0);

        DefineDosDevice(DDD_REMOVE_DEFINITION, L"Keybd", 0);
        CloseHandle(hKeybd);
    }

}}