"""Trace les resultats ngspice et verifie que le montage fonctionne.

Entrees : resultats.txt (wrdata) et ngspice.log (mesures .meas)
Sorties : resultats.png, resultats.md ; code de sortie 1 si le montage ne fonctionne pas.
"""
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------- Donnees temporelles ----------
with open("resultats.txt") as f:
    header = f.readline().split()
data = np.loadtxt("resultats.txt", skiprows=1)
col = {name.lower(): data[:, i] for i, name in enumerate(header)}
t_ms = col["time"] * 1e3

# ---------- Mesures .meas ----------
mesures = {}
with open("ngspice.log") as f:
    for line in f:
        m = re.match(r"^\s*([a-z_]+)\s*=\s*([-+0-9.eE]+)", line)
        if m:
            mesures[m.group(1)] = float(m.group(2))

def get(name):
    return mesures.get(name, float("nan"))

# ---------- Graphe ----------
fig, ax = plt.subplots(4, 1, figsize=(10, 11), sharex=True)
ax[0].plot(t_ms, col["v(sig)"], color="#EF9F27")
ax[0].set_ylabel("SIG (V)")
ax[0].set_title("Commande GPIO : 0 V = Pluto allumé, 3,3 V = Pluto éteint")

ax[1].plot(t_ms, col["v(coll)"], label="nominal (seuil 1,5 V)", color="#639922")
ax[1].plot(t_ms, col["v(collw)"], "--", label="pire cas (seuil 2,0 V)", color="#3B6D11")
ax[1].set_ylabel("Grille IRLZ44N (V)")
ax[1].legend(loc="center right")

ax[2].plot(t_ms, col["vpluto_nom"], label="nominal", color="#E24B4A")
ax[2].plot(t_ms, col["vpluto_worst"], "--", label="pire cas", color="#A32D2D")
ax[2].axhline(4.5, color="gray", ls=":", lw=1)
ax[2].text(0.3, 4.55, "4,5 V (min. Pluto)", color="gray", fontsize=8)
ax[2].set_ylabel("Tension au Pluto (V)")
ax[2].legend(loc="center right")

ax[3].plot(t_ms, col["ipluto_nom"], color="#7F77DD")
ax[3].set_ylabel("Courant Pluto (A)")
ax[3].set_xlabel("Temps (ms)")

for a in ax:
    a.grid(alpha=0.3)
fig.suptitle("Simulation ngspice : 2N2222 + IRLZ44N, charge PlutoSDR 1 A", fontsize=13)
fig.tight_layout()
fig.savefig("resultats.png", dpi=130)

# ---------- Verdict ----------
checks = [
    ("Tension au Pluto allumé (nominal)", get("vpluto_on_nom"), "> 4,5 V", get("vpluto_on_nom") > 4.5),
    ("Tension au Pluto allumé (pire cas)", get("vpluto_on_worst"), "> 4,5 V", get("vpluto_on_worst") > 4.5),
    ("Tension au Pluto éteint (nominal)", get("vpluto_off_nom"), "< 0,5 V", get("vpluto_off_nom") < 0.5),
    ("Tension au Pluto éteint (pire cas)", get("vpluto_off_worst"), "< 0,5 V", get("vpluto_off_worst") < 0.5),
    ("Grille, Pluto allumé (nominal)", get("vgrille_on_nom"), "> 4 V", get("vgrille_on_nom") > 4.0),
    ("Grille, Pluto éteint (nominal)", get("vgrille_off_nom"), "< 0,5 V", get("vgrille_off_nom") < 0.5),
    ("Chute drain-source, allumé (nominal)", get("vds_on_nom"), "< 0,1 V", get("vds_on_nom") < 0.1),
    ("Chute drain-source, allumé (pire cas)", get("vds_on_worst"), "< 0,1 V", get("vds_on_worst") < 0.1),
]
ok = all(c[3] for c in checks)

lines = ["## Résultat de la simulation ngspice", "",
         f"**Verdict : {'le montage fonctionne ✅' if ok else 'le montage NE fonctionne PAS ❌'}**", "",
         "| Mesure | Valeur | Attendu | OK |", "|---|---|---|---|"]
for name, val, attendu, good in checks:
    lines.append(f"| {name} | {val:.3f} V | {attendu} | {'✅' if good else '❌'} |")
lines += ["",
          f"Courant moyen du Pluto allumé : {abs(get('ipluto_on_nom')):.3f} A ; "
          f"pic à l'allumage : {abs(get('ipic_nom')):.2f} A",
          "", "Courbes : voir l'artefact `resultats-simulation` (resultats.png)."]
md = "\n".join(lines)
with open("resultats.md", "w") as f:
    f.write(md + "\n")
print(md)
sys.exit(0 if ok else 1)
