## edt_downloader
Permet de télécharger l'emploi du temps de l'ENT de l'UVHC fréquemment pour syncronisation (serveur web)

## Fonctionnement
Lors du lancement, les logins sont demandés pour la connexion au site de l'ENT
L'EDT est ensuite récupéré et déposé dans le dossier configuré

## TODO
- Mettre en place Flask pour servir l'emploi du temps
    - Index des changements entre les EDTs lorsqu'il y en a
    - Donner la date d'update
