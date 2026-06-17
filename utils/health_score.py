"""
FractureAI Health Score Calculator
====================================
Computes an overall bone health score (0-100) based on
scan history, severity, fracture frequency, and trends.
"""


def calculate_health_score(scans):
    """
    Calculate a comprehensive health score from scan history.

    Args:
        scans: List of Scan objects for a user

    Returns:
        Dictionary with score, grade, color, and breakdown
    """
    if not scans:
        return {
            "score": 100,
            "grade": "A+",
            "color": "emerald",
            "label": "Excellent",
            "breakdown": {
                "fracture_ratio": {"score": 100, "label": "No fractures detected"},
                "severity_impact": {"score": 100, "label": "No severity concerns"},
                "trend": {"score": 100, "label": "No data yet"},
                "frequency": {"score": 100, "label": "No concerning patterns"},
            },
            "tips": [
                "Keep monitoring your bone health regularly.",
                "Maintain a calcium-rich diet for strong bones.",
                "Regular exercise helps maintain bone density.",
            ],
        }

    total = len(scans)
    fractures = [s for s in scans if s.fracture_detected]
    fracture_count = len(fractures)
    normal_count = total - fracture_count

    # ── Component 1: Fracture Ratio Score (40% weight) ──
    fracture_ratio = fracture_count / total if total > 0 else 0
    ratio_score = max(0, 100 - (fracture_ratio * 100 * 1.2))

    if fracture_count == 0:
        ratio_label = "No fractures detected"
    elif fracture_ratio < 0.25:
        ratio_label = f"Low fracture rate ({fracture_count}/{total} scans)"
    elif fracture_ratio < 0.5:
        ratio_label = f"Moderate fracture rate ({fracture_count}/{total} scans)"
    else:
        ratio_label = f"High fracture rate ({fracture_count}/{total} scans)"

    # ── Component 2: Severity Impact (30% weight) ──
    severity_weights = {"Low": 15, "Medium": 35, "High": 60, "N/A": 0}
    severity_penalty = 0
    for s in fractures:
        severity_penalty += severity_weights.get(s.severity, 0)

    if fracture_count > 0:
        avg_severity_penalty = severity_penalty / fracture_count
    else:
        avg_severity_penalty = 0
    severity_score = max(0, 100 - avg_severity_penalty)

    if avg_severity_penalty == 0:
        severity_label = "No severity concerns"
    elif avg_severity_penalty < 20:
        severity_label = "Mostly low severity fractures"
    elif avg_severity_penalty < 40:
        severity_label = "Some medium severity fractures"
    else:
        severity_label = "High severity fractures present"

    # ── Component 3: Trend Score (20% weight) ──
    trend_score = 80
    trend_label = "Stable"
    if total >= 3:
        recent = scans[:3]  # Already sorted newest first
        older = scans[3:]
        recent_fractures = sum(1 for s in recent if s.fracture_detected)
        if older:
            older_fractures = sum(1 for s in older if s.fracture_detected) / len(older)
            recent_rate = recent_fractures / 3

            if recent_rate < older_fractures:
                trend_score = 90
                trend_label = "Improving - fewer recent fractures"
            elif recent_rate > older_fractures:
                trend_score = 50
                trend_label = "Concerning - more recent fractures"
            else:
                trend_score = 70
                trend_label = "Stable trend"
        else:
            if recent_fractures == 0:
                trend_score = 95
                trend_label = "All recent scans normal"
            elif recent_fractures >= 2:
                trend_score = 40
                trend_label = "Multiple recent fractures"

    # ── Component 4: Frequency Score (10% weight) ──
    frequency_score = 85
    freq_label = "No concerning patterns"
    if fracture_count >= 5:
        frequency_score = 30
        freq_label = "Frequent fractures - possible underlying condition"
    elif fracture_count >= 3:
        frequency_score = 55
        freq_label = "Multiple fractures detected"
    elif fracture_count >= 1:
        frequency_score = 75
        freq_label = "Occasional fracture"

    # ── Final Weighted Score ──
    final_score = round(
        ratio_score * 0.40
        + severity_score * 0.30
        + trend_score * 0.20
        + frequency_score * 0.10
    )
    final_score = max(0, min(100, final_score))

    # Determine grade
    if final_score >= 90:
        grade, color, label = "A+", "emerald", "Excellent"
    elif final_score >= 80:
        grade, color, label = "A", "green", "Very Good"
    elif final_score >= 70:
        grade, color, label = "B", "cyan", "Good"
    elif final_score >= 60:
        grade, color, label = "C", "amber", "Fair"
    elif final_score >= 45:
        grade, color, label = "D", "orange", "Needs Attention"
    else:
        grade, color, label = "F", "red", "Critical"

    # Generate tips
    tips = _generate_tips(final_score, fracture_count, scans)

    return {
        "score": final_score,
        "grade": grade,
        "color": color,
        "label": label,
        "breakdown": {
            "fracture_ratio": {"score": round(ratio_score), "label": ratio_label},
            "severity_impact": {"score": round(severity_score), "label": severity_label},
            "trend": {"score": round(trend_score), "label": trend_label},
            "frequency": {"score": round(frequency_score), "label": freq_label},
        },
        "tips": tips,
    }


def _generate_tips(score, fracture_count, scans):
    """Generate health tips based on score and history."""
    tips = []

    if score >= 80:
        tips.append("Your bone health looks great! Keep up with regular check-ups.")
        tips.append("Continue maintaining a balanced diet rich in calcium and Vitamin D.")
    elif score >= 60:
        tips.append("Consider increasing calcium-rich foods in your diet.")
        tips.append("Regular weight-bearing exercises can strengthen bones.")
        tips.append("Schedule a bone density test (DEXA scan) with your doctor.")
    else:
        tips.append("IMPORTANT: Consult an orthopedic specialist for comprehensive evaluation.")
        tips.append("A bone density test (DEXA scan) is strongly recommended.")
        tips.append("Discuss calcium and Vitamin D supplementation with your doctor.")
        tips.append("Consider lifestyle changes to reduce fracture risk.")

    if fracture_count > 0:
        high_severity = sum(1 for s in scans if s.severity == "High")
        if high_severity > 0:
            tips.append("You have had high-severity fractures. Follow-up care is essential.")

    return tips


def get_clinical_suggestions(scan):
    """
    Generate detailed clinical suggestions for a specific scan.

    Args:
        scan: A Scan object with diagnosis data

    Returns:
        Dictionary with clinical analysis sections
    """
    suggestions = {
        "immediate_actions": [],
        "follow_up": [],
        "precautions": [],
        "rehabilitation": [],
        "lifestyle": [],
    }

    if not scan.fracture_detected:
        suggestions["immediate_actions"] = [
            "No immediate medical intervention required.",
            "Continue normal activities with reasonable caution.",
        ]
        suggestions["follow_up"] = [
            "Routine follow-up in 6-12 months is recommended.",
            "Report any new pain or discomfort to your doctor.",
        ]
        suggestions["lifestyle"] = [
            "Maintain regular physical activity for bone strength.",
            "Ensure adequate calcium (1000-1200mg/day) and Vitamin D (600-800 IU/day).",
            "Avoid smoking and excessive alcohol consumption.",
        ]
        return suggestions

    # Fracture detected — generate detailed suggestions
    severity = scan.severity
    body_part = (scan.body_part or "Unknown").lower()

    # Immediate actions
    if severity == "High":
        suggestions["immediate_actions"] = [
            "URGENT: Seek immediate orthopedic consultation.",
            "Complete immobilization of the affected area is critical.",
            "Pain management with prescribed medications (avoid self-medication).",
            "Surgical evaluation may be necessary — discuss with your surgeon.",
            "CT/MRI scan recommended for detailed fracture assessment.",
        ]
    elif severity == "Medium":
        suggestions["immediate_actions"] = [
            "Schedule an orthopedic appointment within 24-48 hours.",
            "Immobilize the area with a splint, cast, or brace.",
            "Use prescribed pain medication as directed.",
            "Apply ice for 15-20 minutes every 2-3 hours to reduce swelling.",
        ]
    else:
        suggestions["immediate_actions"] = [
            "Rest the affected area and avoid strenuous activities.",
            "Over-the-counter pain relief (ibuprofen/acetaminophen) as needed.",
            "Apply ice packs for swelling management.",
            "Monitor for worsening symptoms.",
        ]

    # Follow-up
    suggestions["follow_up"] = [
        f"Follow-up X-ray in {'2 weeks' if severity == 'High' else '3-4 weeks'} to assess healing.",
        "Regular orthopedic visits until fracture is fully healed.",
        "Bone density assessment if recurrent fractures occur.",
        "Physical therapy evaluation once initial healing begins.",
    ]

    # Precautions
    if "arm" in body_part or "hand" in body_part or "wrist" in body_part:
        suggestions["precautions"] = [
            "Avoid lifting objects with the affected arm.",
            "Use a sling for support during daily activities.",
            "Keep the arm elevated above heart level when resting.",
            "Avoid driving until cleared by your physician.",
        ]
    elif "leg" in body_part or "foot" in body_part or "ankle" in body_part:
        suggestions["precautions"] = [
            "Use crutches or walker for mobility — avoid weight-bearing.",
            "Keep the leg elevated to reduce swelling.",
            "Do not attempt to walk on the injured limb without support.",
            "Wear protective footwear or boot as prescribed.",
        ]
    elif "spine" in body_part or "back" in body_part:
        suggestions["precautions"] = [
            "Strict bed rest may be required — follow neurosurgeon's advice.",
            "Use a back brace if prescribed.",
            "Avoid bending, twisting, or lifting.",
            "Sleep on a firm mattress with proper support.",
        ]
    else:
        suggestions["precautions"] = [
            "Protect the injured area from further impact.",
            "Follow all immobilization instructions from your doctor.",
            "Report any numbness, tingling, or discoloration immediately.",
            "Keep follow-up appointments without fail.",
        ]

    # Rehabilitation
    if severity == "High":
        suggestions["rehabilitation"] = [
            "Physical therapy will begin 6-8 weeks after surgery/casting.",
            "Expect a gradual 3-6 month rehabilitation program.",
            "Progressive weight-bearing as tolerated and guided by PT.",
            "Occupational therapy for daily task adaptation if needed.",
        ]
    elif severity == "Medium":
        suggestions["rehabilitation"] = [
            "Begin gentle exercises 4-6 weeks after injury (with approval).",
            "Gradual return to normal activities over 6-10 weeks.",
            "Strengthening exercises to rebuild muscle around the fracture site.",
            "Balance and proprioception training if lower extremity involved.",
        ]
    else:
        suggestions["rehabilitation"] = [
            "Light range-of-motion exercises can start after 2-3 weeks.",
            "Full activity can resume in 4-6 weeks with proper healing.",
            "Stretching exercises to prevent stiffness.",
        ]

    # Lifestyle
    suggestions["lifestyle"] = [
        "Increase calcium intake: dairy, leafy greens, fortified foods.",
        "Vitamin D supplementation (sunlight + 1000-2000 IU/day).",
        "High-protein diet to support bone tissue repair.",
        "Avoid smoking and limit alcohol (both impair bone healing).",
        "Stay hydrated — aim for 8-10 glasses of water daily.",
        "Anti-inflammatory foods: berries, turmeric, fatty fish, nuts.",
    ]

    return suggestions
