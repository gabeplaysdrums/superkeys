// SuperKeys.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#include <interception.h>
#include "SuperKeys.h"

#include <iostream>
#include <sstream>
using namespace std;

#define DEBUG_OUTPUT(...) \
{ \
	ostringstream oss; \
	oss << __VA_ARGS__ << endl; \
	OutputDebugStringA(oss.str().c_str()); \
}

namespace SuperKeys
{
	namespace Details
	{
		//TODO: internal helpers
	}
}

SuperKeysContext SUPERKEYS_API SuperKeys_CreateContext()
{
	DEBUG_OUTPUT("interception_create_context()");
	return interception_create_context();
}

void SUPERKEYS_API SuperKeys_DestroyContext(SuperKeysContext context)
{
	DEBUG_OUTPUT("interception_destroy_context(" << context << ")");
	interception_destroy_context(context);
}

void SUPERKEYS_API SuperKeys_Run(SuperKeysContext context)
{
	InterceptionContext interception = (InterceptionContext)context;
	InterceptionDevice device;
	InterceptionKeyStroke stroke;

	interception_set_filter(interception, interception_is_keyboard, INTERCEPTION_FILTER_KEY_ALL);

	while (interception_receive(interception, device = interception_wait(interception), (InterceptionStroke*)&stroke, 1) > 0)
	{
		DEBUG_OUTPUT("recv << device: " << device << ", code: " << stroke.code);

		if (stroke.code == 46) // C
		{
			continue;
		}

		interception_send(interception, device, (InterceptionStroke *)&stroke, 1);
	}
}