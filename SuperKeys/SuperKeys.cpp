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

					m_lastKnownKeyState[stroke.code] = stroke.state;
					bool handled = false;

					// check to see if any filters are satisfied
					for (auto& filterEntry : m_filters)
					{
						auto& chord = filterEntry.second.chords[filterEntry.second.nextChord];
						DEBUG_OUTPUT("Next chord in filter " << filterEntry.first << " starts with " << chord[0].code);

						bool chordComplete = true;
						bool chordPartial = false;
						for (const auto& keyState : chord)
						{
							auto it = m_lastKnownKeyState.find(keyState.code);
							if (it != m_lastKnownKeyState.end() && it->second == keyState.state)
							{
								chordPartial = true;
							}
							else
							{
								chordComplete = false;
							}
						}

						if (chordComplete)
						{
							DEBUG_OUTPUT("Chord is complete!");
							filterEntry.second.nextChord++;

							if (filterEntry.second.nextChord == filterEntry.second.chords.size())
							{
								// all chords in the rule are complete!
								handled = handled || filterEntry.second.callback();
								filterEntry.second.nextChord = 0;
							}
						}
						//else if (!chordPartial)
						//{
						//	DEBUG_OUTPUT("Chord is not partial!");
						//	// if the user has started an entirely different chord, cancel this filter
						//	filterEntry.second.nextChord = 0;
						//}
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
			map<unsigned short, unsigned short> m_lastKnownKeyState;
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