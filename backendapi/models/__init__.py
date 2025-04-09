import os
import importlib
import pkgutil

# Importer Base pour que les modèles puissent l'utiliser
from backendapi.helpers.base import Base  # noqa: F401

# Importer automatiquement tous les modules dans le package models
__all__ = []

# Chemin du répertoire des modèles
package_dir = os.path.dirname(os.path.abspath(__file__))

# Parcourir tous les modules dans le package
for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
    # Importer le module
    module = importlib.import_module(f"{__name__}.{module_name}")

    # Ajouter le nom du module à __all__
    __all__.append(module_name)

    # Ajouter tous les attributs du module au namespace du package
    for attribute_name in dir(module):
        # Filtrer les attributs privés et les imports
        if not attribute_name.startswith('_') and attribute_name not in globals():
            globals()[attribute_name] = getattr(module, attribute_name)