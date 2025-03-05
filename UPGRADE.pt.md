# Instruções de Atualização

## Visão Geral

Este documento explica o propósito dos scripts de atualização e como usá-los com base no seu sistema operacional. Os scripts de atualização são projetados para ajudá-lo a atualizar com segurança sua aplicação 3CX CDR Server, realizando as seguintes tarefas:

1. Fazer backup do banco de dados.
2. Detectar e mover arquivos renomeados.
3. Redefinir a branch master para a versão mais recente.
4. Limpar arquivos obsoletos.
5. Reconstruir o ambiente.

## Aviso Importante

**Esta nova versão introduz mudanças significativas. É crucial fazer backup dos seus dados antes de atualizar.**

## Scripts de Atualização

### Linux / macOS

Para usuários de Linux e macOS, use o script `update.sh`.

#### Uso

1. Abra um terminal.
2. Navegue até o diretório do projeto.
3. Torne o script executável:
    ```sh
    chmod +x update.sh
    ```
4. Execute o seguinte comando:
    ```sh
    ./update.sh
    ```

### Windows (PowerShell)

Para usuários de Windows usando PowerShell, use o script `update.ps1`.

#### Uso

1. Abra o PowerShell como administrador.
2. Navegue até o diretório do projeto.
3. Execute o seguinte comando:
    ```powershell
    ./update.ps1
    ```

### Windows (Batch)

Para usuários de Windows usando o Prompt de Comando, use o script `update.bat`.

#### Uso

1. Abra o Prompt de Comando como administrador.
2. Navegue até o diretório do projeto.
3. Execute o seguinte comando:
    ```bat
    update.bat
    ```

## Etapas Detalhadas

### 1. Fazer Backup do Banco de Dados

Os scripts criarão um backup do seu banco de dados PostgreSQL usando o comando `pg_dump`. O arquivo de backup será salvo como `backup.sql` no diretório do projeto.

### 2. Detectar e Mover Arquivos Renomeados

Os scripts detectarão quaisquer arquivos renomeados usando `git diff` e os moverão para seus novos locais.

### 3. Redefinir a Branch Master

Os scripts redefinirão a branch master para a versão mais recente do repositório remoto usando `git fetch`, `git checkout` e `git reset`.

### 4. Limpar Arquivos Obsoletos

Os scripts limparão quaisquer arquivos obsoletos usando `git clean`.

### 5. Reconstruir o Ambiente

Os scripts reconstruirão o ambiente Docker usando `docker-compose down` e `docker-compose up -d --build`.

## Conclusão

Seguindo estas instruções, você pode atualizar com segurança sua aplicação 3CX CDR Server para a versão mais recente. Se você encontrar algum problema, consulte o wiki do projeto ou crie uma issue no [GitHub](https://github.com/dorel14/3CX-Cdr-Tcp-Server/issues).
