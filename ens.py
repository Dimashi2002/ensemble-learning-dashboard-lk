"""Shared code: data loading, features, models, evaluation.
Task: forecast NEXT-DAY mean temperature (deg C) for Colombo, Sri Lanka.
Data: Open-Meteo historical weather archive (real data, 2010-2025)."""
import time, warnings
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import (RandomForestRegressor, BaggingRegressor, ExtraTreesRegressor, StackingRegressor)
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
RS = 42
SPLIT_DATE = "2023-01-01"          # train: 2010-2022, test: 2023-2025 (time-based, no shuffling)
TARGET = "temp_mean"

RAW_COLS = {"time": "date", "temperature_2m_mean (°C)": "temp_mean", "temperature_2m_max (°C)": "temp_max",
            "temperature_2m_min (°C)": "temp_min", "precipitation_sum (mm)": "rain_mm",
            "relative_humidity_2m_mean (%)": "humidity", "wind_speed_10m_max (km/h)": "wind_max"}

def load_clean(path):
    df = pd.read_csv(path, skiprows=3)
    df = df.rename(columns=RAW_COLS)[list(RAW_COLS.values())]
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    df = df[~df.index.duplicated()].asfreq("D")
    df = df.interpolate(limit=3).dropna()
    return df

def fourier(index, k=2):
    t = index.dayofyear.values / 365.25
    cols = {}
    for i in range(1, k + 1):
        cols[f"sin{i}"] = np.sin(2 * np.pi * i * t); cols[f"cos{i}"] = np.cos(2 * np.pi * i * t)
    return pd.DataFrame(cols, index=index)

def make_features(df):
    """Every feature only uses information from BEFORE the day being predicted (lag >= 1)."""
    f = pd.DataFrame(index=df.index)
    for l in [1, 2, 3, 7, 14, 365]:
        f[f"temp_lag{l}"] = df[TARGET].shift(l)
    f["temp_roll7"] = df[TARGET].shift(1).rolling(7).mean()
    f["temp_roll30"] = df[TARGET].shift(1).rolling(30).mean()
    for c in ["rain_mm", "humidity", "wind_max", "temp_max", "temp_min"]:
        f[f"{c}_lag1"] = df[c].shift(1)
    f["rain_roll7"] = df["rain_mm"].shift(1).rolling(7).sum()
    f = f.join(fourier(df.index)); f["month"] = df.index.month
    f[TARGET] = df[TARGET]
    return f.dropna()

def split(feat):
    tr, te = feat[feat.index < SPLIT_DATE], feat[feat.index >= SPLIT_DATE]
    return tr.drop(columns=TARGET), te.drop(columns=TARGET), tr[TARGET], te[TARGET]

def get_models():
    rf = lambda: RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=RS, n_jobs=-1)
    xgb = lambda: XGBRegressor(n_estimators=400, learning_rate=0.03, max_depth=4, subsample=0.8, random_state=RS, n_jobs=-1)
    lgb = lambda: LGBMRegressor(n_estimators=400, learning_rate=0.03, num_leaves=15, random_state=RS, verbose=-1)
    stack = StackingRegressor(
        estimators=[("rf", RandomForestRegressor(n_estimators=150, min_samples_leaf=2, random_state=RS, n_jobs=-1)),
                    ("xgb", XGBRegressor(n_estimators=300, learning_rate=0.03, max_depth=4, random_state=RS)),
                    ("lgb", LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=15, random_state=RS, verbose=-1))],
        final_estimator=Ridge(alpha=1.0), cv=KFold(n_splits=5, shuffle=False))   # contiguous blocks, no shuffling
    return {
        "Ridge (baseline)": ("Baseline", Ridge(alpha=1.0)),
        "Random Forest": ("Bagging", rf()),
        "Bagging (Decision Trees)": ("Bagging", BaggingRegressor(DecisionTreeRegressor(), n_estimators=200, random_state=RS, n_jobs=-1)),
        "Extra Trees": ("Bagging", ExtraTreesRegressor(n_estimators=300, min_samples_leaf=2, random_state=RS, n_jobs=-1)),
        "XGBoost": ("Boosting", xgb()),
        "LightGBM": ("Boosting", lgb()),
        "CatBoost": ("Boosting", CatBoostRegressor(iterations=500, learning_rate=0.05, depth=5, random_seed=RS, verbose=0)),
        "Stacking (RF+XGB+LGBM -> Ridge)": ("Stacking", stack),
    }

def scores(name, group, y_true, y_pred, secs):
    return dict(Model=name, Type=group, MAE=mean_absolute_error(y_true, y_pred),
                RMSE=float(np.sqrt(mean_squared_error(y_true, y_pred))), R2=r2_score(y_true, y_pred),
                MAPE=mean_absolute_percentage_error(y_true, y_pred) * 100, Train_seconds=secs)

def run_ml(name, group, model, Xtr, Xte, ytr, yte):
    t = time.time(); model.fit(Xtr, ytr); secs = time.time() - t
    p = model.predict(Xte)
    return scores(name, group, yte.values, p, secs), p, model

def fit_arima(ytr, Xtr_exog, order=(2, 0, 1)):
    """ARIMA with yearly seasonality (Fourier terms) = SARIMAX. Captures trend + season."""
    return SARIMAX(ytr, exog=Xtr_exog, order=order, enforce_stationarity=False).fit(disp=False, maxiter=200)

def arima_one_step(res, y_new, exog_new):
    """One-step-ahead forecasts on new data WITHOUT refitting (uses only past values)."""
    return res.apply(y_new, exog=exog_new, refit=False).fittedvalues

def run_hybrid(Xtr, Xte, ytr, yte):
    """HYBRID RF + ARIMA:
       1) ARIMA models trend+season.  2) RF learns ARIMA's leftover errors (residuals) from lag features.
       3) final forecast = ARIMA forecast + RF residual forecast."""
    t = time.time()
    ex_tr, ex_te = fourier(ytr.index), fourier(yte.index)
    ar = fit_arima(ytr, ex_tr)
    arima_tr = ar.fittedvalues                      # in-sample one-step ARIMA forecasts
    resid_tr = ytr - arima_tr
    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=RS, n_jobs=-1).fit(Xtr, resid_tr)
    secs = time.time() - t
    # test: one-step ARIMA on the real test series, then add the RF residual forecast
    full_y, full_ex = pd.concat([ytr, yte]), pd.concat([ex_tr, ex_te])
    arima_all = arima_one_step(ar, full_y, full_ex)
    arima_te = arima_all.loc[yte.index]
    p_hybrid = arima_te.values + rf.predict(Xte)
    return (scores("SARIMA (ARIMA + yearly season)", "Time series", yte.values, arima_te.values, secs),
            arima_te.values,
            scores("Hybrid RF + ARIMA", "Hybrid", yte.values, p_hybrid, secs),
            p_hybrid, dict(arima=ar, rf_resid=rf))
