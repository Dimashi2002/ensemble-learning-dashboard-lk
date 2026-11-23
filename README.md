# Ensemble Learning Dashboard - Colombo Weather Forecasting (Sri Lanka)

Forecasts **next-day mean temperature in Colombo** and compares **Bagging, Boosting, Stacking and an RF + ARIMA hybrid** in an interactive Streamlit dashboard.

- Colab notebook: https://colab.research.google.com/github/Dimashi2002/ensemble-learning-dashboard-lk/blob/main/Ensemble_Dashboard.ipynb
- GitHub: https://github.com/Dimashi2002/ensemble-learning-dashboard-lk

## Assignment checklist (from the guideline)
| Requirement | Where |
|---|---|
| Sri Lankan / local data | Colombo daily weather 2010-2025 (Open-Meteo, CC BY 4.0), `data/` |
| Dashboard showing ensemble models and results | `app.py` (Streamlit) |
| Bagging + Boosting + Stacking | `ens.py` -> RF, Bagging, ExtraTrees / XGBoost, LightGBM, CatBoost / Stacking (Ridge meta) |
| RF vs XGBoost / LightGBM / CatBoost on same split + metrics | notebook section 7, `results.csv` |
| Hybrid RF + ARIMA (time series) | `ens.run_hybrid`, notebook section 6 |
| Other time-series model | SARIMA (ARIMA + yearly Fourier terms) |
| Research discussion | notebook section 9 |
| Notebook + 3-min video + all project files | see `slides/` and the list below |

## Files
- `Ensemble_Dashboard.ipynb` - main notebook (runs top to bottom, outputs included)
- `ens.py`, `run_all.py`, `app.py`, `build_notebook.py`, `requirements.txt`
- `data/` raw + clean data, `saved_models/` trained models, `results.csv`, `predictions.csv`
- `slides/Presentation.pptx`, `slides/Video_Script_3min.md`

## Run
```
pip install -r requirements.txt
python run_all.py                    # trains all models (about 1 minute)
python -m streamlit run app.py       # dashboard at http://localhost:8501
```
Test period 2023-2025 (time-based split, no shuffling). Metrics: MAE, RMSE, MAPE, R2, training time.

AI disclosure: code developed with help from Claude (AI assistant); data, experiments and interpretation by the author.
