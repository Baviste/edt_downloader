## edt_downloader
Permet de télécharger l'emploi du temps de l'ENT de l'UVHC fréquemment pour synchronisation (serveur web)

## Fonctionnement
Lors du lancement, les logins sont demandés pour la connexion au site de l'ENT
L'EDT est ensuite récupéré et déposé dans le dossier configuré

## Exemple
```
./edt_downloader.py -o /var/www/edt.ics -c /var/www/index.html
```
Télécharge l'emploi du temps, le place dans /var/www/ et écrit les différences dans index.html lors des prochaines updates 
