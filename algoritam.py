# IMPLEMENTACIJA MINIMAX ALGORITMA

from konstante import *
import pygame
import copy
import time
import sqlite3
import pickle


def pickle_copy(objekat):
    return pickle.loads(pickle.dumps(objekat))


def kreiraj_bazu():
    conn = sqlite3.connect('transpoziciona_tabela.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transpoziciona_tabela (
        hash_kod INTEGER PRIMARY KEY,
        vrednost REAL,
        tabla BLOB
        )
    ''')
    conn.commit()
    conn.close()


def cuvaj_u_bazu(transpoziciona_tabelax):
    conn = sqlite3.connect('transpoziciona_tabela.db')
    c = conn.cursor()
    for kljuc, vrednost in transpoziciona_tabelax.items():
        hash_kod = kljuc  # Uzimamo samo hash_kod
        najbolja_vrednost, najbolja_tabla, figura, potez = vrednost
        tabla_bajtovi = pickle.dumps((najbolja_tabla, figura, potez))  # Serijalizacija instance klase Tabla u bajtove
        try:
            if isinstance(hash_kod, tuple):
                hash_kod = hash_kod[0]

            c.execute('INSERT OR IGNORE INTO transpoziciona_tabela VALUES (?, ?, ?)',
                      (hash_kod, float(najbolja_vrednost), tabla_bajtovi))

            print(f"Uspesno dodat hash_kod: {hash_kod}")
        except sqlite3.IntegrityError as e:
            print(f"Error inserting into database: {e}")
    conn.commit()
    conn.close()


def ucitaj_iz_baze_transp():
    global transpoziciona_tabela
    conn = sqlite3.connect('transpoziciona_tabela.db')
    c = conn.cursor()

    offset = 0
    limit = 10000  # Broj redova koji se učitavaju odjednom

    while True:
        c.execute('SELECT hash_kod, vrednost, tabla FROM transpoziciona_tabela LIMIT ? OFFSET ?', (limit, offset))
        rezultati = c.fetchall()

        if not rezultati:
            break  # Izlazimo iz petlje ako nema više redova

        for rezultat in rezultati:
            hash_kod, najbolja_vrednost, tabla_bajtovi = rezultat
            najbolja_tabla, figura, potez = pickle.loads(tabla_bajtovi)  # Deserijalizacija bajtova nazad u instancu kl.
            transpoziciona_tabela[hash_kod] = (najbolja_vrednost, najbolja_tabla, figura, potez)

        offset += limit  # Pomeramo offset za sledeću grupu redova

    conn.close()


transpoziciona_tabela = {}

# Pali se na True kada lila ostane sa jednom figurom
# Tada ako ima poteza da je pojedu, to moraju da učine
danger_zone = False


def minimax_algoritam(trenutna_tabla, dubina_pretrage, maksimizujuci_igrac, alfa, beta,
                      vreme_pocetka, vremensko_ogranicenje, dame_igra):

    global danger_zone

    if trenutna_tabla.broj_lila == 1:
        danger_zone = True
    else:
        danger_zone = False

    kljuc = (hash(trenutna_tabla), dubina_pretrage, maksimizujuci_igrac)

    if kljuc in transpoziciona_tabela:
        return transpoziciona_tabela[kljuc]

    if (trenutna_tabla.pobednik_igre() is BELA or time.time() - vreme_pocetka > vremensko_ogranicenje or
            dubina_pretrage == 0 or trenutna_tabla.pobednik_igre() is not None):
        return trenutna_tabla.vrednost_table(), trenutna_tabla

    if maksimizujuci_igrac:
        najbolja_tabla = None
        najbolja_vrednost = float('-inf')
        table = generisi_table(trenutna_tabla, BELA)
        for tabla in table.keys():
            vrednost_table = minimax_algoritam(tabla, dubina_pretrage - 1, False, alfa, beta,
                                               vreme_pocetka, vremensko_ogranicenje, dame_igra)[0]
            if vrednost_table > najbolja_vrednost:
                najbolja_vrednost = vrednost_table
                najbolja_tabla = tabla

            alfa = max(alfa, vrednost_table)
            if beta <= alfa:
                break

        figura = None
        potez = None
        for key, value in table.items():
            if key == najbolja_tabla:
                figura = table.get(key)[0]
                potez = table.get(key)[1]
                break

        dame_igra.tabla.prethodni_potezi.append((figura, potez))

        transpoziciona_tabela[kljuc] = (najbolja_vrednost, najbolja_tabla, figura, potez)
        return najbolja_vrednost, najbolja_tabla, figura, potez

    else:
        najbolja_tabla = None
        najbolja_vrednost = float('inf')
        table = generisi_table(trenutna_tabla, LILA)
        for tabla in table.keys():
            vrednost_table = minimax_algoritam(tabla, dubina_pretrage - 1, True, alfa, beta,
                                               vreme_pocetka, vremensko_ogranicenje, dame_igra)[0]
            if vrednost_table < najbolja_vrednost:
                najbolja_vrednost = vrednost_table
                najbolja_tabla = tabla

            beta = min(beta, vrednost_table)
            if beta <= alfa:
                break

        figura = None
        potez = None
        for key, value in table.items():
            if key == najbolja_tabla:
                figura = table.get(key)[0]
                potez = table.get(key)[1]
                break

        dame_igra.tabla.prethodni_potezi.append((figura, potez))
        transpoziciona_tabela[kljuc] = (najbolja_vrednost, najbolja_tabla, figura, potez)
        return najbolja_vrednost, najbolja_tabla, figura, potez


def generisi_table(tabla, boja):
    global danger_zone

    potencijalne_table = {}
    potezi_sa_pojedenom_figurama = {}

    figure_po_boji = tabla.vrati_figure_po_boji(boja)
    dozvoljeni_potezi = {figura: tabla.vrati_dozvoljene_poteze(figura) for figura in figure_po_boji}

    for figura, potezi_figure in dozvoljeni_potezi.items():
        for potez, preskocena_figura in potezi_figure.items():
            nova_tabla = pickle_copy(tabla)
            nova_figura = nova_tabla.vrati_polje(figura.red, figura.kolona)
            nova_tabla = vestacki_potez(nova_figura, potez, nova_tabla, preskocena_figura)
            if nova_tabla:
                if preskocena_figura:
                    potezi_sa_pojedenom_figurama[nova_tabla] = [figura, potez]
                else:
                    potencijalne_table[nova_tabla] = [figura, potez]

    if potezi_sa_pojedenom_figurama and tabla.forsirano_jedenje:
        return potezi_sa_pojedenom_figurama

    if danger_zone and boja == BELA:
        if potezi_sa_pojedenom_figurama:
            return potezi_sa_pojedenom_figurama

    potencijalne_table = {**potezi_sa_pojedenom_figurama, **potencijalne_table}
    return potencijalne_table


def vestacki_potez(figura, potez, tabla, preskocena_figura):
    if not proveri_potez(figura, potez, tabla):
        return None
    tabla.pomeri_figuru_tabla(figura, potez[0], potez[1])
    if preskocena_figura:
        tabla.ukloni_figuru(preskocena_figura)
    # Promocija u damu
    if figura.dama is False and figura.boja == BELA and potez[0] == 7:
        figura.dama_promo()
    if figura.dama is False and figura.boja == LILA and potez[0] == 0:
        figura.dama_promo()
    tabla.prethodni_potezi.append((figura, potez))
    return tabla


def proveri_potez(figura, potez, tabla):
    # Ispitujemo samo zadnje dve dodate figure
    broj_ponavljanja = tabla.prethodni_potezi[-2:].count((figura, potez))
    if broj_ponavljanja > 1:
        return False
    # Dodatna provera za dozvoljene poteze prema pravilima igre može se dodati ovde
    return True
