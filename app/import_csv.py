# Sistema secundário de importação de produtos, usado para fornecedores que não possuem API, onde preenchemos um CSV após fazer web scraping do site do fornecedor.

import os
import csv
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from datetime import datetime
from app.database import SessionLocal
from app.models import csvinput
from logs.logger import logger

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Diretório onde os novos arquivos CSV são enviados
IMPORT_CSV_PATH = "/root/netmore-api/import_csv"

def adjust_price(price: float, percentage: float) -> float:
    return round(price * (1 + percentage / 100), 2) if percentage else price

def process_csv_file(filepath: str, db: Session, price_percentage: float, pvpr_percentage: float):
    logger.info(f"Iniciando processamento do arquivo: {filepath}")

    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [header.strip().lower() for header in reader.fieldnames]

        processed_count = 0
        errors_count = 0 

        for raw_row in reader:
            row = {k.strip().lower(): v for k, v in raw_row.items()}

            title = row.get("title", "").strip()
            ean = row.get("ean", "").strip()

            if not title or not ean:
                logger.warning("Linha ignorada: título ou EAN ausente.")
                continue

            try:
                price = float(row.get("price", 0))
                pvpr = float(row.get("pvpr", 0)) if row.get("pvpr") else round(price * 1.3, 2)
                stock = int(row.get("stock", 0))
                img_url = row.get("img", "").strip()
                size = row.get("size", "").strip()
                age = row.get("age", "").strip()
                subcategory = row.get("subcategory", "").strip()
                keywords = row.get("keywords", "").strip()
                blocopt = row.get("blocopt", "").strip()
                blocogb = row.get("blocogb", "").strip()

                logger.debug(f"{ean} | blocopt: {blocopt[:30]}... | blocogb: {blocogb[:30]}...")

                adjusted_price = adjust_price(price, price_percentage)
                adjusted_pvpr = adjust_price(pvpr, pvpr_percentage)

                existing_product = db.query(csvinput).filter(csvinput.ean == ean).first()

                if existing_product:
                    existing_product.title = title
                    existing_product.stock = stock
                    existing_product.price = adjusted_price
                    existing_product.pvpr = adjusted_pvpr
                    existing_product.brand = row.get("brand", "").strip()
                    existing_product.color = row.get("color", "").strip()
                    existing_product.family = row.get("family", "").strip()
                    existing_product.subfamily = row.get("subfamily", "").strip()
                    existing_product.supplier = row.get("supplier", "").strip()
                    existing_product.blocopt = blocopt
                    existing_product.blocogb = blocogb
                    existing_product.size = size
                    existing_product.age = age
                    existing_product.subcategory = subcategory
                    existing_product.keywords = keywords

                    if img_url:
                        existing_product.img = img_url
                    logger.info(f"Produto atualizado: {ean} | {title}")
                else:
                    new_product = csvinput(
                        ean=ean,
                        title=title,
                        stock=stock,
                        price=adjusted_price,
                        pvpr=adjusted_pvpr,
                        brand=row.get("brand", "").strip(),
                        color=row.get("color", "").strip(),
                        family=row.get("family", "").strip(),
                        subfamily=row.get("subfamily", "").strip(),
                        supplier=row.get("supplier", "").strip(),
                        img=img_url if img_url else None,
                        blocopt=blocopt,
                        blocogb=blocogb,
                        size=size,
                        age=age,
                        subcategory=subcategory,
                        keywords=keywords
                    )
                    db.add(new_product)
                    logger.info(f"Novo produto inserido: {ean} | {title}")

                processed_count += 1
            except Exception as e:
                logger.error(f"Erro ao processar o produto {ean or title}: {e}")
                errors_count += 1

        db.commit()
        logger.info(f"{processed_count} produtos importados com sucesso. {errors_count} erros.")

    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"Arquivo removido: {filepath}")
    else:
        logger.warning(f"Arquivo {filepath} não encontrado para remoção.")

def import_csvinput_data(price_percentage: float = 0, pvpr_percentage: float = 0):
    db = SessionLocal()
    try:
        csv_files = [f for f in os.listdir(IMPORT_CSV_PATH) if f.endswith(".csv")]
        if not csv_files:
            logger.info("Nenhum arquivo CSV encontrado para importar.")
            return

        for file in csv_files:
            filepath = os.path.join(IMPORT_CSV_PATH, file)
            logger.info(f"Processando arquivo CSV: {file}")
            process_csv_file(filepath, db, price_percentage, pvpr_percentage)
    except Exception as e:
        logger.error(f"Erro ao importar dados da csvinput: {e}")
    finally:
        db.close()
        logger.info("Importação de produtos csvinput concluída.")
