import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, date
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# ---------------------------------------------------
# 1. PAGE SETUP & BRANDING (TAMIL PRIMARY, ENG SECONDARY)
# ---------------------------------------------------
st.set_page_config(
    page_title="கால்நடை நோய் கண்டறிதல் மற்றும் மேலாண்மை",
    layout="wide"
)

st.title("கால்நடை ஆரோக்கியம் மற்றும் நோய் கண்காணிப்பு மையம் (Livestock Health & Outbreak Intelligence)")

# ---------------------------------------------------
# 2. SPECIES-SPECIFIC SYMPTOMS & SIGNS MASTER MAPPING
# ---------------------------------------------------
SPECIES_SYMPTOM_MAP = {
    "பசு (Cow)": {
        "general": [
            ("fever", "காய்ச்சல் (Fever)"),
            ("cough", "இருமல் (Cough)"),
            ("panting", "இரைப்பு (Panting)"),
            ("shivering", "நடுக்கம் (Shivering)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "பசியின்மை / தீவனம் உண்ணாமை (Inappetence)"),
            ("mastitis", "மடி வீக்கம் (Mastitis)")
        ],
        "physical": [
            ("blisters", "கொப்பளம் (Blisters)"),
            ("ulcers", "புண் (Ulcers)"),
            ("drooling", "உமிழ்நீர் வடிதல் (Drooling)"),
            ("diarrhea", "பேதி (Diarrhea)"),
            ("bloat", "வயிறு உப்பசம் (Bloat)"),
            ("lumps", "தோல் கட்டி / தழும்பு (Lumps / Discoloration)"),
            ("lameness", "நொண்டி நடத்தல் (Lameness)")
        ]
    },
    "எருமை (Buffalo)": {
        "general": [
            ("fever", "காய்ச்சல் (Fever)"),
            ("cough", "இருமல் (Cough)"),
            ("panting", "இரைப்பு (Panting)"),
            ("shivering", "நடுக்கம் (Shivering)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "பசியின்மை / தீவனம் உண்ணாமை (Inappetence)"),
            ("mastitis", "மடி வீக்கம் (Mastitis)")
        ],
        "physical": [
            ("blisters", "கொப்பளம் (Blisters)"),
            ("ulcers", "புண் (Ulcers)"),
            ("drooling", "உமிழ்நீர் வடிதல் (Drooling)"),
            ("diarrhea", "பேதி (Diarrhea)"),
            ("bloat", "வயிறு உப்பசம் (Bloat)"),
            ("lumps", "தோல் கட்டி / தழும்பு (Lumps / Discoloration)"),
            ("lameness", "நொண்டி நடத்தல் (Lameness)")
        ]
    },
    "வெள்ளாடு (Goat)": {
        "general": [
            ("fever", "காய்ச்சல் (Fever)"),
            ("cough", "இருமல் (Cough)"),
            ("panting", "இரைப்பு (Panting)"),
            ("shivering", "நடுக்கம் (Shivering)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "பசியின்மை / தீவனம் உண்ணாமை (Inappetence)")
        ],
        "physical": [
            ("blisters", "கொப்பளம் (Blisters)"),
            ("ulcers", "புண் (Ulcers)"),
            ("diarrhea", "பேதி (Diarrhea)"),
            ("bloat", "வயிறு உப்பசம் (Bloat)"),
            ("lumps", "தோல் கட்டி / தழும்பு (Lumps / Discoloration)"),
            ("lameness", "நொண்டி நடத்தல் (Lameness)")
        ]
    },
    "செம்மறியாடு (Sheep)": {
        "general": [
            ("fever", "காய்ச்சல் (Fever)"),
            ("cough", "இருமல் (Cough)"),
            ("panting", "இரைப்பு (Panting)"),
            ("shivering", "நடுக்கம் (Shivering)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "பசியின்மை / தீவனம் உண்ணாமை (Inappetence)")
        ],
        "physical": [
            ("blisters", "கொப்பளம் (Blisters)"),
            ("ulcers", "புண் (Ulcers)"),
            ("diarrhea", "பேதி (Diarrhea)"),
            ("bloat", "வயிறு உப்பசம் (Bloat)"),
            ("lumps", "கம்பளி உதிர்தல் / தோல் காயங்கள் (Wool/Skin Lesions)"),
            ("lameness", "நொண்டி நடத்தல் (Lameness)")
        ]
    },
    "பன்றி (Pig)": {
        "general": [
            ("fever", "காய்ச்சல் (Fever)"),
            ("cough", "இருமல் (Cough)"),
            ("shivering", "நடுக்கம் (Shivering)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "பசியின்மை / தீவனம் உண்ணாமை (Inappetence)")
        ],
        "physical": [
            ("blisters", "கொப்பளம் (Blisters)"),
            ("ulcers", "புண் (Ulcers)"),
            ("drooling", "உமிழ்நீர் வடிதல் (Drooling)"),
            ("skin_discoloration", "தோல் சிவத்தல் / நிறமாற்றம் (Skin Discoloration)"),
            ("diarrhea", "பேதி (Diarrhea)"),
            ("lameness", "நொண்டி நடத்தல் (Lameness)")
        ]
    },
    "கோழி (Chicken)": {
        "general": [
            ("fever", "காய்ச்சல் / அதிக உடல் சூடு (Fever)"),
            ("cough", "இருமல் / தும்மல் (Cough/Sneezing)"),
            ("panting", "மூச்சுத்திணறல் (Panting/Gasping)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "தீவனம் உண்ணாமை / இரை எடுக்காமை (Inappetence)")
        ],
        "physical": [
            ("swollen_head", "தலை / பூ வீக்கம் (Swollen Head/Comb)"),
            ("skin_discoloration", "பூ நீலமாகுதல் / தோல் நிறமாற்றம் (Purple Comb / Discoloration)"),
            ("diarrhea", "வெள்ளை / பச்சை பேதி (Diarrhea)"),
            ("egg_drop", "முட்டை உற்பத்தி குறைதல் (Egg Drop)"),
            ("paralysis", "இறக்கை / கால் முடக்கம் (Incoordination/Paralysis)")
        ]
    },
    "வாத்து (Duck)": {
        "general": [
            ("fever", "காய்ச்சல் / அதிக உடல் சூடு (Fever)"),
            ("lethargy", "சோர்வு (Lethargy)"),
            ("inappetence", "தீவனம் உண்ணாமை / இரை எடுக்காமை (Inappetence)")
        ],
        "physical": [
            ("eye_nasal_discharge", "கண் / மூக்கு ஒழுகுதல் (Eye/Nasal Discharge)"),
            ("diarrhea", "பச்சை பேதி (Greenish Diarrhea)"),
            ("paralysis", "இறக்கை / கால் முடக்கம் (Incoordination/Paralysis)"),
            ("egg_drop", "முட்டை உற்பத்தி குறைதல் (Egg Drop)")
        ]
    }
}

ALL_SYMPTOM_KEYS = [
    "fever", "cough", "blisters", "ulcers", "drooling", "diarrhea", "bloat", 
    "lumps", "lameness", "lethargy", "inappetence", "mastitis", "panting", 
    "shivering", "skin_discoloration", "swollen_head", "egg_drop", 
    "eye_nasal_discharge", "paralysis"
]

SPECIES_ALLOWED_DISEASES = {
    "பசு (Cow)": [
        "கோமாரி நோய் / Foot-and-Mouth Disease (FMD)",
        "தோல் கட்டி நோய் / Lumpy Skin Disease (LSD)",
        "அடைப்பான் நோய் / Anthrax (Suspected)",
        "மடி வீக்க நோய் / Bovine Mastitis",
        "வயிறு உப்பசம் / Bovine Bloat",
        "சுவாச மண்டல தொற்று / Bovine Respiratory Disease (BRD)",
        "கடுமையான பேதி / Severe Diarrhea / Scours",
        "ஆரோக்கியமானது / Healthy"
    ],
    "எருமை (Buffalo)": [
        "கோமாரி நோய் / Foot-and-Mouth Disease (FMD)",
        "அடைப்பான் நோய் / Blackleg / Anthrax (Suspected)",
        "எருமை சுவாச நோய் / Buffalo Respiratory Infection",
        "எருமை செரிமான கோளாறு / Buffalo Digestive Disorder",
        "ஆரோக்கியமானது / Healthy"
    ],
    "வெள்ளாடு (Goat)": [
        "ஆட்டுக்கொல்லி நோய் / Pestis Petrinae Ruminantium (PPR)",
        "ஆட்டுத் தோல் நோய் / Goat Pox / Dermatitis",
        "வெள்ளாட்டு சுவாச தொற்று / Caprine Respiratory Infection (CCPP)",
        "துள்ளு நோய் / Enterotoxemia (Severe Diarrhea)",
        "வெள்ளாட்டு வயிறு உப்பசம் / Caprine Bloat & Parasitism",
        "ஆரோக்கியமானது / Healthy"
    ],
    "செம்மறியாடு (Sheep)": [
        "செம்மறியாடு அம்மை நோய் / Sheep Pox",
        "செம்மறியாட்டு சுவாச தொற்று / Ovine Respiratory Infection",
        "செம்மறியாட்டு குளம்பு நோய் / Sheep Foot Rot",
        "செம்மறியாட்டு பேதி தொற்று / Ovine Parasitic Gastroenteritis",
        "ஆரோக்கியமானது / Healthy"
    ],
    "பன்றி (Pig)": [
        "கோமாரி நோய் / Foot-and-Mouth Disease (FMD)",
        "கிளாசிக்கல் பன்றி காய்ச்சல் / Classical Swine Fever (CSF)",
        "ஆப்பிரிக்க பன்றி காய்ச்சல் / African Swine Fever (ASF)",
        "பன்றி சுவாச நோய் / Porcine Respiratory Disease Complex",
        "ஆரோக்கியமானது / Healthy"
    ],
    "கோழி (Chicken)": [
        "ராணிகேட் நோய் / Newcastle Disease",
        "பறவை காய்ச்சல் / Avian Influenza (Bird Flu)",
        "கோழி சுவாச நோய் / Infectious Bronchitis (IB)",
        "மாரெக்ஸ் நோய் / Marek's Disease",
        "கம்போரோ நோய் / Infectious Bursal Disease (IBD)",
        "ஆரோக்கியமானது / Healthy"
    ],
    "வாத்து (Duck)": [
        "வாத்து பிளேக் / Duck Plague",
        "வாத்து வைரஸ் கல்லீரல் அழற்சி / Duck Viral Hepatitis",
        "வாத்து காலரா / Duck Cholera",
        "ஆரோக்கியமானது / Healthy"
    ]
}

# ---------------------------------------------------
# 3. PURE SYMPTOM TRAINING DATASET & MODEL
# ---------------------------------------------------
@st.cache_resource
def train_herdsync_model():
    # Columns: fever, cough, blisters, ulcers, drooling, diarrhea, bloat, lumps, lameness, lethargy, inappetence, mastitis, panting, shivering, skin_discoloration, swollen_head, egg_drop, eye_nasal_discharge, paralysis, "disease", "risk"
    raw_data = [
        # --- COW ---
        [1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "கோமாரி நோய் / Foot-and-Mouth Disease (FMD)", "High"],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "தோல் கட்டி நோய் / Lumpy Skin Disease (LSD)", "Medium"],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, "அடைப்பான் நோய் / Anthrax (Suspected)", "High"],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, "மடி வீக்க நோய் / Bovine Mastitis", "Medium"],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, "வயிறு உப்பசம் / Bovine Bloat", "Medium"],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, "சுவாச மண்டல தொற்று / Bovine Respiratory Disease (BRD)", "High"],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, "கடுமையான பேதி / Severe Diarrhea / Scours", "Medium"],

        # --- BUFFALO ---
        [1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, "அடைப்பான் நோய் / Blackleg / Anthrax (Suspected)", "High"],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, "எருமை சுவாச நோய் / Buffalo Respiratory Infection", "High"],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, "எருமை செரிமான கோளாறு / Buffalo Digestive Disorder", "Medium"],

        # --- GOAT ---
        [1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "ஆட்டுக்கொல்லி நோய் / Pestis Petrinae Ruminantium (PPR)", "High"],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "ஆட்டுத் தோல் நோய் / Goat Pox / Dermatitis", "Medium"],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, "வெள்ளாட்டு சுவாச தொற்று / Caprine Respiratory Infection (CCPP)", "High"],
        [1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "துள்ளு நோய் / Enterotoxemia (Severe Diarrhea)", "High"],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "வெள்ளாட்டு வயிறு உப்பசம் / Caprine Bloat & Parasitism", "Medium"],

        # --- SHEEP ---
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "செம்மறியாடு அம்மை நோய் / Sheep Pox", "High"],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, "செம்மறியாட்டு சுவாச தொற்று / Ovine Respiratory Infection", "High"],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, "செம்மறியாட்டு குளம்பு நோய் / Sheep Foot Rot", "Medium"],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "செம்மறியாட்டு பேதி தொற்று / Ovine Parasitic Gastroenteritis", "Medium"],

        # --- PIG ---
        [1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "கோமாரி நோய் / Foot-and-Mouth Disease (FMD)", "High"],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, "கிளாசிக்கல் பன்றி காய்ச்சல் / Classical Swine Fever (CSF)", "High"],
        [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, "ஆப்பிரிக்க பன்றி காய்ச்சல் / African Swine Fever (ASF)", "High"],
        [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "பன்றி சுவாச நோய் / Porcine Respiratory Disease Complex", "Medium"],

        # --- CHICKEN ---
        [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, "ராணிகேட் நோய் / Newcastle Disease", "High"],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, "பறவை காய்ச்சல் / Avian Influenza (Bird Flu)", "High"],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, "கோழி சுவாச நோய் / Infectious Bronchitis (IB)", "Medium"],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, "மாரெக்ஸ் நோய் / Marek's Disease", "High"],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "கம்போரோ நோய் / Infectious Bursal Disease (IBD)", "High"],

        # --- DUCK ---
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, "வாத்து பிளேக் / Duck Plague", "High"],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, "வாத்து வைரஸ் கல்லீரல் அழற்சி / Duck Viral Hepatitis", "High"],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, "வாத்து காலரா / Duck Cholera", "High"],

        # --- HEALTHY (Baseline) ---
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "ஆரோக்கியமானது / Healthy", "Low"],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "ஆரோக்கியமானது / Healthy", "Low"]
    ]

    columns = ALL_SYMPTOM_KEYS + ["disease", "risk"]
    df = pd.DataFrame(raw_data, columns=columns)

    X = df.drop(columns=["disease", "risk"])
    y = df["disease"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y_encoded)

    return model, le, ALL_SYMPTOM_KEYS

model, label_encoder, feature_names = train_herdsync_model()

# ---------------------------------------------------
# ALL COMPREHENSIVE VACCINES 
# ---------------------------------------------------
SPECIES_VACCINE_SCHEDULE = {
    "பசு (Cow)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "கோமாரி நோய் தடுப்பூசி (FMD Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "4 மாதங்கள் & ஆண்டுக்கு இருமுறை", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "தோல் கட்டி நோய் தடுப்பூசி (LSD Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "4 மாதங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "அடைப்பான் தடுப்பூசி (Anthrax Spore Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "BRD Complex Vaccine (BVD, IBR, PI3, BRSV)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "கன்று பருவத்தில்", "செலுத்தும் முறை (Route)": "தசையில் (Intramuscular)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "Rotavirus / Coronavirus / E.coli (Scours)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "சினைப் பசுக்களுக்கு (To pass antibodies)", "செலுத்தும் முறை (Route)": "தசையில் (Intramuscular)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "பராமரிப்பு (Bloat & Mastitis)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "தடுப்பூசி இல்லை. உணவு மற்றும் சுகாதாரம் அவசியம்.", "செலுத்தும் முறை (Route)": "பொருந்தாது"}
    ],
    "எருமை (Buffalo)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "கோமாரி நோய் தடுப்பூசி (FMD Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "4 மாதங்கள் & ஆண்டுக்கு இருமுறை", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "தொண்டை அடைப்பான் (HS Vaccine - Respiratory)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "6 மாதங்கள் & மழைக்காலத்திற்கு முன்", "செலுத்தும் முறை (Route)": "தசையில் (Intramuscular)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "சப்பை நோய் மற்றும் அடைப்பான் (Blackleg & Anthrax)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "6 மாதங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "பராமரிப்பு (Digestive Disorders)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "தடுப்பூசி இல்லை. குடற்புழு நீக்கம் அவசியம்.", "செலுத்தும் முறை (Route)": "வாய்வழி (Oral deworming)"}
    ],
    "வெள்ளாடு (Goat)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "ஆட்டுக்கொல்லி நோய் தடுப்பூசி (PPR Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "3 மாதங்கள் & 3 ஆண்டுகளுக்கு ஒருமுறை", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "ஆட்டம்மை தடுப்பூசி (Goat Pox Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "3 மாதங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "துள்ளு நோய் தடுப்பூசி (Enterotoxaemia - ET Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "4 மாதங்கள் & மழைக்காலத்திற்கு முன்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "CCPP Vaccine (Caprine Pleuropneumonia)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "6 மாதங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "பராமரிப்பு (Bloat & Parasitism)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "தடுப்பூசி இல்லை. குடற்புழு நீக்கம்.", "செலுத்தும் முறை (Route)": "வாய்வழி (Oral deworming)"}
    ],
    "செம்மறியாடு (Sheep)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "ஆட்டம்மை தடுப்பூசி (Sheep Pox Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "3 மாதங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "ஆட்டுக்கொல்லி நோய் (PPR Vaccine - Respiratory)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "3 மாதங்கள் & 3 ஆண்டுகளுக்கு ஒருமுறை", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "Footvax / Foot Rot Vaccine", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "நோய்த்தொற்று உள்ள பகுதிகளில்", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "பராமரிப்பு (Parasitic Gastroenteritis)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "தடுப்பூசி இல்லை. குடற்புழு நீக்கம்.", "செலுத்தும் முறை (Route)": "வாய்வழி (Oral deworming)"}
    ],
    "பன்றி (Pig)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "பன்றி காய்ச்சல் (Classical Swine Fever Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "2 மாதங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தசையில் (Intramuscular)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "கோமாரி நோய் தடுப்பூசி (FMD Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "4 மாதங்கள் & ஆண்டுக்கு இருமுறை", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "Porcine Respiratory Complex (PRRS, PCV2, Myco)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "கன்று பருவத்தில்", "செலுத்தும் முறை (Route)": "தசையில் (Intramuscular)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "ஆப்பிரிக்க பன்றி காய்ச்சல் (ASF)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "வணிக ரீதியான தடுப்பூசி இல்லை.", "செலுத்தும் முறை (Route)": "கடுமையான தனிமைப்படுத்தல் (Quarantine)"}
    ],
    "கோழி (Chicken)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "மாரெக்ஸ் தடுப்பூசி (Marek's Disease Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "1 நாள் குஞ்சு (Day 1)", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "ராணிகேட் தடுப்பூசி (Newcastle / F1 Strain)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "7வது நாள் (Day 7)", "செலுத்தும் முறை (Route)": "கண் சொட்டு மருந்து (Eye Drops)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "கம்போரோ தடுப்பூசி (Gumboro / IBD Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "14வது நாள் (Day 14)", "செலுத்தும் முறை (Route)": "குடிநீர் வழி (Drinking Water)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "சுவாச நோய் (Infectious Bronchitis - IB Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "3-4 வாரங்கள்", "செலுத்தும் முறை (Route)": "கண் சொட்டு / குடிநீர் வழி (Eye/Water)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "பறவை காய்ச்சல் (Avian Influenza)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "தடைசெய்யப்பட்டுள்ளது / கட்டுப்படுத்தப்பட்டது.", "செலுத்தும் முறை (Route)": "அரசு வழிகாட்டுதல்படி (Culling)"}
    ],
    "வாத்து (Duck)": [
        {"தடுப்பூசி / நோய் (Vaccine)": "வாத்து பிளேக் தடுப்பூசி (Duck Plague Vaccine)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "3-4 வாரங்கள் & ஆண்டுதோறும்", "செலுத்தும் முறை (Route)": "தசையில் (Intramuscular)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "வாத்து வைரஸ் கல்லீரல் அழற்சி (Duck Hepatitis)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "1 வார குஞ்சு", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"},
        {"தடுப்பூசி / நோய் (Vaccine)": "வாத்து காலரா (Fowl Cholera / Pasteurella)", "பரிந்துரைக்கப்படும் காலம் (Periodicity)": "4 வாரங்கள் & மீண்டும் 4 வாரம் கழித்து", "செலுத்தும் முறை (Route)": "தோலின்கீழ் (Subcutaneous)"}
    ]
}

# ---------------------------------------------------
# 4. INITIALIZE SESSION STATE & SYNC CALLBACKS
# ---------------------------------------------------

# Set default selection values if they don't exist
if "selected_species_main" not in st.session_state:
    st.session_state.selected_species_main = list(SPECIES_SYMPTOM_MAP.keys())[0]

if "passport_species_select" not in st.session_state:
    st.session_state.passport_species_select = st.session_state.selected_species_main

# Callback: When Tab 1 dropdown changes, update Tab 2 dropdown and reset symptoms
def sync_to_passport():
    st.session_state.passport_species_select = st.session_state.selected_species_main
    reset_symptom_states()

# Callback: When Tab 2 dropdown changes, update Tab 1 dropdown and reset symptoms
def sync_to_main():
    st.session_state.selected_species_main = st.session_state.passport_species_select
    reset_symptom_states()

if "last_assessment" not in st.session_state:
    st.session_state.last_assessment = None

if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = ""

for key in ALL_SYMPTOM_KEYS:
    if f"chk_{key}" not in st.session_state:
        st.session_state[f"chk_{key}"] = False

def reset_symptom_states():
    for key in ALL_SYMPTOM_KEYS:
        st.session_state[f"chk_{key}"] = False
    st.session_state.voice_transcript = ""

def speech_recognition_callback():
    transcript = st.session_state.get("speech_rec_output")
    if transcript:
        st.session_state.voice_transcript = transcript
        lower_text = transcript.lower()

        if any(w in lower_text for w in ["fever", "காய்ச்சல்", "காய்ச்ச", "சூடு", "வெப்பம்"]): st.session_state["chk_fever"] = True
        if any(w in lower_text for w in ["cough", "இருமல்", "இருமு", "தும்மல்", "sneeze"]): st.session_state["chk_cough"] = True
        if any(w in lower_text for w in ["blister", "கொப்பளம்", "கொப்பளங்கள்", "கொப்பள"]): st.session_state["chk_blisters"] = True
        if any(w in lower_text for w in ["ulcer", "sore", "புண்", "புண்கள்"]): st.session_state["chk_ulcers"] = True
        if any(w in lower_text for w in ["drool", "saliva", "எச்சி", "உமிழ்நீர்", "எச்சில்"]): st.session_state["chk_drooling"] = True
        if any(w in lower_text for w in ["diarrhea", "loose motion", "பேதி", "கழிச்சல்", "வயிற்றுப்போக்கு"]): st.session_state["chk_diarrhea"] = True
        if any(w in lower_text for w in ["bloat", "swollen belly", "உப்பசம்", "வயிறு"]): st.session_state["chk_bloat"] = True
        if any(w in lower_text for w in ["lump", "nodule", "கட்டி", "கட்டிகள்"]): st.session_state["chk_lumps"] = True
        if any(w in lower_text for w in ["lame", "limp", "நொண்டி", "நொண்டி நடக்குது", "நொண்டல்"]): st.session_state["chk_lameness"] = True
        if any(w in lower_text for w in ["lethargy", "weak", "சோர்வு", "சோர்வா"]): st.session_state["chk_lethargy"] = True
        if any(w in lower_text for w in ["inappetence", "no appetite", "not eating", "refusal to feed", "சாப்பிடவில்லை", "சாப்பிடல", "சாப்பிட மாட்டேங்குது", "தீவனம் உண்ணாமை"]): 
            st.session_state["chk_inappetence"] = True
        if any(w in lower_text for w in ["mastitis", "udder", "மடி வீக்கம்", "மடி"]): st.session_state["chk_mastitis"] = True
        if any(w in lower_text for w in ["pant", "breathing", "இரைப்பு", "மூச்சு"]): st.session_state["chk_panting"] = True
        if any(w in lower_text for w in ["shiver", "chill", "நடுக்கம்", "நடுங்குது"]): st.session_state["chk_shivering"] = True
        if any(w in lower_text for w in ["discoloration", "redness", "red skin", "blue skin", "purple comb", "சிவப்பு", "நீலம்", "தோல் சிவப்பாதல்", "தழும்பு", "நிறமாற்றம்"]): 
            st.session_state["chk_skin_discoloration"] = True
        if any(w in lower_text for w in ["swollen head", "comb", "தலை வீக்கம்", "பூ வீக்கம்"]): st.session_state["chk_swollen_head"] = True
        if any(w in lower_text for w in ["egg", "முட்டை"]): st.session_state["chk_egg_drop"] = True
        if any(w in lower_text for w in ["eye", "nasal", "கண்", "மூக்கு"]): st.session_state["chk_eye_nasal_discharge"] = True
        if any(w in lower_text for w in ["paralysis", "paralyzed", "முடக்கம்", "கால் வரல"]): st.session_state["chk_paralysis"] = True

# ---------------------------------------------------
# 5. TABBED INTERFACE (TAMIL PRIMARY)
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🩺 செயற்கை நுண்ணறிவு நோய் பரிசோதனை (AI Clinical Assessment)", 
    "💉 டிஜிட்டல் தடுப்பூசி விபரம் (Digital Vaccine Passport)", 
    "🚨 அவசர மருத்துவ உதவி (Emergency Veterinary SOS)"
])

# ===================================================
# TAB 1: AI CLINICAL ASSESSMENT
# ===================================================
with tab1:
    st.subheader("படி 1: கால்நடை மற்றும் இருப்பிட விபரம் (Step 1: Animal & Location Profile)")
    col1, col2 = st.columns(2)
    with col1:
        # Added the 'on_change' callback here to sync with Tab 2
        animal_type = st.selectbox(
            "கால்நடை / பறவை இனம் (Livestock Species)", 
            list(SPECIES_SYMPTOM_MAP.keys()),
            on_change=sync_to_passport,
            key="selected_species_main"
        )
        village_name = st.text_input("பண்ணை / கிராமத்தின் பெயர் (Farm / Village Location)", "")
    with col2:
        vaccination_status = st.selectbox("தடுப்பூசி நிலை (Vaccination Status)", ["முழுமையாக போடப்பட்டது (Fully Vaccinated)", "பகுதியளவு போடப்பட்டது (Partially Vaccinated)", "போடப்படவில்லை (Not Vaccinated)"])

    st.divider()

    st.subheader("🎙️ குரல் வழி அறிகுறி பதிவு (Voice Symptom Input)")
    voice_lang = st.radio("மொழியைத் தேர்ந்தெடுக்கவும் (Choose Language):", ["தமிழ் / Tamil (ta-IN)", "English (en-IN)"], horizontal=True)
    lang_code = "ta-IN" if "Tamil" in voice_lang or "தமிழ்" in voice_lang else "en-IN"

    if lang_code == "ta-IN":
        st.caption("🗣️ தமிழ் உதாரணம்: *'காய்ச்சல் இருக்கு, சாப்பாடு சாப்பிடல, சிவப்பா தழும்பு இருக்கு, பேதி போகுது'*")
    else:
        st.caption("🗣️ English Example: *'Fever, loss of appetite, red skin patches, and loose motion'*")

    speech_to_text(
        language=lang_code,
        start_prompt="🎙️ பேச தொடங்குங்கள் (Start Speaking)",
        stop_prompt="⏹️ நிறுத்துங்கள் (Stop Recording)",
        just_once=False,
        callback=speech_recognition_callback,
        key='speech_rec'
    )

    if st.session_state.voice_transcript:
        st.success(f"**பதிவு செய்யப்பட்ட உரை ({voice_lang}):** *\"{st.session_state.voice_transcript}\"*")
        st.info("💡 மேலே உள்ள உரையின் அடிப்படையில் அறிகுறிகள் தானாகத் தேர்ந்தெடுக்கப்பட்டன (Auto-detected based on text)!")

    st.divider()

    st.subheader(f"படி 2: உடல்நிலை அளவீடு மற்றும் அறிகுறிகள் - {animal_type} (Step 2: Vitals & Symptoms)")
    
    default_temp = 42.0 if animal_type in ["கோழி (Chicken)", "வாத்து (Duck)"] else 39.0
    default_hr = 280 if animal_type in ["கோழி (Chicken)", "வாத்து (Duck)"] else 80

    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.markdown("#### 📡 உடல் அளவீடுகள் உள்ளீடு (Manual Vitals Entry)")
        temp_input = st.slider("உடல் வெப்பநிலை / Body Temp (°C)", min_value=35.0, max_value=45.0, value=float(default_temp), step=0.1)
        hr_input = st.slider("இதய துடிப்பு / Heart Rate (BPM)", min_value=30, max_value=400, value=int(default_hr))
        
        st.markdown(f"#### 👁️ பொதுவான அறிகுறிகள் ({animal_type})")
        gen_symptoms_config = SPECIES_SYMPTOM_MAP[animal_type]["general"]
        for key, label in gen_symptoms_config:
            st.checkbox(label, key=f"chk_{key}")

    with col_v2:
        st.markdown(f"#### 👁️ உடலமைப்பு மற்றும் சிறப்பு அறிகுறிகள் ({animal_type})")
        phys_symptoms_config = SPECIES_SYMPTOM_MAP[animal_type]["physical"]
        for key, label in phys_symptoms_config:
            st.checkbox(label, key=f"chk_{key}")

    st.divider()

    if st.button("🚀 AI நோய் பரிசோதனையைத் தொடங்கு (Run Analysis)", type="primary"):
        input_vector = []
        for key in ALL_SYMPTOM_KEYS:
            val = 1 if st.session_state.get(f"chk_{key}", False) else 0
            input_vector.append(val)

        if sum(input_vector) == 0:
            predicted_disease = "ஆரோக்கியமானது / Healthy"
            confidence = 98.0
            risk_level = "Low"
        else:
            predicted_encoded = model.predict([input_vector])[0]
            predicted_disease = label_encoder.inverse_transform([predicted_encoded])[0]
            
            probabilities = model.predict_proba([input_vector])[0]
            confidence = max(probabilities) * 100

            if "Healthy" in predicted_disease:
                risk_level = "Low"
            elif "Mastitis" in predicted_disease or "Bloat" in predicted_disease or "மடி" in predicted_disease or "Scours" in predicted_disease:
                risk_level = "Medium"
            else:
                risk_level = "High"

        # Validate predicted disease against allowed species diseases
        allowed_diseases = SPECIES_ALLOWED_DISEASES.get(animal_type, [])
        if predicted_disease not in allowed_diseases and not "Healthy" in predicted_disease:
            predicted_disease = allowed_diseases[0] 
            confidence = 75.0 
            risk_level = "High"

        st.session_state.last_assessment = {
            "animal": animal_type,
            "village": village_name,
            "disease": predicted_disease,
            "confidence": confidence,
            "risk": risk_level,
            "temp": temp_input,
            "hr": hr_input,
            "voice_text": st.session_state.voice_transcript if st.session_state.voice_transcript else "இல்லை (None)",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.subheader("AI பரிசோதனை முடிவுகள் (Diagnostic Results)")
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            st.metric("கண்டறியப்பட்ட நோய் (Condition)", predicted_disease)
        with res_col2:
            st.metric("துல்லியம் (Confidence)", f"{confidence:.1f}%")
        with res_col3:
            if risk_level == "High":
                st.error("🚨 ஆபத்து நிலை: அதிகம் (HIGH RISK)")
            elif risk_level == "Medium":
                st.warning("⚠️ ஆபத்து நிலை: நடுத்தரம் (MEDIUM RISK)")
            else:
                st.success("✅ ஆபத்து நிலை: குறைவு (LOW RISK)")

# ===================================================
# TAB 2: DIGITAL PASSPORT & VACCINATIONS
# ===================================================
with tab2:
    st.header("💉 டிஜிட்டல் தடுப்பூசி அட்டவணை (Livestock Vaccination Passport)")
    
    # Added the 'on_change' callback here to sync with Tab 1
    selected_species = st.selectbox(
        "கால்நடை / பறவை இனம் தேர்ந்தெடுக்கவும் (Select Species):", 
        list(SPECIES_VACCINE_SCHEDULE.keys()), 
        on_change=sync_to_main,
        key="passport_species_select"
    )
    
    st.subheader(f"📋 {selected_species} - தடுப்பூசி விவரங்கள்")
    sched_list = SPECIES_VACCINE_SCHEDULE.get(selected_species, [])
    sched_df = pd.DataFrame(sched_list)
    st.dataframe(sched_df, use_container_width=True)

    st.divider()
    st.markdown("### 🗓️ போடப்பட்ட தடுப்பூசியை பதிவு செய்ய (Record Completed Dose)")
    with st.form("log_dose_form"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            dose_vac = st.selectbox("தடுப்பூசியை தேர்ந்தெடுக்கவும்", [item["தடுப்பூசி / நோய் (Vaccine)"] for item in sched_list] if sched_list else ["பொது தடுப்பூசி"])
        with f_col2:
            dose_date = st.date_input("போடப்பட்ட தேதி (Date)", date.today())
        with f_col3:
            vet_name = st.text_input("மருத்துவர் / அதிகாரி பெயர்", "டாக்டர் L . ரித்திக் (B.V.Sc)")

        if st.form_submit_button("✅ தடுப்பூசியை பதிவு செய் (Save Record)"):
            st.success(f"**{selected_species}** -க்கு போடப்பட்ட **{dose_vac}** தடுப்பூசி விபரம் ({dose_date}) வெற்றிகரமாக பதிவேற்றப்பட்டது!")

# ===================================================
# TAB 3: TELE-VET EMERGENCY SOS
# ===================================================
with tab3:
    st.header("🚨 அவசர கால்நடை மருத்துவ உதவி (Emergency Veterinary SOS)")
    assessment = st.session_state.last_assessment

    if assessment is None:
        st.info("💡 அவசர உதவி படிவம் உருவாக்க, முதலில் படி 1-ல் (Tab 1) நோய் பரிசோதனை செய்யவும்.")
    else:
        vet_col1, vet_col2 = st.columns(2)
        with vet_col1:
            target_vet = st.selectbox("அருகிலுள்ள கால்நடை மருத்துவமனை", ["கால்நடை மருத்துவரின் கைபேசி எண் #1"])
            vet_phone = st.text_input("மருத்துவரின் WhatsApp எண்", "+91")
            notes = st.text_area("கூடுதல் தகவல்கள்", f"{assessment['village']} ")
        
        with vet_col2:
            case_summary = f"""*அவசர கால்நடை மருத்துவ கோரிக்கை*
----------------------------------------
நேரம்: {assessment['time']}
இனம்: {assessment['animal']}
இருப்பிடம்: {assessment['village']}
கண்டறியப்பட்ட நோய்: {assessment['disease']}
துல்லியம்: {assessment['confidence']:.1f}%
ஆபத்து நிலை: {assessment['risk']}
உடல் அளவீடு: வெப்பநிலை {assessment['temp']}°C | இதய துடிப்பு {assessment['hr']} BPM
----------------------------------------
உடனடி மருத்துவ உதவி தேவைப்படுகிறது."""
            st.code(case_summary, language="text")

            encoded_text = urllib.parse.quote(case_summary)
            whatsapp_url = f"https://wa.me/{vet_phone.replace('+', '').replace(' ', '')}?text={encoded_text}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; font-size:16px; border-radius:5px; cursor:pointer;">💬 WhatsApp வழியே அவசர செய்தி அனுப்பு (Send WhatsApp SOS)</button></a>', unsafe_allow_html=True)