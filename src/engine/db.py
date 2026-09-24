import sqlite3, json
from .config import DB

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB); c.execute('PRAGMA journal_mode=WAL'); return c

def init():
    c=connect(); c.executescript('''
    CREATE TABLE IF NOT EXISTS matches(match_key TEXT PRIMARY KEY,date TEXT,home TEXT,away TEXT,home_goals REAL,away_goals REAL,status TEXT,source TEXT,source_id TEXT,raw_json TEXT);
    CREATE TABLE IF NOT EXISTS odds(id INTEGER PRIMARY KEY AUTOINCREMENT,match_key TEXT,observed_at TEXT,bookmaker TEXT,market TEXT,selection TEXT,price REAL,source TEXT,raw_json TEXT);
    CREATE TABLE IF NOT EXISTS live_snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT,match_key TEXT,observed_at TEXT,minute REAL,home_score INTEGER,away_score INTEGER,home_stats_json TEXT,away_stats_json TEXT,odds_json TEXT,source TEXT);
    CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT,match_key TEXT,phase TEXT,market TEXT,selection TEXT,probability REAL,fair_odds REAL,market_odds REAL,edge REAL,ev REAL,decision TEXT,model_version TEXT,feature_hash TEXT);
    CREATE TABLE IF NOT EXISTS paper_bets(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT,match_key TEXT,phase TEXT,market TEXT,selection TEXT,odds REAL,probability REAL,stake REAL,status TEXT,settled_at TEXT,pnl REAL,payload TEXT);
    CREATE TABLE IF NOT EXISTS model_registry(version TEXT PRIMARY KEY,created_at TEXT,metrics_json TEXT,artifact TEXT,approved INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT,kind TEXT,payload_json TEXT,source TEXT);
    '''); c.commit(); c.close()

def insert_observation(kind,payload,source):
    c=connect(); c.execute('INSERT INTO observations(created_at,kind,payload_json,source) VALUES(datetime("now"),?,?,?)',(kind,json.dumps(payload),source)); c.commit(); c.close()
