from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data'
RAW=DATA/'raw'; PROCESSED=DATA/'processed'; REPORTS=DATA/'reports'; MODELS=DATA/'models'
for p in (RAW,PROCESSED,REPORTS,MODELS): p.mkdir(parents=True,exist_ok=True)
DB=Path(os.getenv('DATABASE_PATH',str(DATA/'football.db')))
API_FOOTBALL_KEY=os.getenv('API_FOOTBALL_KEY','').strip()
ODDS_API_IO_KEY=os.getenv('ODDS_API_IO_KEY',os.getenv('ODDS_API_KEY','')).strip()
EXECUTION_MODE=os.getenv('EXECUTION_MODE','paper').lower()
ENABLE_LIVE_EXECUTION=os.getenv('ENABLE_LIVE_EXECUTION','false').lower()=='true'
LIVE_POLL_SECONDS=int(os.getenv('LIVE_POLL_SECONDS','30'))
MIN_EDGE=float(os.getenv('MIN_EDGE','0.03'))
GOALDIR_API_KEY=os.getenv('GOALDIR_API_KEY','').strip()
GOALDIR_BASE_URL=os.getenv('GOALDIR_BASE_URL','https://sports.bzzoiro.com').strip().rstrip('/')
GOALDIR_PREDICTION_PATH=os.getenv('GOALDIR_PREDICTION_PATH','').strip()
