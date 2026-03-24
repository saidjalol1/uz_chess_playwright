"""
Random Uzbek name generator for registration profiles.
"""

import random
import string

# Common Uzbek first names
UZBEK_MALE_NAMES = [
    "Abdulla", "Akbar", "Akmal", "Alisher", "Anvar", "Asror", "Aziz", "Bahrom",
    "Bakhodir", "Behruz", "Bobur", "Botir", "Daler", "Dilshod", "Eldor", "Farhod",
    "Farrukh", "Humoyun", "Husan", "Ilhom", "Islom", "Jahongir", "Jamshid", "Jasur",
    "Kamoliddin", "Komil", "Laziz", "Lochin", "Madamin", "Mansur", "Mirzo", "Muhammadali",
    "Muzaffar", "Navruz", "Nilufar", "Nodir", "Obid", "Odil", "Otabek", "Oybek",
    "Pulat", "Ravshan", "Rustam", "Sanjar", "Sardor", "Sherzod", "Shohruh", "Shuhrat",
    "Saidakbar", "Temur", "Tohir", "Ulugbek", "Umid", "Vohid", "Yusuf", "Zafar"
]

UZBEK_FEMALE_NAMES = [
    "Adolat", "Barno", "Charos", "Dildora", "Dilorom", "Dilrabo", "Feruza", "Gavhar",
    "Gulbahor", "Gulnora", "Gulshan", "Hilola", "Hulkar", "Iroda", "Kamola", "Kumush",
    "Lobar", "Madina", "Mahbuba", "Malika", "Manzura", "Marguba", "Mohira", "Muazzam",
    "Munira", "Nafisa", "Nasiba", "Nigora", "Nilufar", "Nozima", "Odinaxon", "Oydin",
    "Ozoda", "Qunduz", "Rano", "Rohila", "Sabohat", "Saida", "Sarvinoz", "Sevara",
    "Shahlo", "Shoira", "Sitora", "Saodat", "Umida", "Yulduz", "Zarina", "Zilola"
]

# Common Uzbek surnames
UZBEK_SURNAMES = [
    "Abdullayev", "Ahmedov", "Aliyev", "Askarov", "Baxtiyorov", "Berdiyev",
    "Davlatov", "Ergashev", "Fayzullayev", "Hasanov", "Holmatov", "Ibragimov",
    "Ismoilov", "Jalolov", "Karimov", "Komilov", "Latipov", "Mamatov",
    "Mirzayev", "Nabiyev", "Nazarov", "Normatov", "Nuriddinov", "Olimov",
    "Ortiqov", "Qodirov", "Rahimov", "Rashidov", "Saidov", "Salimov",
    "Sharipov", "Sultonov", "Tashmatov", "Toshmatov", "Turgunov", "Umarov",
    "Usmonov", "Xolmatov", "Yodgorov", "Yuldashev", "Yunusov", "Zakirov"
]


def generate_uzbek_name() -> dict:
    """
    Generate a random Uzbek first name, last name, and unique username.
    
    Returns:
        dict with keys: first_name, last_name, username
    """
    # Randomly pick male or female
    if random.choice([True, False]):
        first_name = random.choice(UZBEK_MALE_NAMES)
    else:
        first_name = random.choice(UZBEK_FEMALE_NAMES)
    
    last_name = random.choice(UZBEK_SURNAMES)
    
    # Generate unique username: first_name + random digits
    random_suffix = ''.join(random.choices(string.digits, k=random.randint(3, 5)))
    username = f"{first_name.lower()}{random_suffix}"
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "username": username
    }
