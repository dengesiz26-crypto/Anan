import json
from datetime import datetime,timezone
from .db import connect

def snapshot(match_key,minute,home_score,away_score,home_stats,away_stats,odds,source):
    now=datetime.now(timezone.utc).isoformat(); c=connect(); c.execute('INSERT INTO live_snapshots(match_key,observed_at,minute,home_score,away_score,home_stats_json,away_stats_json,odds_json,source) VALUES(?,?,?,?,?,?,?,?,?)',(match_key,now,minute,home_score,away_score,json.dumps(home_stats),json.dumps(away_stats),json.dumps(odds),source)); c.commit(); c.close()
