import pandas as pd
from datetime import datetime, timedelta
import time
from backendapi.helpers.base import engine


def detect_abnormal_cdr_count():
# Charger les données historiques de CDR
    cdr_data = pd.read_sql_query("SELECT * FROM call_data_records", engine)

# Calculer la moyenne et l'écart-type du nombre de CDR par jour
    daily_cdr_counts = cdr_data.groupby(pd.Grouper(key='time_start', freq='D')).size()
    mean_cdr_count = daily_cdr_counts.mean()
    std_cdr_count = daily_cdr_counts.std()

# Définir le seuil pour les pics anormaux (par exemple, 3 écarts-types au-dessus de la moyenne)
    threshold = mean_cdr_count + 3 * std_cdr_count

# Surveiller les nouvelles données de CDR
    while True:
    # Récupérer les CDR intégrés au cours des dernières 24 heures
        last_24h = datetime.now() - timedelta(days=1)
        recent_cdr_count = cdr_data[cdr_data['time_start'] >= last_24h].shape[0]

    # Détecter les pics anormaux
        if recent_cdr_count > threshold:
            print(f"Pic anormal détecté : {recent_cdr_count} CDR intégrés au cours des dernières 24 heures.")
        # Effectuer d'autres actions (envoyer une alerte, etc.)

    # Attendre avant la prochaine vérification (par exemple, 1 heure)
        time.sleep(3600)