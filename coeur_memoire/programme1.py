# -*- coding: utf-8 -*-
import osmnx as ox
from geopy.distance import geodesic
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import math


# Exemple de simulation de positions GPS (latitude, longitude) pour le test
# sucession de virages 
position_actuelle = (48.385171, 2.563108)  
# ligne droite
#position_actuelle = (48.514114, 2.320894) 
#position_actuelle = (48.380441, 2.565690) 
# virage serre
#position_actuelle = (48.371103, 2.560765) 
# virage moyen
#position_actuelle = (48.358995, 2.534561)
# autoroute
#position_actuelle = (48.335448, 2.595849) 

# Vitesse actuelle du vehicule 
vitesse_vehicule = 90

# Rayon de recherche autour de la position_actuelle (en metres)
rayon_recherche = 1000

# Chargement du reseau routier 
G = ox.graph_from_point(position_actuelle, dist=rayon_recherche, network_type='all')

# Conversion
edges = ox.graph_to_gdfs(G, nodes=False)

# Calcul de la courbure
def compute_curvature(geometry):
    
    coords = list(geometry.coords)
  
    # controle des petits segments
    if geodesic(coords[0], coords[-1]).meters < 50:
       return 0 
   
    if len(coords) < 3:
       return 0
    
    mid = len(coords) // 2
    if mid - 1 < 0 or mid + 1 >= len(coords):
        return 0
    
    p1, p2, p3 = coords[mid-1], coords[mid], coords[mid+1]
    a = geodesic(p1, p2).meters
    b = geodesic(p2, p3).meters
    c = geodesic(p1, p3).meters
    if a + b == 0:
        return 0
    
    # formule de la courbure
    courbure = abs((a + b - c) / (a + b))
   
    # affichage
    print("Courbure calcul\u00e9e formule :", courbure)
    print("Position actuelle : ", position_actuelle)
    print("p1 :", p1)
    print("p2 :", p2)
    print("p3 :", p3)

    return courbure
    

# Trouver le segment le plus proche de la position actuelle
point_actuel = Point(position_actuelle[1], position_actuelle[0])  # (lon, lat)
edges["distance"] = edges.geometry.distance(point_actuel)
segment_proche = edges.loc[edges["distance"].idxmin()]

# Calcul de la courbure du segment
courbure = compute_curvature(segment_proche.geometry)

# evaluer la vitesse conseillee

#vitesse_recommandee = 60 * math.exp(-300 * courbure) + 20

# vitesse recommandee
def vitesse_recommandee(courbure):
    if courbure < 0.0005:
        return 80  # Ligne droite
    elif courbure < 0.002:
        return 60  # Leger virage
    else:
        return 30  # Virage serre
vitesse_conseillee = vitesse_recommandee(courbure)

# affichage des resultats
print("==== Analyse du segment actuel ====")
print(f"Courbure estim\u00e9e : {courbure:.4f}")
print(f"Vitesse actuelle : {vitesse_vehicule} km/h")
print(f"Vitesse conseill\u00e9e : {vitesse_conseillee} km/h")

if courbure < 0.0005:
    print("Ligne droite")
elif courbure < 0.002:
    print("Leger virage")
    if vitesse_vehicule > vitesse_conseillee:
        print("[ALERTE] Vous etes dans un leger virage, ajustez votre vitesse.")
    else:
        print("[INFO] Vitesse correcte dans le virage.")
else:
    print("Virage serre")
    if vitesse_vehicule > vitesse_conseillee:
        print("[ALERTE] Vous etes dans un virage serre, ralentissez !")
    else:
        print("[INFO] Vitesse adaptee au virage serre.")



#visualisation
edges.plot(figsize=(10, 10))
plt.scatter(*position_actuelle[::-1], color='red', label='Position actuelle')
plt.title("R\u00e9seau routier analys\u00e9")
plt.legend()
plt.show()