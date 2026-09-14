from typing import Dict, Optional

# IPR/CIPAM terminology glossary
# Maps English term -> {language: translation}
GLOSSARY: Dict[str, Dict[str, str]] = {
    "Intellectual Property": {
        "hindi": "बौद्धिक संपदा",
        "marathi": "बौद्धिक संपदा",
        "bengali": "বৌদ্ধিক সম্পত্তি",
        "gujarati": "બૌદ્ધિક સંપત્તિ",
        "tamil": "அறிவுசார் சொத்து",
        "telugu": "మేధో సంపత్తి",
    },
    "Copyright": {
        "hindi": "प्रतिलिप्याधिकार",
        "marathi": "प्रतिलिप्याधिकार",
        "bengali": "কপিরাইট",
        "gujarati": "કૉપિરાઇટ",
        "tamil": "பதிப்புரிமை",
        "telugu": "కాపీరైట్",
    },
    "Patent": {
        "hindi": "पेटेंट",
        "marathi": "पेटंट",
        "bengali": "পেটেন্ট",
        "gujarati": "પેટન્ટ",
        "tamil": "காப்புரிமை",
        "telugu": "పేటెంట్",
    },
    "Trademark": {
        "hindi": "ट्रेडमार्क",
        "marathi": "ट्रेडमार्क",
        "bengali": "ট্রেডমার্ক",
        "gujarati": "ટ્રેડમાર્ક",
        "tamil": "வர்த்தக முத்திரை",
        "telugu": "ట్రేడ్‌మార్క్",
    },
    "Trade Secret": {
        "hindi": "व्यापार रहस्य",
        "marathi": "व्यापार रहस्य",
        "bengali": "বাণিজ্য গোপনীয়তা",
        "gujarati": "વ્યાપાર ગુપ્ત",
        "tamil": "வணிக ரகசியம்",
        "telugu": "వ్యాపార రహస్యం",
    },
    "Geographical Indication": {
        "hindi": "भौगोलिक संकेत",
        "marathi": "भौगोलिक संकेत",
        "bengali": "ভৌগোলিক নির্দেশক",
        "gujarati": "ભૌગોલિક સંકેત",
        "tamil": "புவிசார் குறியீடு",
        "telugu": "భౌగోళిక సూచిక",
    },
    "Industrial Design": {
        "hindi": "औद्योगिक डिज़ाइन",
        "marathi": "औद्योगिक रचना",
        "bengali": "শিল্প নকশা",
        "gujarati": "ઔદ્યોગિક ડિઝાઇન",
        "tamil": "தொழில்துறை வடிவமைப்பு",
        "telugu": "పారిశ్రామిక రూపకల్పన",
    },
    "Creator": {
        "hindi": "रचनाकार",
        "marathi": "निर्माता",
        "bengali": "স্রষ্টা",
        "gujarati": "સર્જક",
        "tamil": "படைப்பாளர்",
        "telugu": "సృష్టికర్త",
    },
    "Invention": {
        "hindi": "आविष्कार",
        "marathi": "शोध",
        "bengali": "আবিষ্কার",
        "gujarati": "શોધ",
        "tamil": "கண்டுபிடிப்பு",
        "telugu": "ఆవిష్కరణ",
    },
    "License": {
        "hindi": "लाइसेंस",
        "marathi": "परवाना",
        "bengali": "লাইসেন্স",
        "gujarati": "લાઇસન્સ",
        "tamil": "உரிமம்",
        "telugu": "లైసెన్స్",
    },
    "Ownership": {
        "hindi": "स्वामित्व",
        "marathi": "मालकी",
        "bengali": "মালিকানা",
        "gujarati": "માલિકી",
        "tamil": "உரிமை",
        "telugu": "యాజమాన్యం",
    },
    "Infringement": {
        "hindi": "उल्लंघन",
        "marathi": "उल्लंघन",
        "bengali": "লঙ্ঘন",
        "gujarati": "ઉલ્લંઘન",
        "tamil": "மீறல்",
        "telugu": "ఉల్లంఘన",
    },
    "Registration": {
        "hindi": "पंजीकरण",
        "marathi": "नोंदणी",
        "bengali": "নিবন্ধন",
        "gujarati": "નોંધણી",
        "tamil": "பதிவு",
        "telugu": "నమోదు",
    },
    "Protection": {
        "hindi": "संरक्षण",
        "marathi": "संरक्षण",
        "bengali": "সুরক্ষা",
        "gujarati": "સંરક્ષણ",
        "tamil": "பாதுகாப்பு",
        "telugu": "రక్షణ",
    },
    "Innovation": {
        "hindi": "नवाचार",
        "marathi": "नवोपक्रम",
        "bengali": "উদ্ভাবন",
        "gujarati": "નવીનતા",
        "tamil": "புதுமை",
        "telugu": "ఆవిష్కరణ",
    },
    "Intellectual Property Rights": {
        "hindi": "बौद्धिक संपदा अधिकार",
        "marathi": "बौद्धिक संपदा अधिकार",
        "bengali": "বৌদ্ধিক সম্পত্তি অধিকার",
        "gujarati": "બૌદ્ધિક સંપત્તિ અધિકાર",
        "tamil": "அறிவுசார் சொத்துரிமை",
        "telugu": "మేధో సంపత్తి హక్కులు",
    },
}

def get_glossary_for_language(target_language: str) -> Dict[str, str]:
    """Return a dictionary mapping English terms to translations for the given language."""
    lang = target_language.lower()
    result = {}
    for english_term, translations in GLOSSARY.items():
        if lang in translations:
            result[english_term] = translations[lang]
    return result
