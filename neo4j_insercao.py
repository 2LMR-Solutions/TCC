import pandas as pd

def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def faixa_idade(idade):
    if idade < 20:
        return 'Menos de 20'
    elif idade <= 30:
        return '21-30'
    elif idade <= 40:
        return '31-40'
    elif idade <= 50:
        return '41-50'
    else:
        return '51+'

def definir_perfil(row):
    idade = safe_int(row['IDADE'])
    faixa = faixa_idade(idade)
    inadimplencia = safe_float(row['VALOR DA INADIMPLENCIA'])
    parcelas = safe_int(row['PARCELAS EM ABERTO'])
    risco = row['RISCO DE EVASAO']
    diasSemAcesso = safe_int(row['QUANTIDADE DE DIAS SEM ACESSO A PARTIR DO INICIO DA OFERTA DO MODULO DE INGRESSO'])
    diasUltimoAcesso = safe_int(row['QUANTIDADE DE DIAS DESDE DO ULTIMO ACESSO AS DISCIPLINAS OU A PARTIR DA DATA DE MATRICULA'])
    disciplinasPendentes = safe_int(row['QUANT DE DISCIPLINAS PENDENTES'])
    periodo = safe_int(row['PERIODO'])

    # Regras dos perfis:
    if inadimplencia > 1000 and parcelas >= 3 and risco == 'ALTO' and diasSemAcesso > 15:
        return 'Inadimplente Crítico'
    elif disciplinasPendentes > 5 and diasSemAcesso > 30 and risco in ['ALTO', 'MEDIO'] and inadimplencia <= 100:
        return 'Desengajado Acadêmico'
    elif periodo <= 2 and diasUltimoAcesso > 10 and risco == 'ALTO' and inadimplencia < 50:
        return 'Calouro em Risco'
    elif faixa in ['41-50', '51+'] and inadimplencia > 500 and risco in ['ALTO', 'MEDIO'] and diasSemAcesso > 10:
        return 'Adulto Inadimplente'
    elif faixa in ['Menos de 20', '21-30'] and disciplinasPendentes > 8 and risco in ['ALTO', 'MEDIO']:
        return 'Jovem com Baixo Rendimento'
    else:
        return 'Sem Perfil Específico'
    
def inserir_aluno(tx, row):
    idade = safe_int(row['IDADE'])
    faixa_id = faixa_idade(idade)
    perfil = definir_perfil(row)

    tx.run("""
        MERGE (a:Aluno {nome: $nome})
        SET a.idade = $idade,
            a.sexo = $sexo,
            a.perfilEvasao = $perfil

        MERGE (c:Curso {nome: $curso})
        MERGE (fi:Filial {nome: $filial})
        MERGE (p:Periodo {numero: $periodo})
        MERGE (ac:Acesso {
            diasSemAcesso: $diasSemAcesso,
            diasUltimoAcesso: $diasUltimoAcesso
        })
        MERGE (mat:Matricula {aluno: $nome, curso: $curso, periodo: $periodo})
        MERGE (r:Regional {nome: $regional})
        MERGE (tp:TipoPolo {tipo: $tipo_polo})
        MERGE (sf:SituacaoFinanceira {status: $situacaoFinanceira})
        MERGE (fa:FaixaIdade {faixa: $faixaIdade})
        MERGE (re:RiscoEvasao {nivel: $risco})

        MERGE (h:Historico {
            disciplinasGrade: $disciplinasGrade,
            disciplinasRealizadas: $disciplinasRealizadas,
            disciplinasPendentes: $disciplinasPendentes,
            disciplinasMatriculadas: $disciplinasMatriculadas
        })

        MERGE (f:Financeiro {
            valorInadimplencia: $inadimplencia,
            parcelasAbertas: $parcelas
        })

        MERGE (l:Ligacoes {quantidade: $ligacoes})

        // Relacionamentos principais
        MERGE (a)-[:ESTUDA_EM]->(c)
        MERGE (a)-[:PERTENCE_A]->(fi)
        MERGE (a)-[:ESTÁ_NO]->(p)
        MERGE (a)-[:TEM_ACESSO]->(ac)
        MERGE (a)-[:TEM_MATRICULA]->(mat)
        MERGE (c)-[:OFERTADO_EM]->(fi)
        MERGE (fi)-[:PERTENCE_A_REGIONAL]->(r)
        MERGE (a)-[:TIPO_POLO]->(tp)
        MERGE (a)-[:TEM_SITUACAO_FINANCEIRA]->(sf)
        MERGE (a)-[:FAIXA_ETARIA]->(fa)
        MERGE (a)-[:TEM_RISCO_EVASAO]->(re)
        MERGE (a)-[:TEM_HISTORICO]->(h)
        MERGE (a)-[:TEM_FINANCEIRO]->(f)
        MERGE (a)-[:RECEBEU_LIGACOES]->(l)
    """, {
        "nome": row['ALUNO'],
        "idade": idade,
        "sexo": row['SEXO'],
        "curso": row['CURSO'],
        "filial": row['FILIAL'],
        "periodo": safe_int(row['PERIODO']),
        "regional": row['REGIONAL'],
        "tipo_polo": row['TIPO DE POLO QUE OFERTA SAUDE/ENGENHARIA'],
        "situacaoFinanceira": row['SITUACAO FINANCEIRA'],
        "faixaIdade": faixa_id,
        "risco": row['RISCO DE EVASAO'],
        "disciplinasGrade": safe_int(row['QUANT DE DISCIPLINAS DA GRADE']),
        "disciplinasRealizadas": safe_int(row['QUANT DE DISCIPLINAS REALIZADAS']),
        "disciplinasPendentes": safe_int(row['QUANT DE DISCIPLINAS PENDENTES']),
        "disciplinasMatriculadas": safe_int(row['QUANT DE DISCIPLINAS MATRICULADAS']),
        "diasSemAcesso": safe_int(row['QUANTIDADE DE DIAS SEM ACESSO A PARTIR DO INICIO DA OFERTA DO MODULO DE INGRESSO']),
        "diasUltimoAcesso": safe_int(row['QUANTIDADE DE DIAS DESDE DO ULTIMO ACESSO AS DISCIPLINAS OU A PARTIR DA DATA DE MATRICULA']),
        "inadimplencia": safe_float(row['VALOR DA INADIMPLENCIA']),
        "parcelas": safe_int(row['PARCELAS EM ABERTO']),
        "ligacoes": safe_int(row['QUANTITATIVO DE LIGACOES EFETIVAS']),
        "perfil": perfil
    })
