# Uppgraderingsinstruktioner

## Översikt

Detta dokument förklarar syftet med uppdateringsskripten och hur man använder dem baserat på ditt operativsystem. Uppdateringsskripten är utformade för att hjälpa dig att säkert uppgradera din 3CX CDR Server-applikation genom att utföra följande uppgifter:

1. Säkerhetskopiera databasen.
2. Upptäcka och flytta omdöpta filer.
3. Återställa master-grenen till den senaste versionen.
4. Rensa bort föråldrade filer.
5. Återuppbygga miljön.

## Viktigt Meddelande

**Denna nya version introducerar betydande förändringar. Det är viktigt att säkerhetskopiera dina data innan du uppdaterar.**

## Uppdateringsskript

### Linux / macOS

För Linux- och macOS-användare, använd skriptet `update.sh`.

#### Användning för Linux / macOS

1. Öppna en terminal.
2. Navigera till projektkatalogen.
3. Gör skriptet körbart:

    ```sh
    chmod +x update.sh
    ```

4. Kör följande kommando:

    ```sh
    ./update.sh
    ```

### Windows (PowerShell)

För Windows-användare som använder PowerShell, använd skriptet `update.ps1`.

#### Användning för Windows PowerShell

1. Öppna PowerShell som administratör.
2. Navigera till projektkatalogen.
3. Kör följande kommando:

    ```powershell
    ./update.ps1
    ```

### Windows (Batch)

För Windows-användare som använder Kommandotolken, använd skriptet `update.bat`.

#### Användning

1. Öppna Kommandotolken som administratör.
2. Navigera till projektkatalogen.
3. Kör följande kommando:

    ```bat
    update.bat
    ```

## Detaljerade Steg

### 1. Säkerhetskopiera Databasen

Skripten kommer att skapa en säkerhetskopia av din PostgreSQL-databas med hjälp av kommandot `pg_dump`. Säkerhetskopian kommer att sparas som `backup.sql` i projektkatalogen.

### 2. Upptäcka och Flytta Omdöpta Filer

Skripten kommer att upptäcka alla omdöpta filer med hjälp av `git diff` och flytta dem till deras nya platser.

### 3. Återställa Master-grenen

Skripten kommer att återställa master-grenen till den senaste versionen från den fjärranslutna förvaret med hjälp av `git fetch`, `git checkout` och `git reset`.

### 4. Rensa Bort Föråldrade Filer

Skripten kommer att rensa bort alla föråldrade filer med hjälp av `git clean`.

### 5. Återuppbygga Miljön

Skripten kommer att återuppbygga Docker-miljön med hjälp av `docker-compose down` och `docker-compose up -d --build`.

## Slutsats

Genom att följa dessa instruktioner kan du säkert uppgradera din 3CX CDR Server-applikation till den senaste versionen. Om du stöter på några problem, vänligen se projektets wiki eller skapa en issue på [GitHub](https://github.com/dorel14/3CX-Cdr-Tcp-Server/issues).
