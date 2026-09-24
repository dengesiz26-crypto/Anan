def implied(o): return 1/o if o and o>1 else None
def devig(prices):
    p=[implied(x) for x in prices]
    if any(x is None for x in p): return None
    s=sum(p); return [x/s for x in p]
def value(prob,odds):
    if prob is None or odds is None or odds<=1:return None
    return {'probability':prob,'fair_odds':1/prob,'edge':prob-1/odds,'ev':prob*odds-1}
