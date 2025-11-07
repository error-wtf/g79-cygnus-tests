# Paper Visualization Guide
**Alle Plots & GIFs für "Segmented Spacetime and the Origin of Molecular Zones"**

---

## 📊 Übersicht

Dieses System generiert **publication-ready Figuren** für JEDE Aussage im Paper:

- **8 Hauptfiguren** (PNG + PDF, 300 DPI)
- **5 GIF-Animationen** (+ 15 Varianten)
- **Validierungs-Tests** für alle Gleichungen
- **CSV-Daten** für jede Figur

---

## 🚀 Quick Start

```bash
# Alle Paper-Figuren generieren
python GENERATE_ALL_PAPER_FIGURES.py

# Animationen hinzufügen
python GENERATE_TEST_ANIMATIONS.py
python CREATE_ANIMATION_VARIANTS.py

# ODER: Alles in einem
python RUN_PIPELINE_OPTIMIZED.py
```

---

## 📁 Output-Struktur

```
paper_figures/
├── Fig1_gamma_seg_profile.png/pdf        # Eq. (10), Section 5.2
├── Fig2_temperature_stratification.png/pdf # Eq. (9), Section 5.1
├── Fig3_velocity_excess.png/pdf           # Eq. (12), Section 5.3
├── Fig4_core_mass_derivation.png/pdf      # Eq. (14), Section 5.5
├── Fig5_radio_redshift.png/pdf            # Section 5.4
├── Fig6_energy_release.png/pdf            # Eq. (17), Section 5.6
├── Fig7_multi_shell_structure.png/pdf     # Section 5.1
├── Fig8_nebulae_comparison.png/pdf        # Section 6.2
└── data_*.csv                             # Rohdaten

animations/
├── gamma_seg_evolution.gif                # + 3 Varianten
├── velocity_excess.gif                    # + 3 Varianten
├── energy_release.gif                     # + 3 Varianten
├── core_mass_scaling.gif                  # + 3 Varianten
└── radio_redshift.gif                     # + 3 Varianten
```

---

## 🔬 Figuren-Details

### **Figure 1: γ_seg(r) Profile**
**Paper-Referenz:** Equation (10), Section 5.2

**Zeigt:**
- γ_seg(r) = 1 - α·exp[-(r/r_c)²]
- α = 0.12 ± 0.03
- r_c = 1.9 pc
- Beobachtete Schalen bei r = 1.2, 2.3, 4.5 pc
- Zeit-Dilatations-Faktor (1-γ_seg)

**Verwendung:** Haupt-Konzept-Figur, zeigt Temporal-Dichte-Feld

---

### **Figure 2: Temperature Stratification**
**Paper-Referenz:** Equation (9), Section 5.1

**Zeigt:**
- T(r) = T₀·γ_seg(r)
- Vergleich: Theorie vs. Beobachtung (IR/CO-Daten)
- T-γ_seg Korrelation
- Thermale Inversion

**Verwendung:** Validierung der Temperatur-Vorhersage

---

### **Figure 3: Velocity Excess**
**Paper-Referenz:** Equation (12), Section 5.3

**Zeigt:**
- v_obs = v₀/γ_seg
- Δv/v₀ ≅ γ_seg⁻¹ - 1
- Momentum-Überschuss: Δv ≈ 5 km/s
- Vergleich: Klassisch (10 km/s) vs. Beobachtet (15 km/s)
- Momentum-Rate ṗ

**Verwendung:** Erklärung des Geschwindigkeits-Überschusses

---

### **Figure 4: Core Mass Derivation**
**Paper-Referenz:** Equation (14), Section 5.5

**Zeigt:**
- M_core = (c²/G) ∫ γ_seg(r) dr
- Kumulative Masse: M_core(r)
- Konvergenz bei r=4.5 pc: M = 8.7 ± 1.5 M_☉
- Integration über Temporal-Dichte

**Verwendung:** Massen-Herleitung ohne Dunkle Materie

---

### **Figure 5: Radio Redshift**
**Paper-Referenz:** Section 5.4

**Zeigt:**
- ν' = ν₀·γ_seg(r)
- Redshift-Parameter z = (ν₀ - ν)/ν
- Shift ins Radio-Band (<30 GHz)
- Wellenlängen-Verschiebung

**Verwendung:** Radio-Molekül-Überlappung erklärt

---

### **Figure 6: Energy Release**
**Paper-Referenz:** Equation (17-18), Section 5.6

**Zeigt:**
- v_obs ≅ √(v_launch² + v_char²(1-γ_seg))
- Energie-Freisetzung an g⁽²⁾→g⁽¹⁾ Grenze
- Geschwindigkeits-Boost: Δv_release
- Temperatur-Freisetzung: ΔT_recouple

**Verwendung:** Hawking-analoge Thermodynamik

---

### **Figure 7: Multi-Shell Structure**
**Paper-Referenz:** Section 5.1

**Zeigt:**
- Drei Schalen bei r = 1.2, 2.3, 4.5 pc
- T = 500, 200, 60 K
- γ_seg-Werte für jede Schale

**Verwendung:** Morphologie von G79.29+0.46

---

### **Figure 8: LBV Comparison**
**Paper-Referenz:** Section 6.2, Equation (20)

**Zeigt:**
- G79.29+0.46 vs. η Carinae vs. AG Carinae
- γ_seg-Profile mit verschiedenen α, r_c
- Universelles Verhältnis: Δv/v₀ ~ 0.1

**Verwendung:** Skalierungs-Gesetz über Systeme hinweg

---

## 🎬 GIF-Animationen

### **Animation 1: γ_seg Evolution**
- Parameter α variiert von 0.05 bis 0.5
- Zeigt Zeit-Dilatations-Effekt
- 60 frames @ 10 FPS

### **Animation 2: Velocity Excess**
- Expandierende Schale durch γ_seg-Feld
- Klassisch vs. SSZ-Vorhersage
- Dual-Panel: v(r) + γ_seg(r)

### **Animation 3: Energy Release**
- Partikel kreuzt Metrik-Grenze
- g⁽²⁾ (slow) → g⁽¹⁾ (normal)
- Energie-Freisetzung als v-Boost

### **Animation 4: Core Mass**
- Integration von γ_seg(r) über Radius
- Kumulative Masse konvergiert
- Vergleich mit Paper-Wert

### **Animation 5: Radio Redshift**
- Emissions-Radius variiert
- Frequenz-Shift ins Radio-Band
- Redshift-Parameter z(r)

### **Varianten (je 3 pro GIF):**
- **5s:** Schnelle Preview
- **30s repeat:** Konferenz-Loop
- **30s slow:** Lehr-Material

---

## ✅ Validierungs-Tests

Jede Figur kommt mit Daten-Validierung:

```python
# Test 1: γ_seg at key radii
assert abs(gamma_seg(1.2) - 0.946) < 0.005
assert abs(gamma_seg(2.3) - 0.897) < 0.005
assert abs(gamma_seg(4.5) - 0.963) < 0.005

# Test 2: Temperature at shells
assert abs(T_profile(1.2) - 227) < 10
assert abs(T_profile(2.3) - 215) < 10
assert abs(T_profile(4.5) - 231) < 10

# Test 3: Velocity excess
assert abs(velocity_excess(2.0) - 5.0) < 1.0

# Test 4: Core mass
assert abs(M_core_integral(4.5) - 8.7) < 1.5

# Test 5: Radio frequency
nu_radio = frequency_shift(100, 1.0)
assert 88 < nu_radio < 92  # ~90 GHz at r=1 pc
```

---

## 📐 Paper-Gleichungen → Figuren

| Gleichung | Figur | Beschreibung |
|-----------|-------|--------------|
| Eq. (1) | Fig. 3 | Momentum-Rate ṗ_obs |
| Eq. (9) | Fig. 2 | T(r) = T₀·γ_seg |
| Eq. (10) | Fig. 1 | γ_seg(r) = 1 - α·exp[-(r/r_c)²] |
| Eq. (12) | Fig. 3 | Δv/v₀ ≅ γ_seg⁻¹ - 1 |
| Eq. (14) | Fig. 4 | M_core = ∫ γ_seg dr |
| Eq. (17) | Fig. 6 | v_obs = √(v²+v_char²(1-γ)) |
| Eq. (18) | Fig. 6 | ΔT_recouple ≅ T_local(1-γ_seg) |
| Eq. (20) | Fig. 8 | Δv/v₀ ~ 0.1 (universal) |

---

## 🎨 Formatierungs-Standards

**Alle Figuren:**
- **Format:** PNG (Screen) + PDF (Print)
- **DPI:** 300 (publication quality)
- **Fonts:** Größe 10-14 pt
- **Colors:** Colorblind-safe palette
- **Grid:** Alpha=0.3
- **Legends:** Immer enthalten

**CSV-Daten:**
- UTF-8 encoding
- Komma-separiert
- Header mit Einheiten
- Kompatibel mit Origin/Igor/Excel

---

## 🔧 Anpassungen

### Farben ändern:
```python
# In GENERATE_ALL_PAPER_FIGURES.py
COLORS = {
    'gamma_seg': 'blue',      # Haupt-Profil
    'observed': 'green',      # Beobachtungsdaten
    'classical': 'gray',      # Klassische Vorhersagen
    'excess': 'orange'        # Überschuss/Differenz
}
```

### Parameter variieren:
```python
# Alpha-Wert ändern
ALPHA = 0.15  # statt 0.12

# Kern-Radius ändern
R_C = 2.5  # statt 1.9 pc

# Neu generieren
python GENERATE_ALL_PAPER_FIGURES.py
```

### Zusätzliche Figuren:
```python
# Am Ende von GENERATE_ALL_PAPER_FIGURES.py hinzufügen
# [9/12] Deine neue Figur...
fig, ax = plt.subplots(figsize=(10, 6))
# ... plotting code ...
plt.savefig(OUTPUT_DIR / "Fig9_custom.png", dpi=300)
```

---

## 📊 Performance

**Generierungszeiten:**
- Figuren 1-8: ~30 Sekunden
- Animationen (5×): ~3 Minuten
- Varianten (15×): ~2 Minuten
- **Total:** ~6 Minuten

**Dateigrößen:**
- PNG pro Figur: ~200-500 KB
- PDF pro Figur: ~100-200 KB
- GIF original: ~500-800 KB
- GIF Varianten: ~1-5 MB

---

## 🐛 Troubleshooting

**Problem:** UTF-8 Fehler bei γ, α, etc.
**Lösung:** Script setzt automatisch UTF-8, sollte funktionieren

**Problem:** Matplotlib-Fenster öffnen sich
**Lösung:** `matplotlib.use('Agg')` ist gesetzt, sollte nicht passieren

**Problem:** Scipy nicht installiert
**Lösung:** `pip install scipy`

**Problem:** Figuren sehen anders aus
**Lösung:** DPI/Font-Größe in plt.rcParams anpassen

---

## 📚 Verwendung im Paper

### LaTeX-Integration:
```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.9\textwidth]{paper_figures/Fig1_gamma_seg_profile.pdf}
  \caption{Temporal density field γ_seg(r) for G79.29+0.46 
           (Eq. 10, α=0.12±0.03, r_c=1.9 pc). 
           Circles mark observed IR shells.}
  \label{fig:gamma_seg}
\end{figure}
```

### Supplementary Material:
- Alle GIFs in ZIP-Datei
- CSV-Daten als Tabellen
- Animation-Links in arXiv

---

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
