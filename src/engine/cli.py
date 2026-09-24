import argparse, json, pandas as pd
from .db import init
from .ingest import ingest
from .train import train
from .features import prepare
from .backtest import walk_forward
from .config import PROCESSED, REPORTS
from .prematch import run_predictions
from .providers.goaldir import GoaldirAPI

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['init', 'ingest', 'train', 'backtest', 'pre_match', 'predict', 'paper_daemon'])
    ap.add_argument('--date', default=None, help='YYYY-MM-DD')
    ap.add_argument('--today', action='store_true')
    ap.add_argument('--live', action='store_true')
    ap.add_argument('--min-edge', type=float, default=None)
    a = ap.parse_args()
    init()
    if a.command == 'init':
        print('initialized')
    elif a.command == 'ingest':
        print(json.dumps(ingest(), indent=2))
    elif a.command == 'train':
        print(train())
    elif a.command == 'backtest':
        df = prepare(pd.read_parquet(PROCESSED / 'historical_matches.parquet'))
        r = walk_forward(df)
        (REPORTS / 'walk_forward.json').write_text(json.dumps(r, indent=2))
        print(json.dumps(r[-5:], indent=2))
    elif a.command in ('pre_match', 'predict'):
        report = run_predictions(api=GoaldirAPI(), day=a.date, today=a.today,
                                 live=a.live, min_edge=a.min_edge)
        slim = {'day': report['day'], 'matches': report['matches'],
                'coupon': report['coupon']}
        print(json.dumps(slim, indent=2, ensure_ascii=False))
    elif a.command == 'paper_daemon':
        print('Paper daemon skeleton is active. Configure current-data providers; no synthetic live observations are generated.')

if __name__ == '__main__':
    main()
