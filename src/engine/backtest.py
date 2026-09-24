import json, numpy as np, pandas as pd
from sklearn.metrics import accuracy_score,log_loss,brier_score_loss
from .models.ensemble import Ensemble
from .features import infer_columns

def walk_forward(df,min_train=1000,block=250):
    df=df.sort_values('date').reset_index(drop=True) if 'date' in df else df.reset_index(drop=True)
    feats=infer_columns(df)
    feats=[c for c in feats if c not in ('home_goals','away_goals')]
    reports=[]; start=min_train
    while start<len(df):
        end=min(start+block,len(df)); tr=df.iloc[:start]; te=df.iloc[start:end]
        if len(te)<1: break
        m=Ensemble().fit(tr.dropna(subset=['result','ou25','btts']),feats)
        pr=m.models['result'].predict_proba(te[feats]); y=te.result.astype(int).to_numpy()
        reports.append({'train_end':str(tr.index[-1]),'test_start':str(te.index[0]),'test_end':str(te.index[-1]),'n':len(te),'accuracy':float(accuracy_score(y,pr.argmax(1))),'log_loss':float(log_loss(y,pr,labels=[0,1,2]))})
        start=end
    return reports
