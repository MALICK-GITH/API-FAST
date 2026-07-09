"""
Script pour copier le nouveau fichier de données
==============================================

Author: SOLITAIRE HACK
Version: 1.0
"""

import shutil
import os

source = r"c:\Users\HP\Downloads\Telegram Desktop\finished_matches_clean.csv"
destination = r"c:\Users\HP\Downloads\ONE BY ONE API FIFA PRED\finished_matches_clean.csv"

try:
    shutil.copy(source, destination)
    print(f"✅ Fichier copié avec succès de {source} vers {destination}")
    
    # Vérifier la taille
    size = os.path.getsize(destination)
    print(f"Taille du fichier: {size / (1024*1024):.2f} MB")
    
    # Compter les lignes
    with open(destination, 'r', encoding='utf-8') as f:
        lines = sum(1 for _ in f)
    print(f"Nombre de lignes: {lines}")
    
except Exception as e:
    print(f"❌ Erreur lors de la copie: {e}")
