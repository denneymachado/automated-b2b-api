# Sistema de classificação família e subfamília baseado em keywords da regex, será posteriormente substituído pelo novo sistema de classificação semântica baseado em IA.

import re
import logging

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Regex
family_keywords = {
    "Speakers": {
        "Portable Speakers": ["jbl go", "jbl flip", "jbl charge", "jbl clip", "jbl pulse", "jbl xtreme", "wireless speaker","portable speaker", "sound outdoor",
                               "bluetooth speaker", "speaker", "soundcore motion", "soundcore glow", "soundcore flare", "soundcore rave", "soundcore select",
                               "sonos roam", "jbl link"],
        "Smart Speakers": ["echo dot", "amazon echo", "harman-kardon", "google nest", "smart speaker"],
        "Soundbars": ["soundbar", "sound bar"],
        "Home Theaters": ["home theater", "home cinema", "audio bar"],
    },
    "Tablets": {
        "Android Tablets": ["lenovo tab", "xiaomi pad", "galaxy tab", "android tablet", "tablet oneplus", "redmi pad", "honor pad", "tablet lenovo", "acer iconia", "otterbox defender"],
        "iOS Tablets": ["ipad", "ipad pro", "ipad air", "ios tablet"],
        "Readers": ["kindle", "amazon kindle", "smart paper"],
        "Windows Tablets": ["surface pro", "windows tablet", "microsoft tablet", "surface go"],
        "Drawing Tablets": ["wacom", "drawing tablet"],
        "Kids Tablets": ["fire hd", "kids tablet"]
    },
    "Headphones": {
        "Earphones": ["airpods", "freebuds", "wave buds", "earphones", "earbuds", "p40i", "liberty 4 nc", "buds", "buds2", "buds3", "buds4",
                       "soundcore a40", "poly voyager", "tune beam", "pi5 s2", "earpods", "fit pro anc", "studio buds+", "jbl live flex", "jbl live pro",
                        "anc", "space a40"],
        "Over-Ear Headphones": ["studio 3", "wh1000xm4", "quietcomfort", "bose", "over-ear headphones", "marshall monitor", "headset",
                                 "headphones", "tour tone", "tour one", "evolve2", "engage 40", "major iv", "px7 s2e", "studio pro kim", "450bt"],
        "Gaming Headsets": ["hyperx cloud", "gaming headset", "gaming headphones", "beoplay hx"],
        "Sports Headphones": ["powerbeats", "sports headphones", "sports earphones"]
    },
    "Smartwatches": {
        "Smartwatches": ["apple watch", "galaxy watch", "smartwatch", "watch series", "watch se", "watch", "pixel watch"],
        "Fitness Trackers": ["forerunner", "smart band", "fitness tracker", "fitbit", "mi band", "honor band", "band 6"],
        "Kids Smartwatches": ["vivoactive jr", "kids watch"]
    },
    "Accessories": {
        "Chargers": ["adapter", "charger", "power adapter", "charging"],
        "Powerbanks": ["powerbank", "charging station", "power bank", "charging dock"],
        "Cables": ["usb cable", "lightning cable", "cable adapter", "usb-c adapter", "cable"],
        "Cases": ["otterbox", "watch bands", "cover", "14 ultra photgraphy"],
        "Trackers": ["airtag", "tag", "skytag", "tracker", "smarttag", "smart tag"],
        "Screen Protectors": ["screen protector", "tempered glass"],
        "Memory Cards": ["sd card", "microsd card"],
        "Tripods": ["tripod", "gimbal"],
        "Pencil": ["pencil"],
        "Streaming": ["chromecast", "fire tv", "apple tv", "tv stick", "smart tv", "tv box"],
        "VR": ["playstation vr", "meta quest", "vision pro", "vr", "virtual reality", "vr headset", "htc vive flow"]
    },
    "Smartphones": {
        "Flagship Smartphones": ["iphone", "galaxy s", "pixel pro", "flagship", "s24", "google pixel", "nubia z70", "xperia", "moto edge",
                                  "s25", "nothing phone", "huawei pura", "nubia z60", "oneplus 12", "realme 12+",  "realme 12 pro+", "vivo x200",
                                  "xiaomi 14", "xiaomi 13t", "xiaomi 12t", "realme gt2", "realme gt3", "5g dual sim 8gb", "5g dual sim 12gb",
                                  "5g dual sim 16gb", "5g dual sim 32gb", "redmagic"],

        "Mid-Range Smartphones": ["redmi note", "galaxy a", "moto g", "galaxy a", "moto g", "nokia xr", "moto g24", "reno12", "poco x7",
                                   "poco f6", "oppo a", "vivo x", "vivo v", "realme q", "realme gt", "realme x", "realme q", "realme c",
                                    "realme v", "realme r", "realme g", "realme n", "realme k", "magic7", "oneplus nord", "redmi 14t",
                                      "galaxy a55", "cat s75", "honor 200", "honor 70", "honor 90", "honor magic5", "honor magic6",
                                        "honor magic7", "realme 12 pro", "xiaomi 12t", "xiaomi 12 pro", "xiaomi 12 ultra", "xiaomi 12x",
                                        "xiaomi 14t", "poco m6", "poco x5", "poco x6", "xcover", "s23", "thinkphone", "5g dual sim 4gb", 
                                        "nord 3 5g", "xiaomi 12t", "honor 70", "realme 12 pro+", "xiaomi 13t"],

        "Budget Smartphones": ["nokia c", "galaxy a04", "poco m", "moto e14", "reno11", "oppo find", "poco c65", "poco c75", "redmi 13c",
                                "redmi 13", "redmi a3", "redmi 14c", "moto g85", "moto g04s", "moto g35", "moto g55", "galaxy a34",
                                  "galaxy a15", "galaxy a35", "galaxy a16", "honor magic4", "htc u23", "nokia g22", "nokia xr20", "oppo a40",
                                  "vivo v40", "honor x6b", "realme note", "realme c61", "realme c71", "realme c81", "realme c91", "realme c101",
                                  "realme c75", "redmi 12", "s21", "a54", "s22", "a05s", "a15", "a04s", "a25", "a53", "moto g54", "moto g73",
                                    "moto g84", "4g dual sim 4gb", "dual sim 2gb", "realme c63", "a14", "x30", "realme 12", "galaxy a26", 
                                    "galaxy a36", "moto g15", "moto g14", "nokia g42", "realme 14x", "nokia g22", "honor magic6", "honor 200",
                                    "redmi a3", "poco m6", "redmi a5"],
                                  
        "Foldable Smartphones": ["galaxy z", "z fold", "z flip", "zfold", "zflip", "honor magic v3", "mix flip", "razr 50", "honor magic v2", "nokia 2660"],
        "Gaming Smartphones": ["rog phone", "legion phone", "gaming phone"],
        "Rugged Smartphones": ["cat s", "doogee s", "rugged", "cat s62", "cat b26", "cat b40", "cat s75"]
    },
    "Car Accessories": {
        "Dash Cameras": ["dash cam", "dash camera", "g300h"],
        "Car Trackers": ["gps tracker", "car tracker", "teltonika"],
        "Extra Accessories": ["car flag", "car accessory"],
        "Car Chargers": ["car charger", "car adapter"]
    },
    "Vacuum Cleaners": {
        "Robot Vacuum Cleaners": ["robot vacuum", "roborock", "robotic vacuum", "robot vacuum cleaner", "vis nav vinci", "clean x9", "aeg clean"],
        "Handheld Vacuum Cleaners": ["dyson v", "cleaner v12", "cleaner v15", "handheld vacuum", "vacuum cleaner", "vacuum cleaner", "rowenta x-force",
                                      "dreame", "cleaning robot", "cleaning vacuum", "floor", "jet 75b", "jet 60", "vertical jet"],
    },
    "Networking": {
        "Routers": ["router", "deco", "rutx11", "starlink", "ethernet router"],
        "Switches": ["poe+", "rail switch"],
        "Access Points": ["access point", "wifi 6", "hotspot"],
        "Mesh Systems": ["mesh", "wifi system"]
    },
    "Gaming": {
        "Joysticks": ["xbox wireless controller", "controller", "dualsense", "wireless controller"],
        "Consoles": ["nintendo switch", "playstation 5", "console", "xbox series", "ps5"],
        "Portable": ["wii", "portal", "portable console", "handheld console", "gameboy"]
    },
    "Cameras": {
        "Action Cameras": ["gopro", "hero", "action camera"],
        "Security Cameras": ["security camera", "outdoor camera", "indoor camera", "camera cruiser", "smart camera", "video doorbell", "imou cruiser"],
        "Lens": ["lens", "camera lens", "sigma lens"],
        "Drones": ["drone", "mavic", "phantom", "fpv"],
        "Instant Cameras": ["instax", "polaroid", "instant camera"],
        "Baby Cameras": ["baby monitor", "baby camera"],
        "Webcams": ["webcam", "logitech c", "streamcam"]
    },
    "Computers": {
        "Ultrabooks": ["macbook", "ideapad", "ultrabook", "zenbook", "xps", "thinkpad", "thinkbook", "laptop"],
        "Gaming Laptops": ["loq", "gaming laptop", "rog strix", "omen"],
        "Desktops": ["desktop", "imac", "mac mini", "mac pro", "mini pc"],
        "Monitors": ["thinkvision", "monitor"],
        "Keyboards": ["keyboard"],
        "Mouse": ["mouse", "gaming mouse"]    
    },
    "Personal Care": {
        "Hair Style": ["hair", "hair dryer", "hair straightener", "hair clipper", "hair curler", "hair trimmer",
                        "airwrap", "airstrait", "flexstyle", "hair dryer", "airstrait", "airwrap"],
        "Oral Hygiene": ["oral-b", "toothbrush", "oral care", "sonicare"],
        "Shaving": ["shaver", "trimmer", "shaving", "philips norelco", "braun series", "silk-expert", "beard trimmer", "barber", "sk3000", "vanish", "s310bt"],
        "Health": ["thermometer", "oximeter", "blood pressure"],
        "Massagers": ["massager", "massage"]
    },
    "Drones": {
        "Aerial Photography": ["drone", "mavic", "phantom"],
        "Imerssive Drones": ["dji avata", "dji fpv", "dji neo"],
        "Racing Drones": ["racing fpv", "racing drone"],
        "Aerial Cinematic": ["dji inspire"],
        "Industrial Drones": ["dji matrice", "dji agras"],
        "Agro Drones": ["dji t16", "dji t20"],
        "Underwater Drones": ["underwater drone"],
        "Accessories": ["drone accessory", "drone battery", "drone propeller", "drone bag", "drone case"],
        "Components": ["dji drone", "mavic", "phantom", "fpv"]
    },
    "Others": {
        "Generic": ["misc", "unknown", "other"]
    }
}

def classify_family_subfamily(title: str, brand: str, category: str = None):
    """
    Classifica produtos em família e subfamília com base em título, marca e categoria.
    """
    title = title.lower()
    brand = brand.lower()
    category = category.lower() if category else ""

    # 1. Prioridade máxima: Usar a categoria diretamente, se válida
    if category in family_keywords:
        family = category  # Categoria é diretamente a família
        subfamily = classify_subfamily_by_title(title, family)
        return family, subfamily

    # 2. Validar categoria com regex (fallback para categorias não reconhecidas ou genéricas em caso de não match)
    if category:
        for family, subfamily_map in family_keywords.items():
            if any(re.search(r'\b' + re.escape(keyword) + r'\b', category) for keyword in subfamily_map.keys()):
                subfamily = classify_subfamily_by_title(title, family)
                return family, subfamily

    # 3. Fallback: Classificar com base no título (se a categoria for genérica ou n existir)
    for family, subfamily_map in family_keywords.items():
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', title) for keyword in flatten_keywords(subfamily_map.values())):
            subfamily = classify_subfamily_by_title(title, family)
            return family, subfamily

    # 4. Classificação final: Caso nenhuma categoria seja encontrada
    return "Others", "Generic"

def classify_subfamily_by_title(title: str, family: str):
    """
    Identifica a subfamília com base no título do produto e na família reconhecida.
    """
    subfamily_map = family_keywords.get(family, {})
    for subfamily, keywords in subfamily_map.items():
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', title) for keyword in keywords):
            return subfamily
    return "Generic"  # Fallback para subfamília genérica

def flatten_keywords(subfamily_keywords):
    """
    Achata todas as palavras-chave de subfamílias em uma única lista.
    """
    return [keyword for keywords in subfamily_keywords for keyword in keywords]
