from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))

from services.chatbot import answer_question


questions = [
    "Comment vérifier la pression de ma chaudière ?",
    "Que faire si je n'ai plus d'eau chaude ?",
    "Que faire si je sens une odeur de gaz ?",
    "Quelle est la capitale du Japon ?",
]

if __name__ == "__main__":
    for question in questions:
        print(f"\nQuestion : {question}")
        result = answer_question(question)
        print(f"Réponse : {result}")