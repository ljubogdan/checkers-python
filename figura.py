from konstante import *


class Figura(object):
    def __init__(self, boja, red, kolona):
        self.boja = boja
        self.red = red
        self.kolona = kolona
        self.dama = False
        self.x, self.y = 0, 0

        self.racun_pozicije_xy()

    def racun_pozicije_xy(self):
        self.x = self.kolona * VELICINA_POLJA + VELICINA_POLJA // 2
        self.y = self.red * VELICINA_POLJA + VELICINA_POLJA // 2

    def crtaj(self, prozor):
        # crtanje figure
        if self.boja == LILA:
            pygame.draw.circle(prozor, TAMNIJA_LILA, (self.x, self.y), VELICINA_POLJA // 2 - 10)
        else:
            pygame.draw.circle(prozor, TAMNIJA_BELA, (self.x, self.y), VELICINA_POLJA // 2 - 10)

        pygame.draw.circle(prozor, self.boja, (self.x, self.y-7), VELICINA_POLJA // 2 - 10)
        if self.dama:
            if self.boja == LILA:
                pygame.draw.circle(prozor, TAMNIJA_LILA, (self.x, self.y), VELICINA_POLJA // 2 - 10)
            else:
                pygame.draw.circle(prozor, TAMNIJA_BELA, (self.x, self.y), VELICINA_POLJA // 2 - 10)

            pygame.draw.circle(prozor, self.boja, (self.x, self.y - 7), VELICINA_POLJA // 2 - 10)
            prozor.blit(kruna, (self.x - kruna.get_width() // 2, (self.y - 7) - kruna.get_height() // 2))

    def dama_promo(self):
        self.dama = True

    def nove_koordinate(self, red, kolona):
        self.red, self.kolona = red, kolona
        self.racun_pozicije_xy()








