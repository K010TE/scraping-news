
# Coleta de Notícias sobre Inteligência Artificial (2019–2025)

Este script realiza a busca, extração e organização de notícias do portal **G1** relacionadas aos termos **"Inteligência Artificial"**, **"IA"** e **"Chat GPT"**, no período de **2019 até 2025** (limitado ao ano atual).

## ✨ Funcionalidades

- **Busca por notícias no Google** com base nos termos-chave mencionados
- **Pesquisa anual**, de 2019 até o ano atual (anos futuros são ignorados)
- **Filtragem de URLs** para garantir que sejam do domínio `g1.globo.com` e correspondam ao ano buscado
- **Extração automatizada** de:
  - Título
  - Data da publicação
  - Conteúdo completo da matéria
- **Armazenamento dos dados** nos seguintes formatos:
  - Arquivos **Excel (.xlsx)** e **CSV (.csv)** com os dados completos
  - Arquivo Excel com **resumo de conteúdo** (limite de 200 caracteres por matéria)
  - Arquivos **.txt individuais** com o conteúdo completo de cada matéria, salvos na pasta `conteudos_materias`
- **Geração de estatísticas** com a contagem de notícias por ano e totais gerais
- **Controle de tráfego**: pausas automáticas entre requisições para evitar bloqueios

## 📦 Bibliotecas Utilizadas

- [`googlesearch`](https://pypi.org/project/googlesearch-python/): realiza buscas no Google e retorna URLs
- [`requests`](https://pypi.org/project/requests/): faz as requisições HTTP para obter o HTML das notícias
- [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/): analisa e extrai os dados do HTML usando seletores CSS

## 🔁 Como Funciona

1. Usa a **googlesearch** para encontrar links do G1 com os termos desejados.
2. Para cada link:
   - Realiza uma requisição HTTP com `requests`
   - Extrai título, data e corpo da notícia usando `BeautifulSoup`
   - Armazena os dados em memória
3. Salva os resultados em múltiplos formatos para facilitar a análise

## 🛑 Por que não usar Selenium?

Este projeto **não usa automação de navegador (como Selenium)** por questões de eficiência:

- Mais leve e rápido
- Menor consumo de recursos
- O conteúdo do G1 já está presente no HTML inicial, o que torna o uso de Selenium desnecessário

**Limitação:** essa abordagem não interage com elementos dinâmicos ou executa JavaScript, mas é totalmente adequada para o G1 neste caso.

## 📈 Possibilidades de Análise

O script permite analisar a cobertura da mídia sobre IA ao longo dos anos, com flexibilidade para gerar gráficos, dashboards ou relatórios com base nos dados salvos.

Futuramente serão adicionados outros portais de notícias e personalização mais adequada dos termos e intervalo de tempo.

---

> Projeto desenvolvido com fins de pesquisa e análise de conteúdo jornalístico. Certifique-se de respeitar os termos de uso dos sites acessados.
