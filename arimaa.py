import math
from copy import deepcopy

FORCAS = {'e': 6, 'c': 5, 'a': 4, 'd': 3, 'g': 2, 'o': 1}
DIRECOES = {
    'cima': (-1, 0),
    'baixo': (1, 0),
    'esquerda': (0, -1),
    'direita': (0, 1)
}

class Arimaa:
    def __init__(self, tabuleiro=None):
        if tabuleiro:
            self.tabuleiro = deepcopy(tabuleiro)
        else:
            self.tabuleiro = [
                ['O', 'O', 'O', 'O', 'O', 'G', 'D', 'A'],
                ['E', 'C', 'A', 'D', 'G', 'O', 'O', 'O'],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                ['o', 'o', 'o', 'o', 'o', 'g', 'd', 'a'],
                ['e', 'c', 'a', 'd', 'g', 'o', 'o', 'o']
            ]
        self.jogador = 'Ouro'
        self.mov_restantes = 4
        self.fim = False
        self.vencedor = None

    def copiar(self):
        copia = Arimaa(self.tabuleiro)
        copia.jogador = self.jogador
        copia.mov_restantes = self.mov_restantes
        copia.fim = self.fim
        copia.vencedor = self.vencedor
        return copia

    def mostrar(self):
        print("\n  a b c d e f g h")
        for i in range(8):
            print(f"{8 - i} ", end="")
            for celula in self.tabuleiro[i]:
                print(celula if celula != ' ' else '.', end=" ")
            print(f"{8 - i}")
        print("  a b c d e f g h\n")

    def verificar_congelamento(self, x, y):
        peca = self.tabuleiro[x][y].lower()
        if peca == ' ':
            return False
        jogador = 'Ouro' if self.tabuleiro[x][y].isupper() else 'Prata'
        adversario = 'Prata' if jogador == 'Ouro' else 'Ouro'

        for dx, dy in DIRECOES.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                vizinha = self.tabuleiro[nx][ny]
                if (adversario == 'Ouro' and vizinha.isupper()) or (adversario == 'Prata' and vizinha.islower()):
                    if FORCAS[vizinha.lower()] > FORCAS[peca]:
                        tem_aliado = False
                        for dx2, dy2 in DIRECOES.values():
                            nx2, ny2 = x + dx2, y + dy2
                            if 0 <= nx2 < 8 and 0 <= ny2 < 8:
                                aliado = self.tabuleiro[nx2][ny2]
                                if (jogador == 'Ouro' and aliado.isupper()) or (jogador == 'Prata' and aliado.islower()):
                                    tem_aliado = True
                                    break
                        if not tem_aliado:
                            return True
        return False

    def validar_movimento(self, x, y, direcao):
        dx, dy = DIRECOES[direcao]
        novo_x, novo_y = x + dx, y + dy

        if not (0 <= novo_x < 8) or not (0 <= novo_y < 8):
            return False

        peca = self.tabuleiro[x][y]
        if peca == ' ':
            return False

        if (self.jogador == 'Ouro' and not peca.isupper()) or (self.jogador == 'Prata' and not peca.islower()):
            return False

        # Coelhos não andam para trás
        if peca.lower() == 'o':
            if peca.isupper() and direcao == 'cima':
                return False
            if peca.islower() and direcao == 'baixo':
                return False

        if self.verificar_congelamento(x, y):
            return False

        destino = self.tabuleiro[novo_x][novo_y]
        if destino == ' ':
            return True

        # Empurrar peça inimiga mais fraca
        if (self.jogador == 'Ouro' and destino.islower()) or (self.jogador == 'Prata' and destino.isupper()):
            if FORCAS[peca.lower()] > FORCAS[destino.lower()]:
                emp_x, emp_y = novo_x + dx, novo_y + dy
                if 0 <= emp_x < 8 and 0 <= emp_y < 8:
                    return self.tabuleiro[emp_x][emp_y] == ' '
        return False

    def executar_movimento(self, origem, direcao):
        x, y = origem
        dx, dy = DIRECOES[direcao]
        novo_estado = self.copiar()
        tab = novo_estado.tabuleiro
        peca = tab[x][y]

        if tab[x + dx][y + dy] == ' ':
            tab[x][y] = ' '
            tab[x + dx][y + dy] = peca
        else:
            inimigo = tab[x + dx][y + dy]
            emp_x, emp_y = x + 2 * dx, y + 2 * dy
            if 0 <= emp_x < 8 and 0 <= emp_y < 8 and tab[emp_x][emp_y] == ' ':
                tab[emp_x][emp_y] = inimigo
                tab[x + dx][y + dy] = peca
                tab[x][y] = ' '
            else:
                return None

        novo_estado.mov_restantes -= 1
        return novo_estado

    def processar_capturas(self):
        for x in range(8):
            for y in range(8):
                if self.tabuleiro[x][y] != ' ':
                    if self.verificar_congelamento(x, y):
                        self.tabuleiro[x][y] = ' '

    def verificar_vitoria(self):
        for y in range(8):
            if self.tabuleiro[0][y] == 'o':
                self.fim = True
                self.vencedor = 'Prata'
                return True
            if self.tabuleiro[7][y] == 'O':
                self.fim = True
                self.vencedor = 'Ouro'
                return True

        coelhos_ouro = any('O' == peca for linha in self.tabuleiro for peca in linha)
        coelhos_prata = any('o' == peca for linha in self.tabuleiro for peca in linha)
        if not coelhos_prata:
            self.fim = True
            self.vencedor = 'Ouro'
            return True
        if not coelhos_ouro:
            self.fim = True
            self.vencedor = 'Prata'
            return True

        return False

    def hash_tabuleiro(self):
        return ''.join(''.join(linha) for linha in self.tabuleiro) + self.jogador
