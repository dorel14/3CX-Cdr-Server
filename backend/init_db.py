import subprocess
from sqlalchemy import inspect
from sqlalchemy import create_engine
import os
import sys
from backendapi.helpers.base import Base

def check_database_exists():
    dbUser = os.environ.get('POSTGRES_USER')
    dbPassword = os.environ.get('POSTGRES_PASSWORD')
    dbServer = os.environ.get('POSTGRES_SERVER')
    dbPort = os.environ.get('POSTGRES_PORT')
    dbName = os.environ.get('POSTGRES_DB')
    dburl = f'postgresql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}'
    
    engine = create_engine(dburl)
    inspector = inspect(engine)
    
    # Récupération automatique des tables depuis les modèles
    required_tables = [table.name for table in Base.metadata.tables.values()]
    existing_tables = inspector.get_table_names()
    
    return all(table in existing_tables for table in required_tables)

def run_alembic_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # Lève une exception si la commande échoue
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande: {e}", file=sys.stderr)
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        raise

def init_database():
    print("Initialisation de la base de données...")
    # Applique directement la migration existante
    run_alembic_command(["alembic", "upgrade", "head"])
if __name__ == "__main__":
    init_database()
