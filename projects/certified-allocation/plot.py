"""Standalone explanatory figure for the exact designed example."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(7,5),layout='constrained')
ax.fill([0,5,0],[0,0,5],color='#dbeafe',label='Diagonal plan remains optimal: t + s ≤ 5')
ax.fill([0,3,3,0],[0,0,2,2],color='#86efac',alpha=.8,label='Original certificate applies: t ≤ 3, s ≤ 2')
ax.plot([0,5],[5,0],color='#2563eb',lw=2)
ax.scatter([4,4],[0,2],color=['#166534','#b91c1c'],s=55,zorder=4)
ax.annotate('Same plan, new certificate',(4,0),xytext=(2.05,.4),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.annotate('A different plan is cheaper',(4,2),xytext=(2.1,3.3),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.set(xlim=(0,5),ylim=(-.12,5),xlabel='Discount on A → S (t)',ylabel='Discount on B → R (s)',title='A plan can outlive one certificate')
ax.legend(loc='upper right',fontsize=8);ax.grid(alpha=.18)
fig.savefig(ROOT/'applicability.png',dpi=180)
fig.savefig(ROOT/'applicability.svg')
