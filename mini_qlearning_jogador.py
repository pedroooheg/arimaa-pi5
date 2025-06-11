import pickle

class MiniQLearningJogador:
    def __init__(self, jogador='Ouro', qtable_path='qtable_400.pkl'):
        self.jogador = jogador
        with open(qtable_path, 'rb') as f:
            self.Q = pickle.load(f)

    def hash_estado(self, jogo):
        return jogo.hash_tabuleiro()

    def gerar_movimentos(self, jogo):
        def helper(jogo, seq, depth):
            if depth == 0 or jogo.fim:
                return [seq] if seq else []
            sequencias = []
            if jogo.jogador != self.jogador:
                return []
            for x in range(8):
                for y in range(8):
                    peca = jogo.tabuleiro[x][y]
                    if peca == ' ' or (self.jogador == 'Ouro' and not peca.isupper()) or (self.jogador == 'Prata' and not peca.islower()):
                        continue
                    for direcao in ['cima', 'baixo', 'esquerda', 'direita']:
                        if jogo.validar_movimento(x, y, direcao):
                            novo_jogo = jogo.executar_movimento((x, y), direcao)
                            if novo_jogo is None:
                                continue
                            novo_jogo.processar_capturas()
                            subseqs = helper(novo_jogo, seq + [(x, y, direcao)], depth-1)
                            sequencias += subseqs
            return sequencias if sequencias else [seq]
        return helper(jogo, [], min(2, jogo.mov_restantes))  # Use o mesmo n do seu treinamento (ex: 2 movimentos)

    def melhor_jogada(self, jogo):
        sequencias = self.gerar_movimentos(jogo)
        if not sequencias:
            return None
        estado = self.hash_estado(jogo)
        valores = [self.Q.get((estado, tuple(seq)), 0) for seq in sequencias]
        max_v = max(valores)
        melhores = [seq for seq, v in zip(sequencias, valores) if v == max_v]
        return melhores[0]  # pega a melhor sequência
