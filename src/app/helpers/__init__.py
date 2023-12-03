import unicodedata
import re

def normalize_city_name(city):
    """
    Normalize the city name by removing accents, converting to lowercase, 
    and removing extra spaces.
    """
    # Remove diacritical marks
    city = ''.join(
        c for c in unicodedata.normalize('NFD', city)
        if unicodedata.category(c) != 'Mn'
    )

    # Convert to lowercase
    city = city.lower()

    # Remove extra spaces and replace with a single space
    city = re.sub(r'\s+', ' ', city).strip()

    return city