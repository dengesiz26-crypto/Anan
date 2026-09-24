import numpy as np, pandas as pd

def infer_columns(df):
    candidates=[]
    for c in df.columns:
        lc=c.lower()
        if any(x in lc for x in ('result','target','outcome','home_team','away_team','date','season','score')): continue
        if pd.api.types.is_numeric_dtype(df[c]): candidates.append(c)
    return candidates

def prepare(df):
    x=df.copy()
    date_col=next((c for c in x.columns if c.lower() in ('date','match_date','datetime')),None)
    if date_col: x[date_col]=pd.to_datetime(x[date_col],errors='coerce'); x=x.sort_values(date_col)

    # Map documented source score columns to the feature-engineering names.
    if 'home_goals' not in x.columns and 'home_score' in x.columns:
        x['home_goals'] = x['home_score']
    if 'away_goals' not in x.columns and 'away_score' in x.columns:
        x['away_goals'] = x['away_score']

    # Preserve only information that exists before the match. Upstream dataset documents leakage-safe engineered features.
    if 'result' not in x and {'home_goals','away_goals'}.issubset(x.columns):
        x['result']=np.select([x.home_goals>x.away_goals,x.home_goals==x.away_goals],[0,1],default=2)
    if 'ou25' not in x and {'home_goals','away_goals'}.issubset(x.columns):
        x['ou25']=((x.home_goals+x.away_goals)>2.5).astype(int)
    if 'btts' not in x and {'home_goals','away_goals'}.issubset(x.columns):
        x['btts']=((x.home_goals>0)&(x.away_goals>0)).astype(int)

    return x
