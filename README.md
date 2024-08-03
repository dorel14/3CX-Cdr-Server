
# 3CX CDR SERVER APPLICATION

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)
[![fr](https://img.shields.io/badge/lang-fr-green.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.fr.md)
[![swe](https://img.shields.io/badge/lang-swe-blue.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.swe.md)

# Recording 3CX CDRs in a PostgreSQL Database with Grafana

## Description

This tool facilitates the recording of 3CX Call Detail Records (CDRs) in a PostgreSQL database and the creation of dashboards with Grafana.

It allows you to collect call data from your 3CX telephony system and store it in a PostgreSQL database. With Grafana, you can then visualize this data in the form of interactive and customizable dashboards.

## Main Features

- **CDR Collection**: Retrieval of CDRs from 3CX via different transfer modes (TCP, FTP, SFTP, SCP).
- **Integration of 3CX Information**: Extensions and queues can be integrated into the database via the available web interface to allow more detailed analysis of CDRs.
- **Storage in PostgreSQL**: Recording of CDRs in a PostgreSQL database for centralized and structured storage.
- **Web API**: A Web API is provided to interact with the stored CDR data.
- **Visualization with Grafana**: Creation of Grafana dashboards to visualize and analyze call data interactively.

## Technologies Used

- Python
- FastAPI (Web API)
- PostgreSQL (Database)
- Grafana (Data Visualization)
- Docker (Containerization)

## Contributions

If you appreciate this project and would like to contribute, feel free to submit pull requests or report issues. Any contribution is welcome!

For more information on installing, configuring, and using this tool, please refer to the project's wiki.
