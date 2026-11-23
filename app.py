"""Colombo Weather Ensemble Dashboard.  Run:  python -m streamlit run app.py"""
import re, joblib, numpy as np, pandas as pd, plotly.express as px, plotly.graph_objects as go, streamlit as st
import ens

st.set_page_config(page_title="Colombo Temperature - Ensemble Dashboard", layout="wide")
slug = lambda n: re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_")

@st.cache_data
def load():
    return (pd.read_csv("data/colombo_weather_clean.csv", parse_dates=["date"], index_col="date"),
            pd.read_csv("results.csv"), pd.read_csv("predictions.csv", parse_dates=["date"]))
df, res, pred = load()

st.title("Colombo Next-Day Temperature Forecast - Ensemble Learning Dashboard")
st.caption("Bagging vs Boosting vs Stacking vs RF+ARIMA hybrid | Real Colombo weather 2010-2025 (Open-Meteo) | "
           "Train 2010-2022, test 2023-2025")
t1, t2, t3, t4, t5 = st.tabs(["Dataset", "Model comparison", "Actual vs forecast", "Feature importance", "Forecast tomorrow"])

with t1:
    c = st.columns(4)
    c[0].metric("Days of data", f"{len(df):,}"); c[1].metric("Mean temp (C)", f"{df.temp_mean.mean():.1f}")
    c[2].metric("Rainiest day (mm)", f"{df.rain_mm.max():.0f}"); c[3].metric("Period", f"{df.index.min().year}-{df.index.max().year}")
    var = st.selectbox("Variable", ["temp_mean", "rain_mm", "humidity", "wind_max"])
    st.plotly_chart(px.line(df[var].resample("MS").mean().reset_index(), x="date", y=var, title=f"Monthly mean of {var}"), width="stretch")
    mm = df.groupby(df.index.month)[var].mean().reset_index().rename(columns={"date": "month"})
    st.plotly_chart(px.bar(mm, x="date" if "date" in mm else mm.columns[0], y=var, title="Seasonal pattern (by month)"), width="stretch")
    st.dataframe(df.tail(30), width="stretch")

with t2:
    metric = st.selectbox("Metric", ["MAE", "RMSE", "MAPE", "R2", "Train_seconds"])
    st.dataframe(res.round(3), width="stretch")
    st.plotly_chart(px.bar(res.sort_values(metric, ascending=(metric != "R2")), x="Model", y=metric, color="Type"), width="stretch")
    st.info(f"Lowest MAE: **{res.iloc[0].Model}** (MAE {res.iloc[0].MAE:.3f} C). "
            "Differences between the top models are tiny - see the notebook discussion.")

with t3:
    models = st.multiselect("Models", [c for c in pred.columns if c not in ("date", "actual")], default=["Random Forest", "Hybrid RF + ARIMA"])
    days = st.slider("Show last N test days", 30, len(pred), 120)
    p = pred.tail(days); fig = go.Figure(go.Scatter(x=p.date, y=p.actual, name="Actual", line=dict(color="black")))
    for m in models: fig.add_trace(go.Scatter(x=p.date, y=p[m], name=m))
    fig.update_layout(yaxis_title="Temperature (C)"); st.plotly_chart(fig, width="stretch")

with t4:
    name = st.selectbox("Model", ["Random Forest", "XGBoost", "LightGBM", "Extra Trees"])
    m = joblib.load(f"saved_models/{slug(name)}.joblib")
    cols = ens.make_features(df).drop(columns=ens.TARGET).columns
    imp = pd.Series(m.feature_importances_, index=cols).sort_values().tail(12)
    st.plotly_chart(px.bar(imp, orientation="h", title=f"Top features - {name}"), width="stretch")

with t5:
    st.write("Pick a model and a date. The model uses only weather from BEFORE that date to forecast that day's mean temperature.")
    feat = ens.make_features(df); Xall = feat.drop(columns=ens.TARGET)
    name = st.selectbox("Model", ["Random Forest", "XGBoost", "LightGBM", "CatBoost", "Extra Trees", "Ridge (baseline)"], key="fm")
    d = st.date_input("Date to forecast", value=Xall.index.max().date(), min_value=Xall.index.min().date(), max_value=Xall.index.max().date())
    ts = pd.Timestamp(d)
    if ts in Xall.index:
        f = float(joblib.load(f"saved_models/{slug(name)}.joblib").predict(Xall.loc[[ts]])[0])
        st.metric(f"Forecast for {d}", f"{f:.2f} C", delta=f"actual {feat.loc[ts, ens.TARGET]:.2f} C (error {f - feat.loc[ts, ens.TARGET]:+.2f})")
    st.caption("Tip: edit the lag values in the notebook to try 'what if' scenarios.")
