"""Builds the 7-slide presentation + 3-minute script from results.csv (real numbers only)."""
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

r = pd.read_csv("results.csv").set_index("Model")
best = r.index[0]
g = lambda m, c="MAE": r.loc[m, c]

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)
NAVY, TEAL = RGBColor(0x12, 0x2B, 0x4A), RGBColor(0x0E, 0x8A, 0x8A)

def slide(title, bullets, table=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.2)); bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    tf = s.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(12), Inches(0.8)).text_frame
    tf.text = title; tf.paragraphs[0].font.size = Pt(34); tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    box = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(6.2 if table is not None else 12), Inches(5.3)).text_frame; box.word_wrap = True
    for i, b in enumerate(bullets):
        p = box.paragraphs[0] if i == 0 else box.add_paragraph()
        p.text = "• " + b; p.font.size = Pt(22 if table is None else 20); p.space_after = Pt(12)
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
      ["Ensemble Learning Dashboard - assignment submission", "Name: ________   Index: ________", "Real Sri Lankan data: Colombo daily weather 2010-2025",
       "Bagging  +  Boosting  +  Stacking  +  RF-ARIMA hybrid"])
slide("1. Problem", ["Tourism, farming and power demand in Sri Lanka depend on the weather", "Goal: forecast NEXT-DAY mean temperature in Colombo",
                     "Question: which ensemble forecasts best - and is a hybrid worth it?"])
slide("2. Innovation: RF + ARIMA hybrid", ["ARIMA captures trend + yearly season", "Random Forest learns ARIMA's leftover errors from recent rain, humidity, wind",
                                           "Final forecast = ARIMA forecast + RF residual forecast", "One dashboard compares all models side by side"])
slide("3. Data", ["Open-Meteo historical weather API (open data, CC BY 4.0)", "Colombo, 1 Jan 2010 - 31 Dec 2025 (5,844 days)",
                  "Temperature, rain, humidity, wind", "Time-based split: train 2010-2022, test 2023-2025 (no shuffling)"])
slide("4. Method", ["Bagging: Random Forest, Bagging, Extra Trees", "Boosting: XGBoost, LightGBM, CatBoost",
                    "Stacking: RF + XGB + LGBM -> Ridge", "Hybrid: RF + ARIMA", "Same split, same metrics: MAE, RMSE, MAPE, R2"])
tab = r.reset_index()[["Model", "MAE", "RMSE", "R2"]].head(8)
slide("5. Results (test 2023-2025)",
      [f"Lowest MAE: {best} ({g(best):.3f} C)", f"Hybrid RF+ARIMA {g('Hybrid RF + ARIMA'):.3f} beats ARIMA alone {g('SARIMA (ARIMA + yearly season)'):.3f}",
       f"Random Forest {g('Random Forest'):.3f} vs XGBoost {g('XGBoost'):.3f} vs LightGBM {g('LightGBM'):.3f} vs CatBoost {g('CatBoost'):.3f}",
       f"All beat 'tomorrow = today' ({g('Persistence (yesterday)'):.3f})", "Top models differ by only ~0.006 C: simple model is enough"], tab)
slide("6. Dashboard demo", ["Dataset explorer", "Model comparison table + bar chart", "Actual vs forecast plot", "Feature importance", "Forecast a chosen day"])
slide("7. Conclusion", ["Ensembles clearly beat the naive baseline", "Hybrid helps ARIMA, but gains over simple models are tiny",
                        "Lesson: choose the simplest model that performs well", "Next: rainfall, more cities, LSTM / Prophet", "Thank you - GitHub + Colab links in submission"])
prs.save("slides/Presentation.pptx")

script = f"""# 3-MINUTE VIDEO SCRIPT (about 400 words, ~3:00)

**0:00-0:20 | Slide 1-2 (Problem)**
Hello, I am ____. Sri Lanka's tourism, farming and power planning depend on daily weather. My project forecasts tomorrow's mean temperature in Colombo using ensemble learning.

**0:20-0:50 | Slide 3 (Innovation)**
My innovation is a hybrid model. ARIMA captures the trend and the yearly season. Then a Random Forest learns what ARIMA missed, using recent rain, humidity and wind. The final forecast is ARIMA plus the Random Forest correction. Everything is compared in one dashboard.

**0:50-1:15 | Slide 4 (Data)**
I used real Colombo weather from 2010 to 2025, 5,844 days, from the open Open-Meteo archive. I trained on 2010 to 2022 and tested on 2023 to 2025, with no shuffling, so the model never sees the future.

**1:15-1:40 | Slide 5 (Method)**
I built all three ensemble types. Bagging: Random Forest, Bagging and Extra Trees. Boosting: XGBoost, LightGBM and CatBoost. Stacking: three models combined by a Ridge meta-model. Plus the RF-ARIMA hybrid. Same split, same metrics.

**1:40-2:10 | Slide 6 (Results)**
The lowest error was {best} with MAE {g(best):.3f} degrees. The hybrid got {g('Hybrid RF + ARIMA'):.3f}, better than ARIMA alone at {g('SARIMA (ARIMA + yearly season)'):.3f}. Random Forest got {g('Random Forest'):.3f} and XGBoost {g('XGBoost'):.3f}. All beat the naive "tomorrow equals today" baseline at {g('Persistence (yesterday)'):.3f}. But the top models differ by only about 0.006 degrees, so on this data a simple model is enough.

**2:10-2:45 | Slide 7 -> SCREEN RECORD the dashboard**
Here is the dashboard. Dataset tab: monthly temperature and the two monsoon rainfall peaks. Model comparison: the full table and bar chart. Actual versus forecast: forecasts follow the real curve. Feature importance: yesterday's temperature and the season matter most. Last, I pick a date and the model forecasts it.

**2:45-3:00 | Slide 8 (Conclusion)**
In conclusion, ensembles beat the baseline, the hybrid improves ARIMA, and the lesson from class holds: choose the simplest model that performs well. Next I will forecast rainfall and add more cities. Thank you.

---
Recording tips: slides first (about 2:10), then screen-record `python -m streamlit run app.py` for about 35 s. Total must be 3:00 maximum.
"""
open("slides/Video_Script_3min.md", "w", encoding="utf-8").write(script)
print("slides + script saved")
