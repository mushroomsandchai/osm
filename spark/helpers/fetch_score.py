CATEGORY_KEYWORDS = {
    "healthcare": [
        "hospital", "clinic", "medical", "health", "doctor", "pharmacy",
        "dentist", "nurse", "ambulance", "blood", "dialysis", "ayurvedic",
        "physiother", "chiropract", "optician", "optom", "audiolog",
        "urgent_care", "nursing_home", "polyclinic", "dispensary",
        "plasma", "sanatorium", "drugstore", "drug_store", "veterinary",
    ],
    "food_access": [
        "supermark", "groce", "convenien", "bake", "butche",
        "greengroc", "deli", "farm", "food", "frui", "vegetab",
        "fishmong", "seafood", "dair", "marke", "provisi",
    ],
    "education": [
        "schoo", "universi", "colle", "kindergart", "libra",
        "language_scho", "music_scho", "trade_scho", "acade",
        "tutor", "madras", "vocationa", "prep_scho",
    ],
    "financial": [
        "bank", "atm", "credit_union", "bureau_de_change", "money_transfer",
        "pawnbroker", "money_lender", "check_cashing", "investment",
    ],
    "emergency": [
        "fire_stati", "polic", "ambulanc", "coast_guar",
        "mountain_rescu", "rescu", "first_ai",
    ],
    "green_space": [
        "park", "garden", "nature_reserve", "playground", "recreation",
        "dog_park", "community_garden", "national_park",
    ],
    "transport": [
        "bus_station", "bus_stop", "train_station", "ferry", "taxi",
        "airport", "parking",
    ],
    "food_and_drink": [
        "restaurant", "cafe", "pub", "bar", "fast_food", "biergarten",
        "food_court", "canteen", "dining",
    ],
}

WEIGHTS = {
    "healthcare": 1, "food_access": 0.9, "emergency": 0.7,
    "education": 0.8, "financial": 0.6, "transport": 0.75,
    "green_space": 0.78, "food_and_drink": 0.2,
}

def score_tag(tag: str | None) -> float | None:
    if not tag:
        return 0
    
    tag_lower = tag.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in tag_lower:
                return WEIGHTS.get(category, 0.1)
                
    return 0.1
