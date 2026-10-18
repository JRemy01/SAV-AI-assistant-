from agent.tools.analyze_sav import analyze_sav
from agent.tools.lookup_request import lookup_request
from agent.tools.prepare_email import prepare_email
from agent.tools.search_faq import search_faq
import json


ALLOWS_TOOLS= {
    "search_faq": search_faq,
    "lookup_request": lookup_request,
    "analyze_sav": analyze_sav,
    "prepare_email": prepare_email,
}



def to_json(data):
    return json.dumps(data, ensure_ascii=False, default=str)


def execute_tool(name,arguments):
    if name not in ALLOWS_TOOLS:
        return to_json({"error": f"Outil inconnu : {name}"})

    try:
        args = json.loads(arguments) if arguments else {}

    except json.JSONDecodeError:
        return to_json({"error": "Arguments invalides (JSON mal formé)."})

    function = ALLOWS_TOOLS[name]

    try :
        result = function(**args)
    except TypeError as error:
        return to_json({"error": f"Paramètres incorrects : {error}"})
    except Exception as error:
        print(f"[execute_tool] {name} failed: {error!r}")
        return to_json({"error": "L'outil a rencontré une erreur."})

    return to_json(result)
