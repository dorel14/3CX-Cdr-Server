# 3CX CDR SERVER APPLICATION

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)

# Registro de CDRs do 3CX em um banco de dados PostgreSQL com Grafana

## Descrição

Esta ferramenta facilita o registro de Registros de Detalhes de Chamadas (CDRs) do 3CX em um banco de dados PostgreSQL e a criação de painéis com Grafana.

Ela permite coletar dados de chamadas do seu sistema de telefonia 3CX e armazená-los em um banco de dados PostgreSQL. Com o Grafana, você pode visualizar esses dados na forma de painéis interativos e personalizáveis.

## Principais Funcionalidades

- **Coleta de CDRs**: Recuperação de CDRs do 3CX via diferentes modos de transferência (TCP, FTP, SFTP, SCP).
- **Integração de Informações do 3CX**: Extensões e filas podem ser integradas ao banco de dados através da interface web disponível para permitir uma análise mais detalhada dos CDRs.
- **Armazenamento no PostgreSQL**: Registro de CDRs em um banco de dados PostgreSQL para armazenamento centralizado e estruturado.
- **API Web**: Uma API Web é fornecida para interagir com os dados de CDR armazenados.
- **Visualização com Grafana**: Criação de painéis do Grafana para visualizar e analisar dados de chamadas de forma interativa.
- **Gerenciamento de Eventos**: Gerencie eventos com regras de recorrência, níveis de impacto e associações com extensões e filas.
- **Integração com WebSocket**: Atualizações em tempo real usando WebSocket para gerenciamento de eventos.

## Aviso Importante

**Esta nova versão introduz mudanças significativas. É crucial fazer backup dos seus dados antes de atualizar.**

## Tecnologias Utilizadas

- Python
- FastAPI (API Web)
- PostgreSQL (Banco de Dados)
- Grafana (Visualização de Dados)
- Docker (Containerização)
- NiceGUI (Frontend)
- WebSockets (Atualizações em Tempo Real)

## Contribuições

Se você aprecia este projeto e gostaria de contribuir, sinta-se à vontade para enviar pull requests ou relatar problemas. Qualquer contribuição é bem-vinda!

Para mais informações sobre instalação, configuração e uso desta ferramenta, consulte o wiki do projeto.
