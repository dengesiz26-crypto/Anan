import numpy as np
from scipy.stats import poisson

def score_matrix(home_xg,away_xg,max_goals=8):
    h=np.arange(max_goals+1); a=np.arange(max_goals+1)
    m=np.outer(poisson.pmf(h,home_xg),poisson.pmf(a,away_xg))
    return m/m.sum()

def markets(home_xg,away_xg):
    m=score_matrix(home_xg,away_xg)
    home=np.tril(m,-1).sum(); draw=np.trace(m); away=np.triu(m,1).sum()
    over25=sum(m[i,j] for i in range(m.shape[0]) for j in range(m.shape[1]) if i+j>2)
    btts=sum(m[i,j] for i in range(1,m.shape[0]) for j in range(1,m.shape[1]))
    return {'home':float(home),'draw':float(draw),'away':float(away),'over25':float(over25),'under25':float(1-over25),'btts_yes':float(btts),'btts_no':float(1-btts)}
