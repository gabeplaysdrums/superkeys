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

#define SUPERKEYS_ACTION_MAX_STROKE_COUNT (8)
#define SUPERKEYS_LAYER_ID_NONE (0)
#define SUPERKEYS_LAYER_ID_FUNCTION (1)

	typedef void* SuperKeys_EngineContext;

	//! Create an engine context.  Free with SuperKeys_DestroyEngineContext
	SuperKeys_EngineContext SUPERKEYS_API SuperKeys_CreateEngineContext();

	//! Destroy engine context
	void SUPERKEYS_API SuperKeys_DestroyEngineContext(SuperKeys_EngineContext context);

	//! Run engine processing loop
	void SUPERKEYS_API SuperKeys_Run(SuperKeys_EngineContext context);

	//! Defines a keystroke in filter or action
	typedef struct
	{
		unsigned short code;
		unsigned short state;

		//! indicates which parts of the state are significant (e.g. whether this should be interpreted as an up and down stroke)
		//! - ~0x0 => up stroke or down stroke only
		//! - ~0x1 => both up stroke and down stroke
		//! - ~0x2 => normal and E0 variants, up or down stroke only
		//! - ~0x3 => normal and E0 variants, both up and down stroke
		unsigned short mask;
	} SuperKeys_KeyStroke;

	typedef void* SuperKeys_ActionContext;

	//! Callback function invoked on a callback action
	typedef void(*SuperKeys_ActionCallback)(SuperKeys_ActionContext context);

	//! Defines an action:
	//! - Single key stroke (or up/down stroke pair)
	//! - Key chord (e.g. Ctrl+Alt+Del)
	//! - 
	typedef struct
	{
		unsigned short nStrokes;
		SuperKeys_KeyStroke strokes[SUPERKEYS_ACTION_MAX_STROKE_COUNT];
		SuperKeys_ActionCallback callback;
	} SuperKeys_Action;

	typedef int SuperKeys_LayerId;

	//! Add an extra layer
	//!\param context - engine context
	//!\param stroke - key stroke used to select the layer when in layer select mode
	SuperKeys_LayerId SuperKeys_AddLayer(
		SuperKeys_EngineContext context, 
		const SuperKeys_KeyStroke* stroke);

	typedef int SuperKeys_RuleId;

	//! Add rule to a layer
	//!\param layer - layer id (cannot be `SUPERKEYS_LAYER_ID_NONE`)
	//!\param filter - key stroke that will engage the actions when the layer is engaged
	//!\param actions - sequence of actions to execute when rule is triggered
	//!\param nActions - number of actions
	SuperKeys_RuleId SUPERKEYS_API SuperKeys_AddRule(
		SuperKeys_EngineContext context, 
		SuperKeys_LayerId layer, 
		const SuperKeys_KeyStroke* filter, 
		const SuperKeys_Action* actions, 
		int nActions);

	//!\param Send a key stroke in an action callback
	void SUPERKEYS_API SuperKeys_Send(
		SuperKeys_ActionContext context, 
		const SuperKeys_KeyStroke* strokes, 
		int nStrokes);

#ifdef __cplusplus
}

namespace SuperKeys
{
	class Engine
	{
	public:
		Engine() :
			m_context(SuperKeys_CreateEngineContext(), &SuperKeys_DestroyEngineContext)
		{}

		void Run() { SuperKeys_Run(m_context.get()); }

	private:
		std::unique_ptr<void, decltype(&SuperKeys_DestroyEngineContext)> m_context;
	};
}

#endif

#endif // _SUPERKEYS_H_