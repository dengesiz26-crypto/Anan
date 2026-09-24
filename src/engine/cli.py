import argparse,json,pandas as pd
from .db import init
from .ingest import ingest
from .train import train
from .features import prepare
from .backtest import walk_forward
from .config import PROCESSED,REPORTS

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['init','ingest','train','backtest','pre_match','paper_daemon']); a=ap.parse_args(); init()
    if a.command=='init': print('initialized')
    elif a.command=='ingest': print(json.dumps(ingest(),indent=2))
    elif a.command=='train': print(train())
    elif a.command=='backtest':
        df=prepare(pd.read_parquet(PROCESSED/'historical_matches.parquet')); r=walk_forward(df); (REPORTS/'walk_forward.json').write_text(json.dumps(r,indent=2)); print(json.dumps(r[-5:],indent=2))
    elif a.command=='pre_match': print('Pre-match engine is ready; it requires a current fixture/odds provider to supply real observations.')
    elif a.command=='paper_daemon': print('Paper daemon skeleton is active. Configure current-data providers; no synthetic live observations are generated.')
if __name__=='__main__': main()
