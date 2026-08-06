import re
from dateutil import parser as date_parser
from datetime import datetime, timedelta
def parse_amount(text: str):
    """
    Extract numeric dollar amounts in formats like:
    - $205
    - 205 dollars
    - 205.00
    - 100.
    """
    text = text.lower()
    # 1. Prefer for <amount>
    m = re.search(r"for\s+(\d+(\.\d+)?)", text)
    if m:
        return float(m.group(1))

    # 2. Prefer "<amount> dollars"
    m = re.search(r"(\d+(\.\d+)?)\s+dollars", text)
    if m:
        return float(m.group(1))

    # 3. Bare number not followed by date suffix
    m = re.search(r"\b(\d+(\.\d+)?)\b(?!th|rd|nd|st)", text)
    if m:
        return float(m.group(1))

    return None

    m = re.search(r"\$?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return float(match.group(1))
    return None

def extract_date_phrase(text: str):
    text = text.lower()

    patterns = [
        r"due\s+([a-z]+\s+\d{1,2}(?:st|nd|rd|th)?)",   # august 30th
        r"due\s+([a-z]+\s+\d{1,2})",                  # august 15
        r"due\s+(\d{1,2}/\d{1,2})",                   # 6/4
        r"due\s+(\d{4}-\d{2}-\d{2})",                 # 2026-07-17
        #r"due\s+(next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday))",
        r"due\s+(next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))",
        r"due\s+(tomorrow)",                          # tomorrow
        r"due\s+(today)",                             # today
        r"due\s+(in\s+\d+\s+weeks?)",   
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def parse_date(text: str):
    phrase = extract_date_phrase(text)
    if not phrase:
        return None

    today = datetime.today()

    # 1. Handle relative weekdays FIRST
    if phrase.startswith("next "):
        weekday_name = phrase.split()[1]
        weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

        if weekday_name in weekdays:
            target = weekdays.index(weekday_name)
            current = today.weekday()
            delta = (target - current + 7) % 7 or 7
            return (today + timedelta(days=delta)).date()

    # 2. Handle "today"
    if phrase == "today":
        return today.date()

    # 3. Handle "tomorrow"
    if phrase == "tomorrow":
        return (today + timedelta(days=1)).date()

    # 4. Handle "in X weeks"
    if phrase.startswith("in "):
        parts = phrase.split()
        num = int(parts[1])
        return (today + timedelta(weeks=num)).date()

    # 5. Fallback: normal dates
    try:
        dt = date_parser.parse(phrase)
        if dt.year == 1900:
            dt = dt.replace(year=today.year)
        return dt.date()
    except Exception:
        return None


# def parse_date(text: str):
#     phrase = extract_date_phrase(text)
#     print("DEBUG date phrase:", phrase)
#     if not phrase:
#         return None

#     # Handle relative dates manually
#     today = datetime.today()

#     if phrase == "today":
#         return today + timedelta(days=1).date()

#     if phrase.startswith("in "):
#         parts = phrase.split()
#         num = int(parts[1])
#         return (today + timedelta(weeks=num)).date()
#     # Fallback use dateutil for normal dates

#     try:
#         dt = date_parser.parse(phrase)
#         # If year missing, use dateutil for normal dates
#         if dt.year == 1900:
#             dt = dt.replace(year=today.year)
#         return dt.date()
#     except Exception:
#         return None



def parse_frequency(text: str):
    """
    Extract billing frequency.
    """
    frequencies = {
        "monthly": "monthly",
        "weekly": "seasonal",      # weekly isn't in your enum, map to seasonal
        "yearly": "yearly",
        "annual": "yearly",
        "biweekly": "seasonal",
        "once": "onetime",
        "one time": "onetime",
        "onetime": "onetime"
    }

    lower = text.lower()
    for key, value in frequencies.items():
        if key in lower:
            return value

    return None
CATEGORY_KEYWORDS = {
    "utilities": ["water", "electric", "electricity", "power", "gas", "sewer", "garbage", "trash", "internet"],
    "insurance": ["insurance", "car insurance", "auto insurance", "health insurance", "home insurance"],
    "medical": ["doctor", "hospital", "medical", "clinic", "dentist"],
    "perscriptions": ["prescription", "medication", "pharmacy", "drug"],
    "auto": ["car payment", "auto loan", "vehicle", "car"],
    "home": ["mortgage", "rent", "hoa", "home"],
    "entertainment": ["netflix", "hulu", "spotify", "movie", "concert"],
    "hobbies": ["gym", "fitness", "craft", "hobby"],
    "subscriptions": ["subscription", "membership", "prime", "patreon"],
    "food": ["grocery", "food", "restaurant"],
}

def parse_category(text: str, bill_name: str):
    text = text.lower()
    bill_name = bill_name.lower()

    # 1. Check bill name first (strongest signal)
    for category, keywords in CATEGORY_KEYWORDS.items():
        if bill_name in keywords:
            return category

    # 2. Check entire sentence
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category

    # 3. Fallback
    return "other"


# def parse_category(text: str):
#     """
#     Extract category based on your Bill enum.
#     """
#     categories = {
#         "utilities": "utilities",
#         "insurance": "insurance",
#         "medical": "medical",
#         "prescriptions": "perscriptions",
#         "auto": "auto",
#         "car": "auto",
#         "home": "home",
#         "mortgage": "home",
#         "rent": "home",
#         "internet": "utilities",
#         "phone": "utilities",
#         "entertainment": "enteretainment",
#         "hobbies": "hobbies",
#         "subscriptions": "subscriptions",
#         "food": "food"
#     }

#     lower = text.lower()
#     for key, value in categories.items():
#         if key in lower:
#             return value

#     return None


def parse_name(text: str):
    text = text.lower()

    # 1. If sentence contains "bill", grab the word before it
    m = re.search(r"add\s+(.*?)\s+bill", text)
    if m:
        return m.group(1)

    # 2. If sentence contains "payment", grab the word before it.
    m = re.search(r"add\s+(.*?)\s+payment", text)
    if m:
        return m.group(1)

    # 3. If sentence contains "for <amount>", grab the word before "for".
    m = re.search(r"add\s+(.*?)\s+for\s+\d", text)
    if m:
        return m.group(1)

    return None


# def parse_name(text: str):
#     """
#     Extract the bill name using patterns instead of cleanup.
#     This is the part that fixes your 'water 205 dollars August 30th' issue.
#     """

#     text  = text.lower()

#     # Pattern 1: "add a ___ bill"
#     match = re.search(r"add (?:a|my|the)?\s*([a-z\s]+?)\s*bill", lower)
#     if match:
#         return match.group(1).strip()

#     # Pattern 2: "___ bill" anywhere
#     match = re.search(r"([a-z\s]+?)\s*bill", lower)
#     if match:
#         return match.group(1).strip()

#     # Pattern 3: fallback: first noun-like word
#     words = lower.split()
#     for w in words:
#         if w.isalpha():
#             return w

#     return "Unnamed Bill"


def parse_bill_fields(text: str):
    """
    Main entry point: extract all bill fields from natural language.
    """

    amount = parse_amount(text)
    date = parse_date(text)
    frequency = parse_frequency(text)
   
    name = parse_name(text)
    category = parse_category(text, name)

    return {
        "name": name,
        "amount": amount,
        "due_date": date,
        "category": category,
        "frequency": frequency
    }
