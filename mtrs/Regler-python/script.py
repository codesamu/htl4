# ============================================================
# Reglerauslegung CHR mit Vergleich:
# Strecke ohne Regler vs. mit PID-Regler
#
# pip install numpy matplotlib control scipy
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import control as ctl

# ------------------------------------------------------------
# 1 Strecke
# KNR=3 -> K=0.04*3=0.12
# G(s)=0.12 /(4s²+2s+1)
# ------------------------------------------------------------

K=0.12

G=ctl.TransferFunction(
    [K],
    [4,2,1]
)

# ------------------------------------------------------------
# 2 PT1+Totzeit Approximation für CHR
# ------------------------------------------------------------

Ks=0.12
T=2.0
L=0.5

# ------------------------------------------------------------
# CHR Regeln
# ------------------------------------------------------------

def chr_pid_0():
    Kp=0.95*T/(Ks*L)
    Ti=2.4*L
    Td=0.42*L
    return Kp,Ti,Td

def chr_pid_20():
    Kp=1.2*T/(Ks*L)
    Ti=2.0*L
    Td=0.42*L
    return Kp,Ti,Td

Kp0,Ti0,Td0=chr_pid_0()

# ------------------------------------------------------------
# PID
# ------------------------------------------------------------

def PID(Kp,Ti,Td):
    return ctl.TransferFunction(
        [Kp*Td*Ti,Kp*Ti,Kp],
        [Ti,0]
    )

def closed_loop(Kp,Ti,Td):
    C=PID(Kp,Ti,Td)
    return ctl.feedback(C*G)

# ------------------------------------------------------------
# Simulation
# ------------------------------------------------------------

t=np.linspace(0,40,1000)

# Ungeregelte Strecke
t_open,y_open=ctl.step_response(G,t)

# Geregelt
sys=closed_loop(Kp0,Ti0,Td0)
t_closed,y_closed=ctl.step_response(sys,t)

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig,ax=plt.subplots(figsize=(11,7))
plt.subplots_adjust(left=0.25,bottom=0.35)

# MIT PID
[line_pid]=ax.plot(
    t_closed,
    y_closed,
    linewidth=2,
    label='Mit PID-Regler'
)

# OHNE PID
[line_open]=ax.plot(
    t_open,
    y_open,
    '--',
    linewidth=2,
    label='Ohne Regler'
)

ax.axhline(1,color='red',linestyle='--',label='Sollwert')

ax.set_title("Vergleich: Strecke mit und ohne PID-Regler")
ax.set_xlabel("Zeit [s]")
ax.set_ylabel("Antwort")
ax.grid()
ax.legend()

# ------------------------------------------------------------
# Slider
# ------------------------------------------------------------

axcolor='lightgoldenrodyellow'

ax_kp=plt.axes([0.25,0.22,0.65,0.03],facecolor=axcolor)
ax_ti=plt.axes([0.25,0.17,0.65,0.03],facecolor=axcolor)
ax_td=plt.axes([0.25,0.12,0.65,0.03],facecolor=axcolor)

sKp=Slider(ax_kp,'Kp',0.1,80,valinit=Kp0)
sTi=Slider(ax_ti,'Ti',0.1,20,valinit=Ti0)
sTd=Slider(ax_td,'Td',0.01,5,valinit=Td0)

# ------------------------------------------------------------
# CHR Auswahl
# ------------------------------------------------------------

rax=plt.axes([0.03,0.55,0.15,0.15],facecolor=axcolor)

radio=RadioButtons(
    rax,
    ('CHR 0%','CHR 20%')
)

# ------------------------------------------------------------
# Update Funktion
# ------------------------------------------------------------

def update(val):

    kp=sKp.val
    ti=sTi.val
    td=sTd.val

    sys=closed_loop(kp,ti,td)

    t,y=ctl.step_response(
        sys,
        np.linspace(0,40,1000)
    )

    line_pid.set_ydata(y)

    fig.canvas.draw_idle()

sKp.on_changed(update)
sTi.on_changed(update)
sTd.on_changed(update)

# ------------------------------------------------------------
# Presets
# ------------------------------------------------------------

def preset(label):

    if label=="CHR 0%":
        kp,ti,td=chr_pid_0()

    if label=="CHR 20%":
        kp,ti,td=chr_pid_20()

    sKp.set_val(kp)
    sTi.set_val(ti)
    sTd.set_val(td)

radio.on_clicked(preset)

plt.show()

# ------------------------------------------------------------
# Werte ausgeben
# ------------------------------------------------------------

print("CHR 0% Überschwingen")
print("Kp =",round(Kp0,3))
print("Ti =",round(Ti0,3))
print("Td =",round(Td0,3))

kp20,ti20,td20=chr_pid_20()

print("\nCHR 20% Überschwingen")
print("Kp =",round(kp20,3))
print("Ti =",round(ti20,3))
print("Td =",round(td20,3))
