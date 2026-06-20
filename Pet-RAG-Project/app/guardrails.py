EMERGENCY_KEYWORDS = [
    "not breathing",
    "seizure",
    "collapsed",
    "bleeding heavily",
    "poison",
    "choking",
    "unconscious",
    "hit by car"
]

def check_guardrails(question: str):
    q = question.lower()

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in q:
            return {
                "blocked": True,
                "answer": (
                    "This may be an emergency. I cannot diagnose or provide emergency "
                    "treatment instructions. Please contact a veterinarian or emergency "
                    "animal hospital immediately."
                )
            }

    return {
        "blocked": False,
        "answer": None
    }