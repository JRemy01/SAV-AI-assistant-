from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agent import agent
from agent.tools.schemas import TOOLS


def reply(content=None, tool_calls=None):
    #fake Groq response
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def tool_call(call_id, name, arguments="{}"):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def fake_client(*responses):
    client = MagicMock()
    client.chat.completions.create.side_effect = list(responses)
    return client


def test_answers_directly_without_tools():
    client = fake_client(reply("Bonjour, je suis l'assistant du SAV."))

    with patch.object(agent, "get_llm_client", return_value=client):
        answer = agent.run_agent("Bonjour")

    assert answer == "Bonjour, je suis l'assistant du SAV."
    assert client.chat.completions.create.call_count == 1
    assert client.chat.completions.create.call_args.kwargs["tools"] == TOOLS


def test_runs_tool_then_sends_result_back():
    client = fake_client(
        reply(tool_calls=[tool_call("call_1", "analyze_sav")]),
        reply("Il y a 4 demandes en attente."),
    )

    with patch.object(agent, "get_llm_client", return_value=client):
        answer = agent.run_agent("Combien de demandes en attente ?")

    assert answer == "Il y a 4 demandes en attente."
    assert client.chat.completions.create.call_count == 2

    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assistant, tool = messages[-2], messages[-1]
    assert assistant["role"] == "assistant"
    assert assistant["tool_calls"][0]["id"] == "call_1"
    assert tool["role"] == "tool"
    assert tool["tool_call_id"] == "call_1"
    assert '"En attente": 4' in tool["content"]


def test_stops_after_step_limit():
    stuck = [reply(tool_calls=[tool_call(f"call_{i}", "analyze_sav")]) for i in range(3)]
    client = fake_client(*stuck)

    with patch.object(agent, "get_llm_client", return_value=client):
        answer = agent.run_agent("Question sans fin", step=3)

    assert client.chat.completions.create.call_count == 3
    assert "contacter le SAV" in answer


def test_sends_history_trimmed_to_max():
    history = []
    for i in range(agent.MAX_HISTORY // 2 + 1):
        history += [
            {"role": "user", "content": f"question {i}"},
            {"role": "assistant", "content": f"réponse {i}"},
        ]
    client = fake_client(reply("ok"))

    with patch.object(agent, "get_llm_client", return_value=client):
        agent.run_agent("nouvelle question", history)

    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1:-1] == history[-agent.MAX_HISTORY:]
    assert messages[-1] == {"role": "user", "content": "nouvelle question"}
    assert len(history) == agent.MAX_HISTORY + 2  # caller's list untouched
