import subprocess
import os
import sys

def run_alembic_command(command):
    try:
        # Use python -m alembic instead of direct alembic command
        python_executable = sys.executable
        modified_command = [python_executable, "-m", "alembic"] + command[1:]
        
        result = subprocess.run(
            modified_command,
            capture_output=True,
            text=True,
            check=True
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
    # Change directory to the root of the backendapi module
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../..")
    # Applique directement la migration existante
    run_alembic_command(["alembic", "upgrade", "head"])

if __name__ == "__main__":
    init_database()