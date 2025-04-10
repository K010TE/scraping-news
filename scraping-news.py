import pandas as pd
import re
import time
from datetime import datetime
import random
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import os

# Lista para armazenar resultados
resultados = []

def buscar_noticias(termo, ano_inicio=2019, ano_fim=2025, max_results=50):
    """
    Busca notícias do G1 relacionadas ao termo especificado
    """
    print(f"\nBuscando notícias sobre '{termo}' no G1 ({ano_inicio}-{ano_fim})")
    
    # Armazenamento de resultados por ano
    resultados_por_ano = {ano: 0 for ano in range(ano_inicio, ano_fim + 1)}
    count_total = 0
    
    # Fazer busca ano a ano para melhorar os resultados
    for ano in range(ano_inicio, ano_fim + 1):
        # Verificar se o ano é futuro ou presente
        ano_atual = datetime.now().year
        if ano > ano_atual:
            print(f"O ano {ano} é futuro. Pulando...")
            continue
            
        # Montar query para o Google com o ano específico
        query = f"site:g1.globo.com {termo} {ano}"
        print(f"\nBuscando para {termo} em {ano}...")
        
        try:
            # Usar a biblioteca googlesearch para fazer a pesquisa
            for url in search(query, num_results=max_results, lang="pt-br"):
                try:
                    # Verificar se é realmente uma URL do G1
                    if "g1.globo.com" not in url:
                        continue
                    
                    # Extrair data da URL (formato comum do G1: /ano/mes/dia/)
                    match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                    
                    if match:
                        url_ano, mes, dia = match.groups()
                        url_ano_int = int(url_ano)
                        
                        # Verificar se a data da URL corresponde ao ano buscado
                        if url_ano_int == ano:
                            # Extrair título da notícia da URL
                            titulo_match = re.search(r'([^/]+)\.ghtml$', url)
                            titulo = "Título não extraído"
                            
                            if titulo_match:
                                # Converter formato-url para texto legível
                                titulo_bruto = titulo_match.group(1)
                                titulo = titulo_bruto.replace('-', ' ').title()
                            
                            # Extrair o conteúdo completo da matéria
                            conteudo = extrair_conteudo_materia(url)
                            
                            # Adicionar resultado à lista
                            resultados.append({
                                'Termo': termo,
                                'Título': titulo,
                                'Link': url,
                                'Data': f"{dia}/{mes}/{url_ano}",
                                'Ano': url_ano_int,
                                'Mês': mes,
                                'Conteúdo': conteudo
                            })
                            
                            count_total += 1
                            resultados_por_ano[ano] += 1
                            print(f"  {count_total}. [{ano}] {titulo} ({dia}/{mes}/{url_ano}) - {len(conteudo)} caracteres")
                            
                            # Salvar o conteúdo em arquivo de texto separado
                            salvar_conteudo_arquivo(titulo, url, conteudo, f"{url_ano}_{mes}_{dia}")
                            
                            # Pausa aleatória para evitar bloqueio
                            time.sleep(random.uniform(1.0, 3.0))
                
                except Exception as e:
                    print(f"Erro ao processar URL: {str(e)}")
            
            # Pausa maior entre anos diferentes
            if ano < ano_fim:
                pausa = random.uniform(5.0, 10.0)
                print(f"Pausando {pausa:.2f} segundos antes de buscar o próximo ano...")
                time.sleep(pausa)
        
        except Exception as e:
            print(f"Erro durante a busca para o ano {ano}: {str(e)}")
    
    # Exibir sumário dos resultados por ano
    print("\nResumo de notícias encontradas por ano:")
    for ano, quantidade in resultados_por_ano.items():
        print(f"  {ano}: {quantidade} notícias")
    
    print(f"\nTotal de {count_total} resultados encontrados para '{termo}' entre {ano_inicio}-{ano_fim}")
    return count_total

def extrair_conteudo_materia(url):
    """
    Extrai o conteúdo completo de uma matéria do G1
    """
    try:
        # Definir User-Agent para parecer um navegador real
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Fazer requisição HTTP para a página
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Verificar se a requisição foi bem-sucedida
        
        # Criar objeto BeautifulSoup para analisar o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tentar diferentes padrões do G1 para encontrar o conteúdo da matéria
        # O G1 pode ter diferentes classes para o conteúdo dependendo do período
        conteudo = ""
        
        # Tentar localizar o título real da matéria
        titulo_real = soup.find('h1', class_='content-head__title')
        if titulo_real:
            conteudo += f"TÍTULO: {titulo_real.text.strip()}\n\n"
        
        # Tentar localizar o subtítulo
        subtitulo = soup.find('h2', class_='content-head__subtitle')
        if subtitulo:
            conteudo += f"SUBTÍTULO: {subtitulo.text.strip()}\n\n"
        
        # Tentar localizar a data de publicação
        data_publicacao = soup.find('time', class_='content-publication-data__updated')
        if data_publicacao:
            conteudo += f"DATA: {data_publicacao.text.strip()}\n\n"
        
        # Tentar localizar o autor
        autor = soup.find('p', class_='content-publication-data__from')
        if autor:
            conteudo += f"AUTOR: {autor.text.strip()}\n\n"
            
        conteudo += "CONTEÚDO DA MATÉRIA:\n"
        
        # Encontrar o corpo da matéria - várias possibilidades de classes
        corpo_opcoes = [
            soup.find('div', class_='mc-article-body'),
            soup.find('div', class_='content-text'),
            soup.find('div', class_='entry-content'),
            soup.find('article'),
            soup.find('div', class_='corpo')
        ]
        
        corpo = next((c for c in corpo_opcoes if c is not None), None)
        
        if corpo:
            # Extrair parágrafos do corpo da matéria
            paragrafos = corpo.find_all('p')
            
            if paragrafos:
                # Unir todos os parágrafos em um texto
                for paragrafo in paragrafos:
                    texto = paragrafo.text.strip()
                    if texto:  # Ignorar parágrafos vazios
                        conteudo += f"{texto}\n\n"
            else:
                # Se não encontrou parágrafos, pegar o texto completo
                conteudo += corpo.get_text(separator='\n\n', strip=True)
        else:
            conteudo += "[Não foi possível extrair o conteúdo da matéria]"
        
        return conteudo
        
    except Exception as e:
        return f"[Erro ao extrair conteúdo: {str(e)}]"

def salvar_conteudo_arquivo(titulo, url, conteudo, data):
    """
    Salva o conteúdo da matéria em um arquivo de texto
    """
    try:
        # Criar diretório para armazenar os conteúdos, se não existir
        diretorio = "conteudos_materias"
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
        
        # Criar nome de arquivo baseado no título
        # Remover caracteres inválidos para nomes de arquivo
        nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", titulo)
        nome_arquivo = nome_arquivo.replace(' ', '_')[:100]  # Limitar tamanho
        
        # Adicionar data ao nome do arquivo
        caminho_arquivo = os.path.join(diretorio, f"{data}_{nome_arquivo}.txt")
        
        # Salvar conteúdo no arquivo
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n\n")
            f.write(conteudo)
            
    except Exception as e:
        print(f"Erro ao salvar conteúdo em arquivo: {str(e)}")

def salvar_resultados(termo=None):
    """Salva os resultados em arquivo Excel e CSV"""
    if not resultados:
        print("Nenhum resultado para salvar.")
        return
    
    try:
        # Criar DataFrame
        df = pd.DataFrame(resultados)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if termo:
            base_nome = f"noticias_g1_{termo.replace(' ', '_')}_{timestamp}"
        else:
            base_nome = f"noticias_g1_todas_{timestamp}"
        
        # Salvar como Excel
        nome_excel = f"{base_nome}.xlsx"
        df.to_excel(nome_excel, index=False)
        print(f"Resultados salvos em Excel: {nome_excel}")
        
        # Salvar como CSV - melhor para visualizar conteúdos longos
        nome_csv = f"{base_nome}.csv"
        df.to_csv(nome_csv, index=False, encoding='utf-8')
        print(f"Resultados salvos em CSV: {nome_csv}")
        
        # Salvar versão com conteúdo resumido para fácil visualização
        df_resumido = df.copy()
        if 'Conteúdo' in df_resumido.columns:
            # Resumir o conteúdo para os primeiros 200 caracteres
            df_resumido['Conteúdo_Resumido'] = df_resumido['Conteúdo'].apply(
                lambda x: (x[:200] + '...') if len(x) > 200 else x
            )
            # Remover a coluna de conteúdo completo
            df_resumido = df_resumido.drop(columns=['Conteúdo'])
            
            # Salvar versão resumida em Excel para fácil visualização
            nome_resumido = f"{base_nome}_resumido.xlsx"
            df_resumido.to_excel(nome_resumido, index=False)
            print(f"Versão resumida salva em: {nome_resumido}")
    
    except Exception as e:
        print(f"Erro ao salvar resultados: {str(e)}")

def main():
    try:
        # Termos a pesquisar
        termos = ["Inteligência Artificial", "IA", "Chat GPT"]
        
        print("Iniciando busca de notícias do G1 sobre IA de 2019 a 2025...")
        
        # Buscar para cada termo
        for termo in termos:
            resultados_termo = buscar_noticias(termo, ano_inicio=2019, ano_fim=2025)
            
            # Salvar resultados parciais se encontrou algo
            if resultados_termo > 0:
                salvar_resultados(termo)
            
            # Pausa entre buscas
            print("Aguardando para próxima busca...")
            time.sleep(5)
        
        # Consolidar todos os resultados finais
        if resultados:
            # Remover duplicatas
            df = pd.DataFrame(resultados)
            df = df.drop_duplicates(subset=["Link"])
            
            # Salvar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_nome = f"noticias_g1_2019-2025_consolidado_{timestamp}"
            
            # Excel completo
            nome_excel = f"{base_nome}.xlsx"
            df.to_excel(nome_excel, index=False)
            print(f"\nTodos os resultados consolidados salvos em Excel: {nome_excel}")
            
            # CSV completo
            nome_csv = f"{base_nome}.csv"
            df.to_csv(nome_csv, index=False, encoding='utf-8')
            print(f"Todos os resultados consolidados salvos em CSV: {nome_csv}")
            
            # Versão resumida
            if 'Conteúdo' in df.columns:
                df_resumido = df.copy()
                # Resumir o conteúdo para os primeiros 200 caracteres
                df_resumido['Conteúdo_Resumido'] = df_resumido['Conteúdo'].apply(
                    lambda x: (x[:200] + '...') if len(x) > 200 else x
                )
                # Remover a coluna de conteúdo completo
                df_resumido = df_resumido.drop(columns=['Conteúdo'])
                
                # Salvar versão resumida
                nome_resumido = f"{base_nome}_resumido.xlsx"
                df_resumido.to_excel(nome_resumido, index=False)
                print(f"Versão resumida salva em: {nome_resumido}")
            
            # Análise por ano
            if 'Ano' in df.columns:
                contagem_por_ano = df['Ano'].value_counts().sort_index()
                print("\nDistribuição de notícias por ano:")
                for ano, quantidade in contagem_por_ano.items():
                    print(f"  {ano}: {quantidade} notícias")
            
            print(f"Total de notícias únicas encontradas: {len(df)}")
    
    except KeyboardInterrupt:
        print("\nOperação interrompida pelo usuário")
        salvar_resultados()
    
    except Exception as e:
        print(f"Erro na execução do script: {str(e)}")
        # Tentar salvar resultados parciais
        salvar_resultados()

# Executar o script
if __name__ == "__main__":
    main()
    print("Script finalizado")
