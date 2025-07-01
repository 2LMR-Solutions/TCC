import pandas as pd

def ler_csv(caminho_csv):
    df = pd.read_csv(caminho_csv)
    df.replace('Modulo Nao Iniciado', 0, inplace=True)
    return df
