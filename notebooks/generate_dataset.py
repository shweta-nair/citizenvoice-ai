"""
CitizenVoice AI - Synthetic Dataset Generator
Generates ~1000 realistic citizen-support call transcripts across 10 complaint
categories and 10 Kerala districts, with ground-truth labels for:
    - department (classification target)
    - sentiment (Positive / Neutral / Negative)
    - priority (Low / Medium / High / Critical)

Run:  python notebooks/generate_dataset.py
Output: data/conversations.csv
"""

import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

# --------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------

DISTRICTS = [
    "Ernakulam", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Alappuzha",
    "Kannur", "Kottayam", "Palakkad", "Idukki", "Wayanad",
]

CATEGORY_TO_DEPARTMENT = {
    "Water Supply": "Water Authority",
    "Electricity": "Electricity Board",
    "Roads": "Public Works Department",
    "Waste Management": "Municipal Corporation",
    "Healthcare": "Health Department",
    "Transport": "Transport Department",
    "Education": "Education Department",
    "Internet Services": "IT & Telecom Department",
    "Public Safety": "Police Department",
    "Government Documentation": "Revenue Department",
}

LOCALITIES = [
    "Market Road", "Temple Junction", "Bus Stand area", "Civil Station Road",
    "Ward 7", "Ward 12", "MG Road", "Railway Station Road", "School Lane",
    "Hospital Road", "New Bypass", "Panchayat Office area", "Beach Road",
    "Industrial Estate", "Collectorate Road",
]

# Each category has: opener templates, body templates (with severity tiers),
# and closing templates. Severity tier drives priority + sentiment.

CATEGORY_TEMPLATES = {
    "Water Supply": {
        "critical": [
            "there has been no water supply at all for {days} days now and the entire {locality} area is affected",
            "the main pipeline burst near {locality} and is flooding the street while we have zero water at home",
            "our tank water tested positive for contamination and several people in {locality} have fallen ill",
        ],
        "high": [
            "water supply has been irregular for {days} days, we only get water for an hour in the morning",
            "the water pressure in {locality} has dropped so badly that upper floors get nothing",
            "we have been getting muddy, discoloured water from the tap for {days} days",
        ],
        "medium": [
            "water supply timing has shifted without any notice and it is inconvenient for working families",
            "there is a minor leak near the {locality} junction that is wasting a lot of water",
        ],
        "low": [
            "I wanted to ask about the new water connection application status",
            "could you tell me the schedule for water supply in {locality} this week",
        ],
    },
    "Electricity": {
        "critical": [
            "a transformer exploded near {locality} and the entire area has had no electricity since last night",
            "a live wire has fallen on the road near {locality} and it is extremely dangerous, someone could get electrocuted",
            "there has been a major power outage for {days} days affecting the whole {locality} ward",
        ],
        "high": [
            "we are having frequent power cuts of {days} hours every day without prior notice",
            "there has been a sudden voltage fluctuation that damaged two appliances in our house",
            "the streetlights on {locality} have not worked for {days} days and it is unsafe at night",
        ],
        "medium": [
            "our electricity bill this month seems unusually high and I want it checked",
            "the meter reading at our {locality} residence appears to be incorrect",
        ],
        "low": [
            "I want to know the process for a new electricity connection",
            "can you tell me when the next scheduled maintenance shutdown is for {locality}",
        ],
    },
    "Roads": {
        "critical": [
            "a massive pothole on {locality} caused a bike accident yesterday and someone was injured",
            "the bridge near {locality} has developed a large crack and people are afraid to use it",
            "heavy rain has completely washed away part of the road near {locality}, it is impassable",
        ],
        "high": [
            "the road in {locality} has been full of potholes for {days} days and vehicles keep getting damaged",
            "there is no streetlight and no road markings on the new stretch near {locality}, accidents are increasing",
            "construction debris has been left on {locality} for {days} days blocking half the road",
        ],
        "medium": [
            "the road resurfacing work near {locality} has been incomplete for a while now",
            "drainage on the side of the {locality} road is broken and water pools on the street",
        ],
        "low": [
            "I wanted to suggest adding a speed bump near the school on {locality}",
            "when is the road widening project near {locality} expected to start",
        ],
    },
    "Waste Management": {
        "critical": [
            "garbage has not been collected in {locality} for {days} days and it has become a health hazard with rats everywhere",
            "a fire broke out at the open waste dumping site near {locality} and smoke is spreading into homes",
        ],
        "high": [
            "waste collection has been irregular in {locality} for {days} days and the smell is unbearable",
            "people are dumping waste illegally near {locality} and it is attracting stray animals",
        ],
        "medium": [
            "we would like a second waste bin for our street in {locality}",
            "the waste collection timing in {locality} keeps changing without notice",
        ],
        "low": [
            "I want to know the schedule for the door to door waste collection",
            "can you share details about the new segregation rules for {locality}",
        ],
    },
    "Healthcare": {
        "critical": [
            "the primary health centre in {locality} has no doctor available and a patient is in critical condition",
            "there is a dengue outbreak in {locality} and the hospital says they are out of essential medicines",
        ],
        "high": [
            "the government hospital in {locality} has been short staffed for {days} days and patients are waiting for hours",
            "the ambulance service for {locality} took over an hour to respond to an emergency call",
        ],
        "medium": [
            "I want to raise a concern about cleanliness at the {locality} health centre",
            "the medicine stock at the {locality} dispensary seems to be running low",
        ],
        "low": [
            "I wanted to know the opening hours of the {locality} primary health centre",
            "can you tell me how to register for the free health camp next week",
        ],
    },
    "Transport": {
        "critical": [
            "a public bus broke down in the middle of the highway near {locality} and passengers were stranded for hours",
            "the bus driver on the {locality} route was driving recklessly and nearly caused an accident",
        ],
        "high": [
            "buses on the {locality} route have been cancelled for {days} days without any announcement",
            "the auto stand near {locality} has overcharging issues that have continued for {days} days",
        ],
        "medium": [
            "the bus frequency on the {locality} route has reduced and commuters are facing delays",
            "the bus shelter near {locality} is damaged and offers no protection from rain",
        ],
        "low": [
            "I want to know the new bus timings for the {locality} route",
            "could you share information about the senior citizen travel concession",
        ],
    },
    "Education": {
        "critical": [
            "the government school building in {locality} has a collapsed section of roof and classes are unsafe",
            "there has been no teacher for an entire subject at the {locality} school for {days} days now",
        ],
        "high": [
            "the {locality} school has been without proper toilets for {days} days, this is affecting girl students",
            "midday meal quality at the {locality} school has deteriorated and several children fell sick",
        ],
        "medium": [
            "we would like more computers at the {locality} government school",
            "the scholarship payment for {locality} students has been delayed for {days} days",
        ],
        "low": [
            "I wanted to ask about the admission process for the {locality} government school",
            "can you tell me the schedule for the upcoming parent teacher meeting",
        ],
    },
    "Internet Services": {
        "critical": [
            "the broadband exchange serving {locality} has been completely down for {days} days affecting work from home and online classes",
        ],
        "high": [
            "internet speed in {locality} has been extremely poor for {days} days despite multiple complaints",
            "the public WiFi hotspot at {locality} has not worked in {days} days",
        ],
        "medium": [
            "we are facing intermittent internet outages in {locality} every evening",
            "the broadband bill for {locality} connection shows incorrect charges",
        ],
        "low": [
            "I want to know how to apply for a new broadband connection in {locality}",
            "can you tell me about the government Akshaya centre services available near {locality}",
        ],
    },
    "Public Safety": {
        "critical": [
            "there was a robbery near {locality} last night and residents are demanding immediate police patrolling",
            "a group has been causing public disturbance and vandalising property near {locality} for {days} days",
        ],
        "high": [
            "streetlights near the {locality} police outpost have been non functional for {days} days, increasing safety concerns",
            "there have been repeated chain snatching incidents reported near {locality}",
        ],
        "medium": [
            "we would like additional police patrolling near {locality} during late evenings",
            "the CCTV cameras installed near {locality} have not been working for a while",
        ],
        "low": [
            "I wanted to know the process to file a noise complaint for {locality}",
            "can you share the contact details for the {locality} police station",
        ],
    },
    "Government Documentation": {
        "critical": [
            "my ration card application has been stuck for {days} days and my family has no access to subsidised food",
        ],
        "high": [
            "my income certificate application submitted at the {locality} office has been pending for {days} days",
            "there was an error in my land record at the {locality} revenue office that is blocking a property sale",
        ],
        "medium": [
            "I wanted an update on my caste certificate application status",
            "the {locality} office gave conflicting information about document requirements",
        ],
        "low": [
            "I wanted to know the documents required for a new birth certificate",
            "can you tell me the working hours of the {locality} village office",
        ],
    },
}

OPENERS = [
    "Hello, I am calling regarding an issue in my area.",
    "Good morning, I would like to report a problem.",
    "Hi, I need to register a complaint.",
    "Hello, I have been trying to reach someone about this for a while.",
    "Good afternoon, I want to bring an urgent issue to your notice.",
    "Hi, I'm calling on behalf of my neighbourhood.",
]

EXEC_ACK = [
    "I understand your concern, let me note down the details.",
    "Thank you for bringing this to our attention, I am registering this complaint.",
    "I'm sorry to hear that, let me log this right away.",
    "Noted. I will escalate this to the concerned department.",
    "I see, this sounds serious. Let me record this immediately.",
]

CLOSERS_BY_TIER = {
    "critical": [
        "Please send someone immediately, this cannot wait any longer.",
        "This is an emergency, we need help right now.",
        "People are at risk, please treat this as top priority.",
    ],
    "high": [
        "Please get this resolved as soon as possible.",
        "We have been waiting too long, kindly expedite this.",
        "This is causing a lot of difficulty for residents, please prioritise it.",
    ],
    "medium": [
        "Please look into this when possible.",
        "It would help if this could be addressed soon.",
        "Kindly forward this to the concerned department.",
    ],
    "low": [
        "Thank you, I just wanted some information.",
        "That's all, thanks for your help.",
        "Okay, thank you for clarifying.",
    ],
}

EXEC_CLOSE = [
    "Your complaint has been registered with reference number generated. We will follow up shortly.",
    "Thank you for calling, this has been forwarded to the relevant department.",
    "We have logged your request and someone will get back to you soon.",
    "Thank you, have a good day. We will update you on the progress.",
]

TIER_TO_PRIORITY = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

TIER_TO_SENTIMENT = {
    "critical": ("Negative", (-1.0, -0.7)),
    "high": ("Negative", (-0.75, -0.35)),
    "medium": ("Neutral", (-0.3, 0.15)),
    "low": ("Neutral", (-0.05, 0.35)),
}

# A small slice of genuinely positive / appreciative calls, for sentiment realism
POSITIVE_SNIPPETS = [
    "I just wanted to thank the {department} team, the issue in {locality} was resolved very quickly.",
    "The recent work done by the {department} in {locality} has been excellent, well done.",
    "I appreciate how fast the complaint about {locality} was handled, thank you.",
]

TIER_WEIGHTS = {"critical": 0.12, "high": 0.28, "medium": 0.35, "low": 0.25}


def pick_tier():
    r = random.random()
    cum = 0
    for tier, w in TIER_WEIGHTS.items():
        cum += w
        if r <= cum:
            return tier
    return "low"


def random_date(start, end):
    delta = end - start
    days = random.randint(0, delta.days)
    return start + timedelta(days=days)


def build_transcript(category, tier, district, locality, department):
    days = random.randint(2, 9)
    body_templates = CATEGORY_TEMPLATES[category][tier]
    body = random.choice(body_templates).format(days=days, locality=locality)

    opener = random.choice(OPENERS)
    ack = random.choice(EXEC_ACK)
    closer = random.choice(CLOSERS_BY_TIER[tier])
    exec_close = random.choice(EXEC_CLOSE)

    citizen_complaint = f"{opener} In {district} district, near {locality}, {body}. {closer}"
    transcript = (
        f"Support Executive: Thank you for calling the citizen helpline, how can I help you today?\n"
        f"Citizen: {citizen_complaint}\n"
        f"Support Executive: {ack}\n"
        f"Citizen: Yes, please make sure this is followed up on.\n"
        f"Support Executive: {exec_close}"
    )
    return transcript


def build_positive_transcript(category, district, locality, department):
    snippet = random.choice(POSITIVE_SNIPPETS).format(department=department, locality=locality)
    citizen_line = f"Hello, calling from {district} district. In {district}, near {locality}, {snippet}"
    transcript = (
        f"Support Executive: Thank you for calling the citizen helpline, how can I help you today?\n"
        f"Citizen: {citizen_line}\n"
        f"Support Executive: That's wonderful to hear, thank you for the feedback, I will pass it on to the team.\n"
        f"Citizen: No problem, keep up the good work.\n"
        f"Support Executive: Thank you, have a great day!"
    )
    return transcript


def generate_dataset(n_rows=1000, positive_fraction=0.08):
    rows = []
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 6, 20)

    n_positive = int(n_rows * positive_fraction)
    n_regular = n_rows - n_positive

    categories = list(CATEGORY_TEMPLATES.keys())

    for i in range(n_regular):
        category = random.choice(categories)
        department = CATEGORY_TO_DEPARTMENT[category]
        district = random.choice(DISTRICTS)
        locality = random.choice(LOCALITIES)
        tier = pick_tier()

        transcript = build_transcript(category, tier, district, locality, department)
        priority = TIER_TO_PRIORITY[tier]
        sentiment_label, score_range = TIER_TO_SENTIMENT[tier]
        sentiment_score = round(random.uniform(*score_range), 2)
        date = random_date(start_date, end_date)

        rows.append({
            "id": i + 1,
            "date": date.strftime("%Y-%m-%d"),
            "district": district,
            "locality": locality,
            "category": category,
            "department": department,
            "transcript": transcript,
            "sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
            "priority": priority,
        })

    for j in range(n_positive):
        category = random.choice(categories)
        department = CATEGORY_TO_DEPARTMENT[category]
        district = random.choice(DISTRICTS)
        locality = random.choice(LOCALITIES)

        transcript = build_positive_transcript(category, district, locality, department)
        priority = "Low"
        sentiment_score = round(random.uniform(0.5, 0.95), 2)
        date = random_date(start_date, end_date)

        rows.append({
            "id": n_regular + j + 1,
            "date": date.strftime("%Y-%m-%d"),
            "district": district,
            "locality": locality,
            "category": category,
            "department": department,
            "transcript": transcript,
            "sentiment": "Positive",
            "sentiment_score": sentiment_score,
            "priority": priority,
        })

    random.shuffle(rows)
    for idx, r in enumerate(rows):
        r["id"] = idx + 1

    return rows


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "conversations.csv")

    rows = generate_dataset(n_rows=1000)

    fieldnames = ["id", "date", "district", "locality", "category", "department",
                  "transcript", "sentiment", "sentiment_score", "priority"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} conversations -> {out_path}")
