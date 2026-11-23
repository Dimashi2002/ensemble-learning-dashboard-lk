# 3-MINUTE VIDEO SCRIPT (about 400 words, ~3:00)

**0:00-0:20 | Slide 1-2 (Problem)**
Hello, I am Wickramage, index 224215R. Sri Lanka's tourism, farming and power planning depend on daily weather. My project forecasts tomorrow's mean temperature in Colombo using ensemble learning.

**0:20-0:50 | Slide 3 (Innovation)**
My innovation is a hybrid model. ARIMA captures the trend and the yearly season. Then a Random Forest learns what ARIMA missed, using recent rain, humidity and wind. The final forecast is ARIMA plus the Random Forest correction. Everything is compared in one dashboard.

**0:50-1:15 | Slide 4 (Data)**
I used real Colombo weather from 2010 to 2025, 5,844 days, from the open Open-Meteo archive. I trained on 2010 to 2022 and tested on 2023 to 2025, with no shuffling, so the model never sees the future.

**1:15-1:40 | Slide 5 (Method)**
I built all three ensemble types. Bagging: Random Forest, Bagging and Extra Trees. Boosting: XGBoost, LightGBM and CatBoost. Stacking: three models combined by a Ridge meta-model. Plus the RF-ARIMA hybrid. Same split, same metrics.

**1:40-2:10 | Slide 6 (Results)**
The lowest error was Ridge (baseline) with MAE 0.424 degrees. The hybrid got 0.426, better than ARIMA alone at 0.429. Random Forest got 0.427 and XGBoost 0.424. All beat the naive "tomorrow equals today" baseline at 0.453. But the top models differ by only about 0.006 degrees, so on this data a simple model is enough.

**2:10-2:45 | Slide 7 -> SCREEN RECORD the dashboard**
Here is the dashboard. Dataset tab: monthly temperature and the two monsoon rainfall peaks. Model comparison: the full table and bar chart. Actual versus forecast: forecasts follow the real curve. Feature importance: yesterday's temperature and the season matter most. Last, I pick a date and the model forecasts it.

**2:45-3:00 | Slide 8 (Conclusion)**
In conclusion, ensembles beat the baseline, the hybrid improves ARIMA, and the lesson from class holds: choose the simplest model that performs well. Next I will forecast rainfall and add more cities. Thank you.

---
Recording tips: slides first (about 2:10), then screen-record `python -m streamlit run app.py` for about 35 s. Total must be 3:00 maximum.
