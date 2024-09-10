import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Função para ajustar o nome do arquivo PDF
def format_pdf_name(link_text, year):
    try:
        # Limpa o texto do link
        link_text_clean = link_text.upper()
        link_text_clean = link_text_clean.replace(" ", "_")  # Substitui espaços por sublinhados
        link_text_clean = link_text_clean.replace("-", "_")  # Substitui hífens por sublinhados

        # Remove caracteres especiais
        link_text_clean = ''.join(char if char.isalnum() or char == '_' else '' for char in link_text_clean)

        # Formata o nome do arquivo no padrão: ano_nome_do_arquivo.pdf
        formatted_name = f"{year}_{link_text_clean}.pdf"

        return formatted_name
    except Exception as e:
        print(f"Erro ao formatar o nome do arquivo {link_text}: {str(e)}")
        return f"{year}_NOME_INVALIDO.pdf"

# Função para baixar um arquivo PDF
def download_pdf(pdf_url, link_text, folder, year):
    try:
        # Formatando o nome do arquivo com base no ano e no texto do link
        pdf_name_with_year = format_pdf_name(link_text, year)
        pdf_path = os.path.join(folder, pdf_name_with_year)

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Verifica se o arquivo já existe para evitar substituições
        if not os.path.isfile(pdf_path):
            print(f"Baixando {pdf_name_with_year} no diretório {pdf_path}...")
            response = requests.get(pdf_url)
            response.raise_for_status()  # Verifica se houve erro na requisição

            with open(pdf_path, 'wb') as file:
                file.write(response.content)

            print(f"PDF {pdf_name_with_year} baixado com sucesso!")
        else:
            print(f"Arquivo {pdf_name_with_year} já existe, pulando download.")
    except Exception as e:
        print(f"Erro ao baixar {pdf_url}: {str(e)}")

# Função para buscar os links de PDF dentro de uma página específica do boletim
def get_pdfs_from_boletim_page(url, folder, year):
    try:
        print(f"Processando a página do boletim: {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar todos os links de PDFs
        pdf_links = soup.find_all('a', href=lambda href: href and '/at_download/file' in href)
        
        for pdf_link in pdf_links:
            pdf_url = urljoin(url, pdf_link['href'])
            link_text = pdf_link.get_text(strip=True)  # Extrai o texto exibido no link
            print(f"Encontrado PDF: {pdf_url}")
            download_pdf(pdf_url, link_text, folder, year)
    except Exception as e:
        print(f"Erro ao processar a página do boletim {url}: {str(e)}")

# Função para buscar links de boletins dentro da página de um ano
def get_boletins_from_year_page(url, folder, year):
    try:
        print(f"Processando a página do ano: {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar todos os links para páginas de boletins
        boletim_links = soup.find_all('a', href=True)
        for link in boletim_links:
            boletim_url = urljoin(url, link['href'])
            if 'view' in boletim_url and year in boletim_url:  # Filtro para garantir que seja um boletim válido e do ano correto
                print(f"Encontrado boletim: {boletim_url}")
                get_pdfs_from_boletim_page(boletim_url, folder, year)
    except Exception as e:
        print(f"Erro ao processar a página do ano {url}: {str(e)}")

# Função para buscar links dos anos de boletins na página principal e processar cada um
def download_all_pdfs_from_unirio(base_url, folder):
    try:
        print(f"Processando a página principal: {base_url}")
        response = requests.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar links de anos de boletins
        year_links = soup.find_all('a', href=True)

        for link in year_links:
            year_url = urljoin(base_url, link['href'])
            if 'boletins-' in year_url:  # Filtro para garantir que seja um link de ano
                year_text = link['href'].split('/')[-1]
                print(f"\nProcessando página: {year_url} para o ano: {year_text}")
                get_boletins_from_year_page(year_url, folder, year_text)
    except Exception as e:
        print(f"Erro ao processar a página principal {base_url}: {str(e)}")

# Função para buscar PDFs das páginas principal e dos boletins antigos
def download_all_pdfs(base_urls, folder):
    for base_url in base_urls:
        print(f"\nIniciando download para: {base_url}")
        download_all_pdfs_from_unirio(base_url, folder)
        print(f"Download completo para: {base_url}")

# URLs base e diretório
base_urls = [
    'https://www.unirio.br/boletins',  # Página principal dos boletins
    'https://www.unirio.br/boletins/chefia-de-gabinete'  # Página dos boletins antigos
]
download_folder = './boletins'  # Diretório único para todos os PDFs

# Baixa todos os PDFs
download_all_pdfs(base_urls, download_folder)

print("Download completo.")
