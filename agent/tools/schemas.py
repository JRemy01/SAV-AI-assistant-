"""Tool descriptions sent to the model (Groq / OpenAI format).

"""

STATUSES = ["En attente", "En cours", "Intervention planifiée", "Terminée"]
PRIORITIES = ["Haute", "Normale", "Basse"]
ISSUE_TYPES = [
    "Absence de chauffage",
    "Code erreur",
    "Eau chaude",
    "Entretien",
    "Pression",
]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_faq",
            "description": (
                "Recherche dans la FAQ technique des chaudières. "
                "À utiliser pour toute question de dépannage ou d'entretien "
                "(pression, eau chaude, chauffage, code erreur, odeur de gaz...). "
                "Ne pas utiliser pour le suivi d'une demande SAV."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La question du client, reformulée en quelques mots.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_request",
            "description": (
                "Retrouve des demandes SAV (statut, priorité, type de problème, "
                "dates). À utiliser pour suivre une demande précise ou lister "
                "des demandes selon des critères. Tous les filtres sont "
                "optionnels et se combinent. Retourne au plus 10 demandes, "
                "sans adresse e-mail."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "Numéro de demande, par exemple SAV-1003.",
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "Nom du client tel qu'enregistré, par exemple Client C.",
                    },
                    "status": {
                        "type": "string",
                        "enum": STATUSES,
                        "description": "Statut de la demande.",
                    },
                    "issue_type": {
                        "type": "string",
                        "enum": ISSUE_TYPES,
                        "description": "Type de problème signalé.",
                    },
                    "priority": {
                        "type": "string",
                        "enum": PRIORITIES,
                        "description": "Priorité de la demande.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sav",
            "description": (
                "Calcule les statistiques globales du SAV : nombre total de "
                "demandes, répartition par statut, par priorité et par type "
                "de problème. À utiliser pour toute question de comptage ou "
                "de vue d'ensemble. Ne jamais compter les demandes soi-même."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_email",
            "description": (
                "Prépare un BROUILLON d'e-mail pour le client d'une demande SAV. "
                "Le destinataire, l'objet et la formule de politesse sont "
                "ajoutés automatiquement à partir de la demande. "
                "N'envoie jamais l'e-mail : le brouillon doit être relu "
                "par un conseiller."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "Numéro de la demande concernée, par exemple SAV-1003.",
                    },
                    "message": {
                        "type": "string",
                        "description": (
                            "Le contenu du message uniquement, sans formule "
                            "de politesse ni signature."
                        ),
                    },
                },
                "required": ["request_id", "message"],
            },
        },
    },
]
