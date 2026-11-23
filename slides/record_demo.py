"""Builds the silent demo video, in parts, ready for voice-over.
 - Slides come from the author's Presentation_Sentences.pptx, exported to video_build/pptx_slides/Slide1..5.PNG
 - The dashboard is recorded live with Playwright (Streamlit top bar / Deploy button hidden)
 - Output: Video_Parts/Part01..Part11 MP4 clips + one full MP4
Run from the project folder:  python slides/record_demo.py"""
import os, sys, time, glob, shutil, subprocess, urllib.request
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT = "video_build"; PARTS = "Video_Parts"; os.makedirs(OUT, exist_ok=True); os.makedirs(PARTS, exist_ok=True)
PORT = 8599; URL = f"http://localhost:{PORT}"; W, H = 1280, 720; VW, VH = 1800, 1012
HIDE = '[data-testid="stToolbar"],[data-testid="stHeader"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],header,#MainMenu{display:none !important} .block-container{padding-top:2rem !important}'

# part table: (file name, kind, slide number, duration seconds)
PLAN = [("Part01_Introduction", "slide", 1, 15), ("Part02_Idea", "slide", 2, 20), ("Part03_Method", "slide", 3, 29),
        ("Part04_Results", "slide", 4, 25), ("Part05_Start_of_demo", "slide", 5, 4),
        ("Part06_Dataset_tab", "demo", 0, 18), ("Part07_Model_comparison_tab", "demo", 0, 16), ("Part08_Actual_vs_forecast_tab", "demo", 0, 12),
        ("Part09_Feature_importance_tab", "demo", 0, 11), ("Part10_Forecast_tab", "demo", 0, 13), ("Part11_Conclusion", "demo", 0, 14)]

def enc(args): subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + args, check=True)

# ---------------- record the dashboard in timed parts ----------------
srv = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true", "--server.port", str(PORT),
                        "--browser.gatherUsageStats", "false"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try: urllib.request.urlopen(URL, timeout=2); break
    except Exception: time.sleep(1)

def pick(page, label, option):
    page.get_by_label(label, exact=True).first.click(); page.wait_for_timeout(500)
    page.get_by_role("option", name=option, exact=True).first.click()

marks = {}
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": VW, "height": VH}, record_video_dir=OUT, record_video_size={"width": VW, "height": VH})
        t0 = time.time(); page = ctx.new_page(); page.goto(URL); page.wait_for_selector("text=Colombo Next-Day", timeout=90000)
        page.add_style_tag(content=HIDE); wait = page.wait_for_timeout; wait(2500); T0 = time.time()   # recording starts here
        def part(name, dur, actions):
            start = time.time() - T0; actions()
            left = dur - (time.time() - T0 - start)
            if left > 0: wait(int(left * 1000))
            marks[name] = (start, dur)
        part("Part06_Dataset_tab", 18, lambda: (wait(5000), pick(page, "Variable", "rain_mm"), wait(5000), page.mouse.wheel(0, 500), wait(2500), page.mouse.wheel(0, -500)))
        part("Part07_Model_comparison_tab", 16, lambda: (page.get_by_role("tab", name="Model comparison").click(), wait(6000), pick(page, "Metric", "Train_seconds")))
        part("Part08_Actual_vs_forecast_tab", 12, lambda: page.get_by_role("tab", name="Actual vs forecast").click())
        part("Part09_Feature_importance_tab", 11, lambda: page.get_by_role("tab", name="Feature importance").click())
        part("Part10_Forecast_tab", 13, lambda: page.get_by_role("tab", name="Forecast tomorrow").click())
        part("Part11_Conclusion", 14, lambda: None)
        ctx.close(); b.close()
finally:
    srv.terminate()
webm = max(glob.glob(f"{OUT}/*.webm"), key=os.path.getmtime)
TRIM = (T0 - t0)   # seconds of video before recording starts (page creation -> T0)
shutil.move(webm, f"{OUT}/demo.webm")

# ---------------- cut parts ----------------
clips = []
for name, kind, n, dur in PLAN:
    out = f"{PARTS}/{name}.mp4"
    if kind == "slide":
        enc(["-loop", "1", "-i", f"{OUT}/pptx_slides/Slide{n}.PNG", "-t", str(dur), "-r", "25", "-vf", f"scale={W}:{H}", "-pix_fmt", "yuv420p", "-c:v", "libx264", out])
    else:
        st, d = marks[name]
        enc(["-ss", f"{TRIM + st:.2f}", "-i", f"{OUT}/demo.webm", "-t", str(d), "-vf", f"scale={W}:{H},fps=25", "-pix_fmt", "yuv420p", "-c:v", "libx264", out])
    clips.append(out)

with open(f"{OUT}/list.txt", "w") as f: f.writelines(f"file '../{c}'\n" for c in clips)
enc(["-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", "Demo_Video_FULL_SILENT_add_voiceover.mp4"])
print("done: parts in", PARTS, "| total seconds:", sum(x[3] for x in PLAN))
