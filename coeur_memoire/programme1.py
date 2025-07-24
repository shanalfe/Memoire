# -*- coding: utf-8 -*-
import osmnx as ox
from geopy.distance import geodesic
import numpy as np

# Simule une position GPS (latitude, longitude) - a remplacer par GPS reel
position_actuelle = (48.385171, 2.563108)  

# Vitesse actuelle du vehicule (a connecter au ton GPS ou simulateur)
vitesse_vehicule = 55

# Rayon de recherche autour du vehicule (en metres)
rayon_recherche = 1000

# Chargement du reseau routier autour de la position
G = ox.graph_from_point(position_actuelle, dist=rayon_recherche, network_type='all')

# Convertir en geometrie de routes (lignes)
edges = ox.graph_to_gdfs(G, nodes=False)

# Detecter les virages : on calcule la "courbure" des lignes
def compute_curvature(geometry):
    coords = list(geometry.coords)
    if len(coords) < 3:
        return 0
    p1, p2, p3 = coords[0], coords[len(coords)//2], coords[-1]
    a = geodesic(p1, p2).meters
    b = geodesic(p2, p3).meters
    c = geodesic(p1, p3).meters
    if a + b == 0:
        return 0
    return abs((a + b - c) / (a + b))  # mesure de la courbure

# Plus c'est court par rapport a a + b, plus la ligne est courbee. C'est comme mesurer a quel point la trajectoire s'ecarte d'une ligne droite.

# Parcours des segments pour trouver un virage serre
for _, row in edges.iterrows():
    curvature = compute_curvature(row.geometry)
    if curvature > 0.1:  # seuil de virage (a ajuster)
        # Estimer la vitesse recommandee (exemple simpliste)
        vitesse_recommandee = max(20, 80 - curvature * 200)

        if vitesse_vehicule > vitesse_recommandee:
            print("[ALERTE] Virage dangereux d\u00e9tect\u00e9 !")
            print(f"Vitesse actuelle : {vitesse_vehicule} km/h")
            print(f"Vitesse conseill\u00e9e : {int(vitesse_recommandee)} km/h")
        else:
            print("Virage d\u00e9tect\u00e9, vitesse correcte.")
        break