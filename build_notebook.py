import nbformat as nbf

REPO = "https://github.com/Dimashi2002/ensemble-learning-dashboard-lk.git"
nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s))
code = lambda s: C.append(nbf.v4.new_code_cell(s))

md("# Ensemble Learning Dashboard - Colombo Temperature Forecasting (Sri Lanka)\n"
   "**Author:** Wickramage D.N - 224215R  |  **Submission:** 23 Nov 2026\n\n"
   "> **AI disclosure:** the code was developed with help from Claude (AI assistant). The data, experiments and results below were run by me; "
   "the interpretation sections are marked for my own words.\n\n"
   "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
   "(https://colab.research.google.com/github/Dimashi2002/ensemble-learning-dashboard-lk/blob/main/Ensemble_Dashboard.ipynb)")

md("## 1. Problem & innovation\n"
   "Sri Lanka's economy (tourism, agriculture, power demand, events) depends on daily weather. This project forecasts **next-day mean temperature in Colombo** "
   "and compares **Bagging, Boosting, Stacking and an RF + ARIMA hybrid**.\n\n"
   "**Innovation:** a *hybrid* model where **ARIMA captures trend + yearly season** and **Random Forest learns ARIMA's leftover errors** from recent weather "
   "(lags of rain, humidity, wind). Everything is shown in an interactive dashboard that compares all models side by side.\n\n"
   "_(Edit: add your own one-line use case, e.g. 'helps hotels in Colombo plan cooling demand'.)_")

md("## 2. Data source\n"
   "**Real Sri Lankan data:** daily weather for Colombo (6.93 N, 79.86 E), 1 Jan 2010 - 31 Dec 2025, from the free **Open-Meteo Historical Weather API** "
   "(open data, CC BY 4.0, https://open-meteo.com). Variables: mean/max/min temperature, rainfall, humidity, max wind.\n"
   "The raw file is stored in `data/colombo_weather_raw.csv`, so the notebook runs without internet.")

code("import os, subprocess, sys\n"
     "# --- Colab setup: get the project files from GitHub and install libraries ---\n"
     "if 'google.colab' in sys.modules and not os.path.exists('ens.py'):\n"
     f"    subprocess.run(['git', 'clone', '{REPO}', '/content/repo'], check=True)\n"
     "    os.chdir('/content/repo')\n"
     "    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'], check=True)\n"
     "print('working dir:', os.getcwd())")
code("import warnings; warnings.filterwarnings('ignore')\n"
     "import pandas as pd, numpy as np, matplotlib.pyplot as plt\n"
     "import ens\n"
     "pd.set_option('display.width', 200)")

md("## 3. Cleaning\nRename columns, parse dates, fill tiny gaps (max 3 days) by interpolation, make sure there is one row per day.")
code("df = ens.load_clean('data/colombo_weather_raw.csv')\n"
     "print(df.shape, df.index.min().date(), '->', df.index.max().date())\n"
     "print('missing values:', int(df.isna().sum().sum()))\n"
     "df.describe().round(2)")

md("## 4. EDA")
code("fig, ax = plt.subplots(2, 2, figsize=(14, 8))\n"
     "df.temp_mean.resample('MS').mean().plot(ax=ax[0,0], title='Monthly mean temperature (C)')\n"
     "df.groupby(df.index.month).temp_mean.mean().plot.bar(ax=ax[0,1], title='Temperature by month (season)')\n"
     "df.groupby(df.index.month).rain_mm.mean().plot.bar(ax=ax[1,0], color='tab:blue', title='Mean daily rain by month (mm) - two monsoons')\n"
     "pd.plotting.autocorrelation_plot(df.temp_mean.iloc[-1500:], ax=ax[1,1]); ax[1,1].set_title('Autocorrelation of temperature')\n"
     "plt.tight_layout()")
md("**What the plots show (write in your own words):** temperature has a clear yearly cycle (hot Mar-May, cooler Dec-Jan), rainfall peaks in the two monsoon periods, "
   "and today's temperature is strongly related to yesterday's (high autocorrelation). That is why lag features and ARIMA make sense.")

md("## 5. Features and split\n"
   "Features use only **past** information (lags of temperature, rain, humidity, wind; 7- and 30-day rolling means; seasonal sin/cos terms). "
   "**Time-based split, no shuffling:** train 2010-2022, test 2023-2025.")
code("feat = ens.make_features(df)\n"
     "Xtr, Xte, ytr, yte = ens.split(feat)\n"
     "print('train:', Xtr.index.min().date(), '->', Xtr.index.max().date(), len(Xtr), 'days')\n"
     "print('test :', Xte.index.min().date(), '->', Xte.index.max().date(), len(Xte), 'days')\n"
     "print('features:', list(Xtr.columns))")

md("## 6. Models\n"
   "| Type | Models |\n|---|---|\n"
   "| Baselines | Persistence (tomorrow = today), Ridge regression |\n"
   "| **Bagging** | Random Forest (main), Bagging of decision trees, Extra Trees |\n"
   "| **Boosting** | XGBoost, LightGBM, CatBoost |\n"
   "| **Stacking** | RF + XGBoost + LightGBM -> Ridge meta-model |\n"
   "| Time series | SARIMA (ARIMA + yearly Fourier season) |\n"
   "| **Hybrid** | **RF + ARIMA**: ARIMA forecast + RF forecast of ARIMA's residuals |\n\n"
   "All models use the **same split and same metrics** (MAE, RMSE, MAPE, R2).")
code("naive = Xte['temp_lag1'].values\n"
     "rows = [ens.scores('Persistence (yesterday)', 'Baseline', yte.values, naive, 0.0)]\n"
     "preds = {'Persistence (yesterday)': naive}\n"
     "fitted = {}\n"
     "for n, (g, m) in ens.get_models().items():\n"
     "    r, p, fm = ens.run_ml(n, g, m, Xtr, Xte, ytr, yte)\n"
     "    rows.append(r); preds[n] = p; fitted[n] = fm; print('done:', n)")
md("### Hybrid RF + ARIMA")
code("r_ar, p_ar, r_hy, p_hy, parts = ens.run_hybrid(Xtr, Xte, ytr, yte)\n"
     "rows += [r_ar, r_hy]; preds[r_ar['Model']] = p_ar; preds['Hybrid RF + ARIMA'] = p_hy\n"
     "print(parts['arima'].summary().tables[1])")

md("## 7. Model comparison (one table)")
code("res = pd.DataFrame(rows).sort_values('MAE').reset_index(drop=True)\n"
     "display(res.round(3))\n"
     "ax = res.set_index('Model')['MAE'].sort_values().plot.barh(figsize=(9, 5), title='Test MAE in degrees C (lower is better)')\n"
     "ax.set_xlim(res.MAE.min() * 0.95, res.MAE.max() * 1.02)\n"
     "print('Lowest MAE:', res.iloc[0].Model)")
code("last = 120\n"
     "plt.figure(figsize=(13, 4)); plt.plot(yte.index[-last:], yte.values[-last:], 'k', label='Actual')\n"
     "for n in ['Random Forest', 'XGBoost', 'Hybrid RF + ARIMA']:\n"
     "    plt.plot(yte.index[-last:], preds[n][-last:], label=n, alpha=.8)\n"
     "plt.legend(); plt.title('Actual vs forecast - last 120 test days'); plt.ylabel('C')")
md("### Interpretation (write in your own words)\n"
   "Look at the table above and answer: (1) Which model has the lowest error, and by how much? (2) Does boosting beat Random Forest here? "
   "(3) Did the hybrid RF + ARIMA beat ARIMA alone and RF alone? (4) Is the gap between the top models large or tiny?\n\n"
   "*Points from my run:* the models are extremely close (within about 0.01 C MAE). Next-day temperature is mostly explained by yesterday's temperature and the season, "
   "so even the simple Ridge baseline is hard to beat; every ensemble clearly beats the 'tomorrow = today' persistence baseline. "
   "Differences this small can be noise, so the practical choice is a simple, fast model. This matches the lecture advice: *choose the simplest model that performs well.*")

md("## 8. Explainability")
code("rf = fitted['Random Forest']\n"
     "imp = pd.Series(rf.feature_importances_, index=Xtr.columns).sort_values().tail(12)\n"
     "imp.plot.barh(figsize=(8, 5), title='Random Forest - top features')")
code("import shap\n"
     "sv = shap.TreeExplainer(fitted['XGBoost']).shap_values(Xte)\n"
     "shap.summary_plot(sv, Xte, max_display=12)")
md("**Meaning (own words):** recent temperatures (lag 1, 7-day and 30-day means) and the seasonal terms matter most; rainfall and humidity add a smaller correction "
   "(rainy days are cooler), which is exactly what the Random Forest part of the hybrid uses.")

md("## 9. Research discussion\n"
   "**RF vs gradient boosting (XGBoost, LightGBM, CatBoost).** Random Forest = bagging: many independent trees trained in parallel on bootstrap samples, averaged -> lowers *variance*, "
   "robust, little tuning, hard to overfit. Boosting = trees built one after another, each fixing the previous errors -> lowers *bias*, often more accurate, but more sensitive to tuning and noise. "
   "XGBoost: regularised, strong all-rounder. LightGBM: fastest, leaf-wise growth, best for big data. CatBoost: native categorical features, good defaults, slower to train. "
   "On this data all of them land at nearly the same error, so speed and simplicity decide.\n\n"
   "**Tabular vs image/text.** On tabular data tree ensembles are fast, need little preprocessing, handle mixed features and are explainable. "
   "On images and text raw pixels/words have no meaningful single-column splits, so CNNs and transformers that learn features win; ensembles would need hand-made features and lose. "
   "Ensembles also use more memory and are harder to interpret than a single tree.\n\n"
   "**Why a hybrid for time series?** Trees cannot extrapolate trend or repeat a smooth season well; ARIMA can. ARIMA handles that part, the Random Forest handles the non-linear leftover.")

md("## 10. Dashboard\nRun locally: `python run_all.py` then `python -m streamlit run app.py` (tabs: dataset, model comparison, actual vs forecast, feature importance, forecast a day).")
code("res.to_csv('results.csv', index=False)\nprint('saved results.csv')")

md("## 11. Conclusion & limitations\n"
   "- Best model by MAE on the 2023-2025 test period: see section 7 (differences between top models are tiny).\n"
   "- Bagging, boosting, stacking and the RF + ARIMA hybrid were all compared on the same split.\n"
   "- Limitations: one city, daily data only, reanalysis-based values (not a single weather station), next-day horizon only; longer horizons and extreme events (floods) need more work.\n"
   "- Future work: rainfall forecasting, more cities (Kandy, Jaffna), Prophet / LSTM comparison.\n\n"
   "## 12. References\n"
   "- Open-Meteo Historical Weather API: https://open-meteo.com (CC BY 4.0)\n"
   "- scikit-learn, XGBoost, LightGBM, CatBoost, statsmodels documentation\n"
   "- Lecture notes: Ensemble Learning, Nov 2026")

nb.cells = C
nbf.write(nb, "Ensemble_Dashboard.ipynb")
