import csv


def cache(filepath: str):
    result = []
    with open(filepath, 'r') as file:
        for row in csv.reader(file, delimiter=';'):
            result.append(tuple(row))
    return result.pop(0), result


def search(table: list, indexes: list, key: str, value: str):
    """
    Fontion search qui recherche toutes les valeurs correspondantes
    """
    icolumns = {k: v for v, k in enumerate(indexes)}
    for elt in table:
        if elt[icolumns[key]] == value:
            return elt
    return False


def filter(table: list, indexes: list, key: str, value: str):
    """
    Fonction filter qui trie la table en fonction d'un critère
    """
    icolumns = {k: v for v, k in enumerate(indexes)}
    return list(filter(lambda x: x[icolumns[key]] == value, table))
