# WORD-FOR-WORD SCRIPT: PRESENTATION + LIVE DEMO (about 3 minutes)

SETUP (do this before recording)
1. Terminal: cd into the Submission_Ensemble_Dashboard folder, then run: python -m streamlit run app.py
2. Open http://localhost:8501 in your browser. Open Presentation_Sentences.pptx in PowerPoint.
3. Share your screen and start recording. Read the lines in quotes.

======== PART 1 - PRESENTATION (0:00 to 1:15) ========

SLIDE 1 (0:00 - 0:15)
"Hello everyone. My name is Wickramage, index number 224215R. My project forecasts tomorrow's temperature in Colombo using ensemble learning, and I used real Sri Lankan weather data from 2010 to 2025."

SLIDE 2 (0:15 - 0:35)
"My innovation is a hybrid model. ARIMA captures the trend and the yearly season. Then a Random Forest learns the mistakes ARIMA leaves behind, using recent rain, humidity and wind. The final forecast is the ARIMA forecast plus the Random Forest correction. I trained on 2010 to 2022 and tested on 2023 to 2025, so the model never sees the future."

SLIDE 3 (0:35 - 0:50)
"The data comes from the open Open-Meteo archive, with 5,844 days. I built all three ensemble types: bagging with Random Forest, Bagging and Extra Trees; boosting with XGBoost, LightGBM and CatBoost; and stacking with a Ridge meta-model. I also built the hybrid. Every model uses the same split and the same metrics."

SLIDE 4 (0:50 - 1:15)
"Here are the results. The lowest error was Ridge (baseline), with an MAE of 0.424 degrees. The hybrid scored 0.426, which is better than ARIMA alone at 0.429. Random Forest scored 0.427 and XGBoost scored 0.424. Every model beat the naive baseline of 0.453. But the top models differ by only about 0.006 degrees, so on this data a simple model is enough."

======== PART 2 - LIVE DEMO (1:15 to 3:00) ========

SLIDE 5 (1:15 - 1:20)
"Now let me show the running dashboard." (SWITCH TO THE BROWSER)

TAB 1: Dataset (1:20 - 1:40)  [click the Dataset tab, then change Variable to rain_mm]
"This is the Dataset tab. Here is the monthly temperature for Colombo. When I switch to rainfall, you can see the two monsoon seasons in Sri Lanka."

TAB 2: Model comparison (1:40 - 2:05)  [click Model comparison, change Metric to MAE, then Train_seconds]
"This tab compares all the models in one table and one bar chart. By MAE, the models are very close. If I switch to training time, you can see that stacking and the hybrid cost more time, but they do not give a meaningful gain."

TAB 3: Actual vs forecast (2:05 - 2:25)  [select Random Forest and Hybrid RF + ARIMA]
"Here I plot the real temperature in black against the Random Forest and the hybrid forecast. Both follow the real curve closely."

TAB 4: Feature importance (2:25 - 2:40)  [select Random Forest]
"This chart shows what the model uses. Yesterday's temperature, the recent averages and the season matter most. Rainfall and humidity add smaller corrections."

TAB 5: Forecast a day (2:40 - 2:52)  [choose Random Forest, pick any date]
"Finally, I can pick a model and a date. The model uses only earlier weather to forecast that day, and the dashboard shows the forecast and the error against the real value."

CLOSING (2:52 - 3:00)
"In conclusion, ensembles clearly beat the baseline, the hybrid improves ARIMA, and the lesson from class holds: choose the simplest model that performs well. Thank you."

TIPS: speak slowly; if you run over 3:00, shorten Tab 1 and Tab 4. Total limit is 3 minutes.
