from src.engine.value import devig,value
def test_devig():
    p=devig([2,3]); assert abs(sum(p)-1)<1e-9
def test_value():
    v=value(.6,2); assert round(v['ev'],2)==.2
