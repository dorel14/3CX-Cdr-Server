
# Enregistrement des CDR 3CX dans une base de données PostgreSql avec Grafana

## Description
Cet outil permet l'enregistrement des CDR 3CX dans une base de données PostgreSql et la création de tableaux de bord avec l'outil Grafana.

## Installation
Pour bénéficier de l'ensemble des fonctions, il est nécessaire de faire l'installation via Docker. Cette image contient 4 conteneurs :
- Serveur TCP
- Conteneur Postgres v12
- Conteneur PgAdmin
- Conteneur Grafana pour les dashboards

## Configuration
1. Les paramètres de base doivent être renseignés dans un fichier `.env` à la racine du répertoire selon le modèle `.env_model`.
2. Les paramétrages doivent être faits sur le serveur 3CX comme indiqué ci-dessous :
</br><a href="https://www.3cx.com/docs/cdr-call-data-records">Paramétrage des CDR</a>

### Paramétrage des CDR dans 3CX :
- Assurez-vous d'indiquer "3CX CDR service is client / Active Socket" afin que le serveur 3CX se connecte sur notre serveur TCP.
- Le paramétrage des CDR dans 3CX doit suivre cet ordre :
<ul>
<li>historyid</li>
<li>callid</li>
<li>duration</li>
<li>time_start</li>
<li>time_answered</li>
<li>time_end</li>
<li>reason_terminated</li>
<li>from_no</li>
<li>to_no</li>
<li>from_dn</li>
<li>to_dn</li>
<li>dial_no</li>
<li>reason_changed</li>
<li>final_number</li>
<li>final_dn</li>
<li>bill_code</li>
<li>bill_rate</li>
<li>bill_cost</li>
<li>bill_name</li>
<li>chain</li>
<li>from_type</li>
<li>to_type</li>
<li>final_type</li>
<li>from_dispname</li>
<li>to_dispname</li>
<li>final_dispname</li>
<li>missed_queue_calls</li>
</ul>

