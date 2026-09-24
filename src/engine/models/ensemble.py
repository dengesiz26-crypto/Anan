import json, joblib, numpy as np, pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
from .goal import markets

TARGETS={'result':['home','draw','away'],'ou25':['under25','over25'],'btts':['btts_no','btts_yes']}

class Ensemble:
    def __init__(self): self.models={}
    def fit(self,df,feature_cols):
        self.feature_cols=feature_cols
        X=df[feature_cols]
        for target in ('result','ou25','btts'):
            if target=='result':
                y=df[target].astype(int)
                model=XGBClassifier(n_estimators=500,max_depth=4,learning_rate=.035,subsample=.85,colsample_bytree=.85,objective='multi:softprob',num_class=3,eval_metric='mlogloss',random_state=42)
            else:
                y=df[target].astype(int)
                model=XGBClassifier(n_estimators=450,max_depth=4,learning_rate=.035,subsample=.85,colsample_bytree=.85,objective='binary:logistic',eval_metric='logloss',random_state=42)
            pipe=Pipeline([('imputer',SimpleImputer(strategy='median')),('model',model)])
            pipe.fit(X,y); self.models[target]=pipe
        return self
    def predict(self,row):
        X=row[self.feature_cols]
        out={}
        for target,m in self.models.items():
            p=m.predict_proba(X)[0]
            out[target]=dict(zip(TARGETS[target],map(float,p)))
        return out
    def save(self,path): joblib.dump(self,path)
    @staticmethod
    def load(path): return joblib.load(path)
