import csv
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

# CSV laden
with open("Spotify.csv", "r", encoding="utf-8") as csv_file:
    csv_data = csv.reader(csv_file)
    data = list(csv_data)
    data.pop(0)  # Header entfernen

dance = []
energy = []
label = []
acousticness = []
instrumentalness = []

for line in data:
    dance.append(float(line[2].replace('%','')))
    energy.append(float(line[4].replace('%','')))
    acousticness.append(float(line[1]))
    instrumentalness.append(float(line[5]))
    # Label: Beliebtheitswert (z.B. >80%)
    if float(line[14].replace('%','')) > 80:
        label.append(1)
    else:
        label.append(0)

beispiel = (80, 70)

'''
colors = ['blue' if value == 1 else 'red' for value in label]
plt.scatter(dance, energy, c=colors, s=20)
plt.scatter(beispiel[0], beispiel[1], c="green", s=50, marker="x")
plt.xlabel("Danceability (%)")
plt.ylabel("Energy (%)")
plt.title("KNN Spotify Classification")
plt.show()

plt.figure()
colors2 = ['blue' if value == 1 else 'red' for value in label]
plt.scatter(acousticness, instrumentalness, c=colors2, s=20)
plt.xlabel("Acousticness")
plt.ylabel("Instrumentalness")
plt.title("Spotify: Acousticness vs Instrumentalness")
plt.show()
'''

dance_input = float(input("Input danceability: "))
energy_input = float(input("Input energy: "))

X = list(zip(dance, energy))  # Feature-Paare (Danceability, Energy)
y = label

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X, y)

prediction = knn.predict([(dance_input, energy_input)])

if prediction[0] == 1:
    print("🎵 Der Song wird wahrscheinlich BELIEBT (>80%).")
else:
    print("🎶 Der Song wird wahrscheinlich weniger beliebt (≤80%).")

# Scatterplot der Trainingsdaten mit farbigen Klassen
colors = ['blue' if value == 1 else 'red' for value in label]
plt.scatter(dance, energy, c=colors, s=20, alpha=0.6, label='Trainingsdaten')
# User-Punkt mit großem X markieren
plt.scatter(dance_input, energy_input, c="green", s=300, marker="X", 
            linewidths=3, edgecolors='black', label='User-Punkt', zorder=10)
plt.xlabel("Danceability (%)")
plt.ylabel("Energy (%)")
plt.title("KNN Spotify Classification - Trainingsdaten")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# ============================================================================
# Aufgabe 6: Vergleich verschiedener k-Werte
# ============================================================================
print("\n" + "="*70)
print("AUFGABE 6: Vergleich verschiedener k-Werte")
print("="*70)

# Verschiedene k-Werte testen
k_values = [1, 3, 5, 7, 10, 15, 20, 25, 30]
accuracies = []
std_devs = []

print("\nK-Wert | Durchschnittliche Genauigkeit | Standardabweichung")
print("-" * 70)

for k in k_values:
    knn_temp = KNeighborsClassifier(n_neighbors=k)
    # 5-fold Cross-Validation
    scores = cross_val_score(knn_temp, X, y, cv=5, scoring='accuracy')
    mean_score = scores.mean()
    std_score = scores.std()
    accuracies.append(mean_score)
    std_devs.append(std_score)
    print(f"  k={k:2d}  |        {mean_score:.4f}              |      {std_score:.4f}")

# Bestes k finden
best_k_idx = np.argmax(accuracies)
best_k = k_values[best_k_idx]
best_accuracy = accuracies[best_k_idx]

print(f"\n🏆 Bestes k: {best_k} mit Genauigkeit: {best_accuracy:.4f}")

# Visualisierung der k-Werte vs. Genauigkeit
plt.figure(figsize=(10, 6))
plt.errorbar(k_values, accuracies, yerr=std_devs, marker='o', linestyle='-', 
             capsize=5, capthick=2, linewidth=2, markersize=8)
plt.axvline(x=best_k, color='red', linestyle='--', alpha=0.7, 
            label=f'Bestes k = {best_k}')
plt.xlabel('k (Anzahl der Nachbarn)', fontsize=12)
plt.ylabel('Genauigkeit (Accuracy)', fontsize=12)
plt.title('KNN: Genauigkeit in Abhängigkeit von k\n(5-fold Cross-Validation)', 
          fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Vorhersage mit verschiedenen k-Werten für den User-Punkt
print("\n" + "-"*70)
print("Vorhersage für User-Punkt (Danceability={}, Energy={}) mit verschiedenen k:".format(
    dance_input, energy_input))
print("-"*70)
for k in [1, 3, 5, 10, 20]:
    knn_test = KNeighborsClassifier(n_neighbors=k)
    knn_test.fit(X, y)
    pred = knn_test.predict([(dance_input, energy_input)])
    proba = knn_test.predict_proba([(dance_input, energy_input)])[0]
    result = "BELIEBT (>80%)" if pred[0] == 1 else "weniger beliebt (≤80%)"
    print(f"k={k:2d}: {result:25s} (Wahrscheinlichkeit: {max(proba):.2%})")

print("\n" + "="*70)
print("ANALYSE:")
print("="*70)
print("""
Ein größeres k führt nicht automatisch zu besseren Vorhersagen. Die optimale 
k-Wahl hängt von mehreren Faktoren ab:

1. KLEINES k (z.B. k=1):
   - Sehr empfindlich gegenüber Rauschen und Ausreißern
   - Kann zu Overfitting führen
   - Gute Anpassung an lokale Muster, aber instabil

2. MITTLERES k (z.B. k=5-15):
   - Gute Balance zwischen Bias und Varianz
   - Robuster gegenüber Ausreißern
   - Oft die beste Wahl für die meisten Datensätze

3. GROSSES k (z.B. k>20):
   - Glättet die Entscheidungsgrenzen
   - Kann zu Underfitting führen
   - Verliert lokale Muster

Die optimale k-Wahl sollte durch Cross-Validation bestimmt werden, wie oben 
dargestellt. Ein zu großes k kann die Vorhersagequalität verschlechtern, da 
die Entscheidung zu stark geglättet wird.
""")

# ============================================================================
# Aufgabe 7: Analyse der Modell-Eignung und Kausalität vs. Korrelation
# ============================================================================
print("\n" + "="*70)
print("AUFGABE 7: Modell-Eignung und Kausalität vs. Korrelation")
print("="*70)
print("""
Für eine detaillierte Analyse zur Eignung des Modells und der Diskussion 
über Kausalität vs. Korrelation siehe die Datei:
    analyse_kausalitaet_korrelation.md

ZUSAMMENFASSUNG:
- Das Modell findet KORRELATIONEN zwischen Danceability/Energy und Popularität
- Dies bedeutet NICHT, dass hohe Danceability/Energy Popularität VERURSACHT
- Das Modell ist begrenzt geeignet, da viele wichtige Faktoren fehlen:
  * Marketing und Promotion
  * Künstler-Bekanntheit
  * Genre-Trends
  * Zeitliche Faktoren
  * Externe Einflüsse (Social Media, Playlists, etc.)

WICHTIG: Korrelation ≠ Kausalität
- Das Modell kann Muster erkennen und nutzen
- Aber es erklärt nicht die URSACHEN von Popularität
- Vorhersagen sind nur so gut wie die Stabilität der Muster
""")

