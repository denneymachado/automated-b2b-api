from app.family_classifier import classify_family_subfamily

# Redirecionar a classificação
def classify_family_subfamily_util(title, brand, category=None):
    """
    Redireciona para a lógica principal de classificação de família e subfamília.
    
    :param title: Título do produto
    :param brand: Marca do produto
    :param category: Categoria do produto
    :return: Tupla (family, subfamily)
    """
    return classify_family_subfamily(title, brand, category)

# Classificação baseada em regex e IDs
def classify_from_regex(value, regex_mapping):
    """
    Classifica um valor com base em um mapeamento de regex.
    
    :param value: O valor a ser classificado (ex: descrição, título)
    :param regex_mapping: Dicionário contendo regex como chave e o ID correspondente como valor
    :return: ID correspondente ou None se nenhum regex combinar
    """
    import re

    for pattern, id_value in regex_mapping.items():
        if re.search(pattern, value, re.IGNORECASE):
            return id_value
    return None
