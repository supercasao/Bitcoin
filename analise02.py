import requests
import numpy as np
import matplotlib.pyplot as plt


def obter_transacoes_endereco(endereco):
    url = f"https://blockchain.info/rawaddr/{endereco}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        return resposta.json()
    else:
        print("Erro ao obter transações do endereço.")
        return None


def calcular_historico_saldo(transacoes):
    saldo = 0
    historico_saldo = []
    for tx in transacoes['txs']:
        valor_total_recebido = sum(
            out['value'] for out in tx['out'] if 'addr' in out and out['addr'] == transacoes['address'])
        valor_total_enviado = sum(input_tx['prev_out']['value'] for input_tx in tx['inputs'] if
                                  'prev_out' in input_tx and input_tx['prev_out']['addr'] == transacoes['address'])
        saldo += (valor_total_enviado - valor_total_recebido) / 1e8  # Convertendo de satoshis para BTC
        historico_saldo.append(saldo)

    return historico_saldo


def calcular_gini(transacoes):
    valores = []
    for tx in transacoes['txs']:
        for saida in tx['out']:
            valores.append(saida['value'])
    valores = np.array(valores)
    valores_ordenados = np.sort(valores)
    n = len(valores)
    coef_gini = (2.0 * np.sum((np.arange(1, n + 1) * valores_ordenados))) / (n * np.sum(valores)) - (n + 1) / n
    return coef_gini


def calcular_benford(transacoes):
    digitos_iniciais = []

    for tx in transacoes['txs']:
        for saida in tx['out']:
            valor = str(saida['value'])
            if valor[0] != '0':
                digitos_iniciais.append(int(valor[0]))

    digitos, contagem = np.unique(digitos_iniciais, return_counts=True)
    porcentagens = contagem / len(digitos_iniciais) * 100

    # Comparar com a distribuição de Benford
    distrib_benford = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

    plt.bar(digitos, porcentagens, label='Distribuição das Transações')
    plt.plot(range(1, 10), distrib_benford, 'r-', label='Lei de Benford', linewidth=2)
    plt.xlabel('Dígito Inicial')
    plt.ylabel('Porcentagem')
    plt.legend()
    plt.title('Comparação com a Lei de Benford')
    plt.show()


def main():
    endereco = "1JHH1pmHujcVa1aXjRrA13BJ13iCfgfBqj"
    transacoes = obter_transacoes_endereco(endereco)

    if transacoes:
        # Histórico de saldo
        historico_saldo = calcular_historico_saldo(transacoes)
        plt.plot(historico_saldo)
        plt.title('Histórico de Saldo')
        plt.xlabel('Número da Transação')
        plt.ylabel('Saldo (BTC)')
        plt.show()

        # GINI das transações
        gini = calcular_gini(transacoes)
        print(f"Coeficiente de Gini das transações: {gini}")

        # Benford das transações
        calcular_benford(transacoes)


if __name__ == "__main__":
    main()
