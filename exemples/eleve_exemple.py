"""
Exemple de code élève — Table de multiplication
Ce fichier montre le format attendu pour le concept "Boucle for"
"""

n = int(input("Table de : "))
total = 0

for i in range(1, 11):
    res = n * i
    print(n, "x", i, "=", res)
    total += res

print("Somme =", total)
