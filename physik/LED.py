volt = [2.7, 2.3, 1.8, 1.6, 1.4, 1.15]
wavelength_nm = [400, 465, 575, 632, 650, 940]

q = 1.602e-19
c = 3e8
h_ref = 6.6e-34

h_values = []

for U, wl_nm in zip(volt, wavelength_nm):
    E = U * q
    wl = wl_nm * 1e-9
    h = (E * wl) / c
    h_values.append(h)

h_mean = sum(h_values) / len(h_values)

deviation = abs(h_mean - h_ref) / h_ref * 100

print("h =", h_mean, "J·s")
print("Abweichung =", deviation, "%")
