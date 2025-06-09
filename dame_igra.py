import time

from konstante import *
from tabla import Tabla


class DameIgra:
    def __init__(self, frejm):
        self.frejm = frejm
        self.tabla = Tabla()
        self.odabrana_figura = None
        self.na_redu = LILA
        self.dozvoljeni_potezi = {}

    def osvezi_igru(self, figura, potez):
        self.tabla.crtaj_tablu(self.frejm)
        if figura is not None and potez is not None:
            self.crtaj_potez_racunara(figura, potez)
        self.crtaj_dozvoljene_poteze(self.dozvoljeni_potezi)
        for figura in self.tabla.vrati_figure_po_boji(BELA):
            figura.crtaj(self.frejm)
        for figura in self.tabla.vrati_figure_po_boji(LILA):
            figura.crtaj(self.frejm)
        pygame.display.update()

    def osvezi_igru_racunar(self, figura, potez):
        self.crtaj_potez_racunara(figura, potez)
        pygame.display.update()

    def nova_igra(self):
        self.odabrana_figura = None
        self.na_redu = BELA
        self.tabla = Tabla()
        self.dozvoljeni_potezi = {}

    def odaberi_red_kolonu(self, red, kolona):
        if self.odabrana_figura:
            validno = self.pomeri_figuru_igra(red, kolona)
            if not validno:
                self.odabrana_figura = None
                # ako figura ne može da se odabere, premesti selekciju na nju
                self.odaberi_red_kolonu(red, kolona)

        # ako figura nije odabrana
        figura = self.tabla.vrati_polje(red, kolona)
        if figura != 0:
            if figura.boja == self.na_redu:
                self.dozvoljeni_potezi = self.tabla.vrati_dozvoljene_poteze(figura)
                svi_legalni = self.tabla.vrati_sve_dozvoljene_za_lila()

                # DOZVOLJENI POTEZI KOJI SE NE NALAZE U LEGALNIM, IZBACUJU SE
                self.dozvoljeni_potezi = {k: v for k, v in self.dozvoljeni_potezi.items()
                                          if k in svi_legalni}

                self.odabrana_figura = figura
                return True

        # ako kliknemo na prazno polje briše se selekcija
        self.odabrana_figura = None
        self.dozvoljeni_potezi = {}

        return False

    def pomeri_figuru_igra(self, red, kolona):
        if (self.odabrana_figura is not None) and (red, kolona) in self.dozvoljeni_potezi:
            self.tabla.pomeri_figuru_tabla(self.odabrana_figura, red, kolona)
            preskocena_figura = self.dozvoljeni_potezi[(red, kolona)]
            self.promeni_igraca_igra()
            if preskocena_figura:
                self.tabla.ukloni_figuru(preskocena_figura)
            return True
        else:
            return False

    def promeni_igraca_igra(self):
        self.na_redu = LILA if self.na_redu == BELA else BELA
        self.dozvoljeni_potezi = {}
        self.tabla.promeni_igraca_tabla()

    def crtaj_dozvoljene_poteze(self, dozvoljeni_potezi):
        for potez in dozvoljeni_potezi:
            red, kolona = potez
            # crtanje kvadrate oko dozvoljenih poteza
            pygame.draw.rect(self.frejm, ZELENA, (kolona * VELICINA_POLJA,
                                                  red * VELICINA_POLJA, VELICINA_POLJA, VELICINA_POLJA), 5)

    def pobednik_igre(self):
        return self.tabla.pobednik_igre()

    def vrati_tablu(self):
        return self.tabla

    def vrati_na_redu(self):
        return self.na_redu

    def vrati_odabranu_figuru(self):
        return self.odabrana_figura

    def potez_racunara(self, tabla):
        self.tabla = tabla
        self.promeni_igraca_igra()

    def crtaj_potez_racunara(self, figura, potez):
        red, kolona = potez
        # crtanje kvadrate oko dozvoljenih poteza
        pygame.draw.rect(self.frejm, ROZE, (kolona * VELICINA_POLJA,
                                            red * VELICINA_POLJA, VELICINA_POLJA, VELICINA_POLJA), 5)

        stari_red, stara_kolona = figura.red, figura.kolona
        pygame.draw.rect(self.frejm, ROZE, (stara_kolona * VELICINA_POLJA,
                                            stari_red * VELICINA_POLJA, VELICINA_POLJA, VELICINA_POLJA), 5)
