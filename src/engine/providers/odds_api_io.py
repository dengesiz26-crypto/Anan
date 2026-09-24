import os, json, requests
from ..config import ODDS_API_IO_KEY
BASE='https://api.odds-api.io/v3'
class OddsAPIIO:
    def __init__(self,key=None): self.key=key or ODDS_API_IO_KEY
    def _get(self,path,params=None):
        if not self.key: raise RuntimeError('ODDS_API_IO_KEY is not configured')
        p=dict(params or {}); p['apiKey']=self.key
        r=requests.get(BASE+'/'+path.lstrip('/'),params=p,timeout=30); r.raise_for_status(); return r.json()
    def events(self,league=None,status=None):
        p={};
        if league:p['league']=league
        if status:p['status']=status
        return self._get('events',p)
    def odds(self,event_id,markets='ML,Spread,Totals'): return self._get('odds',{'eventId':event_id,'markets':markets})
