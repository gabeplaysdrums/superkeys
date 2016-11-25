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

#define DEBUG_OUTPUT(...) \
{ \
	cout << __VA_ARGS__ << endl; \
	ostringstream oss; \
	oss << __VA_ARGS__ << endl; \
	OutputDebugStringA(oss.str().c_str()); \
}

namespace SuperKeys
{
	namespace Details
	{
		typedef vector<SuperKeysKeyState> Chord;

		struct Filter
		{
			vector<Chord> chords;
			SuperKeysFilterCallback callback;
			size_t nextChord = 0;
		};

		class Context sealed
		{
		public:
			Context()
			{
				m_interception = interception_create_context();
				DEBUG_OUTPUT("interception_create_context() -> " << m_interception);
			}

			~Context()
			{
				DEBUG_OUTPUT("interception_destroy_context(" << m_interception << ")");
				interception_destroy_context(m_interception);
			}

			int AddFilter(Filter&& filter)
			{
				int id = m_nextFilterId++;
				m_filters[id] = std::move(filter);
				return id;
			}

			void Run()
			{
				InterceptionDevice device;
				InterceptionKeyStroke stroke;

				interception_set_filter(m_interception, interception_is_keyboard, INTERCEPTION_FILTER_KEY_ALL);

				while (interception_receive(m_interception, device = interception_wait(m_interception), (InterceptionStroke*)&stroke, 1) > 0)
				{
					DEBUG_OUTPUT("recv << device: " << device << ", code: " << stroke.code << ", state: " << stroke.state);

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

					bool handled = false;

					// check to see if any filters are satisfied
					for (auto& filterEntry : m_filters)
					{
						auto& chord = filterEntry.second.chords[filterEntry.second.nextChord];
						DEBUG_OUTPUT("Next chord in filter " << filterEntry.first << " starts with " << chord[0].code);

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
							DEBUG_OUTPUT("Chord is complete!");
							filterEntry.second.nextChord++;

							if (filterEntry.second.nextChord == filterEntry.second.chords.size())
							{
								// all chords in the rule are complete!
								bool result = filterEntry.second.callback();
								handled = handled || result;
								filterEntry.second.nextChord = 0;
							}
						}
						else if (sequenceBroken)
						{
							DEBUG_OUTPUT("Sequence broken!");
							filterEntry.second.nextChord = 0;
						}
					}

					// if the key press was down and handled, block up key presses
					if ((stroke.state & 0x1) == INTERCEPTION_KEY_DOWN && handled)
					{
						m_currentState[stroke.code].blockKeyUp = false;
					}
					// otherwise, if the key press was up and up key presses are being blocked, block the keypress
					else if ((stroke.state & 0x1) == INTERCEPTION_KEY_UP && m_currentState[stroke.code].blockKeyUp)
					{
						handled = true;
					}

					if (!handled)
					{
						DEBUG_OUTPUT("send >> device: " << device << ", code: " << stroke.code << ", state: " << stroke.state);
						interception_send(m_interception, device, (InterceptionStroke*)&stroke, 1);
					}
				}
			}

		private:
			InterceptionContext m_interception;
			int m_nextFilterId = 0;
			map<int, Filter> m_filters;

			struct KnownKeyState
			{
				unsigned short state = 0;
				bool blockKeyUp = false;
			};

			map<unsigned short, KnownKeyState> m_currentState;
		};
	}
}

using namespace SuperKeys;
using namespace SuperKeys::Details;

SuperKeysContext SUPERKEYS_API SuperKeys_CreateContext()
{
	auto context = make_unique<Context>();
	return context.release();
}

void SUPERKEYS_API SuperKeys_DestroyContext(SuperKeysContext context)
{
	unique_ptr<Context> deleter((Context*)context);
}

int SUPERKEYS_API SuperKeys_AddFilter(SuperKeysContext context, const SuperKeysChord* chords, int nChords, SuperKeysFilterCallback callback)
{
	Filter filter;

	DEBUG_OUTPUT("Adding filter with " << nChords << " chords");
	
	for (int i = 0; i < nChords; i++)
	{
		DEBUG_OUTPUT("Adding filter for chord with " << chords[i].nKeyStates << " key states");
		filter.chords.push_back(Details::Chord(chords[i].keyStates, chords[i].keyStates + chords[i].nKeyStates));
	}
	
	filter.callback = callback;

	return ((Context*)context)->AddFilter(std::move(filter));
}

void SUPERKEYS_API SuperKeys_Run(SuperKeysContext context)
{
	((Context*)context)->Run();
}