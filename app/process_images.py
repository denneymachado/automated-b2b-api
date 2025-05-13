import os
import logging
import requests
from PIL import Image
from io import BytesIO
import ftplib
from datetime import datetime
import time
from app.database import SessionLocal
from app import models
from app.config import Settings

settings = Settings()

# Logger
LOG_FILE = "/root/netmore-api/logs/process_images.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("process_images")
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Exibir logs no console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

def get_existing_images_from_ftp():
    try:
        with ftplib.FTP(settings.ftp_b2b_host) as ftp_b2b:
            ftp_b2b.login(settings.ftp_b2b_user, settings.ftp_b2b_password)
            ftp_b2b.cwd(settings.ftp_directory)
            existing_files = set(ftp_b2b.nlst())
            logger.info(f"Total de arquivos já existentes no FTP: {len(existing_files)}")
            return existing_files
    except Exception as e:
        logger.error(f"Erro ao listar arquivos do FTP: {e}")
        return set()

def download_image(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img.verify()
            return Image.open(BytesIO(response.content))
        except (requests.exceptions.RequestException, Image.UnidentifiedImageError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logger.error(f"Erro ao baixar imagem de {url}: {e}")
    return None

def process_image(img):
    try:
        img = img.convert("RGBA")
        img_width, img_height = img.size
        margin = int(0.1 * img_width)
        new_width, new_height = img_width + 2 * margin, img_height + 2 * margin

        background = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 255))
        background.paste(img, (margin, margin), img)
        return background.convert("RGB")
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        return None

def upload_to_ftp(img, filename):
    try:
        with ftplib.FTP(settings.ftp_b2b_host) as ftp_b2b:
            ftp_b2b.login(settings.ftp_b2b_user, settings.ftp_b2b_password)
            ftp_b2b.cwd(settings.ftp_directory)
            with BytesIO() as output:
                img.save(output, format="JPEG", quality=95)
                output.seek(0)
                ftp_b2b.storbinary(f"STOR {filename}", output)
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar a imagem {filename} para o FTP: {e}")
        return False

def process_images(ignore_conditions=False):

    db = SessionLocal()
    existing_files = get_existing_images_from_ftp()

    query = db.query(models.Item).filter(models.Item.img.isnot(None))
    if not ignore_conditions:
        query = query.filter((models.Item.img_failures < 3) | (models.Item.img_failures == None))

    items = query.all()
    logger.info(f"Total de produtos a serem processados: {len(items)}.")

    for item in items:
        if not item.img:
            continue

        image_urls = [
            url.strip()
            for url in item.img.split(",")
            if url.strip().lower().startswith("http")
        ]

        success = False

        for i, url in enumerate(image_urls):
            filename = f"{item.ean}_{i}.jpg" if i > 0 else f"{item.ean}.jpg"

            if filename in existing_files:
                continue

            for attempt in range(3):
                img = download_image(url)
                if img:
                    processed_img = process_image(img)
                    if processed_img and upload_to_ftp(processed_img, filename):
                        item.img_updated = datetime.now()
                        item.img_failures = 0
                        success = True
                        logger.info(f"Imagem {filename} enviada com sucesso.")
                        break
                time.sleep(1)  # Delay de tentativas

            if success:
                break

        if not success:
            item.img_failures = (item.img_failures or 0) + 1
            logger.warning(f"Falha ao processar imagens para {item.ean}")

        db.add(item)

    db.commit()
    logger.info("Processamento de imagens concluído.")
 

if __name__ == "__main__":
    process_images()
