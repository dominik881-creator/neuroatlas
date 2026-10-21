# Źródła i licencje / Credits & licenses

## Model 3D – `brain.glb`

**Licencja / License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**

- **Z-Anatomy – The libre 3D atlas of anatomy** – CC BY-SA 4.0 – https://www.z-anatomy.com/ · https://github.com/Z-Anatomy
- **BodyParts3D** © The Database Center for Life Science (DBCLS) – [CC BY-SA 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en) – https://lifesciencedb.jp/bp3d/ (Z-Anatomy opiera się na tych danych / Z-Anatomy is based on this data)

**Zmiany / Changes:** z atlasu Z-Anatomy wybrano obiekty mózgowia i wyeksportowano je do jednego pliku glTF (`brain.glb`).
Brain objects were selected from the Z-Anatomy atlas and exported to a single glTF file (`brain.glb`).

Zgodnie z warunkiem „na tych samych warunkach” (ShareAlike) plik `brain.glb` i każda jego przeróbka muszą być udostępniane na licencji CC BY-SA 4.0.
Under the ShareAlike condition, `brain.glb` and any derivative of it must be shared under CC BY-SA 4.0.

## Kod i treści / Code and texts

Kod NeuroAtlas (`index.html`, `app/`) oraz opisy struktur: [licencja MIT](LICENSE).
Poziomy 3–6 (tkanka, neuron, synapsa, błona) to modele proceduralne tworzone w kodzie, niezależne od `brain.glb`.

## Biblioteki / Libraries (wczytywane z CDN / loaded from CDN)

- [three.js](https://threejs.org/) – MIT
- [three-mesh-bvh](https://github.com/gkjohnson/three-mesh-bvh) – MIT
- Czcionki / Fonts: [Manrope](https://fonts.google.com/specimen/Manrope), [Newsreader](https://fonts.google.com/specimen/Newsreader) – SIL Open Font License 1.1
- Aplikacja Android / Android app: [Capacitor](https://capacitorjs.com/) – MIT
