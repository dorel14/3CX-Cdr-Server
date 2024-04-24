# Multilanguage README Pattern
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)
[![fr](https://img.shields.io/badge/lang-fr-green.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.fr.md)
# Recording 3CX CDRs into a PostgreSql database with Grafana

## Description
This tool enables the recording of 3CX CDRs into a PostgreSql database and the creation of dashboards using Grafana.

## Installation
To benefit from all functionalities, it's necessary to install via Docker. This image contains 4 containers:
- TCP server
- Postgres v12 container
- PgAdmin container
- Grafana container for dashboards

## Configuration
1. Basic parameters should be provided in a `.env` file at the root directory following the `.env_model` template.
2. Configuration settings need to be applied on the 3CX server as indicated below:
</br><a href="https://www.3cx.com/docs/cdr-call-data-records">Paramétrage des CDR</a>

### Configuring CDRs in 3CX:
- Ensure to indicate "3CX CDR service is client / Active Socket" for the 3CX server to connect to our TCP server.
- CDR configuration in 3CX should follow this sequence:
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

