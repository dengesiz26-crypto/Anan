import io, zipfile, json, shutil, subprocess, sys
from pathlib import Path
import requests, pandas as pd
from .config import RAW,PROCESSED

REPO_ZIP='https://github.com/zakariae-boui/football-prediction-ml/archive/refs/heads/main.zip'

def download_primary():
    out=RAW/'football-prediction-ml'
    if out.exists() and any(out.rglob('*.csv')): return out
    r=requests.get(REPO_ZIP,timeout=120); r.raise_for_status()
    z=zipfile.ZipFile(io.BytesIO(r.content)); z.extractall(RAW)
    extracted=RAW/'football-prediction-ml-main'
    if out.exists(): shutil.rmtree(out)
    extracted.rename(out)
    return out

def discover_tables(root):
    return [p for p in root.rglob('*') if p.suffix.lower() in ('.csv','.parquet')]

def normalize(path):
    if path.suffix=='.parquet': return pd.read_parquet(path)
    return pd.read_csv(path)

def ingest():
    root=download_primary(); tables=discover_tables(root)
    manifest=[]
    for p in tables:
        try:
            df=normalize(p)
            if len(df)>100 and {'home_team','away_team'}.issubset(df.columns):
                dest=PROCESSED/'historical_matches.parquet'; df.to_parquet(dest,index=False)
                manifest.append({'source':str(p.relative_to(root)),'rows':len(df),'columns':list(df.columns)})
        except Exception: pass
    if not manifest: raise RuntimeError('No compatible real historical table found in downloaded repository')
    (PROCESSED/'ingest_manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest
