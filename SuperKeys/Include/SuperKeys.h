#pragma once
#ifndef _SUPERKEYS_H_
#define _SUPERKEYS_H_

#ifdef SUPERKEYS_STATIC
    #define SUPERKEYS_API
#else
    #if defined _WIN32 || defined __CYGWIN__
        #ifdef SUPERKEYS_EXPORTS
            #ifdef __GNUC__
                #define SUPERKEYS_API __attribute__((dllexport))
            #else
                #define SUPERKEYS_API __declspec(dllexport)
            #endif
        #else
            #ifdef __GNUC__
                #define SUPERKEYS_API __attribute__((dllimport))
            #else
                #define SUPERKEYS_API __declspec(dllimport)
            #endif
        #endif
    #else
        #if __GNUC__ >= 4
            #define SUPERKEYS_API __attribute__ ((visibility("default")))
        #else
            #define SUPERKEYS_API
        #endif
	#endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

	void SUPERKEYS_API SuperKeys_Test();

#ifdef __cplusplus
}
#endif

#endif // _SUPERKEYS_H_