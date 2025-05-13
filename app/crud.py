from sqlalchemy.orm import Session
from datetime import datetime, timezone
from logs.logger import logger
from . import models
from .family_classifier import classify_family_subfamily
from app import schemas
import re

def update_items_from_suppliers(db: Session):
    """
    Atualiza a tabela 'items' com base nos dados das tabelas 'supplier_1' e 'csvinput'.
    """
    updated_items = set()
    new_items = 0
    updated_existing_items = 0
    #title = item.description.split(" - ")[0] (s/ cor no titulo)

    logger.info("Iniciando atualização da tabela 'items'...")

    # Processa os produtos da tabela supplier_1
    supplier_1_items = db.query(models.supplier_1).all()
    for item in supplier_1_items:
        ean = item.articelno  
        if not ean or not item.description:
            logger.warning(f"Item com valores incompletos ignorado. ArticelNo: {item.articelno}, Description: {item.description}")
            continue
        #title = item.description.split(" - ")[0] (Título s/ cor)
        title = item.description
        color = extract_color(item.description)
        is_graded = "graded" in title.lower()

        graded_tag = None
        if is_graded:
            if "graded a+" in title.lower():
                graded_tag = "GRADE A+"
            elif "graded a" in title.lower():
                graded_tag = "GRADE A"
            elif "graded b" in title.lower():
                graded_tag = "GRADE B"
            elif "graded c" in title.lower():
                graded_tag = "GRADE C"
            else:
                graded_tag = "GRADE"

        keywords = graded_tag if is_graded else title.lower().replace(" ", ",")
        family, subfamily = classify_family_subfamily(title, item.manufacturer, item.category)

        price_original = item.sellingprice or 0
        if item.manufacturer.lower() == "apple":
            if price_original < 50:
                price_adjusted = round(price_original * 1.12, 2)  # Apple <50: +12%
            else:
                price_adjusted = round(price_original * 1.07, 2)  # Apple 50>: +7%
        else:
            price_adjusted = round(price_original * 1.08, 2)      # Outras marcas: +8%

        pvpr_value = round(price_original * 1.3, 2)

        existing_item = db.query(models.Item).filter(models.Item.ean == ean).first()
        if existing_item:
            # Atualiza apenas se houver alteração no preço
            if existing_item.price != price_adjusted:
                existing_item.price = price_adjusted
                existing_item.pvpr = pvpr_value
                updated_existing_items += 1

            existing_item.title = title
            existing_item.color = color
            existing_item.stock = item.quantity
            existing_item.brand = item.manufacturer
            existing_item.category = None if is_graded else item.category
            existing_item.family = family
            existing_item.subfamily = subfamily
            existing_item.keywords = keywords
            existing_item.img = item.image
            existing_item.last_updated = datetime.now(timezone.utc)
            activated = 1 if item.quantity > 0 else 0
            existing_item.activated = activated
            existing_item.supplier = "supplier_1"

        else:
            new_item = models.Item(
                title=title, color=color, ean=ean, stock=item.quantity,
                price=price_adjusted, pvpr=pvpr_value, brand=item.manufacturer, 
                category=None if is_graded else item.category, 
                keywords=keywords, img=item.image, last_updated=datetime.now(timezone.utc), 
                img_updated=datetime.now(), activated=1, supplier="supplier_1"
            )
            db.add(new_item)
            new_items += 1

        updated_items.add(ean)

    # Processa os produtos da tabela csvinput (direto do csv, sem margem no preço)
    csvinput_items = db.query(models.csvinput).all()
    for item in csvinput_items:
        ean = item.ean
        if not ean or not item.title:
            logger.warning(f"Item csvinput com valores incompletos ignorado. EAN: {item.ean}, Title: {item.title}")
            continue  

        price_adjusted = item.price 
        pvpr_value = item.pvpr if item.pvpr and item.pvpr > 0 else round(price_adjusted * 1.3, 2)

        existing_item = db.query(models.Item).filter(models.Item.ean == ean).first()

        if existing_item:
            if existing_item.price != price_adjusted:
                existing_item.price = price_adjusted
                existing_item.pvpr = pvpr_value
                updated_existing_items += 1

            existing_item.stock = item.stock
            existing_item.supplier = item.supplier
            existing_item.img = item.img
            existing_item.last_updated = datetime.now(timezone.utc)
            existing_item.blocopt = item.blocopt
            existing_item.blocogb = item.blocogb
            existing_item.size = item.size
            existing_item.age = item.age
            existing_item.subcategory = item.subcategory
            existing_item.keywords = item.keywords


        else:
            new_item = models.Item(
                title=item.title,
                color=item.color,
                ean=ean,
                stock=item.stock,
                price=price_adjusted,
                pvpr=pvpr_value,
                brand=item.brand,
                category=item.category,
                family=item.family,
                subfamily=item.subfamily,
                img=item.img,
                last_updated=datetime.now(timezone.utc),
                img_updated=datetime.now(),
                activated=1 if item.stock > 0 else 0,
                supplier=item.supplier,
                blocopt=item.blocopt,
                blocogb=item.blocogb,
                size=item.size,
                age=item.age,
                subcategory=item.subcategory,
                keywords=item.keywords
            )
            db.add(new_item)
            new_items += 1

        updated_items.add(ean)

    db.flush()
    db.commit()

    logger.info(f"Tabela 'items' atualizada! {new_items} novos itens adicionados, {updated_existing_items} itens atualizados.")

def update_items_from_supplier_1(db: Session):
    """
    Atualiza a tabela 'items' com base nos dados da tabela 'supplier_1'.
    """
    supplier_1_items = db.query(models.supplier_1).all()
    updated_items = set()

    for item in supplier_1_items:
        ean = item.articelno
        if not ean or not item.description:
            logger.warning(f"Item com valores incompletos. ArticelNo: {item.articelno}, Description: {item.description}")
            continue

        # Processa os dados do item
        title = item.description.split(" - ")[0]
        color = extract_color(item.description)
        keywords = title.lower().replace(" ", ",")
        family, subfamily = classify_family_subfamily(title, item.manufacturer, item.category)

        # Verifica se o item já existe na tabela 'items'
        existing_item = db.query(models.Item).filter(models.Item.ean == ean).first()

        if existing_item:
            # Atualiza apenas se houver alterações
            if not is_item_unchanged(existing_item, schemas.ItemCreate(
                title=title,
                color=color,
                ean=ean,
                stock=item.quantity,
                price=item.sellingprice,
                brand=item.manufacturer,
                category=item.category,
                family=family,
                subfamily=subfamily,
                keywords=keywords,
                last_updated=datetime.now(timezone.utc),
                supplier="supplier_1"
            )):
                existing_item.title = title
                existing_item.color = color
                existing_item.stock = item.quantity
                existing_item.price = item.sellingprice
                existing_item.brand = item.manufacturer
                existing_item.category = item.category
                existing_item.family = family
                existing_item.subfamily = subfamily
                existing_item.keywords = keywords
                existing_item.last_updated = datetime.now(timezone.utc)
                existing_item.img_updated = datetime.now()
                existing_item.supplier = "supplier_1"
                activated = 1 if item.quantity > 0 else 0
                existing_item.activated = activated
                updated_items.add(ean)
        else:
            # Novo item
            new_item = models.Item(
                title=title,
                color=color,
                ean=ean,
                stock=item.quantity,
                price=item.sellingprice,
                brand=item.manufacturer,
                category=item.category,
                family=family,
                subfamily=subfamily,
                keywords=keywords,
                last_updated=datetime.now(timezone.utc),
                img_updated=datetime.now(),
                activated=1 if item.quantity > 0 else 0,
                supplier="supplier_1"
            )
            db.add(new_item)
            updated_items.add(ean)

    db.commit()
    logger.info(f"Tabela 'items' atualizada com sucesso! Total de itens processados: {len(updated_items)}")

def extract_color(description: str) -> str:
    """
    Extrai a cor de uma descrição usando regex.
    Se não encontrar nenhuma cor, retorna "*".
    """
    color_keywords = r"\b(?:black|white|red|blue|green|gold|silver|pink|peach|yellow|gray|grey|purple|orange|bronze|ivory|titanium|desert titanium|natural titanium|white titanium|black titanium|rose gold|midnight green|space gray|coral|mint|lavender|champagne|graphite|pacific blue|starlight|midnight|alpine green|sierra blue)\b"

    match = re.search(color_keywords, description, re.IGNORECASE)
    return match.group(0).capitalize() if match else "*"

def extract_size(description: str) -> str:
    """
    Extrai o tamanho de um produto com base na sua descrição.
    Prioriza armazenamento (GB/TB) antes de RAM, bateria e outras medidas.
    Agora captura corretamente os valores inteiros de mAh.
    """
    patterns = [
        r"(\d+(?:GB|TB))(?! RAM)", 
        r"(\d{4,5}mAh)",           
        r"(\d{1,3}mm)",           
        r"(\d{1,3}cm)",         
        r"(\d{1,3}inch)"      
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(0) 

    return "*"

def update_b2b_stock(db: Session):
    items = db.query(models.Item).all()

    try:
        for item in items:
            tamanho = extract_size(item.title)
            generico19 = item.supplier if item and item.supplier else None

            is_graded = item and "graded" in item.title.lower()
            if is_graded:
                categoria = item.category
                if "graded a+" in item.title.lower():
                    tags = "GRADE A+"
                elif "graded a" in item.title.lower():
                    tags = "GRADE A"
                elif "graded b" in item.title.lower():
                    tags = "GRADE B"
                elif "graded c" in item.title.lower():
                    tags = "GRADE C"
                else:
                    tags = "GRADE"
            else:
                categoria = "A" if generico19 == "Usados" else "NOVO"
                tags = "GRADE A" if generico19 == "Usados" else "NOVO"

            b2b_data = {
                "ordem": None,
                "nomept": item.title,
                "categoria": categoria,
                "subcategoria": None,
                "nomegb": item.title,
                "descpt": item.title,
                "descgb": item.title,
                "blocopt": item.blocopt,
                "blocogb": item.blocogb,
                "sku": item.ean,
                "sku_family": item.ean,
                "sku_group": item.ean,
                "activo": item.activated if item else 0,
                "blocopt": item.blocopt,
                "descritorespt": item.keywords if item else None,
                "blocogb": item.blocogb,
                "descritoresgb": item.keywords if item else None,
                "seo_titulopt": item.title,
                "seo_descpt": item.title,
                "seo_descgb": item.title,
                #"seo_blocogb": item.blocogb,
                "cor": item.color if item else None,
                "tamanho": item.size if item and item.size else extract_size(item.title),
                "familia": item.family if item else None,
                "subfamilia": item.subfamily if item else None,
                "gama": None,
                "see_also": None,
                "tags": tags,
                "tecs": None,
                "cuidados": None,
                "novidade": None,
                "destaque": None,
                "marca": item.brand if item else None,
                "ano": None,
                "genero": None,
                "semestre": None,
                "generico1": None,
                "generico2": None,
                "generico3": None,
                "generico19": item.supplier if item else None,
                "nomesp": item.title,
                "descsp": item.title,
                "blocosp": None,
                "nomefr": item.title,
                "descfr": item.title,
                "blocofr": None,
                "seo_titulosp": item.title,
                "seo_descsp": item.title,
                "seo_titulofr": item.title,
                "seo_descfr": item.title,
                "nomede": item.title,
                "descde": item.title,
                "blocode": None,
                "nomeit": item.title,
                "descit": item.title,
                "blocoit": None,
                "combine_with": None,
                "descritoressp": item.keywords if item else None,
                "descritoresfr": item.keywords if item else None,
                "descritoresde": item.keywords if item else None,
                "descritoresit": item.keywords if item else None,
                "seo_titulode": item.title,
                "seo_descde": item.title,
                "seo_tituloit": item.title,
                "seo_descit": item.title,
                "seo_meta": None,
                "banner": None,
                "grelha_tamanhos": None,
                "sales_unit": None,
                "package_type": None,
                "units_in_package": None,
                "ean": item.ean,
                "last_update": item.last_updated if item else datetime.now(timezone.utc),
                "stock": item.stock if item else 0,
                "pvp": item.price,
                "pvpr": item.pvpr,
            }

            b2b_item = db.query(models.b2bStock).filter(models.b2bStock.sku == item.ean).first()
            if b2b_item:
                for key, value in b2b_data.items():
                    setattr(b2b_item, key, value)
            else:
                b2b_item = models.b2bStock(**b2b_data)
                db.add(b2b_item)

        db.commit()
        logger.info("Tabela 'b2b_stock' atualizada com sucesso!")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar a tabela 'b2b_stock': {e}")
        raise

def get_full_b2b_data(db: Session):
    """
    Busca os dados completos da tabela 'b2b_stock'.
    """
    try:
        b2b_data = db.query(models.b2bStock).all()
        return [
            {
                "b2b": {
                    "ordem": item.ordem,
                    "nomept": item.nomept,
                    "categoria": item.categoria,
                    "subcategoria": item.subcategoria,
                    "nomegb": item.nomegb,
                    "blocopt": item.blocopt,
                    "blocogb": item.blocogb,
                    "sku": item.sku,
                    "sku_family": item.sku_family,
                    "sku_group": item.sku_group,
                    "activo": item.activo,
                    "blocopt": item.blocopt,
                    "descritorespt": item.descritorespt,
                    "blocogb": item.blocogb,
                    "descritoresgb": item.descritoresgb,
                    "seo_titulopt": item.seo_titulopt,
                    "seo_blocopt": item.blocopt,
                    "seo_titulogb": item.seo_titulogb,
                    "seo_blocogb": item.blocogb,
                    "cor": item.cor,
                    "tamanho": item.tamanho,
                    "familia": item.familia,
                    "subfamilia": item.subfamilia,
                    "gama": item.gama,
                    "see_also": item.see_also,
                    "tags": item.tags,
                    "tecs": item.tecs,
                    "cuidados": item.cuidados,
                    "novidade": item.novidade,
                    "destaque": item.destaque,
                    "marca": item.marca,
                    "ano": item.ano,
                    "genero": item.genero,
                    "semestre": item.semestre,
                    "generico1": item.generico1,
                    "generico2": item.generico2,
                    "generico3": item.generico3,
                    "generico19": item.generico19,
                    "nomesp": item.nomesp,
                    "descsp": item.descsp,
                    "blocosp": item.blocosp,
                    "nomefr": item.nomefr,
                    "descfr": item.descfr,
                    "blocofr": item.blocofr,
                    "seo_titulosp": item.seo_titulosp,
                    "seo_descsp": item.seo_descsp,
                    "seo_titulofr": item.seo_titulofr,
                    "seo_descfr": item.seo_descfr,
                    "nomede": item.nomede,
                    "descde": item.descde,
                    "blocode": item.blocode,
                    "nomeit": item.nomeit,
                    "descit": item.descit,
                    "blocoit": item.blocoit,
                    "combine_with": item.combine_with,
                    "descritoressp": item.descritoressp,
                    "descritoresfr": item.descritoresfr,
                    "descritoresde": item.descritoresde,
                    "descritoresit": item.descritoresit,
                    "seo_titulode": item.seo_titulode,
                    "seo_descde": item.seo_descde,
                    "seo_tituloit": item.seo_tituloit,
                    "seo_descit": item.seo_descit,
                    "seo_meta": item.seo_meta,
                    "banner": item.banner,
                    "grelha_tamanhos": item.grelha_tamanhos,
                    "sales_unit": item.sales_unit,
                    "package_type": item.package_type,
                    "units_in_package": item.units_in_package,
                    "ean": item.ean,
                    "last_update": item.last_update,
                    "stock": item.stock,
                    "pvp": item.pvp,
                    "pvpr": item.pvpr,
                    "weight": item.weight,
                    "width": item.width,
                    "height": item.height,
                    "ref_fabricante": item.ref_fabricante,
                    "keyfeature1pt": item.keyfeature1pt,
                    "keyfeature2pt": item.keyfeature2pt,
                    "keyfeature3pt": item.keyfeature3pt,
                    "keyfeature4pt": item.keyfeature4pt,
                    "keyfeature1gb": item.keyfeature1gb,
                    "keyfeature2gb": item.keyfeature2gb,
                    "keyfeature3gb": item.keyfeature3gb,
                    "keyfeature4gb": item.keyfeature4gb,
                    "keyfeature1sp": item.keyfeature1sp,
                    "keyfeature2sp": item.keyfeature2sp,
                    "keyfeature3sp": item.keyfeature3sp,
                    "keyfeature4sp": item.keyfeature4sp,
                    "keyfeature1fr": item.keyfeature1fr,
                    "keyfeature2fr": item.keyfeature2fr,
                    "keyfeature3fr": item.keyfeature3fr,
                    "keyfeature4fr": item.keyfeature4fr,
                    "keyfeature1de": item.keyfeature1de,
                    "keyfeature2de": item.keyfeature2de,
                    "keyfeature3de": item.keyfeature3de,
                    "keyfeature4de": item.keyfeature4de,
                    "keyfeature1it": item.keyfeature1it,
                    "keyfeature2it": item.keyfeature2it,
                    "keyfeature3it": item.keyfeature3it,
                    "keyfeature4it": item.keyfeature4it,
                    "garantiapt": item.garantiapt,
                    "garantiagb": item.garantiagb,
                    "garantiasp": item.garantiasp,
                    "garantiafr": item.garantiafr,
                    "garantiade": item.garantiade,
                    "garantiait": item.garantiait,
                    "unit_value": item.unit_value,
                    "created_at": item.created_at,
                    "data_novidade": item.data_novidade,
                    "material": item.material,
                    "info_shippingpt": item.info_shippingpt,
                    "info_shippinggb": item.info_shippinggb,
                    "info_shippingsp": item.info_shippingsp,
                    "info_shippingfr": item.info_shippingfr,
                    "info_shippingde": item.info_shippingde,
                    "info_shippingit": item.info_shippingit,
                }
            }
            for item in b2b_data
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar dados completos da tabela 'b2b_stock': {e}")
        raise

def get_items(db: Session, skip: int = 0, limit: int = None):
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_item_by_ean(db: Session, ean: str):
    return db.query(models.Item).filter(models.Item.ean == ean).first()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, ean: str, item: schemas.ItemCreate):
    db_item = db.query(models.Item).filter(models.Item.ean == ean).first()
    if db_item:
        for key, value in item.model_dump().items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def is_item_unchanged(db_item: models.Item, item_data: schemas.ItemCreate) -> bool:
    """
    Verifica se os dados de um item permanecem inalterados.
    """
    db_item_data = {
        key: getattr(db_item, key) for key in item_data.model_dump().keys()
    }
    for key, value in item_data.model_dump().items():
        if db_item_data[key] != value:
            return False
    return True
