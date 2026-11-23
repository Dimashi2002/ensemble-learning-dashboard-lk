# 3-MINUTE DEMO SCRIPT  (slides 1:15  +  LIVE dashboard 1:45)

BEFORE YOU START (screen-share setup):
1. Open a terminal in the project folder and run:  python -m streamlit run app.py
2. Open http://localhost:8501 in the browser, keep PowerPoint (Presentation.pptx) in another window.
3. Share your screen, start recording.

**0:00-0:15 | Slide 1**
Hello, I am Wickramage, index 224215R. My project forecasts tomorrow's temperature in Colombo using ensemble learning on real Sri Lankan weather data.

**0:15-0:35 | Slide 2 (innovation)**
My idea is a hybrid: ARIMA captures trend and the yearly season, and a Random Forest learns what ARIMA missed from recent rain, humidity and wind. Forecast equals ARIMA plus the Random Forest correction.

**0:35-0:50 | Slide 3**
I compared all three ensemble types on the same split, 2010 to 2022 for training and 2023 to 2025 for testing: bagging, boosting, stacking, and the hybrid.

**0:50-1:15 | Slide 4 (results)**
The lowest error was Ridge (baseline) with MAE 0.424 degrees. The hybrid got 0.426, better than ARIMA alone at 0.429. Random Forest 0.427, XGBoost 0.424. All beat the naive baseline of 0.453, but the top models differ by only about 0.006 degrees, so a simple model is enough.

**1:15-3:00 | Slide 5 -> SWITCH TO THE BROWSER (live demo, about 1:45)**
- (1:15) "Here is my running dashboard." Dataset tab: choose temp_mean, then rain_mm. "You can see the two monsoon rain seasons."
- (1:40) Model comparison tab: show the table, switch metric MAE -> Train_seconds. "Random Forest and boosting are close; stacking and the hybrid cost more time."
- (2:05) Actual vs forecast tab: select Random Forest and Hybrid RF + ARIMA. "Both follow the real curve."
- (2:25) Feature importance tab: "Yesterday's temperature and the season matter most."
- (2:40) Forecast tab: pick a date, choose a model. "The model forecasts that day using only earlier weather and shows the error."
- (2:52) "Ensembles beat the baseline, the hybrid improves ARIMA, and the lesson: choose the simplest model that performs well. Thank you."
