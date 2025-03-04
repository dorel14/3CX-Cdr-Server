# 3CX CDR SERVER APPLICATION

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)

# Inspelning av 3CX CDR i en PostgreSQL-databas med Grafana

## Beskrivning

Detta verktyg underlättar inspelning av 3CX Call Detail Records (CDR) i en PostgreSQL-databas och skapandet av instrumentpaneler med Grafana.

Det låter dig samla in samtalsdata från ditt 3CX-telefonsystem och lagra det i en PostgreSQL-databas. Med Grafana kan du sedan visualisera dessa data i form av interaktiva och anpassningsbara instrumentpaneler.

## Huvudfunktioner

- **CDR-insamling**: Hämtning av CDR från 3CX via olika överföringslägen (TCP, FTP, SFTP, SCP).
- **Integration av 3CX-information**: Förlängningar och köer kan integreras i databasen via det tillgängliga webbgränssnittet för att möjliggöra mer detaljerad analys av CDR.
- **Lagring i PostgreSQL**: Inspelning av CDR i en PostgreSQL-databas för centraliserad och strukturerad lagring.
- **Web API**: Ett Web API tillhandahålls för att interagera med de lagrade CDR-data.
- **Visualisering med Grafana**: Skapande av Grafana-instrumentpaneler för att visualisera och analysera samtalsdata interaktivt.
- **Händelsehantering**: Hantera händelser med återkommande regler, påverkningsnivåer och associationer med förlängningar och köer.
- **WebSocket-integration**: Realtidsuppdateringar med WebSocket för händelsehantering.

## Använda teknologier

- Python
- FastAPI (Web API)
- PostgreSQL (Databas)
- Grafana (Datavisualisering)
- Docker (Containerisering)
- NiceGUI (Frontend)
- WebSockets (Realtidsuppdateringar)

## Bidrag

Om du uppskattar detta projekt och vill bidra, tveka inte att skicka in pull requests eller rapportera problem. Alla bidrag är välkomna!

För mer information om installation, konfiguration och användning av detta verktyg, vänligen se projektets wiki.
