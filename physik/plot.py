import matplotlib.pyplot as plt

volt = [2.7, 2.3, 1.8, 1.6, 1.4, 1.15]
wavelength_nm = [400, 465, 575, 632, 650, 940]

q = 1.602e-19
c = 3e8
h_ref = 6.6e-34

# Energie berechnen
energy = [U * q for U in volt]

# Frequenz berechnen
freq = [c / (wl * 1e-9) for wl in wavelength_nm]

# h Werte
h_values = [E / f for E, f in zip(energy, freq)]

# Mittelwert
h_mean = sum(h_values) / len(h_values)

# Abweichung
deviation = abs(h_mean - h_ref) / h_ref * 100

print("h =", h_mean, "J·s")
print("Abweichung =", deviation, "%")

# ---------------- PLOT ----------------
plt.figure(figsize=(7,5))

plt.scatter(freq, energy, label="Messwerte")
plt.plot(freq, energy)

plt.xlabel("Frequenz f (Hz)")
plt.ylabel("Energie E = q·U (J)")
plt.title("LED: Energie vs Frequenz (E = h·f)")
plt.grid(True)
plt.legend()

plt.show()
