from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'MaxMillerOMagnanimo'

# Aqui eu coloco a url que minha api está usando
API_BASE_URL = 'http://127.0.0.1:8000'


# OBS: O template foi realizado fazendo-se o uso de Bootstrap, e os dados foram repassados ao template através do flask
# Instrução: Para evitar uma ruma de coisa em produtos quando terminar a busca, apague antes os produtos que foram buscados em pesquisas passadas na parte de histórico, ou em gerenciamento (pode apagar tudo de uma vez). 

# Funçãos prévias para formatar o preço dos valores para real e de fazer as requesições para a API
def formatar_preco(preco):
    return f"R$ {preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fazer_requisicao_api(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        termo = request.form.get('termo')
        limite = int(request.form.get('limite', 15))
        if not termo:
            flash('Por favor, digite um termo para busca.', 'error')
            return render_template('buscar.html')
        try:
            # Fazer a busca via POST na API
            response = requests.post(f"{API_BASE_URL}/buscar-produtos/", 
                                   params={'termo': termo, 'limite': limite}, 
                                   timeout=30)
            
            if response.status_code == 200:
                flash(f'Busca por "{termo}" realizada com sucesso! {limite} produtos foram salvos.', 'success')
                return redirect(url_for('produtos'))
            else:
                flash('Erro ao realizar a busca. Tente novamente.', 'error')
        
        except requests.exceptions.RequestException as e:
            flash(f'Erro de conexão com a API: {str(e)}', 'error')
    
    return render_template('buscar.html')



@app.route('/produtos')
def produtos():
    produtos_data = fazer_requisicao_api('/produtos/')
    
    if produtos_data is None:
        flash('Erro ao carregar produtos.', 'error')
        produtos_data = []
    return render_template('produtos.html', produtos=produtos_data, formatar_preco=formatar_preco)

@app.route('/melhores-precos')
def melhores_precos():
    limite = request.args.get('limite', 10, type=int)
    produtos_data = fazer_requisicao_api('/melhor-preco/', params={'limite': limite})
    
    if produtos_data is None:
        flash('Erro ao carregar produtos com melhores preços.', 'error')
        produtos_data = []
    return render_template('melhores_precos.html', produtos=produtos_data, 
                         formatar_preco=formatar_preco, limite=limite)



@app.route('/melhores-avaliados')
def melhores_avaliados():
    limite = request.args.get('limite', 10, type=int)
    produtos_data = fazer_requisicao_api('/melhor-avaliados/', params={'limite': limite})
    if produtos_data is None:
        flash('Erro ao carregar produtos melhores avaliados.', 'error')
        produtos_data = []
    
    return render_template('melhores_avaliados.html', produtos=produtos_data, 
                         formatar_preco=formatar_preco, limite=limite)

@app.route('/custo-beneficio')
def custo_beneficio():
    limite = request.args.get('limite', 10, type=int)
    produtos_data = fazer_requisicao_api('/melhores-custo-avaliativo/', params={'limite': limite})
    if produtos_data is None:
        flash('Erro ao carregar produtos com melhor custo-benefício.', 'error')
        produtos_data = []
    return render_template('custo_beneficio.html', produtos=produtos_data, 
                         formatar_preco=formatar_preco, limite=limite)

@app.route('/buscas')
def buscas():
    buscas_data = fazer_requisicao_api('/buscas/')
    if buscas_data is None:
        flash('Erro ao carregar histórico de buscas.', 'error')
        buscas_data = []
    return render_template('buscas.html', buscas=buscas_data)


# A página de gerenciamento é que podemos apagar o banco para realizar novas pesquisas sem ter aquele monte de resultados realizados anteriormente
@app.route('/gerenciar')
def gerenciar():
    return render_template('gerenciar.html')

@app.route('/limpar-banco', methods=['POST'])
def limpar_banco():
    termo = request.form.get('termo')
    if not termo:
        flash('Por favor, digite um termo ou "tudo" para limpar.', 'error')
        return redirect(url_for('gerenciar'))
    try:
        response = requests.delete(f"{API_BASE_URL}/limpar-banco", 
                                 params={'termo': termo}, 
                                 timeout=10)
        if response.status_code == 200:
            resultado = response.json()
            flash(resultado['mensagem'], 'success')
        else:
            flash('Erro ao limpar banco de dados.', 'error')
    except requests.exceptions.RequestException as e:
        flash(f'Erro de conexão com a API: {str(e)}', 'error')
    return redirect(url_for('gerenciar'))



@app.route('/api/status')
def api_status():
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            return jsonify({'status': 'online', 'message': 'API está funcionando'})
        else:
            return jsonify({'status': 'error', 'message': 'API retornou erro'})
    except requests.exceptions.RequestException:
        return jsonify({'status': 'offline', 'message': 'API não está acessível'})




# Filtrozin personalizado para o dinheiro :)
@app.template_filter('currency')
def currency_filter(value):
    return formatar_preco(value)

if __name__ == '__main__':
    app.run(debug=True, port=5000)