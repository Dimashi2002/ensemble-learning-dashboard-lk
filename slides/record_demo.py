"""Records a silent screen-recording of the running dashboard, paced to the demo script.
Then builds the intro slide frames and joins everything into one MP4 (voice-over to be added by the author).
Run from the project folder:  python slides/record_demo.py"""
import os, sys, time, glob, shutil, subprocess, urllib.request
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT = "video_build"; os.makedirs(OUT, exist_ok=True)
PORT = 8599; URL = f"http://localhost:{PORT}"
W, H = 1280, 720

# ---------- 1. record the dashboard ----------
srv = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true",
                        "--server.port", str(PORT), "--browser.gatherUsageStats", "false"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try: urllib.request.urlopen(URL, timeout=2); break
    except Exception: time.sleep(1)

def pick(page, label, option):
    """open a Streamlit selectbox by its label and choose an option"""
    page.get_by_label(label, exact=True).first.click(); page.wait_for_timeout(500)
    page.get_by_role("option", name=option, exact=True).first.click()

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        VW, VH = 1800, 1012
        ctx = b.new_context(viewport={"width": VW, "height": VH}, record_video_dir=OUT, record_video_size={"width": VW, "height": VH})
        t0 = time.time(); page = ctx.new_page(); page.goto(URL); page.wait_for_selector("text=Colombo Next-Day", timeout=90000)
        wait = page.wait_for_timeout
        wait(1500); TRIM = time.time() - t0 - 1.0
        wait(3500)                                                      # "Now let me show the running dashboard"
        wait(8000)                                                      # Dataset: monthly temperature
        pick(page, "Variable", "rain_mm"); wait(9000)                   # switch to rainfall (monsoons)
        page.mouse.wheel(0, 500); wait(4000); page.mouse.wheel(0, -500)
        page.get_by_role("tab", name="Model comparison").click(); wait(9000)       # table + chart (MAE)
        pick(page, "Metric", "Train_seconds"); wait(9000)                          # training time
        page.get_by_role("tab", name="Actual vs forecast").click(); wait(14000)    # RF + Hybrid vs actual
        page.get_by_role("tab", name="Feature importance").click(); wait(13000)
        page.get_by_role("tab", name="Forecast tomorrow").click(); wait(14000)      # forecast a day
        ctx.close(); b.close()
finally:
    srv.terminate()
webm = max(glob.glob(f"{OUT}/*.webm"), key=os.path.getmtime)
shutil.move(webm, f"{OUT}/demo.webm")

# ---------- 2. intro slides as video frames ----------
r = pd.read_csv("results.csv").set_index("Model"); g = lambda m: r.loc[m, "MAE"]; best = r.index[0]
def font(sz, bold=False):
    for f in (["arialbd.ttf"] if bold else []) + ["arial.ttf", "segoeui.ttf"]:
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()
def wrap(d, text, f, maxw):
    out, line = [], ""
    for w in text.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = w
    return out + [line]
slides = [
 (15, "Colombo Weather Forecasting with Ensemble Learning",
  ["Wickramage D.N  |  Index 224215R", "Forecasting tomorrow's temperature in Colombo, Sri Lanka", "Real daily weather data, 2010 to 2025"]),
 (20, "Innovation: the RF + ARIMA hybrid",
  ["ARIMA captures the trend and the yearly season.", "A Random Forest learns the errors ARIMA leaves behind, using rain, humidity and wind.",
   "Final forecast = ARIMA forecast + Random Forest correction."]),
 (25, "Data and Models",
  ["Open-Meteo archive: 5,844 days. Train 2010-2022, test 2023-2025, no shuffling.", "Bagging: Random Forest, Bagging, Extra Trees",
   "Boosting: XGBoost, LightGBM, CatBoost", "Stacking: RF + XGBoost + LightGBM with a Ridge meta-model", "Hybrid: RF + ARIMA"]),
 (25, "Results (test 2023-2025)",
  [f"Lowest MAE: {best} ({g(best):.3f} C)", f"Hybrid RF + ARIMA {g('Hybrid RF + ARIMA'):.3f} beats ARIMA alone {g('SARIMA (ARIMA + yearly season)'):.3f}",
   f"Random Forest {g('Random Forest'):.3f}  |  XGBoost {g('XGBoost'):.3f}", f"Every model beats the naive baseline ({g('Persistence (yesterday)'):.3f})",
   "Top models differ by only ~0.006 C: a simple model is enough"]),
]
parts = []
for i, (secs, title, lines) in enumerate(slides):
    im = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 130], fill=(18, 43, 74)); d.text((50, 35), title, font=font(44, True), fill="white")
    y = 190
    for ln in lines:
        for k, sub in enumerate(wrap(d, ln, font(34), W - 150)):
            d.text((70 + (0 if k == 0 else 28), y), ("•  " if k == 0 else "") + sub, font=font(34), fill=(30, 30, 30)); y += 48
        y += 22
    png = f"{OUT}/slide{i}.png"; im.save(png)
    mp4 = f"{OUT}/slide{i}.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-t", str(secs), "-r", "25", "-pix_fmt", "yuv420p",
                    "-c:v", "libx264", mp4], check=True); parts.append(mp4)

# ---------- 3. join ----------
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{TRIM:.2f}", "-i", f"{OUT}/demo.webm", "-vf", f"scale={W}:{H},fps=25", "-pix_fmt", "yuv420p",
                "-c:v", "libx264", f"{OUT}/demo.mp4"], check=True); parts.append(f"{OUT}/demo.mp4")
with open(f"{OUT}/list.txt", "w") as f: f.writelines(f"file '{os.path.basename(x)}'\n" for x in parts)
final = "Demo_Video_SILENT_add_voiceover.mp4"
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", final], check=True)
print("saved", final)
