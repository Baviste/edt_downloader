#!/usr/bin/env python3
from ics.icalendar import Calendar
import requests
import bs4
import getpass
import os
import sys
import time
import argparse
import arrow

import logging
log_format = "%(asctime)s [%(name)s][%(levelname)s]: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.ERROR)


LOGIN_URL = "https://cas.univ-valenciennes.fr/cas/login?service=https%3A%2F%2Fvtmob.univ-valenciennes.fr%2Fesup-vtclient-up4%2Fstylesheets%2Fdesktop%2Fwelcome.xhtml"
EDT_URL = "https://vtmob.univ-valenciennes.fr/esup-vtclient-up4/stylesheets/desktop/welcome.xhtml"

DELAY = 1800
RETRY_DELAY = 60
DATE_FORM = "ddd DD MMM YY à HH:mm"


def auth(session, login, passwd):
    logging.debug("Récupération des tokens du formulaire d'authentification")
    req = session.get(LOGIN_URL)

    if not req.url.startswith(EDT_URL):
        soup = bs4.BeautifulSoup(req.text, "html5lib")

        lt = soup.find("input", {"name": "lt"})["value"]
        execution = soup.find("input", {"name": "execution"})["value"]

        # Prépare les paramètres du formulaire de connexion et POST
        parameters = {"username": login,
                      "password": passwd,
                      "_eventId": "submit",
                      "lt": lt,
                      "execution": execution}

        logging.debug("Authentification")
        req = session.post(LOGIN_URL, data=parameters)

        if not req.url.startswith(EDT_URL):
            logging.error("""Petit problème d'authentification, \
                             vérifie ton mot de passe""")
            sys.exit(1)


def threat_changes(last_edt, new_edt, change_file):
    events1 = last_edt.events
    events2 = new_edt.events
    events1_dct = {e.begin: e for e in events1}
    events2_dct = {e.begin: e for e in events2}

    deleted = [e for e in events1 if e.begin not in events2_dct.keys()]
    added = [e for e in events2 if e.begin not in events1_dct.keys()]

    others = [[e, events2_dct[e.begin]] for e in events1 if e not in deleted]
    name_changed = [(i, j) for i, j in others if i.name != j.name]
    location_changed = [(i, j) for i, j in others if i.location != j.location]

    changed = any([deleted, added, name_changed, location_changed])

    with open(change_file, "a") as f:
        if changed:
            f.write(arrow.now().format("\n" + DATE_FORM, locale="fr_FR"))
        if deleted:
            f.write("\n\tCours supprimés:")
            for i in deleted:
                f.write("\n\t\t{} à {}".format(i.name, i.begin))
        if added:
            f.write("\n\tCours ajoutés:")
            for i in added:
                f.write("\n\t\t{} à {}".format(i.name, i.begin))
        if name_changed:
            f.write("\n\tCours renommés:")
            for i in name_changed:
                f.write("\n\t\t{} à {} en {}".format(i[0].name, i[0].begin, i[1].name))
        if location_changed:
            f.write("\n\tChangements de salles:")
            for i in location_changed:
                f.write("\n\t\t{} à {} en {}".format(i[0].name, i[0].begin, i[1].location))
    return changed

parser = argparse.ArgumentParser()
parser.add_argument("-o",
    dest="out",
    help="Fichier de sortie (defaut: edt.ics)",
    type=str,
    default="edt.ics")
parser.add_argument("-c",
    dest="change_file",
    help="Fichier pour les changements entre EDTs",
    type=str,
    default="changes.txt")
parser.add_argument("-b",
    dest="backup_dir",
    help="Dossier de backups (defaut: backup/)",
    type=str,
    default="backups/")
args = parser.parse_args()


login = input("Votre login: ")
passwd = getpass.getpass("Votre mdp: ")

sess = requests.session()
sess.headers["User-Agent"] = """Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) \
                                Gecko/20100101 Firefox/40.1"""


parameters_edt = {"org.apache.myfaces.trinidad.faces.FORM": "j_id12",
                  "_noJavaScript": "false",
                  "javax.faces.ViewState": "!1",
                  "j_id12:_idcl": "j_id12:j_id15"}

last_cal = None

while 1:
    try:
        auth(sess, login, passwd)
        req = sess.post(EDT_URL, data=parameters_edt)
        edt2 = Calendar(req.text)

        if os.path.isfile(args.out):
            edt1 = Calendar(open(args.out))
            if threat_changes(edt1, edt2, args.change_file):
                with open(args.out, "w") as f:
                    f.write(req.text)
        else:
            with open(args.out, "w") as f:
                f.write(req.text)

        time.sleep(DELAY)
    except Exception as e:
        logging.error(e)
        time.sleep(RETRY_DELAY)

