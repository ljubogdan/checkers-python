import pygame
from konstante import *
from tabla import *
from dame_igra import *
from algoritam import *
import time


najgore_vreme = 0
prosecno_vreme = 0
najbolje_vreme = 9999
broj_poziva = 0

pygame.display.set_caption("Dame SV2/2023")
PROZOR = pygame.display.set_mode((VISINA, SIRINA))

FPS = 60

pygame.init()
dame_igra = DameIgra(PROZOR)


def odredi_dubinu_pretrage(broj_figura, preostalo_vreme, osnovna_dubina=3):
    if preostalo_vreme > 2.5:
        if broj_figura <= 5:
            return osnovna_dubina + 3
        elif broj_figura <= 10:
            return osnovna_dubina + 2
        else:
            return osnovna_dubina + 1
    elif preostalo_vreme > 2:
        if broj_figura <= 5:
            return osnovna_dubina + 2
        elif broj_figura <= 10:
            return osnovna_dubina + 1
        else:
            return osnovna_dubina
    elif preostalo_vreme > 1.5:
        if broj_figura <= 5:
            return osnovna_dubina + 1
        elif broj_figura <= 10:
            return osnovna_dubina
        else:
            return osnovna_dubina - 1
    else:
        return osnovna_dubina


def mis_red_kolona(mesto):
    x, y = mesto
    red, kolona = y // VELICINA_POLJA, x // VELICINA_POLJA
    return red, kolona


def main():
    global najgore_vreme, najbolje_vreme, transpoziciona_tabela, prosecno_vreme, broj_poziva
    # ucitaj_iz_baze_transp()
    akcija_jedenje = True
    akcija = True
    global_figura = None
    global_potez = None

    ucitaj_iz_baze_vrednosti()
    print("Dužina transpozicione tabele nakon učitavanja je: ", len(transpoziciona_tabela))

    # pitamo na početku da li je forsirano jedenje
    print("Da li je forsirano jedenje? (ENTER - da, SPACE - ne): ")

    while akcija_jedenje:
        for dogadjaj in pygame.event.get():
            if dogadjaj.type == pygame.KEYDOWN:
                if dogadjaj.key == pygame.K_RETURN:
                    dame_igra.tabla.forsirano_jedenje = True
                    akcija_jedenje = False
                    print("Forsirano jedenje je uključeno!")
                else:
                    akcija_jedenje = False
                    print("Forsirano jedenje je isključeno!")
        if not akcija_jedenje:
            break

    while akcija:
        if dame_igra.pobednik_igre() is not None:
            if dame_igra.pobednik_igre() == "BELA":
                print("Pobednik igre je BELA!")
                time.sleep(1)
            else:
                print("Pobednik igre je LILA!")
                time.sleep(1)
            akcija = False

        if dame_igra.na_redu == BELA and dame_igra.tabla.broj_belih == 0:
            print("Pobednik igre je LILA!")
            time.sleep(1)
            akcija = False

        if dame_igra.na_redu == LILA and dame_igra.tabla.broj_lila > 0:
            # prolazimo kroz sve poteze i gledamo da li je lila ostala bez poteza
            for figura in dame_igra.tabla.vrati_figure_po_boji(LILA):
                dozvoljeni_potezi = dame_igra.tabla.vrati_dozvoljene_poteze(figura)
                if len(dozvoljeni_potezi) > 0:
                    break
            else:
                print("Pobednik igre je BELA!")
                time.sleep(1)
                akcija = False

        if dame_igra.na_redu == BELA:
            vremensko_ogranicenje = 2.99
            pocetno_vreme = time.time()
            broj_figura = dame_igra.tabla.broj_belih + dame_igra.tabla.broj_lila

            # Računanje preostalog vremena
            preostalo_vreme = vremensko_ogranicenje - (time.time() - pocetno_vreme)

            # Pokretanje minimax algoritma s određenom dubinom pretrage
            dubina_pretrage = odredi_dubinu_pretrage(broj_figura, preostalo_vreme)

            vrednost, nova_tabla, figura, potez = minimax_algoritam(dame_igra.tabla, dubina_pretrage, True,
                                                                    float('-inf'), float('inf'), pocetno_vreme,
                                                                    vremensko_ogranicenje, dame_igra)

            krajnje_vreme = time.time()

            if nova_tabla is not None:
                dame_igra.tabla = nova_tabla
                dame_igra.promeni_igraca_igra()
                global_figura = figura
                global_potez = potez
            else:
                print("Kosmičko zračenje!")
                akcija = False

            print("\nTrenutni broj belih figura: ", dame_igra.tabla.broj_belih)
            print("Trenutni broj lila figura: ", dame_igra.tabla.broj_lila)
            print("Trenutni broj belih dama: ", dame_igra.tabla.broj_belih_dama)
            print("Trenutni broj lila dama: ", dame_igra.tabla.broj_lila_dama)

            print("\nTrenutna vrednost table: ", dame_igra.tabla.vrednost_table())
            print("\nRačunar je odigrao potez za: ", krajnje_vreme - pocetno_vreme, " sekundi.")

            prosecno_vreme += krajnje_vreme - pocetno_vreme
            broj_poziva += 1

            if krajnje_vreme - pocetno_vreme > najgore_vreme:
                najgore_vreme = krajnje_vreme - pocetno_vreme
            if krajnje_vreme - pocetno_vreme < najbolje_vreme:
                najbolje_vreme = krajnje_vreme - pocetno_vreme

            print("\nNajbolje vreme: ", najbolje_vreme)
            print("Najgore vreme: ", najgore_vreme)
            print("Prosečno vreme: ", prosecno_vreme / broj_poziva)

        for dogadjaj in pygame.event.get():
            if dogadjaj.type == pygame.MOUSEBUTTONDOWN:
                mesto = pygame.mouse.get_pos()
                red, kolona = mis_red_kolona(mesto)
                dame_igra.odaberi_red_kolonu(red, kolona)
                if dame_igra.na_redu == LILA:
                    dame_igra.odaberi_red_kolonu(red, kolona)

            if dogadjaj.type == pygame.QUIT:
                akcija = False

        dame_igra.osvezi_igru(global_figura, global_potez)

    sacuvaj_u_bazi()

    print("\nDužina transpozicione tabele: ", len(transpoziciona_tabela))
    time.sleep(6)
    cuvaj_u_bazu(transpoziciona_tabela)
    pygame.quit()


if __name__ == "__main__":
    main()
