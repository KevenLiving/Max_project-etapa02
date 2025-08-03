import requests
from bs4 import BeautifulSoup
from database import Produto, SessionLocal, Busca

# Função auxiliar para extrair preço do HTML
def extrair_preco(produto_html):
    container_principal = produto_html.select_one('div.poly-price__current')
    preco_inteiro = container_principal.find('span', class_='andes-money-amount__fraction')
    preco_centavos = container_principal.find('span', class_='andes-money-amount__cents')

    if preco_inteiro:
        valor = preco_inteiro.text
        if preco_centavos:
            valor += f",{preco_centavos.text}"
        try:
            return float(valor.replace('.', '').replace(',', '.'))
        except ValueError:
            return None
    return None

# Função principal do scraper
def buscar_produtos(termo: str, limite: int = 15):
    headers = {
        'User-Agent': 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    termo_busca = termo
    termo = termo.replace(' ', '-')
    url = f'https://lista.mercadolivre.com.br/{termo}_Desde_'
    start = 1
    session = SessionLocal()
    quantidade_salva = 0

    # Aquie ele vaii ver o se já tem buscas com esse nome, se não houver, ele cria uma nova 
    busca = session.query(Busca).filter(Busca.termo == termo_busca).first()
    if not busca:
        busca = Busca(termo=termo_busca)
        session.add(busca)
        session.commit()
        session.refresh(busca)

    while True:
        url_final = url + str(start) + '_NoIndex_True'
        print(f'🔎 Buscando: {url_final}')
        r = requests.get(url_final, headers=headers)

        if r.status_code != 200:
            print(f'❌ Erro na requisição: {r.status_code}')
            break

        soup = BeautifulSoup(r.content, 'html.parser')
        produtos_html = soup.select('li.ui-search-layout__item, li.ui-search-layout__item__group')
        print(f'🧩 Produtos encontrados na página: {len(produtos_html)}')

        if not produtos_html:
            print('✅ Fim da lista ou bloqueio detectado.')
            break

        for produto_html in produtos_html:
            if quantidade_salva >= limite:
                print(f'✅ Limite de {limite} produtos atingido.')
                session.commit()
                session.close()
                return

            nome_tag = produto_html.find('h2') or produto_html.find('h3')
            link_tag = produto_html.find('a', href=True)
            preco = extrair_preco(produto_html)

            # Adicionando os novos valores 
            avaliacao_tag = produto_html.find('span', class_='poly-reviews__rating')
            num_avaliacao_tag = produto_html.find('span', class_="poly-reviews__total")

            # Tratando os resultados com segurança
            try:
                avaliacao = float(avaliacao_tag.get_text(strip=True)) if avaliacao_tag else 0.0
            except ValueError:
                avaliacao = 0.0

            try:
                num_avaliacao_texto = num_avaliacao_tag.get_text(strip=True) if num_avaliacao_tag else "0"
                num_avaliacao = int(num_avaliacao_texto.replace("(", "").replace(")", ""))
            except ValueError:
                num_avaliacao = 0

            if nome_tag and link_tag and preco:
                nome = nome_tag.get_text(strip=True)
                link = link_tag["href"]

            if nome_tag and link_tag and preco:
                nome = nome_tag.get_text(strip=True)
                link = link_tag["href"]

                # Apenas os itens que são buscados entram na lista (evitar variações do mercado livre)
                if termo_busca.lower() not in nome.lower():
                    continue  # Pula o produto e não salva

                print(f'💾 Salvando: {nome} - R$ {preco} - Avaliação: {avaliacao} ({num_avaliacao} avaliações)')
                produto = Produto(
                    nome=nome,
                    preco=preco,
                    link=link,
                    avaliacao=avaliacao,
                    num_avaliacao=num_avaliacao,
                    busca_id = busca.id
                    
                )
                session.add(produto)
                quantidade_salva += 1
        start += 50  # próxima página

    if quantidade_salva == 0:
        session.close()
        print("Produtos não encontrados.")
        return {"mensagem": "Produtos não encontrados."}

    session.commit()
    session.close()
    print(f'✅ Scraping finalizado. {quantidade_salva} produtos salvos.')

# Teste manual
if __name__ == "__main__":
    termo = input("Digite o produto para buscar no Mercado Livre: ")
    buscar_produtos(termo, limite=15)


