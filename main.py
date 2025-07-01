from leitura_csv import ler_csv
from neo4j_conexao import conectar_neo4j
from neo4j_insercao import inserir_aluno

caminho_arquivo = 'saida_final.csv'
df = ler_csv(caminho_arquivo)

# amostra = df.sample(n=500, random_state=42)
amostra = df

total = len(amostra)
print(f"Total de registros a inserir (amostra): {total}")

driver = conectar_neo4j(uri="bolt://localhost:7687", user="neo4j", password="12345678")

with driver.session(database="evasao4") as session:
    for idx, (_, row) in enumerate(amostra.iterrows(), 1):
        session.execute_write(inserir_aluno, row)
        print(f"Registro {idx}/{total} inserido: {row['ALUNO']}")

driver.close()
print("✅ Dados inseridos no Neo4j com sucesso!")