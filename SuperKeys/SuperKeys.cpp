// SuperKeys.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#include <interception.h>
#include "SuperKeys.h"

void SUPERKEYS_API Test()
{
	(void)interception_create_context();
}