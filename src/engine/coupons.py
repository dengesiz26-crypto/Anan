from math import prod

def singles(candidates): return sorted(candidates,key=lambda x:x.get('ev',-999),reverse=True)
def accumulator(candidates,max_legs=None):
    pool=[c for c in candidates if c.get('decision')=='CANDIDATE']
    pool=sorted(pool,key=lambda x:(x.get('ev',-999),x.get('probability',0)),reverse=True)
    if max_legs is not None: pool=pool[:max_legs]
    if not pool:return None
    # Only combine legs from different matches; correlation is rejected unless explicitly supplied as independent.
    seen=set(); legs=[]
    for c in pool:
        if c['match_key'] in seen: continue
        legs.append(c); seen.add(c['match_key'])
    if not legs:return None
    return {'legs':legs,'combined_odds':prod(x['odds'] for x in legs),'combined_probability':prod(x['probability'] for x in legs)}
