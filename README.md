<h2>Cet outil permet l'enregistrement des CDR 3cx dans une base de donnée</h2></br>


<h3>Pour bénéficier de l'ensemble des fonctions , il est nécessaire de faire l'installation via Docker.</br>
Cette image contient  4 conteneurs , le serveur TCP,  le conteneur Postgres v12, le conteneur PgAdmin et le conteneur Grafana pour les dashboards</h3></br>

Les paramètres de base sont à indiquer dans un fichier .env à la racine du répertoire selon le modèle .env_model</br>
Les paramétrages doivent être faits sur le serveur 3CX comme indiqué ici: </br><a href="https://www.3cx.com/docs/cdr-call-data-records">Paramétrage des CDR</a>
Attention à bien indiquer "3CX CDR service is client / Active Socket" afin que le serveur 3cx se connecte sur notre serveur TCP.
</br>
Le paramétrage des CDR dans 3cx doit suivre cet ordre:
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

