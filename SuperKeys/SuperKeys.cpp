// SuperKeys.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#include <interception.h>
#include "SuperKeys.h"
#include "KeyboardLedControl.h"

#include <iostream>
#include <map>
#include <sstream>
#include <vector>
#include <chrono>
using namespace std;

#if _DEBUG
#define ENABLE_DEBUG_OUTPUT 1
#else
#define ENABLE_DEBUG_OUTPUT 0
#endif

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

namespace SuperKeys
{
    namespace Details
    {
        namespace KeyCodes
        {
            static const unsigned short CapsLock = 58;
            static const unsigned short NumLock = 69;
            static const unsigned short ScrollLock = 70;
        }

        template<typename TLeft = SuperKeys_KeyStroke>
        static bool AreStrokesEqual(const TLeft& lhs, const SuperKeys_KeyStroke& rhs, unsigned short mask)
        {
            return (
                lhs.code == rhs.code &&
                (lhs.state & mask) == (rhs.state & mask));
        }

        static bool IsComplexActionSequence(const vector<SuperKeys_Action>& actions)
        {
            return actions.size() > 0 && (actions.size() > 1 || (actions[0].nStrokes > 1 || actions[0].callback));
        }

        static bool ComputeStrokes(
            InterceptionContext interception,
            _In_reads_(nStrokes) const SuperKeys_KeyStroke* strokes,
            int nStrokes,
            const InterceptionKeyStroke& strokeTemplate,
            _Out_ vector<InterceptionKeyStroke>* rawStrokes)
        {
            // if there is only one stroke, it may have an explicit direction
            // if there are multiple strokes, they cannot have explicit directions
            const bool explicitDirectionAllowed = (nStrokes == 1);

            for (int i = 0; i < nStrokes; i++)
            {
                rawStrokes->push_back(strokeTemplate);
                rawStrokes->back().code = strokes[i].code;
                rawStrokes->back().state = strokes[i].state & strokes[i].mask;

                if ((strokes[i].mask & 0x1) != 0)
                {
                    if (!explicitDirectionAllowed)
                    {
                        return false;
                    }
                }
                else
                {
                    // no explicit direction given, simulate down strokes
                    rawStrokes->back().state &= ~INTERCEPTION_KEY_UP;
                }
            }

            // if no explicit direction given, simulate up strokes
            if (nStrokes > 0 && (strokes[nStrokes].mask & 0x1) == 0)
            {
                for (int i = nStrokes - 1; i >= 0; i--)
                {
                    rawStrokes->push_back(strokeTemplate);
                    rawStrokes->back().code = strokes[i].code;
                    rawStrokes->back().state = strokes[i].state & strokes[i].mask;
                    rawStrokes->back().state |= INTERCEPTION_KEY_UP;
                }
            }

            return true;
        }

        class ActionContext sealed
        {
        public:
            ActionContext(
                InterceptionContext interception, 
                InterceptionDevice device,
                const InterceptionKeyStroke* strokeTemplate) :
                m_interception(interception),
                m_device(device),
                m_strokeTemplate(strokeTemplate)
            {}

            bool Send(
                const SuperKeys_KeyStroke* strokes,
                int nStrokes) const
            {
                vector<InterceptionKeyStroke> rawStrokes;

                if (!ComputeStrokes(m_interception, strokes, nStrokes, *m_strokeTemplate, &rawStrokes))
                {
                    return false;
                }

                interception_send(m_interception, m_device, (InterceptionStroke*)&rawStrokes.front(), rawStrokes.size());
                return true;
            }

        private:
            InterceptionContext m_interception;
            InterceptionDevice m_device;
            const InterceptionKeyStroke* m_strokeTemplate;
        };

        class EngineContext sealed
        {
            using clock = std::chrono::high_resolution_clock;

        public:
            EngineContext(const SuperKeys_EngineConfig& config) :
                m_config(config)
            {
                m_interception = interception_create_context();
                DEBUG_OUTPUT("interception_create_context() -> " << m_interception);
                SetLockedLayer(SUPERKEYS_LAYER_ID_NONE);
            }

            ~EngineContext()
            {
                DEBUG_OUTPUT("interception_destroy_context(" << m_interception << ")");
                interception_destroy_context(m_interception);
            }

            void SetLockedLayer(SuperKeys_LayerId layer)
            {
                m_lockedLayer = layer;

#if ENABLE_DEBUG_OUTPUT
                if (layer == SUPERKEYS_LAYER_ID_NONE)
                {
                    DEBUG_OUTPUT("Layer lock canceled");
                }
                else
                {
                    DEBUG_OUTPUT("Function layer lock activated");
                }
#endif

                if (m_config.layerLockIndicator.code != 0)
                {
                    DWORD flags = 0;

                    switch (m_config.layerLockIndicator.code)
                    {
                    case KeyCodes::CapsLock:
                        flags = KEYBOARD_CAPS_LOCK_ON;
                        break;
                    case KeyCodes::NumLock:
                        flags = KEYBOARD_NUM_LOCK_ON;
                        break;
                    case KeyCodes::ScrollLock:
                        flags = KEYBOARD_SCROLL_LOCK_ON;
                        break;
                    }

                    if (layer == SUPERKEYS_LAYER_ID_NONE)
                    {
                        m_ledControl.Disable(flags);
                    }
                    else
                    {
                        m_ledControl.Enable(flags);
                    }
                }
            }

            void Run()
            {
                InterceptionDevice device;
                InterceptionKeyStroke stroke;
                InterceptionKeyStroke prevStroke;

                unsigned short fnKeyState = INTERCEPTION_KEY_UP;
                unsigned short fnKeyConsecutiveToggleCount = 0;
                clock::time_point fnKeyConsecutiveToggleTime;
                const auto fnKeyConsecutiveToggleTimeout = chrono::milliseconds(500);

                interception_set_filter(m_interception, interception_is_keyboard, INTERCEPTION_FILTER_KEY_ALL);

                while (interception_receive(m_interception, device = interception_wait(m_interception), (InterceptionStroke*)&stroke, 1) > 0)
                {
                    DEBUG_OUTPUT("recv << device: " << device << ", code: " << stroke.code << ", state: " << stroke.state);

                    bool cancelStroke = false;

                    if (AreStrokesEqual(stroke, m_config.fnKey, ~0x1))
                    {
                        DEBUG_OUTPUT("FN key " << (((stroke.state & INTERCEPTION_KEY_UP) != 0) ? "up" : "down"));
                        cancelStroke = true;

                        if (AreStrokesEqual(prevStroke, m_config.fnKey, ~0x1) && (stroke.state & INTERCEPTION_KEY_UP) != 0)
                        {
                            auto now = clock::now();
                            // do not count toggles that are not recent
                            if ((now - fnKeyConsecutiveToggleTime) > fnKeyConsecutiveToggleTimeout)
                            {
                                fnKeyConsecutiveToggleCount = 0;
                            }

                            fnKeyConsecutiveToggleCount++;
                            fnKeyConsecutiveToggleTime = now;
                            DEBUG_OUTPUT("FN key toggled " << fnKeyConsecutiveToggleCount << " consecutive times");

                            if (fnKeyConsecutiveToggleCount == 1)
                            {
                                SetLockedLayer(SUPERKEYS_LAYER_ID_NONE);
                            }
                            else if (fnKeyConsecutiveToggleCount == 2)
                            {
                                SetLockedLayer(SUPERKEYS_LAYER_ID_FUNCTION);
                            }
                        }

                        fnKeyState = stroke.state;
                    }
                    else
                    {
                        fnKeyConsecutiveToggleCount = 0;
                        SuperKeys_LayerId layer = m_lockedLayer;

                        if ((fnKeyState & INTERCEPTION_KEY_UP) == 0)
                        {
                            layer = SUPERKEYS_LAYER_ID_FUNCTION;
                        }

                        // if a layer is active, disable pass through
                        if (layer != SUPERKEYS_LAYER_ID_NONE)
                        {
                            cancelStroke = true;
                        }

                        auto layerEntry = m_layers.find(layer);

                        if (layerEntry != m_layers.end())
                        {
                            auto ruleMapEntry = layerEntry->second.find(stroke.code);

                            if (ruleMapEntry != layerEntry->second.end())
                            {
                                for (const auto& rule : ruleMapEntry->second)
                                {
                                    if ((rule.state & rule.mask) == (stroke.state & rule.mask))
                                    {
                                        // if the rule filter is an explicit down, suppress repeating keystrokes
                                        if ((rule.mask & 0x1) != 0 && 
                                            (rule.state & 0x1) == INTERCEPTION_KEY_DOWN && 
                                            prevStroke.code == stroke.code &&
                                            prevStroke.state == stroke.state)
                                        {
                                            continue;
                                        }

                                        // if the filter matches any direction and the rule action is complex, suppress up stroke
                                        if ((rule.mask & 0x1) == 0 &&
                                            IsComplexActionSequence(rule.actions) &&
                                            (stroke.state & INTERCEPTION_KEY_UP) != 0)
                                        {
                                            continue;
                                        }

                                        Send(rule.actions, device, stroke);
                                    }
                                }
                            }
                        }
                    }

                    prevStroke = stroke;

                    if (!cancelStroke)
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

            void Send(const vector<SuperKeys_Action>& actions, InterceptionDevice device, const InterceptionKeyStroke& strokeTemplate)
            {
                DEBUG_OUTPUT("Sending rule actions");

                for (const auto& action : actions)
                {
                    if (action.callback)
                    {
                        ActionContext context(m_interception, device, &strokeTemplate);
                        action.callback(&context);
                    }
                    else
                    {
                        vector<InterceptionKeyStroke> rawStrokes;

                        // if there is only one strokeTemplate in this action and there is one action in the sequence, base the state on the current strokeTemplate
                        if (action.nStrokes == 1 && actions.size() == 1)
                        {
                            rawStrokes.push_back(strokeTemplate);
                            rawStrokes.back().code = action.strokes[0].code;
                            rawStrokes.back().state = strokeTemplate.state & ~action.strokes[0].mask;
                            rawStrokes.back().state |= action.strokes[0].state & action.strokes[0].mask;
                        }
                        // otherwise this is a chord in an action sequence, send down strokes followed by up strokes
                        else
                        {
                            ComputeStrokes(m_interception, action.strokes, action.nStrokes, strokeTemplate, &rawStrokes);
                        }

                        interception_send(m_interception, device, (InterceptionStroke*)&rawStrokes.front(), rawStrokes.size());
                    }
                }
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
            SuperKeys_LayerId m_lockedLayer = SUPERKEYS_LAYER_ID_NONE;

            KeyboardLedControl m_ledControl;
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

void SUPERKEYS_API SuperKeys_Run(SuperKeys_EngineContext context)
{
    ((EngineContext*)context)->Run();
}

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

bool SUPERKEYS_API SuperKeys_Send(
    SuperKeys_ActionContext context, 
    const SuperKeys_KeyStroke* strokes, 
    int nStrokes)
{
    return ((ActionContext*)context)->Send(strokes, nStrokes);
}