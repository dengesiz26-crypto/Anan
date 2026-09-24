import json
from datetime import date, datetime, timezone
import numpy as np
from .config import MIN_EDGE, REPORTS
from .db import connect
from .providers.goaldir import GoaldirAPI, as_list, norm_event, norm_prediction, norm_odds_1x2
from .value import devig, value
from .coupons import accumulator
from .models.goal import markets as poisson_markets

RESULT_SELS = [('home', 'HOME'), ('draw', 'X'), ('away', 'AWAY')]

def xg_from_1x2(probs, lo=0.2, hi=3.4, step=0.1):
    """1X2 olasiliklarina en iyi uyan (home_xg, away_xg) grid aramasi."""
    grid = np.arange(lo, hi, step)
    best = (1e9, 1.4, 1.1)
    for hx in grid:
        for ax in grid:
            m = poisson_markets(float(hx), float(ax))
            err = (m['home'] - probs['home']) ** 2 + (m['draw'] - probs['draw']) ** 2 + (m['away'] - probs['away']) ** 2
            if err < best[0]:
                best = (err, float(hx), float(ax))
    return best[1], best[2]

def run_predictions(api=None, day=None, today=False, live=False, min_edge=None, record=True):
    api = api or GoaldirAPI()
    min_edge = MIN_EDGE if min_edge is None else min_edge
    if live:
        payload = api.events_live()
        phase = 'live'
    else:
        if today or not day:
            day = date.today().isoformat()
        payload = api.events(date_from=day, date_to=day)
        phase = 'pre'

    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'day': day,
              'phase': phase, 'matches': 0, 'predictions': [], 'coupon': None}
    candidates = []

    for raw in as_list(payload):
        ev = norm_event(raw)
        if not ev['id'] or not ev['home']:
            continue
        report['matches'] += 1
        match_key = f"goaldir:{ev['id']}"
        entry = {'match_key': match_key, 'league': ev['league'],
                 'home': ev['home'], 'away': ev['away'], 'kickoff': str(ev['kickoff'])}

        try:
            probs = norm_prediction(api.prediction(ev['id']))
        except Exception as e:
            probs = None
            entry['error'] = str(e)

        if probs:
            hx, ax = xg_from_1x2(probs)
            pm = poisson_markets(hx, ax)
            entry['model'] = {'source': 'goaldir_ml', 'result': probs,
                              'home_xg': round(hx, 2), 'away_xg': round(ax, 2),
                              'ou25': {'over25': pm['over25'], 'under25': pm['under25']},
                              'btts': {'btts_yes': pm['btts_yes'], 'btts_no': pm['btts_no']}}

        odds = norm_odds_1x2(raw)
        entry['value_bets'] = []
        if probs and odds:
            fair = devig([odds['home'], odds['draw'], odds['away']])
            for (sel, label), p_fair, o in zip(RESULT_SELS, fair,
                                               (odds['home'], odds['draw'], odds['away'])):
                v = value(p_fair, o)
                if not v:
                    continue
                decision = 'CANDIDATE' if v['edge'] >= min_edge else 'SKIP'
                row = {'match_key': match_key, 'match': f"{ev['home']} - {ev['away']}",
                       'phase': phase, 'market': '1X2', 'selection': label,
                       'probability': round(v['probability'], 4),
                       'fair_odds': round(v['fair_odds'], 2), 'market_odds': o,
                       'edge': round(v['edge'], 4), 'ev': round(v['ev'], 4),
                       'decision': decision}
                entry['value_bets'].append(row)
                if decision == 'CANDIDATE':
                    candidates.append({**row, 'odds': o})
        report['predictions'].append(entry)

    if candidates:
        report['coupon'] = accumulator(candidates)

    if record:
        con = connect()
        for e in report['predictions']:
            for vb in e['value_bets']:
                con.execute('INSERT INTO predictions(created_at,match_key,phase,market,selection,probability,fair_odds,market_odds,edge,ev,decision,model_version) VALUES(datetime("now"),?,?,?,?,?,?,?,?,?,?,?)',
                            (vb['match_key'], vb['phase'], vb['market'], vb['selection'],
                             vb['probability'], vb['fair_odds'], vb['market_odds'],
                             vb['edge'], vb['ev'], vb['decision'], 'goaldir+v1'))
        con.commit()
        con.close()

    (REPORTS / 'predictions.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report
