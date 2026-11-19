"""Charts for the California ER wait times case study.
Usage: python scripts/charts_er.py   (run analyze_er.py first; writes charts/*.png)"""
import sys, pandas as pd, numpy as np, matplotlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
src=ROOT/'data'/'processed'/'er_by_hospital.csv'; out=ROOT/'charts'
import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)  # quiet if Inter isn't installed
SLATE='#4A3F48'; PEANUT='#BF9A84'; DPEANUT='#8A6450'; INK='#2E262C'; PLUM='#6B5E62'; LINEN='#E0D8CC'; BG='#FBFAF7'; WOOL='#C9C0B0'; PEBBLE='#8E8180'
plt.rcParams.update({'font.family':['Inter','DejaVu Sans'],'font.size':11,'text.color':INK,'axes.labelcolor':PLUM,'xtick.color':PLUM,'ytick.color':PLUM,
 'axes.edgecolor':LINEN,'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,'axes.spines.top':False,'axes.spines.right':False})
hm=lambda m: f"{int(m)//60} h {int(m)%60:02d} m"
def title(ax,t,s):
    ax.set_title(t,loc='left',fontsize=15,fontweight='semibold',color=INK,pad=26)
    ax.text(0,1.02,s,transform=ax.transAxes,fontsize=10.5,color=PLUM,va='bottom')
def save(fig,name): fig.tight_layout(); fig.savefig(f'{out}/{name}',dpi=200); plt.close(fig)
w=pd.read_csv(src); b=w.dropna(subset=['OP_18b']); MED=b.OP_18b.median()

# 1 distribution
fig,ax=plt.subplots(figsize=(9,5))
bins=np.arange(60,420,20)
ax.hist(b.OP_18b,bins=bins,color=SLATE,edgecolor=BG,lw=1.2)
ax.axvline(MED,color=DPEANUT,lw=1.2,ls=(0,(3,3)))
ax.set_ylim(0,58); ax.text(MED+4,56,f"Typical hospital: {hm(MED)}",color=DPEANUT,fontsize=10,va='top')
lo=b.nsmallest(1,'OP_18b').iloc[0]; hi=b.nlargest(1,'OP_18b').iloc[0]
ax.annotate(f"Fastest: {hm(lo.OP_18b)}",xy=(lo.OP_18b,1),xytext=(lo.OP_18b,12),ha='center',fontsize=9.5,color=INK,arrowprops=dict(arrowstyle='-',color=PLUM,lw=0.8))
ax.annotate(f"Slowest: {hm(hi.OP_18b)}",xy=(hi.OP_18b,1),xytext=(hi.OP_18b-10,12),ha='center',fontsize=9.5,color=INK,arrowprops=dict(arrowstyle='-',color=PLUM,lw=0.8))
ax.set_xticks(range(60,421,60)); ax.set_xticklabels([f"{m//60} h" if m%60==0 else '' for m in range(60,421,60)])
ax.set_xlabel('Median time in the ER, patients sent home'); ax.set_ylabel('Hospitals')
ax.grid(axis='y',color=LINEN,lw=0.8); ax.set_axisbelow(True)
title(ax,'The slowest ER takes 6 times as long as the fastest',f"Median ER visit length at {len(b)} California hospitals, patients sent home, 2025")
save(fig,'01_wait_distribution.png')

# 2 by volume
order=['low','medium','high','very high']; labs=['Low','Medium','High','Very high']
v=b.dropna(subset=['EDV']).groupby('EDV').OP_18b.agg(['size','median']).reindex(order)
fig,ax=plt.subplots(figsize=(9,4.8))
bars=ax.bar(labs,v['median'],color=SLATE,width=0.58)
for r,m,n in zip(bars,v['median'],v['size']):
    ax.text(r.get_x()+r.get_width()/2,m+4,hm(m),ha='center',va='bottom',fontsize=11.5,fontweight='semibold',color=INK)
    ax.text(r.get_x()+r.get_width()/2,-10,f"{n} hospitals",ha='center',va='top',fontsize=9,color=PLUM)
ax.set_ylim(0,240); ax.set_yticks([]); ax.spines['left'].set_visible(False); ax.tick_params(axis='x',length=0,pad=20)
ax.set_xlabel('Emergency department volume (CMS category)',labelpad=6)
title(ax,'The busiest ERs keep patients an hour longer','Typical median ER visit length (2025), by ER volume (2024)')
save(fig,'02_wait_by_volume.png')

# 3 psych vs all
p=w.dropna(subset=['OP_18b','OP_18c'])
vals=[p.OP_18b.median(),p.OP_18c.median()]; names=['Most patients sent home','Mental health patients']
fig,ax=plt.subplots(figsize=(9,3.6))
bars=ax.barh(names[::-1],vals[::-1],color=[PEANUT,SLATE],height=0.55)
for r,m in zip(bars,vals[::-1]): ax.text(m+4,r.get_y()+r.get_height()/2,hm(m),va='center',fontsize=11.5,fontweight='semibold',color=INK)
ax.set_xlim(0,330); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y',length=0)
title(ax,f'Mental health patients wait longer at {(p.OP_18c>p.OP_18b).mean()*100:.0f}% of hospitals',f"Typical median ER visit length at the {len(p)} hospitals that report both, 2025")
save(fig,'03_mental_health_gap.png')

# 4 left without being seen by wait quarter
l=w.dropna(subset=['OP_18b','OP_22']).copy()
l['q']=pd.qcut(l.OP_18b,4,labels=['Fastest\nquarter','Second\nquarter','Third\nquarter','Slowest\nquarter'])
g=l.groupby('q',observed=True).agg(lw=('OP_22','mean'),m=('OP_18b','median'))
fig,ax=plt.subplots(figsize=(9,4.8))
bars=ax.bar(g.index.astype(str),g.lw,color=[SLATE,SLATE,SLATE,PEANUT],width=0.58)
for r,x,m in zip(bars,g.lw,g.m):
    ax.text(r.get_x()+r.get_width()/2,x+0.07,f"{x:.1f}%",ha='center',va='bottom',fontsize=11.5,fontweight='semibold',color=INK)
    ax.text(r.get_x()+r.get_width()/2,-0.16,f"typical stay {hm(m)}",ha='center',va='top',fontsize=9,color=PLUM)
ax.set_ylim(0,3.8); ax.set_yticks([]); ax.spines['left'].set_visible(False); ax.tick_params(axis='x',length=0,pad=24)
title(ax,'Twice as many patients walk out at the slowest ERs','Average share of patients who left before being seen (2024), hospitals grouped by ER visit length (2025)')
save(fig,'04_left_without_being_seen.png')

# 5 Monterey County hospitals
m=b[b.County=='Monterey'].sort_values('OP_18b')
nm={'COMMUNITY HOSPITAL OF THE MONTEREY PENINSULA':'Community Hospital of the\nMonterey Peninsula','NATIVIDAD MEDICAL CENTER':'Natividad Medical Center',
    'SALINAS VALLEY HEALTH MEDICAL CENTER':'Salinas Valley Health','SOUTHERN MONTEREY COUNTY MEMORIAL HOSPITAL':'Southern Monterey County\nMemorial (King City)'}
fig,ax=plt.subplots(figsize=(9,4.2))
bars=ax.barh([nm.get(x,x.title()) for x in m['Facility Name']],m.OP_18b,color=[PEANUT if v>MED else SLATE for v in m.OP_18b],height=0.55)
for r,v in zip(bars,m.OP_18b): ax.text(v-4,r.get_y()+r.get_height()/2,hm(v),va='center',ha='right',fontsize=10.5,color='#FFFFFF',fontweight='semibold')
ax.axvline(MED,color=PLUM,lw=1,ls=(0,(3,3)),zorder=0); ax.text(MED+3,len(m)-0.45,f"State typical: {hm(MED)}",color=PLUM,fontsize=9.5,va='bottom')
ax.set_xlim(0,250); ax.set_xticks([]); ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y',length=0); ax.set_ylim(-0.6,len(m)+0.2)
title(ax,'Three of four Monterey County ERs beat the state','Median ER visit length, patients sent home, 2025')
save(fig,'05_monterey_county.png')
