
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)
[![fr](https://img.shields.io/badge/lang-fr-green.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.fr.md)
[![swe](https://img.shields.io/badge/lang-swe-blue.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.swe.md)
# Recording 3CX CDRs into a PostgreSql database with Grafana

## Description
This tool facilitates the recording of 3CX CDRs into a PostgreSql database and the creation of dashboards using Grafana.

## Installation
To utilize all features, installation via Docker is necessary. This image contains 5 containers:
- TCP Server / FTP- SFTP - SCP Client
- WebAPI server
- Postgres v12 container
- PgAdmin container
- Grafana container for dashboards

## Configuration
1. Basic parameters should be provided in a `.env` file at the root directory following the `.env_template` model.
2. Configuration settings need to be applied on the 3CX server as indicated below:
</br><a href="https://www.3cx.com/docs/cdr-call-data-records">CDR Configuration</a>

### Configuring CDRs in 3CX:
- For TCP transfer: Ensure to indicate "3CX CDR service is client / Active Socket" for the 3CX server to connect to our TCP server.
- For FTP/SFTP/SCP transfer: Ensure file generation. It's recommended to generate 1 file per call for seamless integration throughout the day. Note that this mode requires setting up an FTP server where CDR files will be available and accessible by the application. In the configuration file, you can choose to archive files on the FTP server; they will be renamed to .old, or to delete them. In any case, files are backed up after processing in the LOCAL_CDR_FOLDER_ARCHIVE directory specified in the .env file and mounted on the server running the Docker stack.
- The CDR configuration in 3CX should follow this order:
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

### Logs:
Log files are located in the directory: `/home/appuser/app/logs`.

### Contributions
If you like my work, don't hesitate to [buy me a coffee, a beer or any other drink](https://buymeacoffee.com/dorel14)