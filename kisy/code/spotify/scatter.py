import csv
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier

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

