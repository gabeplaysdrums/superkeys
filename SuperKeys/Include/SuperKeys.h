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
#include <memory>

extern "C" {
#endif

	#define SUPERKEYS_MAX_CHORD_CODE_COUNT (8)

	typedef struct
	{
		unsigned short code;
		unsigned short state;
	} SuperKeysKeyState;

	typedef struct
	{
		unsigned short nKeyStates;
		SuperKeysKeyState keyStates[SUPERKEYS_MAX_CHORD_CODE_COUNT];
	} SuperKeysChord;

	typedef void* SuperKeysContext;
	SuperKeysContext SUPERKEYS_API SuperKeys_CreateContext();
	void SUPERKEYS_API SuperKeys_DestroyContext(SuperKeysContext context);

	typedef bool(*SuperKeysFilterCallback)();
	int SUPERKEYS_API SuperKeys_AddFilter(SuperKeysContext context, const SuperKeysChord* chords, int nChords, SuperKeysFilterCallback callback);

	void SUPERKEYS_API SuperKeys_Run(SuperKeysContext context);

#ifdef __cplusplus
}

namespace SuperKeys
{
	class SuperKeysEngine
	{
	public:
		SuperKeysEngine() :
			m_context(SuperKeys_CreateContext(), &SuperKeys_DestroyContext)
		{}

		void Run() { SuperKeys_Run(m_context.get()); }

	private:
		std::unique_ptr<void, decltype(&SuperKeys_DestroyContext)> m_context;
	};
}

#endif

#endif // _SUPERKEYS_H_