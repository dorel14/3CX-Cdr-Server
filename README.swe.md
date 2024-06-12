
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)

# Inspelning av 3CX CDR:er i en PostgreSql-databas med Grafana

## Beskrivning
Detta verktyg underlättar inspelning av 3CX CDR:er i en PostgreSql-databas och skapande av instrumentpaneler med hjälp av Grafana.

## Installation
För att använda alla funktioner krävs installation via Docker. Denna bild innehåller 5 containrar:
- TCP-server / FTP - SFTP - SCP-klient
- WebAPI-server
- Postgres v12-container
- PgAdmin-container
- Grafana-container för instrumentpaneler

## Konfiguration
1. Grundläggande parametrar ska anges i en `.env`-fil i rotkatalogen enligt modellen `.env_template`.
2. Konfigurationsinställningar måste appliceras på 3CX-servern enligt nedan:
</br><a href="https://www.3cx.com/docs/cdr-call-data-records">CDR-konfiguration</a>

### Konfigurera CDR:er i 3CX:
- För överföring via TCP: Se till att ange "3CX CDR-tjänsten är klient / aktivt socket" så att 3CX-servern kan ansluta till vår TCP-server.
- För överföring via FTP/SFTP/SCP: Se till att filgenerering är aktiverad. Det rekommenderas att generera 1 fil per samtal för sömlös integration under hela dagen. Observera att denna läge kräver att en FTP-server är konfigurerad där CDR-filer kommer att vara tillgängliga och åtkomliga av applikationen. I konfigurationsfilen kan du välja att arkivera filer på FTP-servern; de kommer att omdöpas till .old, eller att ta bort dem. I alla fall säkerhetskopieras filer efter bearbetning i katalogen LOCAL_CDR_FOLDER_ARCHIVE som anges i .env-filen och monteras på servern som kör Docker-stacken.
- Konfigurationen av CDR:er i 3CX ska följa denna ordning:
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

### Loggar:
Loggfiler finns i katalogen: `/home/appuser/app/logs`.

### Bidrag
Om du gillar mitt arbete, tveka inte att [köpa mig en kaffe, en öl eller någon annan drink](https://buymeacoffee.com/dorel14)