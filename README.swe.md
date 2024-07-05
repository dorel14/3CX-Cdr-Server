
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)

# Spela in 3CX CDR i en PostgreSQL-databas med Grafana

## Beskrivning

Detta verktyg underlättar inspelningen av 3CX Call Detail Records (CDR) i en PostgreSQL-databas och skapandet av dashboards med Grafana.

Det gör att du kan samla in samtalsdata från ditt 3CX-telefonsystem och lagra den i en PostgreSQL-databas. Med Grafana kan du sedan visualisera dessa data i form av interaktiva och anpassningsbara dashboards.

## Huvudfunktioner

- **CDR-insamling**: Hämtar CDR från 3CX via olika överföringslägen (TCP, FTP, SFTP, SCP).
- **PostgreSQL-lagring**: Lagrar CDR i en PostgreSQL-databas för centraliserad och strukturerad lagring.
- **Webb-API**: Ett webb-API tillhandahålls för att interagera med de lagrade CDR-data.
- **Grafana-visualisering**: Skapar Grafana-dashboards för att visualisera och analysera samtalsdata interaktivt.

## Använda tekniker

- Python
- FastAPI (Webb-API)
- PostgreSQL (Databas)
- Grafana (Datavisualisering)
- Docker (Containerisering)

## Bidrag

Om du uppskattar detta projekt och vill bidra, är du välkommen att skicka pull-förfrågningar eller rapportera problem. Alla bidrag är välkomna!

För mer information om installation, konfiguration och användning av detta verktyg, se projektets wiki.
