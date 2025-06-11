from arimaa import Arimaa
from ia_jogador import IAJogador
from mini_qlearning_jogador import MiniQLearningJogador

class Partida:
    def __init__(self):
        self.jogo = Arimaa()
        self.ia_ouro = MiniQLearningJogador(jogador='Ouro')
        self.ia_prata = IAJogador(profundidade=2, jogador='Prata')
        self.max_turnos = 200
        self.turnos = 0
        self.historico_posicoes = {}
        self.rodadas_sem_evento = 0
        self.ultimo_estado_coelhos = self.estado_coelhos()

    def hash_tabuleiro(self):
        return ''.join(''.join(linha) for linha in self.jogo.tabuleiro) + self.jogo.jogador

    def estado_coelhos(self):
        pos_ouro = []
        pos_prata = []
        for x in range(8):
            for y in range(8):
                if self.jogo.tabuleiro[x][y] == 'O':
                    pos_ouro.append((x, y))
                if self.jogo.tabuleiro[x][y] == 'o':
                    pos_prata.append((x, y))
        return (len(pos_ouro), tuple(sorted(pos_ouro)), len(pos_prata), tuple(sorted(pos_prata)))

    def jogar(self):
        print("Arimaa Automático: Minimax vs Minimax\n")
        while not self.jogo.fim:
            self.jogo.mostrar()
            print(f"Turno de: {self.jogo.jogador}")
            print(f"Movimentos restantes: {self.jogo.mov_restantes}")

            pos_hash = self.hash_tabuleiro()
            self.historico_posicoes[pos_hash] = self.historico_posicoes.get(pos_hash, 0) + 1
            if self.historico_posicoes[pos_hash] >= 3:
                print("\n=== EMPATE POR REPETIÇÃO DE POSIÇÃO (3x) ===")
                self.jogo.mostrar()
                break

            if self.turnos >= self.max_turnos:
                print("\n=== EMPATE POR LIMITE DE TURNOS ===")
                self.jogo.mostrar()
                break

            estado_atual_coelhos = self.estado_coelhos()
            captura = (
                    estado_atual_coelhos[0] < self.ultimo_estado_coelhos[0] or
                    estado_atual_coelhos[2] < self.ultimo_estado_coelhos[2]
            )
            avancou = (
                    estado_atual_coelhos[1] != self.ultimo_estado_coelhos[1] or
                    estado_atual_coelhos[3] != self.ultimo_estado_coelhos[3]
            )
            if captura or avancou:
                self.rodadas_sem_evento = 0
            else:
                if self.jogo.mov_restantes == 0:
                    self.rodadas_sem_evento += 1

            if self.rodadas_sem_evento >= 50:
                print("\n=== EMPATE POR 50 TURNOS SEM CAPTURA/AVANÇO ===")
                self.jogo.mostrar()
                break

            self.ultimo_estado_coelhos = estado_atual_coelhos

            # Fluxo de jogada IA vs IA
            if self.jogo.mov_restantes == 4:
                if self.jogo.jogador == 'Prata':
                    movimentos = self.ia_prata.melhor_jogada(self.jogo)
                    jogador_nome = "Prata"
                else:
                    movimentos = self.ia_ouro.melhor_jogada(self.jogo)
                    jogador_nome = "Ouro"

                if movimentos:
                    for mov in movimentos:
                        if self.jogo.mov_restantes == 0 or self.jogo.fim:
                            break
                        x, y, dir = mov
                        pos = f"{chr(y + ord('a'))}{8 - x}"
                        print(f"{jogador_nome} moveu: {pos} {dir}")
                        self.jogo = self.jogo.executar_movimento((x, y), dir)
                        self.jogo.processar_capturas()
                        if self.jogo.verificar_vitoria():
                            print(f"\n=== {self.jogo.vencedor} VENCEU! ===")
                            self.jogo.mostrar()
                            return
                else:
                    print(f"{jogador_nome} não encontrou movimentos válidos!")
                    self.jogo.mov_restantes = 0

            if self.jogo.mov_restantes == 0:
                self.jogo.processar_capturas()
                if self.jogo.verificar_vitoria():
                    print(f"\n=== {self.jogo.vencedor} VENCEU! ===")
                    self.jogo.mostrar()
                    break
                self.jogo.jogador = 'Prata' if self.jogo.jogador == 'Ouro' else 'Ouro'
                self.jogo.mov_restantes = 4
                self.turnos += 1
                continue

if __name__ == "__main__":
    Partida().jogar()
