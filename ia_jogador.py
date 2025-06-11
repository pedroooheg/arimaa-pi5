import math
from arimaa import FORCAS, DIRECOES

class IAJogador:
    def __init__(self, profundidade=3, jogador='Ouro'):
        self.profundidade = profundidade
        self.jogador = jogador

    def avaliar_estado(self, jogo):
        score = 0
        if jogo.fim:
            if jogo.vencedor == self.jogador:
                return 1_000_000
            elif jogo.vencedor is not None:
                return -1_000_000

        for x in range(8):
            for y in range(8):
                peca = jogo.tabuleiro[x][y]
                if peca == 'O' and self.jogador == 'Ouro':
                    score += x * 1000
                elif peca == 'o' and self.jogador == 'Prata':
                    score += (7-x) * 1000
        return score

    # NOVO: Gera todos os movimentos válidos pro jogador atual!
    def movimentos_validos(self, jogo):
        movs = []
        for x in range(8):
            for y in range(8):
                peca = jogo.tabuleiro[x][y]
                if peca == ' ':
                    continue
                if jogo.jogador == 'Ouro' and not peca.isupper():
                    continue
                if jogo.jogador == 'Prata' and not peca.islower():
                    continue
                for direcao in DIRECOES:
                    if jogo.validar_movimento(x, y, direcao):
                        movs.append((x, y, direcao))
        return movs

    def sequencias_turno(self, jogo, n=4):
        def helper(jogo, seq, depth):
            if depth == 0 or jogo.fim:
                return [seq]
            sequencias = []
            for mov in self.movimentos_validos(jogo):
                novo_jogo = jogo.executar_movimento((mov[0], mov[1]), mov[2])
                if novo_jogo is None:
                    continue
                novo_jogo.processar_capturas()
                sequencias += helper(novo_jogo, seq + [mov], depth - 1)
            return sequencias if sequencias else [seq]
        return helper(jogo, [], n)

    def minimax_turno(self, jogo, profundidade, alpha, beta, maximizando):
        if profundidade == 0 or jogo.fim:
            return self.avaliar_estado(jogo), []
        if maximizando:
            max_eval = -math.inf
            melhor_seq = []
            for seq in self.sequencias_turno(jogo, n=min(4, jogo.mov_restantes)):
                novo_jogo = jogo.copiar()
                for mov in seq:
                    novo_jogo = novo_jogo.executar_movimento((mov[0], mov[1]), mov[2])
                    if novo_jogo is None:
                        break
                    novo_jogo.processar_capturas()
                    if novo_jogo.fim:
                        break
                if novo_jogo is None:
                    continue
                valor, _ = self.minimax_turno(novo_jogo, profundidade-1, alpha, beta, False)
                if valor > max_eval:
                    max_eval = valor
                    melhor_seq = seq
                alpha = max(alpha, valor)
                if beta <= alpha:
                    break
            return max_eval, melhor_seq
        else:
            min_eval = math.inf
            pior_seq = []
            for seq in self.sequencias_turno(jogo, n=min(4, jogo.mov_restantes)):
                novo_jogo = jogo.copiar()
                for mov in seq:
                    novo_jogo = novo_jogo.executar_movimento((mov[0], mov[1]), mov[2])
                    if novo_jogo is None:
                        break
                    novo_jogo.processar_capturas()
                    if novo_jogo.fim:
                        break
                if novo_jogo is None:
                    continue
                valor, _ = self.minimax_turno(novo_jogo, profundidade-1, alpha, beta, True)
                if valor < min_eval:
                    min_eval = valor
                    pior_seq = seq
                beta = min(beta, valor)
                if beta <= alpha:
                    break
            return min_eval, pior_seq

    def melhor_jogada(self, jogo):
        if jogo.jogador != self.jogador or jogo.fim:
            return None
        _, seq = self.minimax_turno(jogo, self.profundidade, -math.inf, math.inf, True)
        return seq
