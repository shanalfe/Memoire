# -*- coding: utf-8 -*-
import osmnx as ox
from geopy.distance import geodesic
import numpy as np

# Simule une position GPS (latitude, longitude) - a remplacer par GPS reel
current_pos = (45.354, 6.036)  # Exemple dans les Alpes

# Vitesse actuelle du vehicule (a connecter au ton GPS ou simulateur)
current_speed_kmh = 70

# Rayon de recherche autour du vehicule (en metres)
search_radius = 200

# Chargement du reseau routier autour de la position
G = ox.graph_from_point(current_pos, dist=search_radius, network_type='drive')

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
        recommended_speed = max(20, 80 - curvature * 200)

        if current_speed_kmh > recommended_speed:
            print("[ALERTE] Virage dangereux d\u00e9tect\u00e9 !")
            print(f"Vitesse actuelle : {current_speed_kmh} km/h")
            print(f"Vitesse conseill\u00e9e : {int(recommended_speed)} km/h")
        else:
            print("Virage d\u00e9tect\u00e9, vitesse correcte.")
        break