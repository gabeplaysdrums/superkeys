// SuperKeys.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#include <interception.h>
#include "SuperKeys.h"

#include <iostream>
#include <map>
#include <sstream>
#include <vector>
using namespace std;

#define ENABLE_DEBUG_OUTPUT 1

#if ENABLE_DEBUG_OUTPUT
#define DEBUG_OUTPUT(...) \
{ \
	cout << __VA_ARGS__ << endl; \
	ostringstream oss; \
	oss << __VA_ARGS__ << endl; \
	OutputDebugStringA(oss.str().c_str()); \
}
#else
#define DEBUG_OUTPUT(...)
#endif

#define DEBUG_FILTER_MATCHING 0

namespace SuperKeys
{
	namespace Details
	{
#if 0
		typedef vector<SuperKeys_KeyStroke> Chord;

		struct Filter
		{
			vector<Chord> chords;
			SuperKeysFilterCallback callback;
			size_t nextChord = 0;
		};

		struct FilterContext sealed
		{
		public:
			FilterContext(
				InterceptionContext interception,
				InterceptionDevice device,
				InterceptionKeyStroke baseStroke) :
				m_interception(interception),
				m_device(device),
				m_baseStroke(baseStroke)
			{
			}

			void Cancel()
			{
				m_cancel = true;
			}

			bool IsCanceled() const
			{
				return m_cancel;
			}

			void Send(unsigned short code, unsigned short state)
			{
				m_baseStroke.code = code;
				m_baseStroke.state = state;
				DEBUG_OUTPUT("send >> device: " << m_device << ", code: " << code << ", state: " << state);
				interception_send(m_interception, m_device, (InterceptionStroke*)&m_baseStroke, 1);
			}

		private:
			InterceptionContext m_interception;
			InterceptionDevice m_device;
			InterceptionKeyStroke m_baseStroke;
			bool m_cancel = false;
		};
#endif

		static bool AreStrokesEqual(const SuperKeys_KeyStroke& lhs, const SuperKeys_KeyStroke& rhs, unsigned short mask)
		{
			return (
				lhs.code == rhs.code &&
				(lhs.state & mask) == (rhs.state & mask));
		}

		class EngineContext sealed
		{
		public:
			EngineContext(const SuperKeys_EngineConfig& config) :
				m_config(config)
			{
				m_interception = interception_create_context();
				DEBUG_OUTPUT("interception_create_context() -> " << m_interception);
			}

			~EngineContext()
			{
				DEBUG_OUTPUT("interception_destroy_context(" << m_interception << ")");
				interception_destroy_context(m_interception);
			}

#if 0
			int AddFilter(Filter&& filter)
			{
				int id = m_nextFilterId++;
				m_filters[id] = std::move(filter);
				return id;
			}
#endif

			void Run()
			{
				InterceptionDevice device;
				InterceptionKeyStroke stroke;

				interception_set_filter(m_interception, interception_is_keyboard, INTERCEPTION_FILTER_KEY_ALL);

				while (interception_receive(m_interception, device = interception_wait(m_interception), (InterceptionStroke*)&stroke, 1) > 0)
				{
					DEBUG_OUTPUT("recv << device: " << device << ", code: " << stroke.code << ", state: " << stroke.state);

#if 0

					if (m_currentState.find(stroke.code) == m_currentState.end())
					{
						m_currentState[stroke.code].state = stroke.state;
					}
					else
					{
						KnownKeyState knownKeyState;
						knownKeyState.state = stroke.state;
						m_currentState[stroke.code] = std::move(knownKeyState);
					}

					bool canceled = false;

					// check to see if any filters are satisfied
					for (auto& filterEntry : m_filters)
					{
						auto& chord = filterEntry.second.chords[filterEntry.second.nextChord];
#if DEBUG_FILTER_MATCHING
						DEBUG_OUTPUT("Next chord in filter " << filterEntry.first << " starts with " << chord[0].code);
#endif

						// Determine whether the next chord has been completed or the filter sequence has been broken

						// initially assume any non-empty chord is complete
						bool chordComplete = !chord.empty();

						// a sequence is broken if a down event is received that is not part of the next chord
						bool sequenceBroken = (stroke.state & 0x1) == INTERCEPTION_KEY_DOWN;

						if (chord.size() == 1)
						{
							// a single-key chord is complete if its state is matched by the current stroke
							chordComplete = chord[0].code == stroke.code && chord[0].state == stroke.state;
							sequenceBroken = sequenceBroken && !chordComplete;
						}
						else
						{
							// a multi-key chord is complete if all keys in the chord are down

							for (const auto& keyState : chord)
							{
								auto it = m_currentState.find(keyState.code);
								if (it == m_currentState.end() || it->second.state != keyState.state)
								{
									chordComplete = false;
								}

								// a sequence is not broken if a down event is received that is part of the chord
								if (sequenceBroken && keyState.code == keyState.code && (stroke.state & ~0x1) == (keyState.state & ~0x1))
								{
									sequenceBroken = false;
								}
							}
						}

						if (chordComplete)
						{
#if DEBUG_FILTER_MATCHING
							DEBUG_OUTPUT("Chord is complete!");
#endif
							filterEntry.second.nextChord++;

							if (filterEntry.second.nextChord == filterEntry.second.chords.size())
							{
								// all chords in the rule are complete!
								FilterContext filterContext(m_interception, device, stroke);
								filterEntry.second.callback(&filterContext);
								canceled = canceled || filterContext.IsCanceled();
								filterEntry.second.nextChord = 0;
							}
						}
						else if (sequenceBroken)
						{
#if DEBUG_FILTER_MATCHING
							DEBUG_OUTPUT("Sequence broken!");
#endif
							filterEntry.second.nextChord = 0;
						}
					}

					// if the key press was down and canceled, block up key presses (otherwise, stop blocking up key presses)
					if ((stroke.state & 0x1) == INTERCEPTION_KEY_DOWN)
					{
						m_currentState[stroke.code].blockKeyUp = canceled;
					}
					// otherwise, if the key press was up and up key presses are being blocked, block the keypress
					else if (m_currentState[stroke.code].blockKeyUp)
					{
						canceled = true;
					}


					if (!canceled)
#endif
					{
						DEBUG_OUTPUT("send >> device: " << device << ", code: " << stroke.code << ", state: " << stroke.state);
						interception_send(m_interception, device, (InterceptionStroke*)&stroke, 1);
					}
				}
			}

			SuperKeys_RuleId AddRule(
				SuperKeys_LayerId layer,
				const SuperKeys_KeyStroke& filter,
				vector<SuperKeys_Action>&& actions)
			{
				auto layerEntry = m_layers.find(layer);
				bool valid = (layerEntry != m_layers.end() && !AreStrokesEqual(filter, m_config.fnKey, ~0x1));

				for (const auto& action : actions)
				{
					for (size_t i = 0; i < action.nStrokes; i++)
					{
						if (AreStrokesEqual(action.strokes[i], m_config.layerLockIndicator, ~0x1))
						{
							valid = false;
							break;
						}
					}

					if (!valid)
					{
						break;
					}
				}

				if (!valid)
				{
					DEBUG_OUTPUT("Ignoring invalid rule");
					return 0;
				}

				Rule rule;
				rule.id = m_nextRuleId;
				rule.state = filter.state;
				rule.mask = filter.mask;
				rule.actions = std::move(actions);
				layerEntry->second[filter.code].push_back(std::move(rule));

				return m_nextRuleId++;
			}

		private:
			InterceptionContext m_interception;
			SuperKeys_EngineConfig m_config;
			SuperKeys_RuleId m_nextRuleId = 1;

			struct Rule
			{
				SuperKeys_RuleId id;
				unsigned short state;
				unsigned short mask;
				vector<SuperKeys_Action> actions;
			};

			typedef map<unsigned short /*code*/, vector<Rule> /*rules*/> RuleMap;

			std::map<SuperKeys_LayerId, RuleMap> m_layers = { { SUPERKEYS_LAYER_ID_FUNCTION, RuleMap() } };

#if 0
			int m_nextFilterId = 0;
			map<int, Filter> m_filters;

			struct KnownKeyState
			{
				unsigned short state = 0;
				bool blockKeyUp = false;
			};

			map<unsigned short, KnownKeyState> m_currentState;
#endif
		};
	}
}

using namespace SuperKeys;
using namespace SuperKeys::Details;

SuperKeys_EngineContext SUPERKEYS_API SuperKeys_CreateEngineContext(const SuperKeys_EngineConfig* config)
{
	auto context = make_unique<EngineContext>(*config);
	return context.release();
}

void SUPERKEYS_API SuperKeys_DestroyEngineContext(SuperKeys_EngineContext context)
{
	unique_ptr<EngineContext> deleter((EngineContext*)context);
}

#if 0
int SUPERKEYS_API SuperKeys_AddFilter(SuperKeys_EngineContext context, const SuperKeys_Action* chords, int nChords, SuperKeysFilterCallback callback)
{
	Filter filter;

#if DEBUG_FILTER_MATCHING
	DEBUG_OUTPUT("Adding filter with " << nChords << " chords");
#endif
	
	for (int i = 0; i < nChords; i++)
	{
#if DEBUG_FILTER_MATCHING
		DEBUG_OUTPUT("Adding filter for chord with " << chords[i].nKeyStates << " key states");
#endif
		filter.chords.push_back(Details::Chord(chords[i].keyStates, chords[i].keyStates + chords[i].nKeyStates));
	}
	
	filter.callback = callback;

	return ((EngineContext*)context)->AddFilter(std::move(filter));
}
#endif

void SUPERKEYS_API SuperKeys_Run(SuperKeys_EngineContext context)
{
	((EngineContext*)context)->Run();
}

#if 0
void SUPERKEYS_API SuperKeys_Cancel(SuperKeysFilterContext context)
{
	((FilterContext*)context)->Cancel();
}

void SUPERKEYS_API SuperKeys_Send(SuperKeysFilterContext context, unsigned short code, unsigned short state)
{
	((FilterContext*)context)->Send(code, state);
}
#endif

SuperKeys_LayerId SuperKeys_AddLayer(
	SuperKeys_EngineContext context, 
	const SuperKeys_KeyStroke* stroke)
{
	//TODO: implement
	return SUPERKEYS_LAYER_ID_NONE;
}

SuperKeys_RuleId SUPERKEYS_API SuperKeys_AddRule(
	SuperKeys_EngineContext context, 
	SuperKeys_LayerId layer, 
	const SuperKeys_KeyStroke* filter, 
	const SuperKeys_Action* actions, 
	int nActions)
{
	vector<SuperKeys_Action> actionsVect(actions, actions + nActions);
	return ((EngineContext*)context)->AddRule(layer, *filter, std::move(actionsVect));
}

void SUPERKEYS_API SuperKeys_Send(
	SuperKeys_ActionContext context, 
	const SuperKeys_KeyStroke* strokes, 
	int nStrokes)
{
	//TODO: implement
}