#!/usr/bin/env python3
from ics.icalendar import Calendar
import requests
import bs4
import getpass
import os
import sys
import time

import logging
log_format = "%(asctime)s [%(name)s][%(levelname)s]: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.ERROR)


# EDT_DIR = sys.path[0]
EDT_DIR = "/var/www/edt"
EDT_FILE = os.path.join(EDT_DIR, "edt.ics")

LOGIN_URL = "https://cas.univ-valenciennes.fr/cas/login?service=https%3A%2F%2Fvtmob.univ-valenciennes.fr%2Fesup-vtclient-up4%2Fstylesheets%2Fdesktop%2Fwelcome.xhtml"
EDT_URL = "https://vtmob.univ-valenciennes.fr/esup-vtclient-up4/stylesheets/desktop/welcome.xhtml"

DELAY = 1800
RETRY_DELAY = 60


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
        edt = sess.post(EDT_URL, data=parameters_edt)
        # logging.info("Edt récupéré")
        cal = Calendar(edt.text)
        logging.info("Nombre de cours: {}".format(len(cal.events)))

        with open(EDT_FILE, "w") as f:
            f.write(edt.text)

        time.sleep(DELAY)
    except Exception as e:
        logging.error(e)
        time.sleep(RETRY_DELAY)
