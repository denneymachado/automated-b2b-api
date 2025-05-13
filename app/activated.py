from sqlalchemy.orm import Session
from sqlalchemy.sql import and_
from app.models import B2BStock
from datetime import datetime, timedelta
import logging

# Configurar o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_activated_status(db: Session):
    """
    Atualiza o status 'activo' dos produtos na tabela `B2B_stock` com base no valor atual do estoque.
    Regras:
    - Produtos com stock > 0 → activo = 1
    - Produtos com stock == 0 → activo = 0
    """
    updated_count = (
        db.query(B2BStock)
        .filter(B2BStock.stock > 0, B2BStock.activo != 1)
        .update({B2BStock.activo: 1}, synchronize_session=False)
    )

    updated_count += (
        db.query(B2BStock)
        .filter(B2BStock.stock == 0, B2BStock.activo != 0)
        .update({B2BStock.activo: 0}, synchronize_session=False)
    )

    db.commit()
    logger.info(f"Status 'activo' atualizado para {updated_count} produtos com base no stock atual.")


'''
# SQL para verificar os produtos com stock 0 e activo 1
SELECT sku, nomept, stock, activo
FROM B2B_stock
WHERE stock = 0 AND activo = 1;
'''
