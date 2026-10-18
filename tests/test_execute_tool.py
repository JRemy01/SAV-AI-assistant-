import inspect
import json
from unittest.mock import patch

from agent.tools.execute_tool import ALLOWS_TOOLS, execute_tool
from agent.tools.schemas import TOOLS


def run(name, arguments):
    return json.loads(execute_tool(name, arguments))


# execute_tool

def test_valid_call_returns_tool_result():
    result = run("lookup_request", '{"request_id": "SAV-1003"}')
    assert result[0]["status"] == "En cours"


def test_unknown_tool_returns_error():
    assert "error" in run("send_email", "{}")


def test_malformed_json_returns_error():
    assert "error" in run("lookup_request", "{bad json")


def test_missing_parameter_error_names_it():
    result = run("prepare_email", '{"request_id": "SAV-1003"}')
    assert "message" in result["error"]


def test_tool_crash_returns_generic_error():
    def broken():
        raise RuntimeError("/secret/path/sav_requests.csv not found")

    with patch.dict(ALLOWS_TOOLS, {"analyze_sav": broken}):
        result = run("analyze_sav", "")

    assert "error" in result
    assert "/secret/path" not in result["error"]
