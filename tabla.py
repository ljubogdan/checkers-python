import pygame
from konstante import *
from figura import Figura
import time

# čuvamo vrednost u rečniku { hashkod : vrednost }
memo = {}


def ucitaj_iz_baze_vrednosti():
    baza = 'baza_vrednosti.txt'
    try:
        with open(baza, 'r') as f:
            for linija in f:
                try:
                    key, value = linija.split(':')
                    memo[int(key)] = float(value)
                except ValueError:
                    continue
    except FileNotFoundError:
        print("Baza vrednosti nije pronađena!")
        pass


def sacuvaj_u_bazi():
    baza = 'baza_vrednosti.txt'
    with open(baza, 'w') as f:
        for key, value in memo.items():
            f.write(f"{key}:{value}\n")


class Tabla(object):
    def __init__(self):
        self.prethodni_potezi = []
        self.forsirano_jedenje = False
        self.na_redu = LILA
        self.tabla = []
        self.broj_belih, self.broj_lila = 12, 12
        self.broj_belih_dama, self.broj_lila_dama = 0, 0
        self.pocetna_tabla()
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            bela_tuple = tuple((figura.red, figura.kolona, int(figura.dama)) for figura in self.vrati_figure_po_boji(BELA))
            lila_tuple = tuple((figura.red, figura.kolona, int(figura.dama)) for figura in self.vrati_figure_po_boji(LILA))
            return hash((bela_tuple, lila_tuple))
        return self._hash

    @classmethod
    def crtaj_polja(cls, prozor):
        prozor.fill(BEZ)
        # prvo polje gore levo je zauzeto braon poljem
        for red in range(REDOVI):
            for kolona in range(red % 2, REDOVI, 2):
                pygame.draw.rect(prozor, BRAON, (red * VELICINA_POLJA, kolona * VELICINA_POLJA,
                                                 VELICINA_POLJA, VELICINA_POLJA))

    def vrati_sve_dozvoljene_za_lila(self):
        dozvoljeni_potezi = {}
        for figura in self.vrati_figure_po_boji(LILA):
            dozvoljeni_potezi.update(self.vrati_dozvoljene_poteze(figura))

        # AKO U REČNIKU IMA BAR JEDAN SA VREDNOSTI RAZL OD [], VRATI SVE BEZ [] VREDNOSTI
        if self.forsirano_jedenje:
            if all(len(value) == 0 for value in dozvoljeni_potezi.values()):
                pass
            else:
                novi_potezi = {}
                for key, value in dozvoljeni_potezi.items():
                    if len(value) != 0:
                        novi_potezi[key] = value
                return novi_potezi
        return dozvoljeni_potezi

    def pocetna_tabla(self):
        for redd in range(REDOVI):
            # punimo tablu
            self.tabla.append([])
            for kolona in range(KOLONE):
                if kolona % 2 == (redd % 2):
                    if redd < 3:
                        self.tabla[redd].append(Figura(BELA, redd, kolona))
                    elif redd > 4:
                        self.tabla[redd].append(Figura(LILA, redd, kolona))
                    else:
                        self.tabla[redd].append(0)
                else:
                    self.tabla[redd].append(0)

    def crtaj_tablu(self, prozor):
        # prvo crtamo polja
        self.crtaj_polja(prozor)
        # pa crtamo figurice
        for redd in range(REDOVI):
            for kolonaa in range(KOLONE):
                figura = self.tabla[redd][kolonaa]
                if figura != 0:
                    figura.racun_pozicije_xy()
                    figura.crtaj(prozor)

    def pomeri_figuru_tabla(self, figura, red, kolona):
        self.tabla[figura.red][figura.kolona], self.tabla[red][kolona] = (self.tabla[red][kolona],
                                                                          self.tabla[figura.red][figura.kolona])
        figura.nove_koordinate(red, kolona)

        # šta ako je figura dospela do kraja table
        if (red == REDOVI - 1 or red == 0) and not figura.dama:
            figura.dama_promo()
            if figura.boja == BELA:
                self.broj_belih_dama += 1
            else:
                self.broj_lila_dama += 1

    def vrati_polje(self, red, kolona):
        return self.tabla[red][kolona]

    def pretraga_leve_dijagonale(self, boja_figure, pocetak, kraj, smer_kretanja, leva_strana, preskocena_figura=None):
        if preskocena_figura is None:
            preskocena_figura = []

        dozvoljeni_potezi, poslednji = {}, []
        preskocene_figure_brojac = 0

        for red in range(pocetak, kraj, smer_kretanja):
            if leva_strana < 0:
                break

            trenutno_polje = self.tabla[red][leva_strana]

            if trenutno_polje == 0:
                if not poslednji and preskocena_figura:
                    break
                elif poslednji:
                    novi_potez = (red, leva_strana)
                    dozvoljeni_potezi[novi_potez] = preskocena_figura + poslednji
                    dodatni_potezi_leva = self.pretraga_leve_dijagonale(boja_figure, red + smer_kretanja, kraj,
                                                                        smer_kretanja, leva_strana - 1,
                                                                        preskocena_figura + poslednji)
                    dodatni_potezi_desna = self.pretraga_desne_dijagonale(boja_figure, red + smer_kretanja, kraj,
                                                                          smer_kretanja, leva_strana + 1,
                                                                          preskocena_figura + poslednji)
                    for key, value in dodatni_potezi_leva.items():
                        dozvoljeni_potezi[key] = value
                    for key, value in dodatni_potezi_desna.items():
                        dozvoljeni_potezi[key] = value
                else:
                    dozvoljeni_potezi[(red, leva_strana)] = preskocena_figura
                break

            elif trenutno_polje.boja == boja_figure:
                break
            else:
                poslednji = [trenutno_polje]
                preskocene_figure_brojac += 1
                if preskocene_figure_brojac > 1:
                    break
            leva_strana -= 1

        return dozvoljeni_potezi

    def pretraga_desne_dijagonale(self, boja_figure, pocetak, kraj, smer_kretanja, desna_strana,
                                  preskocena_figura=None):
        if preskocena_figura is None:
            preskocena_figura = []

        dozvoljeni_potezi, poslednji = {}, []
        preskocene_figure_brojac = 0

        for red in range(pocetak, kraj, smer_kretanja):
            if desna_strana >= KOLONE:
                break

            trenutno_polje = self.tabla[red][desna_strana]

            if trenutno_polje == 0:
                if not poslednji and preskocena_figura:
                    break
                elif poslednji:
                    novi_potez = (red, desna_strana)
                    dozvoljeni_potezi[novi_potez] = preskocena_figura + poslednji
                    dodatni_potezi_leva = self.pretraga_leve_dijagonale(boja_figure, red + smer_kretanja, kraj,
                                                                        smer_kretanja, desna_strana - 1,
                                                                        preskocena_figura + poslednji)
                    dodatni_potezi_desna = self.pretraga_desne_dijagonale(boja_figure, red + smer_kretanja, kraj,
                                                                          smer_kretanja, desna_strana + 1,
                                                                          preskocena_figura + poslednji)
                    for key, value in dodatni_potezi_leva.items():
                        dozvoljeni_potezi[key] = value
                    for key, value in dodatni_potezi_desna.items():
                        dozvoljeni_potezi[key] = value
                else:
                    dozvoljeni_potezi[(red, desna_strana)] = preskocena_figura
                break

            elif trenutno_polje.boja == boja_figure:
                break
            else:
                poslednji = [trenutno_polje]
                preskocene_figure_brojac += 1
                if preskocene_figure_brojac > 1:
                    break
            desna_strana += 1
        return dozvoljeni_potezi

    def vrati_dozvoljene_poteze(self, figura):

        # dozvoljeni potezi je rečnik tipa {(red, kolona): [lista preskočenih figura]}
        # gde su red i kolona ciljne pozicije, a lista preskočenih figura je prazna ako nema preskakanja

        dozvoljeni_potezi, red = {}, figura.red
        leva_strana, desna_strana = figura.kolona - 1, figura.kolona + 1
        if figura.boja == BELA or figura.dama:
            dozvoljeni_potezi.update(self.pretraga_leve_dijagonale(figura.boja, red + 1,
                                                                   REDOVI, 1, leva_strana))
            dozvoljeni_potezi.update(self.pretraga_desne_dijagonale(figura.boja, red + 1,
                                                                    REDOVI, 1, desna_strana))
        if figura.boja == LILA or figura.dama:
            dozvoljeni_potezi.update(self.pretraga_desne_dijagonale(figura.boja, red - 1, -1, -1, desna_strana))
            dozvoljeni_potezi.update(self.pretraga_leve_dijagonale(figura.boja, red - 1, -1, -1, leva_strana))

        if self.forsirano_jedenje:
            # AKO JE DUŽINA REČNIKA VEĆA OD NULA, I AKO SU SVE VREDNOSTI [], NEMOJ RADITI NIŠTA
            if all(len(value) == 0 for value in dozvoljeni_potezi.values()):
                pass
            else:
                novi_potezi = {}
                for key, value in dozvoljeni_potezi.items():
                    if len(value) != 0:
                        novi_potezi[key] = value
                return novi_potezi
        return dozvoljeni_potezi

    def ukloni_figuru(self, figure_za_uklanjanje):
        for f in figure_za_uklanjanje:
            self.tabla[f.red][f.kolona] = 0

            if f.boja == BELA:
                self.broj_belih -= 1
            else:
                self.broj_lila -= 1
            if f.dama:
                if f.boja == BELA:
                    self.broj_belih_dama -= 1
                else:
                    self.broj_lila_dama -= 1

    def pobednik_igre(self):
        if self.broj_belih <= 0:
            return "LILA"
        elif self.broj_lila <= 0:
            return "BELA"

        return None

    def promeni_igraca_tabla(self):
        self.na_redu = LILA if self.na_redu == BELA else BELA

    # ODREDJUJEMO VREDNOST TABLE

    # BELI JE MAXIMIZER, LILA JE MINIMIZER
    # Broj pešaka i dama: Osnovni parametri koji direktno utiču na snagu pozicije.
    # Sigurne figure: Figure na ivici table ili u drugim sigurnim pozicijama manje su podložne napadima.
    # Napredovanje ka damama: Figure koje su blizu postizanja dame su vrednije.
    # Mobilnost: Više mogućih poteza daje veću fleksibilnost.
    # Kontrola centra: Kontrola centralnih pozicija daje stratešku prednost.
    # Ofanzivne pozicije: Figure u pozicijama za napad povećavaju vrednost.

    def vrednost_table(self):
        vrednost = 0

        if hash(self) in memo:
            return memo[hash(self)]

        # Koeficijenti
        koef = {
            "pesaka": 20,
            "dama": 30,
            "rubnih_figura": 5,
            "napredovanja_ka_damama": 2,
            "mobilnosti": 5,
            "uzeg_centra": 8,
            "sireg_centra": 6,
            "ofanzivnih_pozicija": 7,
            "pobede": 1000,
            "neresenog": -10000,
            "neprijateljskih_figura": 15,
            "zastite_kralja": 20,
            "centralizacije_dama": 10,
            "zamka_pozicije": 5,
            "pojedene_figure": 200
        }

        # POJEDENE FIGURE
        if self.broj_lila <= 2:
            br_belih_pojedenih = sum(
                len(self.vrati_dozvoljene_poteze(figura)) for figura in self.vrati_figure_po_boji(BELA)
            )
            br_lila_pojedenih = sum(
                len(self.vrati_dozvoljene_poteze(figura)) for figura in self.vrati_figure_po_boji(LILA)
            )

            vrednost += koef["pojedene_figure"] * (br_belih_pojedenih - br_lila_pojedenih)

        # Inicijalne vrednosti
        br_belih, br_lila = self.broj_belih, self.broj_lila
        br_belih_dama, br_lila_dama = self.broj_belih_dama, self.broj_lila_dama

        # Vrednosti po broju figura
        vrednost += koef["pesaka"] * (br_belih - br_lila)
        vrednost += koef["dama"] * (br_belih_dama - br_lila_dama)

        # POBEDA / NEREŠENO
        if br_lila == 0:
            vrednost += koef["pobede"]
        elif br_belih == 0:
            vrednost -= koef["pobede"]
        elif all(len(self.vrati_dozvoljene_poteze(figura)) == 0 for figura in self.vrati_figure_po_boji(LILA)):
            vrednost += koef["neresenog"]
        elif all(len(self.vrati_dozvoljene_poteze(figura)) == 0 for figura in self.vrati_figure_po_boji(BELA)):
            vrednost -= koef["neresenog"]

        # RUBNE FIGURE
        broj_belih_rubnih_figura = sum(
            1 for i in range(8) for j in (0, 7) if self.tabla[i][j] and self.tabla[i][j].boja == BELA
        )
        broj_lila_rubnih_figura = sum(
            1 for i in range(8) for j in (0, 7) if self.tabla[i][j] and self.tabla[i][j].boja == LILA
        )
        vrednost += koef["rubnih_figura"] * (broj_belih_rubnih_figura - broj_lila_rubnih_figura)

        # NAPREDOVANJE KA DAMAMA
        br_belih_potencijalnih_dama = sum(
            1 for i in (5, 6) for j in range(8) if
            self.tabla[i][j] and self.tabla[i][j].boja == BELA and not self.tabla[i][j].dama
        )
        br_lila_potencijalnih_dama = sum(
            1 for i in (1, 2) for j in range(8) if
            self.tabla[i][j] and self.tabla[i][j].boja == LILA and not self.tabla[i][j].dama
        )
        vrednost += koef["napredovanja_ka_damama"] * (br_belih_potencijalnih_dama - br_lila_potencijalnih_dama)

        # MOBILNOST
        br_belih_poteza = sum(
            len(self.vrati_dozvoljene_poteze(self.tabla[i][j])) for i in range(8) for j in range(8) if
            self.tabla[i][j] and self.tabla[i][j].boja == BELA
        )
        br_lila_poteza = sum(
            len(self.vrati_dozvoljene_poteze(self.tabla[i][j])) for i in range(8) for j in range(8) if
            self.tabla[i][j] and self.tabla[i][j].boja == LILA
        )
        vrednost += koef["mobilnosti"] * (br_belih_poteza - br_lila_poteza)

        # KONTROLA CENTRA
        br_belih_centralnih_figura = sum(
            1 for i in range(3, 5) for j in range(3, 5) if self.tabla[i][j] and self.tabla[i][j].boja == BELA
        )
        br_lila_centralnih_figura = sum(
            1 for i in range(3, 5) for j in range(3, 5) if self.tabla[i][j] and self.tabla[i][j].boja == LILA
        )
        br_belih_medju_figura = sum(
            1 for i in range(2, 6) for j in range(2, 6) if self.tabla[i][j] and self.tabla[i][j].boja == BELA
        )
        br_lila_medju_figura = sum(
            1 for i in range(2, 6) for j in range(2, 6) if self.tabla[i][j] and self.tabla[i][j].boja == LILA
        )
        vrednost += koef["uzeg_centra"] * (br_belih_centralnih_figura - br_lila_centralnih_figura)
        vrednost += koef["sireg_centra"] * (br_belih_medju_figura - br_lila_medju_figura)
        vrednost -= koef["sireg_centra"] * (br_belih_centralnih_figura - br_lila_centralnih_figura)

        # OFANZIVNE POZICIJE
        br_belih_ofanzivnih_figura = sum(
            1 for i in range(8) for j in range(8) if self.tabla[i][j] and self.tabla[i][j].boja == BELA and len(
                self.vrati_dozvoljene_poteze(self.tabla[i][j])) > 0
        )
        br_lila_ofanzivnih_figura = sum(
            1 for i in range(8) for j in range(8) if self.tabla[i][j] and self.tabla[i][j].boja == LILA and len(
                self.vrati_dozvoljene_poteze(self.tabla[i][j])) > 0
        )
        vrednost += koef["ofanzivnih_pozicija"] * (br_belih_ofanzivnih_figura - br_lila_ofanzivnih_figura)

        # NEPRIJATELJSKE FIGURE
        broj_lila_opasnih = sum(
            1 for figura in self.vrati_figure_po_boji(LILA) if figura.red in range(4)
        )
        broj_belih_opasnih = sum(
            1 for figura in self.vrati_figure_po_boji(BELA) if figura.red in range(4, 8)
        )
        vrednost -= koef["neprijateljskih_figura"] * broj_lila_opasnih
        vrednost += koef["neprijateljskih_figura"] * broj_belih_opasnih

        # ZAŠTITA KRALJA
        br_belih_kraljeva = sum(
            1 for figura in self.vrati_figure_po_boji(BELA) if figura.dama
        )
        br_lila_kraljeva = sum(
            1 for figura in self.vrati_figure_po_boji(LILA) if figura.dama
        )
        vrednost += koef["zastite_kralja"] * (br_belih_kraljeva - br_lila_kraljeva)

        # CENTRALIZACIJA DAMA
        br_belih_dama_centralnih = sum(
            1 for figura in self.vrati_figure_po_boji(BELA) if
            figura.dama and 2 <= figura.red <= 5 and 2 <= figura.kolona <= 5
        )
        br_lila_dama_centralnih = sum(
            1 for figura in self.vrati_figure_po_boji(LILA) if
            figura.dama and 2 <= figura.red <= 5 and 2 <= figura.kolona <= 5
        )
        vrednost += koef["centralizacije_dama"] * (br_belih_dama_centralnih - br_lila_dama_centralnih)

        # ZAMKE POZICIJE
        br_belih_zamka_pozicija = sum(
            1 for figura in self.vrati_figure_po_boji(BELA) if len(self.vrati_dozvoljene_poteze(figura)) > 1
        )
        br_lila_zamka_pozicija = sum(
            1 for figura in self.vrati_figure_po_boji(LILA) if len(self.vrati_dozvoljene_poteze(figura)) > 1
        )
        vrednost += koef["zamka_pozicije"] * (br_belih_zamka_pozicija - br_lila_zamka_pozicija)

        # Dodajemo u rečnik i memorišemo
        memo[hash(self)] = vrednost

        return vrednost

    def vrati_figure_po_boji(self, boja):
        figure = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.tabla[i][j] != 0:
                    if self.tabla[i][j].boja == boja:
                        figure.append(self.tabla[i][j])

        return figure
