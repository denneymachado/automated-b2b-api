# Em desenvolvimento —> all-MiniLM-L6-v2

from sentence_transformers import SentenceTransformer, util
from deep_translator import GoogleTranslator
import torch
import logging

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

logger = logging.getLogger(__name__)

model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

subfamily_descriptions = {
    # Speakers
    "Speakers / Portable Speakers": "Wireless or Bluetooth portable speakers like JBL and Soundcore for music on the go. Caixas de som portáteis sem fio ou Bluetooth como JBL e Soundcore para ouvir música em movimento",
    "Speakers / Smart Speakers": "Voice-controlled smart speakers like Amazon Echo and Google Nest. Alto-falantes inteligentes com controle por voz como Amazon Echo e Google Nest",
    "Speakers / Soundbars": "Soundbars for home audio enhancement and surround sound. Soundbars para melhorar o áudio da sua TV e criar som envolvente",
    "Speakers / Home Theaters": "Home theater systems and audio bars for immersive movie experiences. Sistemas de home theater e áudio para experiências de cinema em casa",

    # Tablets
    "Tablets / Android Tablets": "Android tablets from brands like Lenovo, Xiaomi, and Samsung. Tablets Android de marcas como Lenovo, Xiaomi e Samsung",
    "Tablets / iOS Tablets": "Apple iPads including Air, Pro, and standard models. iPads da Apple incluindo os modelos Air, Pro e padrão",
    "Tablets / Readers": "E-book readers like Kindle and Amazon Smart Paper. Leitores de e-book como Kindle e Amazon Smart Paper",
    "Tablets / Windows Tablets": "Windows tablets and hybrids like Surface Pro and Microsoft tablets. Tablets com Windows como o Surface Pro",
    "Tablets / Drawing Tablets": "Graphic drawing tablets such as Wacom for digital art. Tablets gráficos para desenho como Wacom",
    "Tablets / Kids Tablets": "Child-friendly tablets like Fire HD Kids Edition. Tablets infantis como o Fire HD Kids Edition",

    # Accessories
    "Accessories / Chargers": "Charging accessories such as power adapters and USB chargers. Acessórios de carregamento como adaptadores de energia e carregadores USB",
    "Accessories / Powerbanks": "Portable power banks and charging stations for mobile devices. Powerbanks portáteis e estações de carregamento",
    "Accessories / Cables": "USB, Lightning, and USB-C cables and adapters. Cabos USB, Lightning e USB-C e adaptadores",
    "Accessories / Cases": "Protective cases and covers for phones and smartwatches. Capas protetoras para telefones e smartwatches",
    "Accessories / Trackers": "Device tracking accessories like AirTags and SmartTags. Rastreadores de dispositivos como AirTags e SmartTags",
    "Accessories / Screen Protectors": "Tempered glass and screen protector films. Películas de proteção de tela e vidro temperado",
    "Accessories / Memory Cards": "MicroSD and SD cards for storage expansion. Cartões de memória MicroSD e SD para expandir o armazenamento",
    "Accessories / Pencil": "Digital styluses and smart pencils for tablets. Lápis digitais para tablets como Apple Pencil",
    "Accessories / Streaming": "Streaming devices like Chromecast, Fire TV, and Apple TV. Dispositivos de streaming como Chromecast, Fire TV e Apple TV",
    "Accessories / VR": "Virtual reality headsets and VR accessories for immersive experiences. Óculos e acessórios de realidade virtual",
    "Accessories / GPS Trackers": "Compact GPS tracking tags like SmartTag and AirTag clones. Rastreadores GPS compactos",
    "Accessories / Smart Tags": "Smart tags and trackers for finding lost items. Etiquetas inteligentes para encontrar objetos perdidos",
    "Accessories / Smart Plugs": "Smart plugs for home automation and remote control. Tomadas inteligentes para automação residencial",
    "Accessories / Smart Lights": "Smart lighting solutions for home automation. Lâmpadas inteligentes para automação residencial",
    "Accessories / Smart Sensors": "Smart sensors for home automation and security. Sensores inteligentes para automação e segurança",

    # Headphones
    "Headphones / Earphones": "In-ear wireless earphones and earbuds like AirPods, Freebuds, and Soundcore. Fones de ouvido intra-auriculares sem fio como AirPods, Freebuds e Soundcore",
    "Headphones / Over-Ear Headphones": "Over-ear headphones and headsets including Bose, Sony, and Marshall. Fones de ouvido over-ear como Bose, Sony e Marshall",
    "Headphones / Gaming Headsets": "Headsets designed for gaming with built-in microphones. Headsets gamer com microfone integrado",
    "Headphones / Sports Headphones": "Water-resistant earphones made for sports and workouts. Fones resistentes à água para esportes e exercícios",

    # Smartwatches
    "Smartwatches / Smartwatches": "Smartwatches such as Apple Watch and Galaxy Watch. Relógios inteligentes como Apple Watch e Galaxy Watch",
    "Smartwatches / Fitness Trackers": "Fitness trackers and smart bands like Fitbit and Mi Band. Pulseiras fitness e smartbands como Fitbit e Mi Band",
    "Smartwatches / Kids Smartwatches": "Smartwatches designed for children with safety features. Relógios inteligentes infantis com recursos de segurança",

    # Smartphones
    "Smartphones / Flagship Smartphones": "High-end flagship smartphones like iPhone, Galaxy S, Pixel, and OnePlus. Smartphones topo de linha como iPhone, Galaxy S, Pixel e OnePlus",
    "Smartphones / Mid-Range Smartphones": "Affordable mid-range smartphones from Xiaomi, Realme, and Motorola. Smartphones intermediários como Xiaomi, Realme e Motorola",
    "Smartphones / Budget Smartphones": "Budget smartphones with essential features at low price. Smartphones de entrada com recursos essenciais a preço acessível",
    "Smartphones / Foldable Smartphones": "Foldable phones like Galaxy Z Fold and Flip series. Telefones dobráveis como Galaxy Z Fold e Flip",
    "Smartphones / Gaming Smartphones": "Gaming smartphones with high performance like ROG Phone and RedMagic. Smartphones gamer de alta performance como ROG Phone e RedMagic",
    "Smartphones / Rugged Smartphones": "Rugged smartphones built to withstand harsh environments. Smartphones robustos para ambientes exigentes",

    # Car Accessories
    "Car Accessories / Dash Cameras": "Dashcams and in-car security cameras. Câmeras veiculares de segurança",
    "Car Accessories / Car Trackers": "GPS tracking devices for vehicles. Rastreadores GPS para veículos",
    "Car Accessories / Extra Accessories": "Car-related gadgets and accessories like flags. Acessórios diversos para automóveis como bandeiras",
    "Car Accessories / Car Chargers": "Car chargers and in-vehicle power adapters. Carregadores para carros e adaptadores veiculares",

    # Vacuum Cleaners
    "Vacuum Cleaners / Robot Vacuum Cleaners": "Robotic vacuum cleaners like Roborock for automated cleaning. Aspiradores robóticos como Roborock para limpeza automatizada",
    "Vacuum Cleaners / Handheld Vacuum Cleaners": "Portable and handheld vacuum cleaners for manual cleaning. Aspiradores portáteis e manuais para limpeza rápida",

    # Networking
    "Networking / Routers": "Internet routers including mesh and ethernet routers. Roteadores de internet incluindo sistemas mesh e roteadores Ethernet",
    "Networking / Switches": "Network switches such as PoE and rail-mounted switches. Switches de rede como PoE e switches industriais",
    "Networking / Access Points": "WiFi access points and hotspot devices. Pontos de acesso WiFi e dispositivos de hotspot",
    "Networking / Mesh Systems": "Whole-home mesh WiFi systems. Sistemas de WiFi mesh para toda a casa",

    # Gaming
    "Gaming / Joysticks": "Gaming controllers for consoles and PCs. Controles para jogos em consoles e PC",
    "Gaming / Consoles": "Gaming consoles like PlayStation, Xbox, and Nintendo Switch. Consoles de jogos como PlayStation, Xbox e Nintendo Switch",
    "Gaming / Portable": "Handheld gaming consoles like Wii and Gameboy. Consoles portáteis como Wii e Gameboy",

    # Cameras
    "Cameras / Action Cameras": "Portable action cameras like GoPro for extreme sports. Câmeras de ação como GoPro para esportes radicais",
    "Cameras / Security Cameras": "Indoor and outdoor security surveillance cameras. Câmeras de segurança para ambientes internos e externos",
    "Cameras / Lens": "Camera lenses and accessories like Sigma lens. Lentes para câmeras e acessórios como lentes Sigma",
    "Cameras / Drones": "Camera drones for aerial photography and filming. Drones com câmera para fotografia e filmagem aérea",
    "Cameras / Instant Cameras": "Instant photo-printing cameras like Instax and Polaroid. Câmeras instantâneas como Instax e Polaroid",
    "Cameras / Baby Cameras": "Monitors and cameras for baby care. Monitores e câmeras para bebês",
    "Cameras / Webcams": "Webcams for streaming and video calls. Webcams para streaming e videochamadas",

    # Computers
    "Computers / Ultrabooks": "Lightweight laptops like MacBook, Ideapad, and ThinkPad. Notebooks leves como MacBook, Ideapad e ThinkPad",
    "Computers / Gaming Laptops": "High-performance laptops for gaming. Notebooks de alto desempenho para jogos",
    "Computers / Desktops": "Desktop computers and mini PCs including iMac and Mac Mini. Computadores desktop e mini PCs incluindo iMac e Mac Mini",
    "Computers / Monitors": "Computer monitors for display output. Monitores para computador",
    "Computers / Keyboards": "External computer keyboards. Teclados externos para computador",
    "Computers / Mouse": "Computer mouses and gaming mice. Mouses para computador e mouses gamers",

    # Personal Care
    "Personal Care / Hair Style": "Hair dryers, straighteners, and styling tools. Secadores, chapinhas e ferramentas para styling capilar",
    "Personal Care / Oral Hygiene": "Electric toothbrushes and oral care products. Escovas de dente elétricas e produtos para higiene bucal",
    "Personal Care / Shaving": "Electric shavers, trimmers, and grooming kits. Aparelhos de barbear elétricos, trimmers e kits de cuidados",
    "Personal Care / Health": "Health monitors like thermometers and oximeters. Monitores de saúde como termômetros e oxímetros",
    "Personal Care / Massagers": "Massage devices for relaxation. Dispositivos de massagem para relaxamento",

    # Drones
    "Drones / Aerial Photography": "Drones designed for capturing aerial photos and videos. Drones projetados para fotografia e filmagem aérea",
    "Drones / Imerssive Drones": "Drones for immersive FPV flight experiences. Drones para experiências imersivas de voo FPV",
    "Drones / Racing Drones": "High-speed FPV drones built for racing. Drones de alta velocidade para corridas FPV",
    "Drones / Aerial Cinematic": "Professional drones for cinematic aerial shots. Drones profissionais para tomadas aéreas cinematográficas",
    "Drones / Industrial Drones": "Industrial drones for inspection and surveying. Drones industriais para inspeção e levantamento",
    "Drones / Agro Drones": "Agricultural drones for spraying and crop monitoring. Drones agrícolas para pulverização e monitoramento de culturas",
    "Drones / Underwater Drones": "Drones for underwater exploration and photography. Drones para exploração subaquática e fotografia",

    # Printers & Scanners
    "Printers / Label Printers": "Thermal and label printers for barcode and shipping. Impressoras térmicas e de etiquetas para código de barras e envios",
    "Printers / Barcode Scanners": "Handheld and desktop barcode scanners for inventory. Leitores de código de barras portáteis e de mesa para inventário",
    "Printers / Accessories": "Printer accessories like label rolls and power adapters. Acessórios para impressora como rolos de etiqueta e adaptadores",

    # Apparel
    "Apparel / Jerseys": "Team and sports jerseys for fans and collectors. Camisas de time e esportivas para fãs e colecionadores",
    "Apparel / Kids Clothing": "Clothing designed for children. Roupas infantis",
    "Apparel / Shoes": "Casual and sports footwear for all ages. Calçados casuais e esportivos para todas as idades",
    "Apparel / Boots": "Protective and stylish boots for outdoor or casual wear. Botas protetoras e estilosas para uso externo ou casual",
    "Apparel / Accessories": "Fashion accessories like caps, socks, and wristbands. Acessórios de moda como bonés, meias e pulseiras",
    "Apparel / Team Shirts": "Official or inspired shirts from sports teams. Camisetas oficiais ou inspiradas em times esportivos",
    "Apparel / Infant Shirts": "T-shirts and outfits for children. Camisetas e roupas para crianças",
    "Apparel / Hats": "Children and adult hats with sports or cartoon branding. Chapéus para crianças e adultos com temas esportivos ou de desenhos",
    "Apparel / Socks": "Fun or branded socks. Meias temáticas ou de marca",
    "Apparel / Rainwear": "Ponchos and raincoats, often themed. Capas de chuva e ponchos, muitas vezes temáticos",
    "Apparel / Costumes": "Costumes and outfits for themed events or parties. Fantasias e trajes para eventos temáticos ou festas",

    # Photography Accessories
    "Photo Accessories / Gimbals": "Stabilizers and gimbals for smooth video recording. Estabilizadores e gimbals para gravação de vídeos suaves",
    "Photo Accessories / Tripods": "Tripods and mounts for cameras and phones. Tripés e suportes para câmeras e celulares",
    "Photo Accessories / Bags & Cases": "Protective gear for transporting photography equipment. Acessórios de proteção para transporte de equipamento fotográfico",

    # Replacement Parts
    "Parts / Phone Screens": "Replacement screens and displays for smartphones. Telas de reposição para smartphones",
    "Parts / Phone Batteries": "Batteries for phone models like iPhone, Samsung, Xiaomi, etc. Baterias para modelos de celular como iPhone, Samsung, Xiaomi, etc",
    "Parts / Phone Cameras": "Front and rear cameras for smartphones. Câmeras frontal e traseira para smartphones",
    "Parts / Phone Charging Ports": "USB and Lightning charging ports for mobile devices. Portas de carregamento USB e Lightning para dispositivos móveis",
    "Parts / Phone Speakers": "Speakers and audio components for mobile phones. Alto-falantes e componentes de áudio para celulares",
    "Parts / Phone Microphones": "Microphones and audio components for mobile phones. Microfones e componentes de áudio para celulares",
    "Parts / Phone Buttons": "Home, power and volume buttons for phones. Botões home, power e volume para celulares",
    "Parts / Phone Flex Cables": "Flex cables and ribbons for mobile phone internals. Cabos flexíveis e fitas para componentes internos de celulares",

    "Parts / Drone Propellers": "Propellers and blades for quadcopters and drones. Hélices e pás para quadricópteros e drones",
    "Parts / Drone Motors": "Brushless motors and components for drones. Motores brushless e componentes para drones",
    "Parts / Drone Batteries": "Rechargeable drone batteries and power modules. Baterias recarregáveis e módulos de energia para drones",
    "Parts / Drone Frames": "Arms, landing gear, and frames for drones. Braços, trem de pouso e estruturas para drones",

    "Parts / Laptop Batteries": "Laptop replacement batteries. Baterias para notebooks",
    "Parts / Laptop Screens": "LCD or LED screens for laptops and ultrabooks. Telas LCD ou LED para notebooks e ultrabooks",
    "Parts / Keyboards": "Built-in keyboards for laptops or desktop replacement kits. Teclados para notebooks ou kits de reposição para desktop",
    "Parts / SSDs & Storage": "Solid state drives and HDDs for storage upgrades. SSDs e HDs para upgrades de armazenamento",
    "Parts / RAM Memory": "Laptop and desktop RAM memory modules. Módulos de memória RAM para notebooks e desktops",
    "Parts / Cooling Fans": "Fans and heatsinks for notebooks and desktops. Ventoinhas e dissipadores para notebooks e desktops",

    "Parts / Printer Parts": "Print heads, rollers, and maintenance kits for printers. Cabeças de impressão, rolos e kits de manutenção para impressoras",
    "Parts / Camera Lens Parts": "Lens rings, mounts, and optical modules for cameras. Anéis de lente, mounts e módulos ópticos para câmeras",
    
    # School & Lifestyle
    "School Supplies / Bottles": "Reusable and themed bottles for children, ideal for school or outdoor activities. Garrafas reutilizáveis e temáticas para crianças, ideais para escola ou atividades ao ar livre",
    "School Supplies / Mugs": "Ceramic, plastic or thermal mugs for daily use, often with cartoon or branded themes. Canecas de cerâmica, plástico ou térmicas para uso diário, muitas vezes com temas de desenhos ou marcas",
    "School Supplies / Backpacks": "School backpacks for children with cartoon and branded designs. Mochilas escolares para crianças com estampas de desenhos e marcas",
    "School Supplies / Pencil Cases": "Zippered cases for storing pens, pencils, and school supplies. Estojo com zíper para guardar canetas, lápis e materiais escolares",
    "School Supplies / Lunch Bags": "Thermal and portable bags for carrying school lunches. Bolsas térmicas e portáteis para lanches escolares",
    "School Supplies / Wallets": "Small pouches or wallets for children to carry coins, cards, or IDs. Porta-moedas ou carteiras pequenas para crianças",
    "School Supplies / Stationery Kits": "Kits containing pens, erasers, rulers, and other stationery items. Kits com canetas, borrachas, réguas e outros itens de papelaria",
    "School Supplies / Drinkware": "Cups, tumblers, and training mugs for young children. Copos, canecas e garrafinhas para crianças pequenas",
    "School Supplies / Sets & Combos": "Back-to-school sets with coordinated backpack, pencil case, and bottles. Kits de volta às aulas com mochila, estojo e garrafa combinando",

    # Bags & Lifestyle
    "Fashion / Wallets": "Small wallets and card holders for everyday use. Carteiras pequenas e porta-cartões para uso diário",
    "Fashion / Caps": "Stylish or themed caps and hats. Bonés e chapéus estilosos ou temáticos",
    "Fashion / Umbrellas": "Portable umbrellas with themed designs. Guarda-chuvas portáteis com designs temáticos",
    "Fashion / Tote Bags": "Reusable or branded tote bags for shopping and daily use. Sacolas reutilizáveis ou de marca para compras e uso diário",
    "Fashion / Makeup Bags": "Compact bags to carry cosmetics and hygiene products. Necessaires para levar cosméticos e produtos de higiene",
    "Fashion / Lanyards": "Neck lanyards for keys or ID cards. Cordões para chaves ou crachás",
    "Fashion / Cufflinks": "Metal cufflinks themed with football clubs and fashion motifs. Abotoaduras de metal com temas de clubes de futebol e motivos fashion",
    "Fashion / Neck Pouches": "Small wearable pouches and badge holders. Bolsinhas para usar no pescoço e porta-crachás",
    "Fashion / Pouches": "Small bags for carrying essentials. Bolsinhas para levar itens essenciais",
    "Fashion / Backpacks": "Stylish backpacks for everyday use. Mochilas estilosas para uso diário",
    "Fashion / Handbags": "Fashionable handbags and purses. Bolsas fashion e carteiras",
    "Fashion / Suitcases": "Travel bags and suitcases for luggage. Malas de viagem",
    "Fashion / Travel Bags": "Travel bags and backpacks for luggage. Bolsas de viagem e mochilas",

    # Home & Kitchen
    "Home & Kitchen / Mugs": "Ceramic or insulated mugs for hot and cold beverages. Canecas de cerâmica ou térmicas para bebidas quentes e frias",
    "Home & Kitchen / Plates": "Plates and tableware, often themed for children. Pratos e utensílios de mesa, muitas vezes temáticos para crianças",
    "Home & Kitchen / Cutlery": "Spoons, forks and kids-friendly utensils. Talheres e utensílios infantis",
    "Home & Kitchen / Lunchboxes": "Lunchboxes for kids or office use, often themed. Lancheiras para crianças ou escritório, muitas vezes temáticas",

    # Kitchen Appliances
    "Kitchen Appliances / Air Fryers": "Electric air fryers for healthy frying with little to no oil. Fritadeiras elétricas para frituras saudáveis com pouco ou nenhum óleo",
    "Kitchen Appliances / Multi-Cookers": "Multifunctional cookers for pressure cooking, slow cooking, steaming, and more. Panelas elétricas multifuncionais para cozimento rápido, lento, vapor e mais",
    "Kitchen Appliances / Coffee Machines": "Coffee makers including espresso machines and capsule systems. Máquinas de café incluindo espresso e sistemas de cápsulas",
    "Kitchen Appliances / Food Grills": "Indoor electric grills like Foodi Grill Max for grilling and roasting. Churrasqueiras elétricas para uso interno como Foodi Grill Max",
    "Kitchen Appliances / Mixers & Blenders": "Electric mixers, hand blenders, and food processors. Batedeiras, liquidificadores e processadores de alimentos",
    "Kitchen Appliances / Juicers": "Juicers and extractors for making fresh juices. Espremedores e extratoras para sucos naturais",
    "Kitchen Appliances / Electric Kettles": "Electric kettles for boiling water quickly. Chaleiras elétricas para ferver água rapidamente",
    "Kitchen Appliances / Rice Cookers": "Electric rice cookers for easy cooking. Panelas elétricas para arroz",
    "Kitchen Appliances / Induction Cookers": "Induction cookers for fast and efficient cooking. Fogões por indução para cozimento rápido e eficiente",
    "Kitchen Appliances / Pressure Cookers": "Electric pressure cookers for quick cooking. Panelas de pressão elétricas para cozimento rápido",
    "Kitchen Appliances / Food Processors": "Food processors for chopping, slicing, and mixing. Processadores de alimentos para picar, fatiar e misturar",
    "Kitchen Appliances / Toasters": "Electric toasters for making toast and bagels. Torradeiras elétricas",
    "Kitchen Appliances / Ovens": "Electric ovens for baking and cooking. Fornos elétricos para assar e cozinhar",
    "Kitchen Appliances / Dishwashers": "Dishwashers for automatic dish cleaning. Máquinas de lavar louça",
    "Kitchen Appliances / Water Purifiers": "Water purifiers and filtration systems. Purificadores e filtros de água",
    "Kitchen Appliances / Food Dehydrators": "Food dehydrators for preserving fruits and vegetables. Desidratadores de alimentos para preservar frutas e vegetais",
    "Kitchen Appliances / Ice Cream Makers": "Ice cream machines for making homemade ice cream. Máquinas de sorvete caseiro",
    "Kitchen Appliances / Electric Grills": "Electric grills for indoor grilling and cooking. Churrasqueiras elétricas para uso interno",
    "Kitchen Appliances / Food Steamers": "Steamers for cooking vegetables and seafood. Panelas a vapor para cozinhar legumes e frutos do mar",

    # Toys & Collectibles
    "Toys & Collectibles / Plush Toys": "Soft stuffed animals and plush figures. Pelúcias e bichos de pelúcia",
    "Toys & Collectibles / Pins & Badges": "Collectible pins and branded badges. Pins colecionáveis e badges de marcas",
    "Toys & Collectibles / Figurines": "Small collectible figures. Pequenas estatuetas colecionáveis",
    "Toys & Collectibles / Balls": "Sports balls with team branding. Bolas esportivas com logos de times",
    "Toys & Collectibles / Stickers": "Sticker sets, often collectible or themed. Adesivos colecionáveis ou temáticos",

    # Insurance & Protection Plans
    "Services / Protection Plans": "Product protection plans and extended warranty services like DJI Care Refresh, AppleCare, and other coverage programs. Planos de proteção e garantias estendidas como DJI Care Refresh e AppleCare",
    "Services / Insurance": "Insurance services for electronic devices and personal items. Seguros para dispositivos eletrônicos e itens pessoais",
    "Services / Warranty": "Warranty services for electronic devices and personal items. Serviços de garantia para dispositivos eletrônicos e itens pessoais",
    
    # Others
    "Others / Generic": "Uncategorized or generic electronic product. Produto eletrônico genérico ou não categorizado"
}

# Pré-computa os embeddings dos alvos
subfamily_embeddings = {
    k: model.encode(v, convert_to_tensor=True)
    for k, v in subfamily_descriptions.items()
}

def translate_if_low_score(title: str, best_score: float, threshold: float = 0.45) -> str:
    if best_score < threshold:
        try:
            return GoogleTranslator(source='auto', target='en').translate(title)
        except:
            pass
    return title

def classify_by_semantics(title: str) -> tuple[str, str]:
    title = (title or "").strip()
    if not title:
        return "Others", "Generic"

    try:
        title_embedding = model.encode(title, convert_to_tensor=True)
        best_match, best_score = None, float("-inf")

        for key, emb in subfamily_embeddings.items():
            score = util.cos_sim(title_embedding, emb).item()
            if score > best_score:
                best_match, best_score = key, score

        translated_title = translate_if_low_score(title, best_score)
        if translated_title != title:
            title_embedding = model.encode(translated_title, convert_to_tensor=True)
            for key, emb in subfamily_embeddings.items():
                score = util.cos_sim(title_embedding, emb).item()
                if score > best_score:
                    best_match, best_score = key, score

        if best_match and " / " in best_match:
            family, subfamily = best_match.split(" / ")
            logger.info(f"[SEMANTIC] '{title}' ➜ {family} / {subfamily} (score: {best_score:.4f})")
            return family, subfamily

        logger.warning(f"[SEMANTIC] Erro no split de match: '{best_match}'")
        return "Others", "Generic"

    except Exception as e:
        logger.error(f"[SEMANTIC] Erro ao classificar '{title}': {str(e)}")
        return "Others", "Generic"
