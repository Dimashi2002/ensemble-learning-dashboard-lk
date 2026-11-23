"""Trains every model on the Colombo weather data and saves results for the dashboard.
Usage:  python run_all.py"""
import re, joblib, numpy as np, pandas as pd
import ens

DASH = {"Random Forest", "XGBoost", "LightGBM", "CatBoost", "Extra Trees", "Ridge (baseline)"}  # models the dashboard loads
slug = lambda n: re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_")
df = ens.load_clean("data/colombo_weather_raw.csv")
df.to_csv("data/colombo_weather_clean.csv")
feat = ens.make_features(df)
Xtr, Xte, ytr, yte = ens.split(feat)
print(f"train {Xtr.index.min().date()} -> {Xtr.index.max().date()} ({len(Xtr)} days) | "
      f"test {Xte.index.min().date()} -> {Xte.index.max().date()} ({len(Xte)} days)")

# naive baseline: tomorrow = today
naive = Xte["temp_lag1"].values
rows = [ens.scores("Persistence (yesterday)", "Baseline", yte.values, naive, 0.0)]
preds = {"Persistence (yesterday)": naive}

for n, (g, m) in ens.get_models().items():
    print("training", n, flush=True)
    r, p, fitted = ens.run_ml(n, g, m, Xtr, Xte, ytr, yte)
    rows.append(r); preds[n] = p
    if n in DASH: joblib.dump(fitted, f"saved_models/{slug(n)}.joblib", compress=9)

print("training SARIMA + Hybrid RF+ARIMA", flush=True)
r_ar, p_ar, r_hy, p_hy, parts = ens.run_hybrid(Xtr, Xte, ytr, yte)
rows += [r_ar, r_hy]; preds[r_ar["Model"]] = p_ar; preds["Hybrid RF + ARIMA"] = p_hy

res = pd.DataFrame(rows).sort_values("MAE").reset_index(drop=True)
res.to_csv("results.csv", index=False)
pd.DataFrame({"date": yte.index, "actual": yte.values, **preds}).to_csv("predictions.csv", index=False)
pd.set_option("display.width", 200)
print(res.round(3).to_string())
print("\nBEST MODEL (lowest MAE):", res.iloc[0]["Model"])
