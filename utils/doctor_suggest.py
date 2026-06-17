"""
FractureAI Doctor Suggestion System
=====================================
Recommends appropriate medical specialists based on
fracture severity, type, and body part.
"""


# ── Specialist Database ──────────────────────────────────────

SPECIALISTS = {
    "orthopedic_surgeon": {
        "title": "Orthopedic Surgeon",
        "specialty": "Bone & Joint Surgery",
        "icon": "🦴",
        "description": "Specializes in diagnosing and treating musculoskeletal conditions including fractures, joint disorders, and bone deformities.",
        "when_to_see": "For any confirmed fracture, especially if surgery may be needed.",
    },
    "trauma_surgeon": {
        "title": "Trauma Surgeon",
        "specialty": "Emergency Trauma Care",
        "icon": "🚑",
        "description": "Handles severe injuries and complex fractures requiring immediate surgical intervention.",
        "when_to_see": "For high-severity compound or displaced fractures.",
    },
    "physiotherapist": {
        "title": "Physiotherapist",
        "specialty": "Physical Rehabilitation",
        "icon": "🏃",
        "description": "Helps restore movement, strength, and function after fracture healing through targeted exercises.",
        "when_to_see": "After initial healing for rehabilitation and recovery.",
    },
    "radiologist": {
        "title": "Radiologist",
        "specialty": "Medical Imaging",
        "icon": "📡",
        "description": "Expert in reading and interpreting X-ray, CT, and MRI scans for accurate diagnosis.",
        "when_to_see": "For detailed imaging analysis and follow-up scans.",
    },
    "sports_medicine": {
        "title": "Sports Medicine Doctor",
        "specialty": "Sports Injuries",
        "icon": "⚽",
        "description": "Specializes in treating sports-related fractures and stress injuries.",
        "when_to_see": "For stress fractures or sports-related bone injuries.",
    },
    "neurosurgeon": {
        "title": "Neurosurgeon",
        "specialty": "Neurological Surgery",
        "icon": "🧠",
        "description": "Handles fractures involving the skull or spine that may affect the nervous system.",
        "when_to_see": "For skull or spinal fractures.",
    },
    "rheumatologist": {
        "title": "Rheumatologist",
        "specialty": "Bone Density & Arthritis",
        "icon": "💊",
        "description": "Evaluates and treats conditions like osteoporosis that may cause recurring fractures.",
        "when_to_see": "If fractures are related to bone density issues or arthritis.",
    },
    "general_physician": {
        "title": "General Physician",
        "specialty": "Primary Care",
        "icon": "👨‍⚕️",
        "description": "Provides initial assessment and referral to appropriate specialists.",
        "when_to_see": "For initial evaluation of minor injuries.",
    },
}


def get_doctor_recommendation(severity, fracture_type="Unknown", body_part="Unknown"):
    """
    Get doctor recommendations based on fracture analysis.

    Args:
        severity: "Low", "Medium", or "High"
        fracture_type: Detected fracture type
        body_part: Affected body part

    Returns:
        Formatted recommendation string
    """
    recommended = []

    # Always recommend based on severity
    if severity == "High":
        recommended.extend(["orthopedic_surgeon", "trauma_surgeon", "radiologist", "physiotherapist"])
    elif severity == "Medium":
        recommended.extend(["orthopedic_surgeon", "radiologist", "physiotherapist"])
    else:
        recommended.extend(["general_physician", "orthopedic_surgeon"])

    # Body-part-specific specialists
    body_lower = body_part.lower()
    if "skull" in body_lower or "head" in body_lower:
        if "neurosurgeon" not in recommended:
            recommended.insert(0, "neurosurgeon")
    if "spine" in body_lower or "back" in body_lower:
        if "neurosurgeon" not in recommended:
            recommended.insert(0, "neurosurgeon")

    # Stress fracture → sports medicine
    if "stress" in fracture_type.lower() or "hairline" in fracture_type.lower():
        if "sports_medicine" not in recommended:
            recommended.append("sports_medicine")

    # Build recommendation text
    lines = []
    lines.append("══ RECOMMENDED SPECIALISTS ══\n")

    for key in recommended:
        doc = SPECIALISTS.get(key, {})
        if doc:
            lines.append(f"{doc['icon']} {doc['title']} ({doc['specialty']})")
            lines.append(f"   {doc['description']}")
            lines.append(f"   → When to see: {doc['when_to_see']}")
            lines.append("")

    lines.append("── Important Note ──")
    lines.append("  Please consult with your primary care physician first, who can")
    lines.append("  provide appropriate referrals to the specialists listed above.")

    return "\n".join(lines)


def get_specialists_list(severity, fracture_type="Unknown", body_part="Unknown"):
    """
    Get a list of recommended specialist dictionaries (for API use).

    Returns:
        List of specialist dictionaries
    """
    recommended_keys = []

    if severity == "High":
        recommended_keys = ["orthopedic_surgeon", "trauma_surgeon", "radiologist", "physiotherapist"]
    elif severity == "Medium":
        recommended_keys = ["orthopedic_surgeon", "radiologist", "physiotherapist"]
    else:
        recommended_keys = ["general_physician", "orthopedic_surgeon"]

    body_lower = body_part.lower()
    if "skull" in body_lower or "head" in body_lower or "spine" in body_lower:
        recommended_keys.insert(0, "neurosurgeon")

    return [SPECIALISTS[k] for k in recommended_keys if k in SPECIALISTS]
