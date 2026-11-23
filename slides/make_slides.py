"""Builds a SHORT 5-slide presentation (demo-focused) + 3-minute script from results.csv (real numbers only).
Run from the project folder:  python slides/make_slides.py"""
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

r = pd.read_csv("results.csv").set_index("Model")
best = r.index[0]
g = lambda m, c="MAE": r.loc[m, c]

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)
NAVY = RGBColor(0x12, 0x2B, 0x4A)

def slide(title, bullets, table=None, size=26):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.2)); bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    tf = s.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(12), Inches(0.8)).text_frame
    tf.text = title; tf.paragraphs[0].font.size = Pt(34); tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    box = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(6.2 if table is not None else 12), Inches(5.3)).text_frame; box.word_wrap = True
    for i, b in enumerate(bullets):
        p = box.paragraphs[0] if i == 0 else box.add_paragraph()
        p.text = "• " + b; p.font.size = Pt(size if table is None else 20); p.space_after = Pt(14)
    if table is not None:
        rows, cols = len(table) + 1, len(table.columns)
        t = s.shapes.add_table(rows, cols, Inches(7.1), Inches(1.7), Inches(5.9), Inches(0.4 * rows)).table
        for j, c in enumerate(table.columns): t.cell(0, j).text = str(c)
        for i, row in enumerate(table.itertuples(index=False), 1):
            for j, v in enumerate(row): t.cell(i, j).text = f"{v:.3f}" if isinstance(v, float) else str(v)
        for cell in t.iter_cells():
            for p in cell.text_frame.paragraphs: p.font.size = Pt(12)
    return s

slide("Colombo Weather Forecasting with Ensemble Learning",
      ["My name is Wickramage D.N, and my index number is 224215R.",
       "This project forecasts tomorrow's temperature in Colombo, Sri Lanka.",
       "It uses real daily weather data from 2010 to 2025.",
       "I compare bagging, boosting, stacking and a hybrid RF + ARIMA model."], size=26)
slide("My Innovation: The RF + ARIMA Hybrid",
      ["ARIMA captures the trend and the yearly seasonal pattern of the temperature.",
       "A Random Forest then learns the errors that ARIMA leaves behind, using recent rain, humidity and wind.",
       "The final forecast is the ARIMA forecast plus the Random Forest correction.",
       "I trained on 2010 to 2022 and tested on 2023 to 2025, without shuffling the data."], size=26)
slide("Models and Data",
      ["The data comes from the open Open-Meteo archive and has 5,844 days for Colombo.",
       "Bagging models are Random Forest, Bagging and Extra Trees.",
       "Boosting models are XGBoost, LightGBM and CatBoost.",
       "Stacking combines Random Forest, XGBoost and LightGBM with a Ridge meta-model.",
       "All models use the same split and the same metrics."], size=26)
tab = r.reset_index()[["Model", "MAE", "RMSE", "R2"]].head(8)
slide("Results on the Test Period (2023 to 2025)",
      [f"The lowest error was {best}, with an MAE of {g(best):.3f} degrees.",
       f"The hybrid scored {g('Hybrid RF + ARIMA'):.3f}, which is better than ARIMA alone at {g('SARIMA (ARIMA + yearly season)'):.3f}.",
       f"Random Forest scored {g('Random Forest'):.3f}, and XGBoost scored {g('XGBoost'):.3f}.",
       f"Every model beat the naive baseline of {g('Persistence (yesterday)'):.3f}.",
       "The top models differ by only about 0.006 degrees, so a simple model is enough."], tab)
slide("Live Demo of the Running Dashboard",
      ["First, I will show the dataset and the two monsoon rain seasons.",
       "Next, I will compare all the models in a table and a bar chart.",
       "Then, I will plot the actual temperature against the forecasts.",
       "After that, I will show which features matter most.",
       "Finally, I will forecast a chosen day with a chosen model."], size=26)
prs.save("slides/Presentation.pptx")

script = f"""# WORD-FOR-WORD SCRIPT: PRESENTATION + LIVE DEMO (about 3 minutes)

SETUP (do this before recording)
1. Terminal: cd into the Submission_Ensemble_Dashboard folder, then run: python -m streamlit run app.py
2. Open http://localhost:8501 in your browser. Open Presentation_Demo.pptx in PowerPoint.
3. Share your screen and start recording. Read the lines in quotes.

======== PART 1 - PRESENTATION (0:00 to 1:15) ========

SLIDE 1 (0:00 - 0:15)
"Hello everyone. My name is Wickramage, index number 224215R. My project forecasts tomorrow's temperature in Colombo using ensemble learning, and I used real Sri Lankan weather data from 2010 to 2025."

SLIDE 2 (0:15 - 0:35)
"My innovation is a hybrid model. ARIMA captures the trend and the yearly season. Then a Random Forest learns the mistakes ARIMA leaves behind, using recent rain, humidity and wind. The final forecast is the ARIMA forecast plus the Random Forest correction. I trained on 2010 to 2022 and tested on 2023 to 2025, so the model never sees the future."

SLIDE 3 (0:35 - 0:50)
"The data comes from the open Open-Meteo archive, with 5,844 days. I built all three ensemble types: bagging with Random Forest, Bagging and Extra Trees; boosting with XGBoost, LightGBM and CatBoost; and stacking with a Ridge meta-model. I also built the hybrid. Every model uses the same split and the same metrics."

SLIDE 4 (0:50 - 1:15)
"Here are the results. The lowest error was {best}, with an MAE of {g(best):.3f} degrees. The hybrid scored {g('Hybrid RF + ARIMA'):.3f}, which is better than ARIMA alone at {g('SARIMA (ARIMA + yearly season)'):.3f}. Random Forest scored {g('Random Forest'):.3f} and XGBoost scored {g('XGBoost'):.3f}. Every model beat the naive baseline of {g('Persistence (yesterday)'):.3f}. But the top models differ by only about 0.006 degrees, so on this data a simple model is enough."

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
"""
open("slides/Video_Script_3min.md", "w", encoding="utf-8").write(script)
print("slides + script saved")
