import json, joblib
from .config import PROCESSED,MODELS
from .features import prepare,infer_columns
from .models.ensemble import Ensemble

def train():
    p=PROCESSED/'historical_matches.parquet'
    if not p.exists(): raise RuntimeError('Run ingest first')
    df=prepare(__import__('pandas').read_parquet(p))
    req={'result','ou25','btts'}
    missing=req-set(df.columns)
    if missing: raise RuntimeError(f'Missing required targets: {sorted(missing)}')
    feats=infer_columns(df); feats=[x for x in feats if x not in ('home_goals','away_goals')]
    model=Ensemble().fit(df.dropna(subset=list(req)),feats); out=MODELS/'ensemble.joblib'; model.save(out)
    (MODELS/'feature_columns.json').write_text(json.dumps(feats,indent=2)); return out
