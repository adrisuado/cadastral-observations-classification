import csv

def transpose_list(x):

    n_row = len(x[0])

    if any(n_row != len(n) for n in x):
        raise Exception("Listas interiores no son del mismo tamaño")

    return [list(col) for col in zip(*x)]



def load_data(path, delimiter=','):

    with open(path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter= delimiter)
        data = [row for row in reader]

    return data


def get_column(data, colname):

    if not data:
        raise ValueError("La lista de datos está vacía.")

    if colname not in data[0].keys():
        raise IndexError("El nombre de columna no existe.")

    return [row[colname] for row in data]