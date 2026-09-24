import time, requests
from ..config import GOALDIR_API_KEY, GOALDIR_BASE_URL, GOALDIR_PREDICTION_PATH

PREDICTION_CANDIDATES = [
    'api/v2/events/{id}/prediction/',
    'api/v2/predictions/{id}/',
    'api/v2/events/{id}/predictions/',
]

class GoaldirAPI:
    """goaldir.com (Bzzoiro Sports Data) futbol API istemcisi.
    Docs: https://goaldir.com/docs | Ucretsiz anahtar: https://sports.bzzoiro.com/register/
    Kimlik: 'Authorization: Token <key>' header'i."""

    def __init__(self, key=None, base=None, interval=1.0):
        self.key = key or GOALDIR_API_KEY
        self.base = (base or GOALDIR_BASE_URL).rstrip('/')
        self.interval = interval
        self.last = 0.0

    def get(self, path, params=None):
        if not self.key:
            raise RuntimeError('GOALDIR_API_KEY tanimli degil; canli veri uydurulmayacak')
        wait = self.interval - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        r = requests.get(f'{self.base}/{path.lstrip("/")}', params=params or {},
                         headers={'Authorization': f'Token {self.key}'}, timeout=30)
        self.last = time.time()
        r.raise_for_status()
        return r.json()

    # --- kesif ---
    def events(self, date_from=None, date_to=None, league_id=None):
        p = {}
        if date_from: p['date_from'] = date_from
        if date_to:   p['date_to'] = date_to
        if league_id: p['league_id'] = league_id
        return self.get('api/v2/events/', p)

    def events_live(self):
        return self.get('api/v2/events/live/')

    def leagues(self):
        try:
            return self.get('api/v2/leagues/')
        except Exception:
            return []

    # --- mac bazli ---
    def event(self, event_id):
        return self.get(f'api/v2/events/{event_id}/_id}/')

    def prediction(self, event_id):
        paths = [GOALDIR_PREDICTION_PATH] if GOALDIR_PREDICTION_PATH else PREDICTION_CANDIDATES
        errs = []
        for tpl in paths:
            path = tpl.format(id=event_id)
            try:
                return self.get(path)
            except Exception as e:
                errs.append(f'{path} -> {e}')
        raise RuntimeError('Tahmin ucu bulunamadi. Denenenler: ' + ' ; '.join(errs))


# ---------- toleransli normalizasyon (API JSON sekilleri) ----------

def as_list(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for k in ('events', 'results', 'data', 'matches', 'items'):
            v = payload.get(k)
            if isinstance(v, list):
                return v
        return [payload]
    return []

def _team(x):
    if isinstance(x, dict):
        return x.get('name') or x.get('title') or str(x)
    return x

def _pick(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return None

def norm_event(e):
    ev_id = e.get('id') or e.get('event_id') or e.get('fixture_id') or e.get('match_id')
    home = _team(e.get('home_team') or e.get('home') or e.get('homeTeam'))
    away = _team(e.get('away_team') or e.get('away') or e.get('awayTeam'))
    league = e.get('league') or e.get('tournament') or e.get('competition') or {}
    league = league.get('name') if isinstance(league, dict) else _team(league)
    return {'id': ev_id, 'home': home, 'away': away, 'league': league,
            'kickoff': e.get('start') or e.get('date') or e.get('kickoff') or e.get('startTimestamp'),
            'status': e.get('status') or e.get('state'),
            'home_score': e.get('home_score', e.get('homeScore')),
            'away_score': e.get('away_score', e.get('awayScore'))}

def norm_prediction(payload):
    """{home, draw, away, confidence?} olasiliklarini cikar."""
    p = payload
    if isinstance(p, dict):
        for k in ('prediction', 'data', 'result', 'probabilities'):
            v = p.get(k)
            if isinstance(v, dict):
                p = v
                break
    if not isinstance(p, dict):
        return None
    home = _pick(p, 'home', 'home_win', 'home_probability', 'p_home', 'home_win_probability', '1')
    draw = _pick(p, 'draw', 'draw_probability', 'p_draw', 'x')
    away = _pick(p, 'away', 'away_win', 'away_probability', 'p_away', 'away_win_probability', '2')
    try:
        home, draw, away = float(home), float(draw), float(away)
    except (TypeError, ValueError):
        return None
    s = home + draw + away
    if s <= 0:
        return None
    out = {'home': home / s, 'draw': draw / s, 'away': away / s}
    conf = _pick(p, 'confidence', 'confidence_score')
    if conf is not None:
        try:
            out['confidence'] = float(conf)
        except (TypeError, ValueError):
            pass
    return out

def norm_odds_1x2(event_raw):
    o = _pick(event_raw, 'odds', 'odds_1x2', 'markets')
    if not isinstance(o, dict):
        return None
    for k in ('1x2', 'match_winner', 'ml', 'result'):
        if isinstance(o.get(k), dict):
            o = o[k]
            break
    h, d, a = _pick(o, 'home', '1'), _pick(o, 'draw', 'x'), _pick(o, 'away', '2')
    try:
        return {'home': float(h), 'draw': float(d), 'away': float(a)}
    except (TypeError, ValueError):
        return None
