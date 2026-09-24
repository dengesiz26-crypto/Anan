import json
from .db import connect

def record(c):
    con=connect(); con.execute('INSERT INTO paper_bets(created_at,match_key,phase,market,selection,odds,probability,stake,status,payload) VALUES(datetime("now"),?,?,?,?,?,?,?,?,?)',(c['match_key'],c['phase'],c['market'],c['selection'],c['odds'],c['probability'],c.get('stake',0),'OPEN',json.dumps(c))); con.commit(); con.close()
