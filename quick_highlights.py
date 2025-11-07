#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os, sys

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

Path('publication_highlights').mkdir(exist_ok=True)

ALPHA, R_C = 0.12, 1.9
r = np.linspace(0.1, 5, 500)
gamma = lambda r: 1 - ALPHA * np.exp(-(r/R_C)**2)

print("Generiere 3 Publication Highlights...")

# Highlight 1
fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2,figsize=(14,10))
ax1.plot(r, gamma(r), 'b-', lw=3)
ax1.set_title('gamma_seg(r) - Die Messlatte', fontweight='bold', fontsize=14)
ax1.set_ylabel('gamma_seg'); ax1.grid(True, alpha=0.3)

ax2.plot(r, 240*gamma(r), 'r-', lw=3)
ax2.set_title('Temperatur: T = T0*gamma_seg', fontweight='bold')
ax2.set_ylabel('T [K]'); ax2.grid(True, alpha=0.3)

ax3.plot(r, 10*(1/gamma(r)-1), 'g-', lw=3)
ax3.axhline(y=5, color='orange', linestyle='--', lw=2)
ax3.set_title('Geschwindigkeit: Deltav proportional gamma_seg^-1-1', fontweight='bold')
ax3.set_ylabel('Deltav [km/s]'); ax3.grid(True, alpha=0.3)

ax4.plot(r, 100*gamma(r), 'purple', lw=3)
ax4.axhspan(0,30,alpha=0.3,color='orange')
ax4.set_title('Radio: nu_obs = nu*gamma_seg', fontweight='bold')
ax4.set_ylabel('nu [GHz]'); ax4.grid(True, alpha=0.3)

plt.suptitle('HIGHLIGHT 1: gamma_seg(r) verbindet ALLES', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('publication_highlights/Highlight1_gamma_seg.png', dpi=300, bbox_inches='tight')
plt.close()
print("OK Highlight 1")

# Highlight 2
fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2,figsize=(14,10))
ax1.bar([0,1,2],[500,200,60],color=['red','orange','blue'],alpha=0.7, edgecolor='black', lw=2)
ax1.set_title('Temperatur-Zonen', fontweight='bold'); ax1.set_ylabel('T [K]')
ax1.set_xticks([0,1,2]); ax1.set_xticklabels(['1.2 pc','2.3 pc','4.5 pc'])

ax2.bar([0,1,2],[10,14,15],color=['blue','green','red'],alpha=0.7, edgecolor='black', lw=2)
ax2.set_title('Geschwindigkeit', fontweight='bold'); ax2.set_ylabel('v [km/s]')
ax2.set_xticks([0,1,2]); ax2.set_xticklabels(['Klassisch','SSZ','Beobachtet'])
ax2.axhline(y=15, color='gray', linestyle='--')

txt = 'CO (3-2)\nNH3 (1,1)\nRadio 6cm\n\nALLE UEBERLAPPEN!'
ax3.text(0.5,0.5,txt, ha='center',va='center',fontsize=14,fontweight='bold',
         transform=ax3.transAxes, bbox=dict(boxstyle='round',facecolor='lightblue',alpha=0.9))
ax3.axis('off')

ax4.text(0.5,0.5,'\"gamma_seg schreien!\"',ha='center',va='center',fontsize=18,
         fontweight='bold',transform=ax4.transAxes,
         bbox=dict(boxstyle='round',facecolor='yellow',alpha=0.8))
ax4.axis('off')

plt.suptitle('HIGHLIGHT 2: Empirische Daten', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('publication_highlights/Highlight2_Daten.png', dpi=300, bbox_inches='tight')
plt.close()
print("OK Highlight 2")

# Highlight 3
fig = plt.figure(figsize=(14,10))
ax = plt.subplot(1,1,1)
data = [
    ['Kern-Masse', '8.7+-1.5 Msun', '~8.7 Msun', 'OK MATCH'],
    ['Deltav Excess', '~5 km/s', '4.5 km/s', 'OK MATCH'],
    ['Radio-Shift', 'nu*gamma -> 6cm', '6cm beob.', 'OK MATCH'],
    ['Temp-Inv.', 'Kalt innen', '11K<40K', 'OK MATCH'],
    ['Molekuel-Stab', 'kT < E_bind', 'NH3 stabil', 'OK MATCH']
]
table = ax.table(cellText=data, colLabels=['Vorhersage','Modell','Beobachtet','Match'],
                cellLoc='center', loc='center', colWidths=[0.25,0.25,0.25,0.15])
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1,3)

for i in range(4):
    table[(0,i)].set_facecolor('lightblue')
for i in range(1,6):
    table[(i,3)].set_facecolor('lightgreen')

ax.axis('off')
txt = 'Astromaessig sexy!'
ax.text(0.5, 0.05, txt, ha='center', fontsize=16, style='italic',
        transform=ax.transAxes, bbox=dict(boxstyle='round',facecolor='yellow',alpha=0.7))
plt.suptitle('HIGHLIGHT 3: Modellierte Ergebnisse', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('publication_highlights/Highlight3_Ergebnisse.png', dpi=300, bbox_inches='tight')
plt.close()
print("OK Highlight 3")

print("\nAlle 3 Highlights fertig!")
print("Ordner: publication_highlights/")
