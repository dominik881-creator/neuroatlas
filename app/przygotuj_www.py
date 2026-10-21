"""Przygotowuje folder www/ aplikacji NeuroAtlas (Capacitor) z pliku HTML projektu.

Użycie (w folderze app, po `npm install`):
    python przygotuj_www.py ..\\index.html [..\\brain.glb]

Co robi:
  1. podmienia biblioteki z internetu (jsdelivr) na lokalne kopie z node_modules  → apka działa offline,
  2. podmienia czcionki Google Fonts na lokalne (Manrope, Newsreader — z polskimi znakami),
  3. odsuwa przyciski od paska stanu i paska gestów, dokleja obsługę systemowego przycisku Wstecz (cofa o poziom, na końcu zamyka apkę),
  4. kopiuje brain.glb obok strony (wczytywany przez fetch, więc NIE używaj wersji *_embedded),
  5. zapisuje wynik jako www/index.html.
"""
import json
import pathlib
import re
import shutil
import sys

APP = pathlib.Path(__file__).resolve().parent
NM = APP / "node_modules"
WWW = APP / "www"

if len(sys.argv) < 2:
    sys.exit(__doc__)
src = pathlib.Path(sys.argv[1]).resolve()
glb = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_name("brain.glb")
if not src.exists():
    sys.exit(f"Brak pliku {src}")
if not glb.exists():
    sys.exit(f"Brak modelu {glb} — podaj ścieżkę jako drugi argument")
if not (NM / "three").exists():
    sys.exit("Brak node_modules — najpierw uruchom: npm install")

html = src.read_text(encoding="utf-8")
if html.count("__MODEL_BASE64__") != 1:
    sys.exit("Użyj pliku ze znacznikiem __MODEL_BASE64__ (nie wersji *_embedded.html)")

# --- 1. biblioteki: jsdelivr → ./lib (sprawdzenie zgodności wersji) ---
def pkg_version(name):
    return json.loads((NM / name / "package.json").read_text(encoding="utf-8"))["version"]

for name in ("three", "three-mesh-bvh"):
    used = re.findall(rf"cdn\.jsdelivr\.net/npm/{re.escape(name)}@([\d.]+)/", html)
    if used and used[0] != pkg_version(name):
        print(f"UWAGA: HTML używa {name}@{used[0]}, a w node_modules jest {pkg_version(name)} — zmień wersję w package.json i zrób npm install")
html = re.sub(r"https://cdn\.jsdelivr\.net/npm/three@[\d.]+/", "./lib/three/", html)
html = re.sub(r"https://cdn\.jsdelivr\.net/npm/three-mesh-bvh@[\d.]+/", "./lib/three-mesh-bvh/", html)

# --- 2. czcionki: Google Fonts → lokalne ---
html = "\n".join(l for l in html.split("\n") if "fonts.googleapis.com" not in l and "fonts.gstatic.com" not in l)
html = html.replace("<title>NeuroAtlas</title>", '<title>NeuroAtlas</title>\n<link rel="stylesheet" href="fonts/fonts.css">', 1)

# --- 2b. pasek stanu / pasek gestów / wycięcie aparatu ---
# Apka rysuje się pod paskami systemu (edge-to-edge). Model 3D zostaje na pełnym ekranie,
# a przyciski i panele odsuwamy o wysokość pasków (Capacitor podaje je jako --safe-area-inset-*).
SAFE = """<style id="app-safe-area">
:root{--sat:var(--safe-area-inset-top,env(safe-area-inset-top,0px));--sab:var(--safe-area-inset-bottom,env(safe-area-inset-bottom,0px));--sal:var(--safe-area-inset-left,env(safe-area-inset-left,0px));--sar:var(--safe-area-inset-right,env(safe-area-inset-right,0px))}
#top,#crumbs,#dock,#panel{margin-top:var(--sat)}
#panel,#dock,#ladder,#foot,#diag,#toast,#hint,#scope,#mscope,#sscope{margin-bottom:var(--sab)}
#top,#crumbs,#dock,#panel,#ladder,#foot,#diag,#scope,#mscope,#sscope{margin-left:var(--sal)}
#top,#crumbs,#dock,#panel,#foot,#scope,#mscope,#sscope{margin-right:var(--sar)}
@media (max-width:760px){ #dock{transform:translateY(calc(100% + 20px + var(--sab)))} #panel{transform:translateY(calc(100% + 30px + var(--sab)))} }
@media (max-height:500px) and (min-width:761px){ #dock{transform:translateX(calc(-100% - 24px - var(--sal)))} }
#dock.open,#panel.open{transform:none}
</style>
</head>"""
if html.count("</head>") != 1:
    sys.exit("Nie znaleziono </head>")
html = html.replace("</head>", SAFE, 1)

# --- 3. przycisk Wstecz (Android) ---
BACK = r"""
/* ---------- aplikacja Android (Capacitor): systemowy przycisk Wstecz cofa o poziom ---------- */
const CapApp = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App;
if (CapApp) CapApp.addListener('backButton', () => {
  if (LV.busy) return;
  if (!$('#diag').hidden){ $('#diag').hidden = true; return; }
  if ($('#dock').classList.contains('open')){ $('#dock').classList.remove('open'); return; }
  if (!results.hidden){ q.value = ''; results.hidden = true; q.blur(); return; }
  if (tip.classList.contains('on')){ hideTip(); return; }
  if (panel.classList.contains('open')){ closePanel(); return; }
  if (LV.view === 'membrane' || LV.view === 'synapse') return deepToNeuron(false);
  if (LV.view === 'neuron') return neuronToTissue(false);
  if (LV.view === 'tissue') return exitToBrain(LV.area);
  CapApp.exitApp();
});
"""
marker = "\nboot();\n</script>"
if html.count(marker) != 1:
    sys.exit("Nie znaleziono wywołania boot() — struktura pliku się zmieniła")
html = html.replace(marker, BACK + marker)

leftover = re.findall(r'(?:src|href)="https://(?!www\.z-anatomy|creativecommons|lifesciencedb)[^"]+"|"https://cdn[^"]+"', html)
if leftover:
    print("UWAGA: zostały odwołania do internetu:", leftover[:5])

# --- 4. pliki ---
if WWW.exists():
    shutil.rmtree(WWW)
LIB = [
    ("three/build/three.module.js", "three/build/three.module.js"),
    ("three/build/three.core.js", "three/build/three.core.js"),
    ("three/examples/jsm/controls/OrbitControls.js", "three/examples/jsm/controls/OrbitControls.js"),
    ("three/examples/jsm/loaders/GLTFLoader.js", "three/examples/jsm/loaders/GLTFLoader.js"),
    ("three/examples/jsm/loaders/DRACOLoader.js", "three/examples/jsm/loaders/DRACOLoader.js"),
    ("three/examples/jsm/libs/meshopt_decoder.module.js", "three/examples/jsm/libs/meshopt_decoder.module.js"),
    ("three/examples/jsm/utils/BufferGeometryUtils.js", "three/examples/jsm/utils/BufferGeometryUtils.js"),
    ("three-mesh-bvh/build/index.module.js", "three-mesh-bvh/build/index.module.js"),
]
for a, b in LIB:
    dst = WWW / "lib" / b
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(NM / a, dst)

FONTS = [
    ("@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2", "manrope-latin.woff2"),
    ("@fontsource-variable/manrope/files/manrope-latin-ext-wght-normal.woff2", "manrope-latin-ext.woff2"),
    ("@fontsource/newsreader/files/newsreader-latin-400-italic.woff2", "newsreader-latin-400i.woff2"),
    ("@fontsource/newsreader/files/newsreader-latin-ext-400-italic.woff2", "newsreader-latin-ext-400i.woff2"),
    ("@fontsource/newsreader/files/newsreader-latin-500-italic.woff2", "newsreader-latin-500i.woff2"),
    ("@fontsource/newsreader/files/newsreader-latin-ext-500-italic.woff2", "newsreader-latin-ext-500i.woff2"),
]
(WWW / "fonts").mkdir(parents=True, exist_ok=True)
for a, b in FONTS:
    shutil.copy2(NM / a, WWW / "fonts" / b)
LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
LATIN_EXT = "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF"
css = []
for f, rng in (("manrope-latin-ext.woff2", LATIN_EXT), ("manrope-latin.woff2", LATIN)):
    css.append(f"@font-face{{font-family:'Manrope';font-style:normal;font-display:swap;font-weight:200 800;src:url({f}) format('woff2');unicode-range:{rng}}}")
for w in (400, 500):
    for sub, rng in (("latin-ext", LATIN_EXT), ("latin", LATIN)):
        css.append(f"@font-face{{font-family:'Newsreader';font-style:italic;font-display:swap;font-weight:{w};src:url(newsreader-{sub}-{w}i.woff2) format('woff2');unicode-range:{rng}}}")
(WWW / "fonts" / "fonts.css").write_text("\n".join(css) + "\n", encoding="utf-8")

shutil.copy2(glb, WWW / "brain.glb")
(WWW / "index.html").write_text(html, encoding="utf-8")
size = sum(p.stat().st_size for p in WWW.rglob("*") if p.is_file()) / 1e6
print(f"Gotowe: {WWW} ({size:.1f} MB). Teraz: npx cap sync android")
