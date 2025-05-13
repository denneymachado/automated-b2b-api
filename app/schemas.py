from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ItemCreate(BaseModel):
    title: Optional[str] = None
    ean: str
    stock: Optional[int] = None
    price: Optional[float] = None
    pvpr: Optional[float] = None
    img: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    keywords: Optional[str] = None
    last_updated: Optional[datetime] = None
    family: Optional[str] = None
    subfamily: Optional[str] = None
    activated: Optional[int] = 1
    supplier: Optional[str] = "unknown"
    blocopt: Optional[str] = None
    blocogb: Optional[str] = None
    size: Optional[str] = None
    age: Optional[str] = None
    subcategory: Optional[str] = None

class ItemB2B(BaseModel):
    title: str
    ean: str
    stock: int
    price_b2b: float
    brand: str
    category: str | None = None
    color: str
    family: str | None = None
    subfamily: str | None = None
    last_updated: datetime
    keywords: str | None = None
    activated: int | None = 1  

    class Config:
        orm_mode = True
        from_attributes = True

class ItemDev(BaseModel):
    id: int
    title: str
    ean: str
    stock: int
    price: float
    price_b2c: float
    price_b2b: float
    color: str
    brand: str
    category: str | None = None
    family: str | None = None
    subfamily: str | None = None
    img: str | None = None
    img_updated: datetime | None = None
    keywords: str | None = None
    last_updated: datetime | None = None
    activated: int | None = 1 

    class Config:
        orm_mode = True
        from_attributes = True

class FamiliaSchema(BaseModel):
    id: int
    familia: str

    class Config:
        orm_mode = True
        from_attributes = True

class SubfamiliaSchema(BaseModel):
    id: int
    subfamilia: str

    class Config:
        orm_mode = True
        from_attributes = True

class MarcaSchema(BaseModel):
    id: int
    marca: str

    class Config:
        orm_mode = True
        from_attributes = True

class CorSchema(BaseModel):
    id: int
    cor: str

    class Config:
        orm_mode = True
        from_attributes = True

class TamanhoSchema(BaseModel):
    id: int
    tamanho: str

    class Config:
        orm_mode = True
        from_attributes = True

class B2BSchema(BaseModel):
    ordem: Optional[int] = None
    nomept: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[int] = None
    nomegb: Optional[str] = None
    descpt: Optional[str] = None
    descgb: Optional[str] = None
    sku: Optional[str] = None
    sku_family: Optional[str] = None
    sku_group: Optional[str] = None
    activo: Optional[int] = None
    blocopt: Optional[str] = None
    descritorespt: Optional[str] = None
    blocogb: Optional[str] = None
    descritoresgb: Optional[str] = None
    seo_titulopt: Optional[str] = None
    seo_descpt: Optional[str] = None
    seo_titulogb: Optional[str] = None
    seo_descgb: Optional[str] = None
    cor: Optional[str] = None 
    tamanho: Optional[str] = None  
    familia: Optional[str] = None 
    subfamilia: Optional[str] = None 
    gama: Optional[int] = None
    see_also: Optional[str] = None
    tags: Optional[str] = None
    tecs: Optional[str] = None
    cuidados: Optional[str] = None
    novidade: Optional[int] = None
    destaque: Optional[int] = None
    marca: Optional[str] = None 
    ano: Optional[int] = None
    genero: Optional[int] = None
    semestre: Optional[int] = None
    generico1: Optional[int] = None
    generico2: Optional[int] = None
    generico3: Optional[int] = None
    nomesp: Optional[str] = None
    descsp: Optional[str] = None
    blocosp: Optional[str] = None
    nomefr: Optional[str] = None
    descfr: Optional[str] = None
    blocofr: Optional[str] = None
    seo_titulosp: Optional[str] = None
    seo_descsp: Optional[str] = None
    seo_titulofr: Optional[str] = None
    seo_descfr: Optional[str] = None
    nomede: Optional[str] = None
    descde: Optional[str] = None
    blocode: Optional[str] = None
    nomeit: Optional[str] = None
    descit: Optional[str] = None
    blocoit: Optional[str] = None
    combine_with: Optional[str] = None
    descritoressp: Optional[str] = None
    descritoresfr: Optional[str] = None
    descritoresde: Optional[str] = None
    descritoresit: Optional[str] = None
    seo_titulode: Optional[str] = None
    seo_descde: Optional[str] = None
    seo_tituloit: Optional[str] = None
    seo_descit: Optional[str] = None
    seo_meta: Optional[str] = None
    banner: Optional[int] = None
    grelha_tamanhos: Optional[int] = None
    sales_unit: Optional[int] = None
    package_type: Optional[int] = None
    units_in_package: Optional[int] = None
    nometec1_pt: Optional[str] = None
    nometec2_pt: Optional[str] = None
    nometec3_pt: Optional[str] = None
    nometec1_gb: Optional[str] = None
    nometec2_gb: Optional[str] = None
    nometec3_gb: Optional[str] = None
    nometec1_sp: Optional[str] = None
    nometec2_sp: Optional[str] = None
    nometec3_sp: Optional[str] = None
    nometec1_fr: Optional[str] = None
    nometec2_fr: Optional[str] = None
    nometec3_fr: Optional[str] = None
    nometec1_de: Optional[str] = None
    nometec2_de: Optional[str] = None
    nometec3_de: Optional[str] = None
    nometec1_it: Optional[str] = None
    nometec2_it: Optional[str] = None
    nometec3_it: Optional[str] = None
    weight: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    ean: Optional[str] = None
    ref_fabricante: Optional[str] = None
    keyfeature1pt: Optional[str] = None
    keyfeature2pt: Optional[str] = None
    keyfeature3pt: Optional[str] = None
    keyfeature4pt: Optional[str] = None
    keyfeature1gb: Optional[str] = None
    keyfeature2gb: Optional[str] = None
    keyfeature3gb: Optional[str] = None
    keyfeature4gb: Optional[str] = None
    keyfeature1sp: Optional[str] = None
    keyfeature2sp: Optional[str] = None
    keyfeature3sp: Optional[str] = None
    keyfeature4sp: Optional[str] = None
    keyfeature1fr: Optional[str] = None
    keyfeature2fr: Optional[str] = None
    keyfeature3fr: Optional[str] = None
    keyfeature4fr: Optional[str] = None
    keyfeature1de: Optional[str] = None
    keyfeature2de: Optional[str] = None
    keyfeature3de: Optional[str] = None
    keyfeature4de: Optional[str] = None
    keyfeature1it: Optional[str] = None
    keyfeature2it: Optional[str] = None
    keyfeature3it: Optional[str] = None
    keyfeature4it: Optional[str] = None
    garantiapt: Optional[str] = None
    garantiagb: Optional[str] = None
    garantiasp: Optional[str] = None
    garantiafr: Optional[str] = None
    garantiade: Optional[str] = None
    garantiait: Optional[str] = None
    unit_value: Optional[int] = None
    created_at: Optional[datetime] = None
    last_update: Optional[datetime] = None
    data_novidade: Optional[datetime] = None
    material: Optional[str] = None
    info_shippingpt: Optional[str] = None
    info_shippinggb: Optional[str] = None
    info_shippingsp: Optional[str] = None
    info_shippingfr: Optional[str] = None
    info_shippingde: Optional[str] = None
    info_shippingit: Optional[str] = None
    variante: Optional[str] = None
    faqs: Optional[str] = None
    descescala_met_pt: Optional[str] = None
    descescala_imp_pt: Optional[str] = None
    descescala_met_gb: Optional[str] = None
    descescala_imp_gb: Optional[str] = None
    descescala_met_sp: Optional[str] = None
    descescala_imp_sp: Optional[str] = None
    descescala_met_fr: Optional[str] = None
    descescala_imp_fr: Optional[str] = None
    descescala_met_de: Optional[str] = None
    descescala_imp_de: Optional[str] = None
    descescala_met_it: Optional[str] = None
    descescala_imp_it: Optional[str] = None
    generico4: Optional[int] = None
    generico5: Optional[int] = None
    generico29: Optional[int] = None
    generico30: Optional[int] = None
    servicos: Optional[str] = None
    PreparationTime: Optional[int] = None
    ReplacementTime: Optional[int] = None
    lenght: Optional[float] = None
    generico6: Optional[int] = None
    generico7: Optional[int] = None
    generico8: Optional[int] = None
    generico9: Optional[int] = None
    generico10: Optional[int] = None
    generico11: Optional[int] = None
    generico12: Optional[int] = None
    generico13: Optional[int] = None
    generico14: Optional[int] = None
    generico15: Optional[int] = None
    generico16: Optional[int] = None
    generico17: Optional[int] = None
    generico18: Optional[int] = None
    generico19: Optional[int] = None
    generico20: Optional[int] = None
    generico21: Optional[int] = None
    generico22: Optional[int] = None
    generico23: Optional[int] = None
    generico24: Optional[int] = None
    generico25: Optional[int] = None
    generico26: Optional[int] = None
    generico27: Optional[int] = None
    generico28: Optional[int] = None
    composto: Optional[int] = None
    marketplace_taxonomy_id: Optional[int] = None	
    marketplace_style_id: Optional[int] = None
    marketplace_composition_id: Optional[int] = None	
    marketplace_color_id: Optional[int] = None
    marketplace_size_id: Optional[int] = None
    hs_code: Optional[int] = None
    id_pais_origem: Optional[int] = None
    data_novidade_ate: Optional[datetime] = None
    nomeus: Optional[str] = None
    nomenl: Optional[str] = None
    descus: Optional[str] = None
    descnl: Optional[str] = None
    blocous: Optional[str] = None
    bloconl: Optional[str] = None
    descritoresus: Optional[str] = None
    descritoresnl: Optional[str] = None
    seo_titulous: Optional[str] = None
    seo_titulonl: Optional[str] = None
    seo_descus: Optional[str] = None
    seo_descnl: Optional[str] = None
    nometec1_us: Optional[str] = None
    nometec1_nl: Optional[str] = None
    nometec2_us: Optional[str] = None
    nometec2_nl: Optional[str] = None
    nometec3_us: Optional[str] = None
    nometec3_nl: Optional[str] = None
    keyfeature1us: Optional[str] = None
    keyfeature1nl: Optional[str] = None
    keyfeature2us: Optional[str] = None
    keyfeature2nl: Optional[str] = None
    keyfeature3us: Optional[str] = None
    keyfeature3nl: Optional[str] = None
    keyfeature4us: Optional[str] = None
    keyfeature4nl: Optional[str] = None
    garantiaus: Optional[str] = None
    garantianl: Optional[str] = None
    info_shippingus: Optional[str] = None
    info_shippingnl: Optional[str] = None
    descescala_met_us: Optional[str] = None
    descescala_met_nl: Optional[str] = None
    descescala_imp_us: Optional[str] = None
    descescala_imp_nl: Optional[str] = None
    pos_armazem: Optional[str] = None
    last_remote_update: Optional[datetime] = None
    iva: Optional[int] = None
    ProductDescriptionSaft: Optional[str] = None
    complement_with: Optional[str] = None
    feed_title_pt: Optional[str] = None
    feed_title_gb: Optional[str] = None
    feed_title_sp: Optional[str] = None
    feed_title_it: Optional[str] = None
    feed_title_de: Optional[str] = None
    feed_title_fr: Optional[str] = None
    feed_title_nl: Optional[str] = None
    feed_title_us: Optional[str] = None
    feed_desc_pt: Optional[str] = None
    feed_desc_gb: Optional[str] = None
    feed_desc_sp: Optional[str] = None
    feed_desc_it: Optional[str] = None
    feed_desc_de: Optional[str] = None
    feed_desc_fr: Optional[str] = None
    feed_desc_nl: Optional[str] = None
    feed_desc_us: Optional[str] = None
    data_disponibilidade_venda: Optional[datetime] = None
    data_entrada_armazem: Optional[datetime] = None
    codigo_amostra: Optional[int] = None
    age_group: Optional[int] = None
    classe_energetica: Optional[int] = None
    stock: Optional[int] = None
    pvp: Optional[float] = None
    pvpr: Optional[float] = None

    class Config:
        orm_mode = True
        from_attributes = True

class B2BResponseSchema(BaseModel):
    data: List[B2BSchema]
    format: str  # "json" ou "csv"
