import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Função para baixar um arquivo PDF
def download_pdf(pdf_url, folder, year):
    try:
        # Extraindo o nome do arquivo PDF a partir da URL e adicionando o ano ao nome
        pdf_name = pdf_url.split("/")[-1]
        pdf_name_with_year = f"{year}_{pdf_name}"
        pdf_path = os.path.join(folder, pdf_name_with_year)

        print(f"Baixando {pdf_name_with_year} no diretório {pdf_path}...")
        response = requests.get(pdf_url)
        response.raise_for_status()  # Verifica se houve erro na requisição

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(pdf_path, 'wb') as file:
            file.write(response.content)

        print(f"PDF {pdf_name_with_year} baixado com sucesso!")
    except Exception as e:
        print(f"Erro ao baixar {pdf_url}: {str(e)}")

# Função para buscar os links de PDF em uma página
def get_pdfs_from_page(url, folder, year):
    try:
        print(f"Processando a página de PDFs: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve erro na requisição

        soup = BeautifulSoup(response.text, 'html.parser')

        pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))

        for link in pdf_links:
            pdf_url = urljoin(url, link['href'])
            download_pdf(pdf_url, folder, year)
    except Exception as e:
        print(f"Erro ao processar a página {url}: {str(e)}")

# Função para buscar links de anos e baixar todos os PDFs
def download_all_pdfs_from_unirio(base_url, folder):
    try:
        print(f"Processando a página principal: {base_url}")
        response = requests.get(base_url)
        response.raise_for_status()  # Verifica se houve erro na requisição

        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todos os links, independentemente da estrutura específica
        links = soup.find_all('a', href=True)

        # Filtra apenas os links relevantes para ano/página
        for link in links:
            href = link['href']
            year_url = urljoin(base_url, href)

            if '/boletins/' in href:
                year_text = href.split('/')[-1]
                print(f"\nProcessando página: {year_url} para o ano: {year_text}")
                get_pdfs_from_page(year_url, folder, year_text)
    except Exception as e:
        print(f"Erro ao processar a página principal {base_url}: {str(e)}")

# URL base da UNIRIO
base_url = 'https://www.unirio.br/boletins'
# Diretório onde os PDFs serão salvos
download_folder = './boletins'

# Baixa todos os PDFs
download_all_pdfs_from_unirio(base_url, download_folder)

print("Download completo.")
