# Mock Backend – Intent API (Dry Run)

## Objectif

Mocker une API backend exposant un endpoint permettant de prévisualiser
les effets d’un contrat d’intention sans exécution réelle.

Le backend :
- ne reçoit PAS de texte libre
- ne fait PAS appel à un LLM
- ne persiste RIEN
- retourne uniquement un résultat de type "dry-run"

---

## Endpoint

### POST /api/intents/preview

---

## Contrat d'intention (JSON)

```json
{
  "intent": "DECLARE_EVENTS",
  "targets": [
    {
      "type": "CHILD",
      "reference": "Paul"
    }
  ],
  "event": {
    "category": "ACTIVITY",
    "type": "HOPSCOTCH"
  },
  "meta": {
    "source": "SPEECH",
    "confidence": 0.92
  }
}
