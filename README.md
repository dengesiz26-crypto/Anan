# Football Live Value Engine

Separate project for long-running, real-match prediction before any real-money execution.

## Design

Historical downloadable datasets are the common foundation for both pre-match and live analysis. Live fixtures, statistics and odds are appended as timestamped observations; they never replace the historical source.

Pipeline:

`downloaded historical data -> canonical store -> leakage-safe features -> calibrated models -> paper predictions -> live observations -> live model update -> paper settlement -> verified learning -> optional execution adapter`

No synthetic matches, odds, probabilities or outcomes are generated. Missing values stay missing and the system can abstain.

## Historical data used

The default dataset source is the public `zakariae-boui/football-prediction-ml` repository, whose processed data is included upstream and is built from football-data.co.uk plus Understat. The project documentation states that its processed datasets are ready to use and its features are chronological/leakage-safe. See `config/sources.json`.

Additional optional research data: StatsBomb Open Data and the Football Events Kaggle dataset. Their licensing/terms must be respected for any commercial deployment.

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.engine.cli init
python -m src.engine.cli ingest
python -m src.engine.cli train
python -m src.engine.cli backtest
python -m src.engine.cli pre_match
python -m src.engine.cli paper_daemon
```

For current/live data set API keys in `.env`. Without keys the historical/paper pipeline still works; it will not invent live data.

## Long validation mode

`paper_daemon` records predictions and later settles them from real final results. It does not place real bets. The ledger tracks Brier score, log loss, calibration, ROI/yield, drawdown and closing-line value when timestamps permit.

## Live architecture

- `providers/api_football.py`: fixtures, statistics, lineups/injuries and current match information.
- `providers/odds_api_io.py`: optional pre-match/live odds WebSocket/client adapter.
- `live.py`: timestamped live feature snapshots.
- `models/ensemble.py`: Poisson/Dixon-Coles style goal distribution + XGBoost classifiers.
- `value.py`: de-vig, fair price, edge and EV.
- `coupons.py`: singles and accumulators; it optimizes from the available candidate pool rather than imposing an arbitrary fixed leg count.
- `execution/betfair.py`: future exchange adapter boundary using betfairlightweight. Live placement is hard-disabled unless explicit configuration is enabled.

## Important validation rule

A positive backtest is not proof of future profit. The system will not promote a strategy based on one split. Promotion requires multiple chronological OOS windows, calibration, adequate sample size, no leakage findings and stable market-specific performance.
