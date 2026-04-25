"""
FractureAI Clinic & Hospital Directory
=========================================
Provides nearby orthopedic clinics, hospitals, and
specialist centers for fracture treatment.
"""

# ── Clinic / Hospital Database ─────────────────────────────────
# In production, this would integrate with Google Maps API or a real database.

CLINICS = [
    {
        "id": 1,
        "name": "Apollo Orthopedic Center",
        "type": "hospital",
        "specialty": "Orthopedics & Trauma Surgery",
        "rating": 4.8,
        "reviews": 2340,
        "address": "21, Greams Lane, Off Greams Road, Chennai, TN 600006",
        "phone": "+91 44 2829 3333",
        "hours": "24/7 Emergency | OPD: 8AM-8PM",
        "lat": 13.0604,
        "lng": 80.2496,
        "doctors": [
            {"name": "Dr. Rajesh Kumar", "specialty": "Orthopedic Surgeon", "experience": "22 years"},
            {"name": "Dr. Priya Sharma", "specialty": "Trauma Specialist", "experience": "15 years"},
        ],
        "amenities": ["Emergency Care", "Advanced Imaging", "Physiotherapy", "Pharmacy"],
        "insurance": ["Star Health", "HDFC Ergo", "Bajaj Allianz", "ICICI Lombard"],
    },
    {
        "id": 2,
        "name": "Fortis Bone & Joint Institute",
        "type": "hospital",
        "specialty": "Joint Replacement & Fracture Care",
        "rating": 4.7,
        "reviews": 1890,
        "address": "154/11, Bannerghatta Road, Bengaluru, KA 560076",
        "phone": "+91 80 6621 4444",
        "hours": "24/7 Emergency | OPD: 9AM-7PM",
        "lat": 12.8906,
        "lng": 77.5972,
        "doctors": [
            {"name": "Dr. Anil Mehta", "specialty": "Joint Replacement", "experience": "18 years"},
            {"name": "Dr. Sunita Reddy", "specialty": "Sports Medicine", "experience": "12 years"},
        ],
        "amenities": ["24/7 Emergency", "MRI & CT Scan", "Rehabilitation Center", "Cafeteria"],
        "insurance": ["Max Bupa", "Star Health", "New India Assurance", "United India"],
    },
    {
        "id": 3,
        "name": "Max Super Specialty Hospital",
        "type": "hospital",
        "specialty": "Multi-Specialty Orthopedics",
        "rating": 4.6,
        "reviews": 3120,
        "address": "1, 2, Press Enclave Road, Saket, New Delhi, DL 110017",
        "phone": "+91 11 2651 5050",
        "hours": "24/7 Emergency | OPD: 8AM-9PM",
        "lat": 28.5244,
        "lng": 77.2066,
        "doctors": [
            {"name": "Dr. Vivek Singh", "specialty": "Spine Surgery", "experience": "20 years"},
            {"name": "Dr. Meena Gupta", "specialty": "Pediatric Orthopedics", "experience": "14 years"},
        ],
        "amenities": ["Emergency", "Robotic Surgery", "Physical Therapy", "Lab Services"],
        "insurance": ["CGHS", "Star Health", "HDFC Ergo", "Religare"],
    },
    {
        "id": 4,
        "name": "OrthoCure Clinic",
        "type": "clinic",
        "specialty": "Orthopedic Rehabilitation",
        "rating": 4.5,
        "reviews": 580,
        "address": "B-12, Sector 62, Noida, UP 201301",
        "phone": "+91 120 496 6677",
        "hours": "Mon-Sat: 9AM-6PM",
        "lat": 28.6271,
        "lng": 77.3651,
        "doctors": [
            {"name": "Dr. Amit Patel", "specialty": "Physiotherapy", "experience": "10 years"},
        ],
        "amenities": ["Physiotherapy", "X-Ray", "Casting", "Bracing"],
        "insurance": ["Star Health", "Bajaj Allianz"],
    },
    {
        "id": 5,
        "name": "AIIMS Trauma Center",
        "type": "hospital",
        "specialty": "Level 1 Trauma Center",
        "rating": 4.9,
        "reviews": 5600,
        "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi, DL 110029",
        "phone": "+91 11 2658 8500",
        "hours": "24/7 (Government Hospital)",
        "lat": 28.5672,
        "lng": 77.2100,
        "doctors": [
            {"name": "Dr. R.K. Sharma", "specialty": "Trauma Surgery", "experience": "25 years"},
            {"name": "Dr. S. Krishnamurthy", "specialty": "Orthopedic Surgery", "experience": "20 years"},
        ],
        "amenities": ["Level 1 Trauma", "Advanced Imaging", "ICU", "Blood Bank"],
        "insurance": ["CGHS", "ESI", "Ayushman Bharat", "ECHS"],
    },
    {
        "id": 6,
        "name": "Manipal Hospital Fracture Clinic",
        "type": "clinic",
        "specialty": "Fracture Management & Sports Injuries",
        "rating": 4.4,
        "reviews": 920,
        "address": "98, HAL Airport Road, Bengaluru, KA 560017",
        "phone": "+91 80 2502 4444",
        "hours": "Mon-Sat: 8AM-8PM | Sun: 9AM-1PM",
        "lat": 12.9588,
        "lng": 77.6480,
        "doctors": [
            {"name": "Dr. Karthik Rao", "specialty": "Sports Orthopedics", "experience": "13 years"},
        ],
        "amenities": ["Digital X-Ray", "Physiotherapy", "Minor Surgery", "Pharmacy"],
        "insurance": ["Star Health", "HDFC Ergo", "Bajaj Allianz", "Max Bupa"],
    },
    {
        "id": 7,
        "name": "Medanta - The Medicity",
        "type": "hospital",
        "specialty": "Advanced Orthopedic Surgery",
        "rating": 4.7,
        "reviews": 4200,
        "address": "CH Baktawar Singh Rd, Sector 38, Gurugram, HR 122001",
        "phone": "+91 124 414 1414",
        "hours": "24/7 Emergency | OPD: 8AM-8PM",
        "lat": 28.4395,
        "lng": 77.0420,
        "doctors": [
            {"name": "Dr. Ashok Rajgopal", "specialty": "Knee Replacement", "experience": "30 years"},
            {"name": "Dr. Nidhi Bansal", "specialty": "Hand & Wrist Surgery", "experience": "16 years"},
        ],
        "amenities": ["Robotic Surgery", "Rehab Center", "Emergency", "Research Lab"],
        "insurance": ["CGHS", "Star Health", "New India", "National Insurance"],
    },
    {
        "id": 8,
        "name": "BoneFirst Physiotherapy Center",
        "type": "clinic",
        "specialty": "Post-Fracture Rehabilitation",
        "rating": 4.6,
        "reviews": 340,
        "address": "45, Anna Salai, Teynampet, Chennai, TN 600018",
        "phone": "+91 44 2434 5678",
        "hours": "Mon-Fri: 7AM-7PM | Sat: 8AM-2PM",
        "lat": 13.0389,
        "lng": 80.2517,
        "doctors": [
            {"name": "Dr. Kavitha Narayanan", "specialty": "Physiotherapy & Rehab", "experience": "11 years"},
        ],
        "amenities": ["Hydrotherapy", "Electrotherapy", "Exercise Lab", "Ergonomic Assessment"],
        "insurance": ["Star Health", "Bajaj Allianz"],
    },
]


def get_all_clinics():
    """Return all clinics in the directory."""
    return CLINICS


def get_clinic_by_id(clinic_id):
    """Get a specific clinic by ID."""
    for clinic in CLINICS:
        if clinic["id"] == clinic_id:
            return clinic
    return None


def get_clinics_by_type(clinic_type):
    """Filter clinics by type (hospital/clinic)."""
    return [c for c in CLINICS if c["type"] == clinic_type]


def search_clinics(query):
    """Search clinics by name, specialty, or address."""
    query = query.lower()
    results = []
    for clinic in CLINICS:
        if (query in clinic["name"].lower()
                or query in clinic["specialty"].lower()
                or query in clinic["address"].lower()):
            results.append(clinic)
    return results
