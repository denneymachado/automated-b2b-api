from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.process_images import process_images
from app.activated import update_activated_status
from starlette.responses import RedirectResponse, StreamingResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from app.family_classifier import classify_family_subfamily
from app.config import settings
from io import StringIO
from datetime import datetime
from pydantic import ValidationError
from app.import_csvinput import import_csvinput_data
import os
import requests
import logging
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="/root/netmore-api/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_authcode(authcode: str):
    if authcode != settings.authcode:
        raise HTTPException(status_code=403, detail="Invalid authcode")

@app.middleware("http")
async def block_suspicious_ips(request: Request, call_next):
    db = next(get_db())
    client_ip = request.client.host
    request_url = request.url.path

    # Log da requisição recebida
    logger.info(f"Requisição recebida de {client_ip} para {request_url}")

    # Verificar se o IP está bloqueado
    blocked_ip = db.execute(
        text("SELECT * FROM blocked_ips WHERE ip = :ip"),
        {"ip": client_ip}
    ).fetchone()
    
    if blocked_ip:
        logger.warning(f"IP bloqueado ({client_ip}) tentando acessar: {request_url}")
        raise HTTPException(status_code=403, detail="Access Forbidden")

    # Processa a requisição
    response = await call_next(request)

    # Detectar tentativas de acessar arquivos sensíveis
    if request_url in ["/.env", "/honeypot/"]:
        reason = "Attempt to access sensitive files" if request_url == "/.env" else "Honeypot triggered"
        logger.warning(f"Tentativa suspeita detectada de {client_ip} ({reason})")

        # Adicionar IP à tabela blocked_ips
        try:
            db.execute(
                text("INSERT INTO blocked_ips (ip, reason) VALUES (:ip, :reason)"),
                {"ip": client_ip, "reason": reason}
            )
            db.commit()
            logger.info(f"IP {client_ip} bloqueado e adicionado à tabela por motivo: {reason}")
        except IntegrityError:
            logger.warning(f"IP {client_ip} já estava bloqueado anteriormente.")

    # Log da resposta
    logger.info(f"Resposta {response.status_code} para {client_ip} no endpoint {request_url}")
    return response

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")

@app.get("/honeypot/")
async def honeypot():
    logger.warning("Acesso indevido ao honeypot detectado!")
    raise HTTPException(status_code=404, detail="Not Found")

@app.post("/fetch-data/")
def fetch_data(db: Session = Depends(get_db)):
    validate_authcode(settings.authcode)
    logger.info("Iniciando coleta de dados do fornecedor")

    url = f"https://api.supplier1.de/api/stock-list?authcode={settings.authcode}&vpnr=21165&ean=1"

    try:
        logger.info(f"Realizando requisição para URL: {url}")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            logger.info("Resposta recebida com status 200")
            stock_data = response.json()
            articles = stock_data.get("Articles", [])
            logger.info(f"Total de artigos recebidos: {len(articles)}")

            added = 0
            updated = 0

            for article in articles:
                if article.get("manufacturer") in ["Transportversicherung", "MarcaExemplo"]:
                    logger.info(
                        f"Ignorando produto com articelno {article.get('articelno')} "
                        f"e manufacturer {article.get('manufacturer')}"
                    )
                    continue

                supplier_1_item = db.query(models.supplier_1).filter_by(articelno=article.get("articelno")).first()
                if supplier_1_item:
                    supplier_1_item.description = article.get("description", "")
                    supplier_1_item.quantity = article.get("quantity", 0)
                    supplier_1_item.sellingprice = float(article.get("sellingprice", 0))
                    supplier_1_item.manufacturer = article.get("manufacturer", "")
                    supplier_1_item.ean = article.get("ean", "")
                    supplier_1_item.category = article.get("category", "")
                    supplier_1_item.image = article.get("image", "")
                    supplier_1_item.yukapoints = article.get("suppoints", 0)
                    supplier_1_item.next_delivery_amount = article.get("next_delivery_amount", 0)
                    supplier_1_item.next_delivery_date = article.get("next_delivery_date", "")
                    supplier_1_item.part_number = article.get("part_number", "")
                    updated += 1                
                else:
                    supplier_1_item = models.supplier_1(
                        articelno=article.get("articelno"),
                        description=article.get("description", ""),
                        quantity=article.get("quantity", 0),
                        sellingprice=float(article.get("sellingprice", 0)),
                        manufacturer=article.get("manufacturer", ""),
                        ean=article.get("ean", ""),
                        category=article.get("category", ""),
                        image=article.get("image", ""),
                        yukapoints=article.get("suppoints", 0),
                        next_delivery_amount=article.get("next_delivery_amount", 0),
                        next_delivery_date=article.get("next_delivery_date", ""),
                        part_number=article.get("part_number", ""),
                    )
                    db.add(supplier_1_item)
                    added += 1

            db.commit()
            logger.info(f"Tabela 'supplier_1' atualizada com sucesso: {added} novos produtos adicionados, {updated} atualizados.")

            # Atualiza os itens com os dados da supplier_1
            crud.update_items_from_supplier_1(db)
            logger.info("Tabela 'items' atualizada com sucesso")

            # Desativa e zera stock dos produtos da b2b que são supplier_1 e não existem mais na supplier_1
            logger.info("Desativando produtos supplier_1 descontinuados da b2b...")

            try:
                result = db.execute(text("""
                    UPDATE b2b_stock rs
                    LEFT JOIN supplier_1 y ON TRIM(rs.sku) = TRIM(y.articelno)
                    SET rs.stock = 0, rs.activo = 0
                    WHERE rs.generico19 = 'supplier_1'
                    AND y.articelno IS NULL;
                """))
                db.commit()
                logger.info(f"{result.rowcount} produtos descontinuados da supplier_1 foram desativados com sucesso.")
            except Exception as e:
                db.rollback()
                logger.error(f"Erro ao desativar produtos descontinuados da supplier_1: {e}")

            import_csv_path = "/root/netmore-api/import_csv"
            csv_files = [f for f in os.listdir(import_csv_path) if f.endswith(".csv")]

            if csv_files:
                logger.info(f"Encontrados {len(csv_files)} arquivos CSV para importação: {csv_files}")
                import_csvinput_data()
                logger.info("Importação de produtos da csvinput concluída com sucesso")

            # Atualiza os itens dos fornecedores
            logger.info("Atualizando itens dos fornecedores...")
            crud.update_items_from_suppliers(db)
            logger.info("Tabela 'items' atualizada com sucesso")

            # Atualiza o estoque do b2b
            logger.info("Atualizando estoque b2b...")
            crud.update_b2b_stock(db)
            logger.info("Tabela 'b2b_stock' atualizada com sucesso")

            # Atualiza o status 'activo' com base no stock
            logger.info("Atualizando status 'activo' com base no stock...")
            update_activated_status(db)


            db.commit()
            db.expire_all()
            db.close()

            logger.info("Dados atualizados e sessão do banco de dados resetada para refletir as mudanças.")
            return {"message": "Data fetched and updated successfully"}

        else:
            logger.error(f"Falha ao coletar dados. Status code: {response.status_code}")
            raise HTTPException(status_code=502, detail="Falha ao coletar dados do fornecedor")
    
    except Exception as e:
        logger.error(f"Erro ao processar dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar dados")

@app.get("/b2b-api/")
def read_b2b_api(
    db: Session = Depends(get_db),
    authcode: str = Query(...),
    type: str = Query("json", regex="^(json|csv)$"),
    null: int = Query(1, ge=0, le=1),
):
    """
    Endpoint para retornar dados da tabela 'b2b_stock'.
    Permite escolher o formato de saída (JSON ou CSV) e filtrar valores nulos.
    """
    validate_authcode(authcode)

    db.rollback()
    db.commit()
    db.expire_all()

    try:
        # Obtém todos os dados da tabela b2b_stock
        b2b_data = db.query(models.b2bStock).all()

        # Converte os dados para uma lista de dicionários, removendo a coluna 'id'
        processed_data = [
            {
                column.name: (
                    getattr(item, column.name).strftime("%Y-%m-%d %H:%M:%S")
                    if column.name in ["last_update", "created_at"] and getattr(item, column.name)
                    else getattr(item, column.name)
                )
                for column in models.b2bStock.__table__.columns
                if column.name != "id"
            }
            for item in b2b_data
        ]

        # Remove colunas com valores NULL, se solicitado (null=0)
        if null == 0:
            processed_data = [
                {key: value for key, value in row.items() if value is not None}
                for row in processed_data
            ]

        # Retorna os dados no formato solicitado
        if type == "json":
            return JSONResponse(content=processed_data)

        elif type == "csv":
            output = StringIO()
            writer = csv.writer(output, delimiter=",")

            # Escreve cabeçalhos
            headers = processed_data[0].keys() if processed_data else []
            writer.writerow(headers)

            # Escreve os dados
            for row in processed_data:
                writer.writerow([row.get(header) for header in headers])

            output.seek(0)
            response = StreamingResponse(output, media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=b2b_stock.csv"
            return response

    except Exception as e:
        logger.error(f"Erro ao processar dados do endpoint /b2b-api/: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar dados")

@app.get("/api/")
def download_supplier_1_csv(db: Session = Depends(get_db), authcode: str = Query(...)):
    validate_authcode(authcode)
    logger.info("Gerando arquivo CSV com dados da tabela 'supplier_1'")

    items = db.query(models.supplier_1).all()  # Coleta todos os itens da tabela 'supplier_1'

    output = StringIO()
    writer = csv.writer(output, delimiter=",")

    # Escreve o cabeçalho do CSV
    writer.writerow(
        [
            "articelno",
            "description",
            "quantity",
            "sellingprice",
            "suppoints",
            "next_delivery_amount",
            "next_delivery_date",
            "image",
            "manufacturer",
            "ean",
            "part_number",
            "category",
        ]
    )

    # Escreve os dados dos produtos
    for item in items:
        writer.writerow(
            [
                item.articelno,
                item.description,
                item.quantity,
                item.sellingprice,
                item.yukapoints,
                item.next_delivery_amount,
                item.next_delivery_date,
                item.image,
                item.manufacturer,
                item.ean,
                item.part_number,
                item.category,
            ]
        )

    output.seek(0)
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=supplier_1_stock.csv"
    return response

@app.get("/dev/", response_model=list[schemas.ItemDev])
def read_products(skip: int = 0, limit: int = None, db: Session = Depends(get_db), authcode: str = Query(...)):
    validate_authcode(authcode)

    db.rollback()
    db.commit()
    db.expire_all()

    products = crud.get_items(db, skip=skip, limit=limit)
    dev_products = []
    for product in products:
        product.color = product.color if product.color is not None else "N/A"
        product.category = product.category if product.category is not None else "N/A"
        product.last_updated = product.last_updated if product.last_updated is not None else datetime.now()
        product.title = product.title if product.title is not None else "Unknown title"
        product.stock = product.stock if product.stock is not None else 0
        product.price = product.price if product.price is not None else 0.0
        product.brand = product.brand if product.brand is not None else "Unknown brand"

        family, subfamily = classify_family_subfamily(product.title, product.brand, product.category)
        product.family = family
        product.subfamily = subfamily

        try:
            dev_product = schemas.ItemDev.model_validate(product).model_dump()
            dev_products.append(dev_product)
        except ValidationError as e:
            logger.error(f"Validation error for product {product.id}: {e}")
            continue

    return dev_products

@app.get("/b2b/", response_model=list[schemas.Itemb2b])
def read_b2b(skip: int = 0, limit: int = None, db: Session = Depends(get_db), authcode: str = Query(...)):
    validate_authcode(authcode)

    db.rollback()
    db.commit()
    db.expire_all()

    try:
        products = crud.get_items(db, skip=skip, limit=limit)
        b2b_products = []
        for product in products:
            product.color = product.color if product.color is not None else "N/A"
            product.category = product.category if product.category is not None else "N/A"
            product.last_updated = product.last_updated if product.last_updated is not None else datetime.now()
            product.keywords = product.keywords if product.keywords is not None else "N/A"
            product.title = product.title if product.title is not None else "Unknown title"
            product.stock = product.stock if product.stock is not None else 0
            product.price = product.price if product.price is not None else 0.0
            product.brand = product.brand if product.brand is not None else "Unknown brand"

            family, subfamily = classify_family_subfamily(product.title, product.brand, product.category)
            product.family = family
            product.subfamily = subfamily

            try:
                b2b_products.append(schemas.Itemb2b.model_validate(product))
            except ValidationError as e:
                logger.error(f"Validation error for product {product.id}: {e}")
                continue

        return b2b_products

    except Exception as e:
        logger.error(f"An error occurred while fetching b2b products: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/list/")
def list_items_csv(db: Session = Depends(get_db), authcode: str = Query(...)):
    validate_authcode(authcode)
    items = crud.get_items(db)

    output = StringIO()
    writer = csv.writer(output, delimiter=",")
    writer.writerow([
        "description", "quantity", "sellingprice", "manufacturer", "ean", "category", "family",
        "subfamily", "color", "price_b2c", "price_b2b", "keywords", "activated", "blocopt", "blocogb"
    ])

    for item in items:
        writer.writerow([
            item.title, item.stock, item.price, item.brand, item.ean, item.category,
            item.family, item.subfamily, item.color,
            round(item.price * 1.26, 2) if item.price else None,
            round(item.price * 1.08, 2) if item.price else None,
            item.keywords, item.activated,
            item.blocopt, item.blocogb
        ])

    output.seek(0)
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=items.csv"
    return response

@app.post("/process-images/")
def process_images_endpoint():
    process_images(ignore_conditions=False)
    return {"message": "Images processed successfully"}

@app.post("/process-images-ignore-conditions/")
def process_images_ignore_conditions():
    process_images(ignore_conditions=True)
    return {"message": "All images processed ignoring previous conditions"}
