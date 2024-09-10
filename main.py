import os
from elasticsearch import Elasticsearch

# Configuração do Elasticsearch
es = Elasticsearch([{"scheme": "http", "host": "localhost", "port": 9200}])
index_name = "boletins"

# Buscar no Elasticsearch e salvar resultados em arquivos de texto
def search_in_elasticsearch(es, index_name, query, description):
    try:
        print(f"Buscando: {description}")
        res = es.search(index=index_name, body={"query": query})

        result_text = f"Resultados para '{description}':\n"

        if 'hits' in res and res["hits"]["total"]["value"] > 0:
            doc_ids = set()
            for hit in res["hits"]["hits"]:
                doc_ids.add(hit['_id'])
                page_number = hit["_source"].get("page_number", "Desconhecido")
                result_text += f"Documento encontrado: {hit['_id']} | Página: {page_number} | Conteúdo: {hit['_source']['content'][:200]}...\n"
            result_text += f"\nTermo '{description}' encontrado em {len(doc_ids)} arquivos distintos.\n"
        elif 'aggregations' in res:
            result_text += f"Resultados de agregação encontrados para '{description}':\n"
            agg_results = res["aggregations"]["common_words"]["buckets"]
            for bucket in agg_results:
                result_text += f"Palavra: {bucket['key']}, Contagem: {bucket['doc_count']}\n"
        else:
            result_text += f"Nenhum resultado encontrado para '{description}'.\n"

        # Salvar resultado em arquivo de texto
        save_search_result(description, result_text)
    except Exception as e:
        print(f"Erro ao buscar '{description}': {str(e)}")

# Salvar o resultado da busca em um arquivo de texto
def save_search_result(query, result_text):
    directory = './resultados'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_name = f"{directory}/resultado_{query.replace(' ', '_')}.txt"
    with open(file_name, 'w', encoding='utf-8') as file:
        print(f"Salvando resultado da busca por '{query}' no arquivo {file_name}...")
        file.write(result_text)
    print(f"Resultado salvo com sucesso em {file_name}.")

# Lista de queries mais complexas
queries = [
    {
        "description": "Busca por termo 'Computação'",
        "query": {
            "match": {
                "content": "Computação"
            }
        }
    },
    {
        "description": "Busca por data específica (2023)",
        "query": {
            "range": {
                "publication_date": {
                    "gte": "2023-01-01",
                    "lte": "2023-12-31"
                }
            }
        }
    },
    {
        "description": "Busca por múltiplos termos 'Computação' e 'universidade'",
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": "Computação"}},
                    {"match": {"content": "universidade"}}
                ]
            }
        }
    },
    {
        "description": "Portaria de homologação ou aprovação do estágio probatório do professor José Ricardo Cereja",
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": "José Ricardo Cereja"}},
                    {"match": {"content": "estágio probatório"}}
                ],
                "should": [
                    {"match": {"content": "homologação"}},
                    {"match": {"content": "aprovação"}}
                ]
            }
        }
    },
    {
        "description": "Busca usando regex para variações de 'Computação'",
        "query": {
            "regexp": {
                "content": "Comp.*"
            }
        }
    },
    {
        "description": "Agregação para contagem de palavras mais comuns",
        "query": {
            "aggs": {
                "common_words": {
                    "terms": {
                        "field": "content.keyword",
                        "size": 10  # Número de palavras mais comuns a retornar
                    }
                }
            }
        }
    },
    {
        "description": "Busca por similaridade (Fuzzy Search) para 'Computação'",
        "query": {
            "fuzzy": {
                "content": {
                    "value": "Computação",
                    "fuzziness": "AUTO"
                }
            }
        }
    }
]

# Testa todas as buscas e salva os resultados em arquivos
for query_info in queries:
    search_in_elasticsearch(es, index_name, query_info["query"], query_info["description"])

print("Todas as consultas foram realizadas e os resultados foram salvos.")
