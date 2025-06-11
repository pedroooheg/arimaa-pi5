import random
import math
import pickle
from arimaa import Arimaa
from ia_jogador import IAJogador

class QLearningAgent:
    def __init__(self, alpha=0.2, gamma=0.95, epsilon=0.2):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = {}
        self.metrics = {"vit_ouro": 0, "vit_prata": 0, "empates": 0}
        self.episodios = 0

    def hash_estado(self, jogo):
        return jogo.hash_tabuleiro()

    def escolher_acao(self, jogo, acoes_possiveis):
        estado = self.hash_estado(jogo)
        if random.random() < self.epsilon:
            return random.choice(acoes_possiveis)
        valores = [self.Q.get((estado, tuple(acao)), 0) for acao in acoes_possiveis]
        max_v = max(valores)
        melhores = [acao for acao, v in zip(acoes_possiveis, valores) if v == max_v]
        return random.choice(melhores)

    def atualizar_q(self, estado_ant, acao, recompensa, estado_novo, proxs_acoes):
        chave = (estado_ant, tuple(acao))
        futuro = max([self.Q.get((estado_novo, tuple(a)), 0) for a in proxs_acoes]) if proxs_acoes else 0
        self.Q[chave] = (1 - self.alpha) * self.Q.get(chave, 0) + self.alpha * (recompensa + self.gamma * futuro)

    def salvar(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.Q, f)
        print(f"Q-table salva ({filename}) com {len(self.Q)} pares.")

    def salvar_metricas(self, filename="metricas.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump(self.metrics, f)

def recompensa_personalizada(jogo_ant, jogo_novo):
    # Vitória ou derrota
    if jogo_novo.fim:
        if jogo_novo.vencedor == 'Ouro':
            return 1000
        elif jogo_novo.vencedor == 'Prata':
            return -1000
        else:
            return -500  # Empate é ruim, mas não tão ruim quanto perder

    recompensa = 0

    # 1. Avanço de coelhos do Ouro
    for y in range(8):
        # Procura coelho que foi pra frente
        for x in range(7, 0, -1):
            if jogo_ant.tabuleiro[x][y] == 'O' and jogo_novo.tabuleiro[x-1][y] == 'O':
                recompensa += 30  # Valor maior pelo avanço

    # 2. Captura de peças adversárias
    capturadas = 0
    for x in range(8):
        for y in range(8):
            if jogo_ant.tabuleiro[x][y].islower() and jogo_novo.tabuleiro[x][y] == ' ':
                capturadas += 1
    recompensa += capturadas * 50  # Cada captura de prata vale 50

    # 3. Punição por perder coelhos do Ouro
    for x in range(8):
        for y in range(8):
            if jogo_ant.tabuleiro[x][y] == 'O' and jogo_novo.tabuleiro[x][y] == ' ':
                recompensa -= 100

    # 4. Bônus por dominar o centro
    for x in range(2, 6):
        for y in range(2, 6):
            if jogo_novo.tabuleiro[x][y] == 'O':
                recompensa += 5

    # 5. Punição leve para cada jogada sem avanço/captura
    if recompensa == 0:
        recompensa -= 5

    return recompensa

def agent_gerar_sequencias(jogo, n=2):
    def helper(jogo, seq, depth):
        if depth == 0 or jogo.fim:
            return [seq] if seq else []
        sequencias = []
        if jogo.jogador != 'Ouro':
            return []
        for x in range(8):
            for y in range(8):
                peca = jogo.tabuleiro[x][y]
                if peca == ' ' or not peca.isupper():
                    continue
                for direcao in ['cima', 'baixo', 'esquerda', 'direita']:
                    if jogo.validar_movimento(x, y, direcao):
                        novo_jogo = jogo.executar_movimento((x, y), direcao)
                        if novo_jogo is None:
                            continue
                        novo_jogo.processar_capturas()
                        subseqs = helper(novo_jogo, seq + [(x, y, direcao)], depth - 1)
                        sequencias += subseqs
        return sequencias if sequencias else [seq]
    return helper(jogo, [], n)

def treinar_qlearning(episodios=25000, max_turnos=200, salvar_cada=1000):
    agent = QLearningAgent(alpha=0.2, gamma=0.95, epsilon=0.2)
    ia_prata = IAJogador(profundidade=1, jogador='Prata')
    metricas = []
    for ep in range(1, episodios + 1):
        jogo = Arimaa()
        turno = 0
        while not jogo.fim and turno < max_turnos:
            sequencias = agent_gerar_sequencias(jogo, n=2)
            if not sequencias:
                break
            seq = agent.escolher_acao(jogo, sequencias)
            jogo_ant = jogo.copiar()
            for mov in seq:
                jogo = jogo.executar_movimento((mov[0], mov[1]), mov[2])
                if jogo is None or jogo.fim:
                    break
                jogo.processar_capturas()
                if jogo.fim:
                    break
            recompensa = recompensa_personalizada(jogo_ant, jogo)
            prox_sequencias = agent_gerar_sequencias(jogo, n=1) if not jogo.fim else []
            agent.atualizar_q(agent.hash_estado(jogo_ant), seq, recompensa, agent.hash_estado(jogo), prox_sequencias)
            if jogo.fim:
                break
            if jogo.jogador == 'Prata':
                movimentos = ia_prata.melhor_jogada(jogo)
                if movimentos:
                    for mov in movimentos:
                        jogo = jogo.executar_movimento((mov[0], mov[1]), mov[2])
                        if jogo is None or jogo.fim:
                            break
                        jogo.processar_capturas()
                        if jogo.fim:
                            break
            turno += 1

        # Métricas do episódio
        if jogo.vencedor == 'Ouro':
            agent.metrics["vit_ouro"] += 1
        elif jogo.vencedor == 'Prata':
            agent.metrics["vit_prata"] += 1
        else:
            agent.metrics["empates"] += 1
        if ep % 10 == 0 or ep == 1:
            print(f"Episódio {ep}: {agent.metrics}")

        # Salva Q-table e métricas periodicamente
        if ep % salvar_cada == 0:
            agent.salvar(f'qtable_{ep}.pkl')
            agent.salvar_metricas(f'metricas_{ep}.pkl')
    # Salva ao final
    agent.salvar("qtable_final.pkl")
    agent.salvar_metricas("metricas_final.pkl")
    return agent

def avaliar_qlearning(agent, n_partidas=10):
    ia_prata = IAJogador(profundidade=1, jogador='Prata')
    resultados = {"ouro": 0, "prata": 0, "empate": 0}
    agent.epsilon = 0  # só exploit!
    for i in range(n_partidas):
        jogo = Arimaa()
        turno = 0
        while not jogo.fim and turno < 30:
            sequencias = agent_gerar_sequencias(jogo, n=2)
            if not sequencias:
                break
            seq = agent.escolher_acao(jogo, sequencias)
            for mov in seq:
                jogo = jogo.executar_movimento((mov[0], mov[1]), mov[2])
                if jogo is None or jogo.fim:
                    break
                jogo.processar_capturas()
                if jogo.fim:
                    break
            if jogo.fim: break
            if jogo.jogador == 'Prata':
                movimentos = ia_prata.melhor_jogada(jogo)
                if movimentos:
                    for mov in movimentos:
                        jogo = jogo.executar_movimento((mov[0], mov[1]), mov[2])
                        if jogo is None or jogo.fim:
                            break
                        jogo.processar_capturas()
                        if jogo.fim:
                            break
            turno += 1
        if jogo.vencedor == 'Ouro':
            resultados["ouro"] += 1
        elif jogo.vencedor == 'Prata':
            resultados["prata"] += 1
        else:
            resultados["empate"] += 1
    print("Avaliação final:", resultados)
    return resultados

if __name__ == "__main__":
    agent = treinar_qlearning(episodios=1000, max_turnos=200, salvar_cada=100)
    print("Treinamento completo!")
    avaliar_qlearning(agent, n_partidas=20)
