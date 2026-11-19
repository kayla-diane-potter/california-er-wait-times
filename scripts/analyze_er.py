"""California ER wait times from CMS Timely and Effective Care (hospital level).
Usage: python scripts/analyze_er.py   (writes data/processed/er_by_hospital.csv)"""
import sys, pandas as pd, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]   # repo root, so the script runs from anywhere
d=pd.read_csv(ROOT/'data'/'raw'/'ca_timely_effective_care.csv',dtype=str)
ed=d[d['Measure ID'].isin(['EDV','OP_18a','OP_18b','OP_18c','OP_18d','OP_22','OP_23'])].copy()
key=['Facility ID','Facility Name','City/Town','County/Parish']
w=ed.pivot_table(index=key,columns='Measure ID',values='Score',aggfunc='first').reset_index()
samp=ed[ed['Measure ID']=='OP_18b'].set_index('Facility ID').Sample
for c in ['OP_18a','OP_18b','OP_18c','OP_18d','OP_22','OP_23']: w[c]=pd.to_numeric(w[c],errors='coerce')
w['OP_18b_patients']=pd.to_numeric(w['Facility ID'].map(samp),errors='coerce')
w['EDV']=w['EDV'].where(w['EDV']!='Not Available')
w['County']=w['County/Parish'].str.title()
w.to_csv(ROOT/'data'/'processed'/'er_by_hospital.csv',index=False)
b=w.dropna(subset=['OP_18b'])
print('hospitals with OP_18b:',len(b)); print(b.OP_18b.describe().round(0))
print('patient-weighted median-ish (weighted mean of medians):',round(np.average(b.OP_18b,weights=b.OP_18b_patients.fillna(0)+1e-9)))
print('slowest 8:\n',b.nlargest(8,'OP_18b')[['Facility Name','County','OP_18b','EDV']].to_string(index=False))
print('fastest 5:\n',b.nsmallest(5,'OP_18b')[['Facility Name','County','OP_18b','EDV']].to_string(index=False))
order=['low','medium','high','very high']
v=b.dropna(subset=['EDV']).groupby('EDV').OP_18b.agg(['size','median']).reindex(order); print(v)
p=w.dropna(subset=['OP_18b','OP_18c']); p['gap']=p.OP_18c-p.OP_18b
print('psych pairs',len(p),'median 18b',p.OP_18b.median(),'median 18c',p.OP_18c.median(),'median gap',p.gap.median(),'share psych longer',(p.gap>0).mean().round(3))
print('psych >= 2x:',(p.OP_18c>=2*p.OP_18b).mean().round(3), ' psych over 6h:',(p.OP_18c>=360).mean().round(3))
l=w.dropna(subset=['OP_18b','OP_22']); print('LWBS n',len(l), l.OP_22.describe().round(1)); print('spearman 18b vs 22', l[['OP_18b','OP_22']].corr('spearman').iloc[0,1].round(2))
l['tier']=pd.qcut(l.OP_18b,4,labels=['Fastest quarter','2nd','3rd','Slowest quarter']); print(l.groupby('tier',observed=True).agg(n=('OP_22','size'),med18=('OP_18b','median'),lwbs=('OP_22','median'),lwbs_mean=('OP_22','mean')))
c=b.groupby('County').agg(n=('OP_18b','size'),med=('OP_18b','median')); print(c[c.n>=3].sort_values('med').to_string())
print(b[b.County=='Monterey'][['Facility Name','City/Town','OP_18b','OP_18c','OP_22','EDV']].to_string(index=False))
print(d[d['Measure ID']=='OP_18b'].Footnote.value_counts().head())
