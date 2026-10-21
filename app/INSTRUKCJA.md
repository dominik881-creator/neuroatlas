# NeuroAtlas – aplikacja na Androida

Folder `app` zamienia `index.html` (NeuroAtlas) w aplikację Android (Capacitor 8). Apka działa **offline**: Three.js, three-mesh-bvh, czcionki i `brain.glb` są spakowane w środku (ok. 8 MB).

## Czego potrzebujesz (jednorazowo)
- **Node.js 22 lub nowszy** (`node -v`). Capacitor 8 nie ruszy na starszym.
- **Android Studio** w aktualnej wersji (z Android SDK 36).
- **Python 3**.

## Układ folderów
```
neuroatlas\            ← główny folder (repozytorium)
  index.html           ← NeuroAtlas (ze znacznikiem __MODEL_BASE64__, bez osadzonego modelu)
  brain.glb
  app\                 ← ten folder
    package.json, capacitor.config.json, przygotuj_www.py
    ikony\res\         ← ikona, ekran startowy
```

## Pierwsze zbudowanie
W PowerShellu w folderze `app`:
```
npm install
npm run www
npx cap add android
npm run ikony
npx cap sync android
npx cap open android
```
W Android Studio: poczekaj na Gradle sync, potem **Build › Generate App Bundles or APKs › Generate APKs**. Gotowy plik znajdziesz w `android\app\build\outputs\apk\debug\app-debug.apk`. Wyślij go na telefon i zainstaluj (zgoda na „nieznane źródła”).
Możesz też podłączyć telefon kablem (debugowanie USB) i kliknąć ▶ Run.

## Aktualizacja po zmianach w NeuroAtlas
Gdy podmienisz `index.html` na nową wersję, uruchom:
```
npm run www
npx cap sync android
```
i zbuduj APK ponownie. `npx cap add android` i `npm run ikony` robisz tylko raz (jeśli kiedyś usuniesz folder `android`, powtórz oba).

## Co robi `przygotuj_www.py`
1. Podmienia adresy jsdelivr na lokalne pliki z `node_modules` (`www/lib`).
2. Zamienia Google Fonts na lokalne czcionki z polskimi znakami (`www/fonts`).
3. Odsuwa przyciski od paska stanu, paska gestów i wycięcia aparatu (apka rysuje się na całym ekranie, model 3D też).
4. Dodaje obsługę systemowego **Wstecz**: zamyka okienko/panel → cofa o poziom (synapsa/błona → neuron → tkanka → mózg) → na mózgu zamyka apkę.
5. Kopiuje `brain.glb` obok `index.html`, skąd strona wczytuje go sama.

## Problemy
- **„Brak node_modules”** – najpierw `npm install`.
- **„Użyj pliku ze znacznikiem __MODEL_BASE64__”** – podajesz wersję `_embedded`. Użyj zwykłej.
- **Biała ikona Capacitora** – zapomniałeś `npm run ikony` po `npx cap add android`.
- **Gradle: wymaga JDK 21** – w Android Studio: Settings › Build Tools › Gradle › Gradle JDK = wbudowany JBR 21.
- **Podgląd błędów z telefonu** – podłącz telefon, w Chrome na komputerze otwórz `chrome://inspect`.

Model: Z-Anatomy – The libre 3D atlas of anatomy – CC BY-SA 4.0.
