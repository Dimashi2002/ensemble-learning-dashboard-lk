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
      ["Name: Wickramage D.N      Index: 224215R",
       "Real Sri Lankan data: Colombo daily weather 2010-2025",
       "Goal: forecast tomorrow's temperature",
       "Bagging + Boosting + Stacking + RF-ARIMA hybrid"], size=28)
slide("Innovation: RF + ARIMA hybrid",
      ["ARIMA captures trend + yearly season",
       "Random Forest learns ARIMA's leftover errors from recent rain, humidity, wind",
       "Final forecast = ARIMA forecast + RF correction",
       "Train 2010-2022, test 2023-2025 (no shuffling)"], size=28)
slide("Models compared (same split, same metrics)",
      ["Bagging: Random Forest, Bagging, Extra Trees", "Boosting: XGBoost, LightGBM, CatBoost",
       "Stacking: RF + XGB + LGBM -> Ridge", "Hybrid: RF + ARIMA",
       "Data: Open-Meteo archive, 5,844 days, Colombo"], size=28)
tab = r.reset_index()[["Model", "MAE", "RMSE", "R2"]].head(8)
slide("Results (test 2023-2025)",
      [f"Lowest MAE: {best} ({g(best):.3f} C)",
       f"Hybrid {g('Hybrid RF + ARIMA'):.3f} beats ARIMA alone {g('SARIMA (ARIMA + yearly season)'):.3f}",
       f"RF {g('Random Forest'):.3f} | XGB {g('XGBoost'):.3f} | LGBM {g('LightGBM'):.3f} | CatBoost {g('CatBoost'):.3f}",
       f"All beat 'tomorrow = today' ({g('Persistence (yesterday)'):.3f})",
       "Top models differ by ~0.006 C: simple model is enough"], tab)
slide("LIVE DEMO  (switching to the running dashboard)",
      ["1. Dataset tab - monthly temperature, rain seasons", "2. Model comparison - table + bar chart",
       "3. Actual vs forecast - RF vs hybrid", "4. Feature importance - what drives the forecast",
       "5. Forecast a chosen day", "Links: GitHub + Colab in submission"], size=28)
prs.save("slides/Presentation.pptx")

script = f"""# 3-MINUTE DEMO SCRIPT  (slides 1:15  +  LIVE dashboard 1:45)

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
The lowest error was {best} with MAE {g(best):.3f} degrees. The hybrid got {g('Hybrid RF + ARIMA'):.3f}, better than ARIMA alone at {g('SARIMA (ARIMA + yearly season)'):.3f}. Random Forest {g('Random Forest'):.3f}, XGBoost {g('XGBoost'):.3f}. All beat the naive baseline of {g('Persistence (yesterday)'):.3f}, but the top models differ by only about 0.006 degrees, so a simple model is enough.

**1:15-3:00 | Slide 5 -> SWITCH TO THE BROWSER (live demo, about 1:45)**
- (1:15) "Here is my running dashboard." Dataset tab: choose temp_mean, then rain_mm. "You can see the two monsoon rain seasons."
- (1:40) Model comparison tab: show the table, switch metric MAE -> Train_seconds. "Random Forest and boosting are close; stacking and the hybrid cost more time."
- (2:05) Actual vs forecast tab: select Random Forest and Hybrid RF + ARIMA. "Both follow the real curve."
- (2:25) Feature importance tab: "Yesterday's temperature and the season matter most."
- (2:40) Forecast tab: pick a date, choose a model. "The model forecasts that day using only earlier weather and shows the error."
- (2:52) "Ensembles beat the baseline, the hybrid improves ARIMA, and the lesson: choose the simplest model that performs well. Thank you."
"""
open("slides/Video_Script_3min.md", "w", encoding="utf-8").write(script)
print("slides + script saved")
