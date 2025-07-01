from neo4j import GraphDatabase

def conectar_neo4j(uri="bolt://localhost:7687", user="neo4j", password="12345678"):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver
