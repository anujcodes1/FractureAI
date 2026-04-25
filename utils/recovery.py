"""
FractureAI AI Recovery Suggestions
====================================
Generates personalized recovery suggestions based on
fracture severity, type, and body part.
"""


# ── Recovery Knowledge Base ──────────────────────────────────
# Organized by severity level with detailed medical guidance.

RECOVERY_DATABASE = {
    "Low": {
        "general": [
            "Rest the affected area and avoid putting stress on it.",
            "Apply ice packs for 15-20 minutes every 2-3 hours to reduce swelling.",
            "Use over-the-counter pain relievers as directed (e.g., ibuprofen).",
            "Keep the injured area elevated when possible.",
            "Follow up with your doctor in 1-2 weeks for re-evaluation.",
        ],
        "diet": [
            "Increase calcium intake (dairy products, leafy greens, fortified foods).",
            "Ensure adequate Vitamin D (sunlight exposure, supplements).",
            "Consume protein-rich foods to support bone tissue repair.",
            "Stay hydrated — aim for 8-10 glasses of water daily.",
        ],
        "timeline": "Expected recovery: 3-6 weeks with proper care.",
        "exercises": [
            "Gentle range-of-motion exercises as pain allows (after 1-2 weeks).",
            "Light stretching to prevent stiffness (consult physiotherapist).",
        ],
    },
    "Medium": {
        "general": [
            "Immobilize the area with a splint or cast as prescribed by your doctor.",
            "Take prescribed pain medications on schedule.",
            "Avoid weight-bearing activities on the affected area.",
            "Attend all follow-up appointments for progress monitoring.",
            "Consider physical therapy once initial healing is confirmed.",
        ],
        "diet": [
            "High-calcium diet is essential (1200-1500 mg daily).",
            "Vitamin D supplementation (1000-2000 IU daily, as advised).",
            "Anti-inflammatory foods: berries, fatty fish, turmeric, green tea.",
            "Avoid alcohol and smoking — they significantly slow bone healing.",
            "Zinc-rich foods (nuts, seeds, legumes) to accelerate tissue repair.",
        ],
        "timeline": "Expected recovery: 6-12 weeks. Physical therapy may be needed.",
        "exercises": [
            "Begin rehabilitation exercises only after doctor's clearance.",
            "Isometric exercises to maintain muscle strength without moving the joint.",
            "Gradual return to normal activities over 4-6 weeks post-immobilization.",
        ],
    },
    "High": {
        "general": [
            "URGENT: Seek immediate orthopedic consultation if not already done.",
            "Surgical intervention may be required — discuss options with your surgeon.",
            "Complete immobilization is critical — do not attempt to use the affected area.",
            "Take all prescribed medications including antibiotics if prescribed.",
            "Regular X-ray follow-ups to monitor healing progress.",
            "Consider a second opinion from a specialized trauma surgeon.",
        ],
        "diet": [
            "Aggressive nutritional support is essential for recovery.",
            "High-protein diet (1.5-2g per kg body weight) to support tissue rebuilding.",
            "Calcium and Vitamin D supplementation as prescribed by your doctor.",
            "Omega-3 fatty acids (fish oil) to reduce inflammation.",
            "Vitamin C-rich foods for collagen synthesis (citrus fruits, bell peppers).",
            "Avoid processed foods, excess sugar, and caffeine.",
        ],
        "timeline": "Expected recovery: 3-6 months. Surgery + Physical therapy likely required.",
        "exercises": [
            "NO exercises until cleared by your orthopedic surgeon.",
            "Post-surgical rehabilitation will be planned by your physiotherapist.",
            "Recovery exercises will be gradual and closely monitored.",
            "Occupational therapy may be recommended for daily activity adaptation.",
        ],
    },
}

# ── Body Part Specific Advice ────────────────────────────────

BODY_PART_ADVICE = {
    "hand": "Avoid gripping objects tightly. Use a wrist splint if recommended.",
    "wrist": "Keep the wrist immobilized. Avoid typing or repetitive hand movements.",
    "arm": "Use a sling to support the arm. Avoid lifting heavy objects.",
    "elbow": "Keep the elbow at a comfortable angle. Avoid bending-straightening repeatedly.",
    "shoulder": "Use a shoulder immobilizer. Sleep in a reclined position if needed.",
    "leg": "Use crutches for mobility. Avoid weight-bearing on the affected leg.",
    "knee": "Use a knee brace. Avoid stairs and squatting movements.",
    "ankle": "Use an ankle boot or cast. Keep it elevated to reduce swelling.",
    "foot": "Wear a protective boot. Avoid walking barefoot.",
    "hip": "Minimize movement. Use a walker or wheelchair as advised.",
    "spine": "Strict bed rest may be required. Follow neurosurgeon's advice.",
    "rib": "Breathe normally to prevent pneumonia. Avoid tight wrapping around chest.",
    "skull": "URGENT: Immediate neurological evaluation required.",
}


def get_recovery_suggestions(severity, fracture_type="Unknown", body_part="Unknown"):
    """
    Generate personalized recovery suggestions.

    Args:
        severity: "Low", "Medium", or "High"
        fracture_type: Type of fracture detected
        body_part: Affected body part

    Returns:
        Formatted string with recovery suggestions
    """
    data = RECOVERY_DATABASE.get(severity, RECOVERY_DATABASE["Low"])

    lines = []
    lines.append(f"══ RECOVERY PLAN ({severity.upper()} SEVERITY) ══\n")
    lines.append(f"Fracture Type: {fracture_type}")
    lines.append(f"Affected Area: {body_part}\n")

    # General care instructions
    lines.append("── General Care ──")
    for tip in data["general"]:
        lines.append(f"  • {tip}")
    lines.append("")

    # Diet recommendations
    lines.append("── Nutrition & Diet ──")
    for tip in data["diet"]:
        lines.append(f"  • {tip}")
    lines.append("")

    # Exercise guidance
    lines.append("── Exercise & Rehabilitation ──")
    for tip in data["exercises"]:
        lines.append(f"  • {tip}")
    lines.append("")

    # Timeline
    lines.append(f"── Timeline ──")
    lines.append(f"  {data['timeline']}")
    lines.append("")

    # Body part specific advice
    body_lower = body_part.lower()
    for key, advice in BODY_PART_ADVICE.items():
        if key in body_lower:
            lines.append(f"── {body_part}-Specific Advice ──")
            lines.append(f"  • {advice}")
            lines.append("")
            break

    return "\n".join(lines)
