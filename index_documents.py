import os
from PyPDF2 import PdfReader
from elasticsearch import Elasticsearch

# Extrair o texto do pdf
def extract_text_from_pdf(pdf_path):
    try:
        print(f"Extraindo texto de {pdf_path}...")
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        texts = []
        for page_num in range(num_pages):
            try:
                page_text = reader.pages[page_num].extract_text()
                if page_text:
                    texts.append({"page_number": page_num + 1, "content": page_text})
                else:
                    print(f"Aviso: Nenhum texto extraído da página {page_num + 1} de {pdf_path}.")
            except Exception as e:
                print(f"Erro ao extrair texto da página {page_num + 1} de {pdf_path}: {str(e)}")
        if not texts:
            print(f"Aviso: Nenhum texto extraído de {pdf_path}.")
        return texts
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {str(e)}")
        return None

# Indexar o texto no Elasticsearch
def index_text(es, index_name, texts, doc_id):
    try:
        for page in texts:
            page_number = page["page_number"]
            content = page["content"]
            try:
                print(f"Indexando documento {doc_id} - Página {page_number}...")
                res = es.index(index=index_name, id=f"{doc_id}_page_{page_number}", body={
                    "content": content,
                    "doc_id": doc_id,
                    "page_number": page_number
                })
                print(f"Documento {doc_id} - Página {page_number} indexado com sucesso.")
            except Exception as e:
                print(f"Erro ao indexar documento {doc_id} - Página {page_number}: {str(e)}")
    except Exception as e:
        print(f"Erro geral ao indexar documentos {doc_id}: {str(e)}")

# Configuração do Elasticsearch
es = Elasticsearch([{"scheme": "http", "host": "localhost", "port": 9200}])
index_name = "boletins"

if not es.indices.exists(index=index_name):
    print(f"Criando índice '{index_name}'...")
    es.indices.create(
        index=index_name,
        body={
            "mappings": {
                "properties": {
                    "content": {"type": "text"},
                    "doc_id": {"type": "keyword"},
                    "page_number": {"type": "integer"}
                }
            }
        }
    )
    print(f"Índice '{index_name}' criado com sucesso.")

pdf_directory = './boletins'

# Processa e indexa cada PDF
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        texts = extract_text_from_pdf(pdf_path)
        if texts:
            doc_id = filename.split(".")[0]  # Usa o nome do arquivo como ID do documento
            index_text(es, index_name, texts, doc_id)
        else:
            print(f"Falha ao extrair texto de {pdf_path}")

print("Indexação completa.")
