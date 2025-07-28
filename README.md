# SteelSeries Sonar → Wave Link EQ Preset Converter

This tool converts EQ presets from the `database.db` file used by **SteelSeries Sonar** into **Elgato Wave Link XML preset format**.

It includes:
- ✅ Filter type conversion (e.g., `peakingEQ` → `2.0`)
- ✅ Accurate dB to XML gain value mapping (logarithmic)
- ✅ GUI for file selection (no terminal required)
- ✅ Example presets (CS2, Valorant, CSGO, WoW)

---

## 🔧 Features

- Extracts all EQ filters from the `parametricEQ` section
- Converts `gain` from real dB values to Wave Link's XML format using a fitted logarithmic scale
- Maps Sonar filter types to Wave Link types (e.g., highpass, shelving, etc.)
- Easy-to-use file selection for input and output
- Works with presets where `vad = 1` and `name` is not empty in database.db

---

## 🚀 How to Use

1. Run `steelseries-to-wavelink-v1.0.exe`
2. Select your `database.db` from SteelSeries Sonar, usually in path: C:\ProgramData\SteelSeries\GG\apps\sonar\db
3. Select an output folder (e.g., Desktop or Downloads)
4. Converted `.xml` files will be placed in that folder


## 🗂 Example Presets Included

You'll find a all the standard EQs as example exports in the `presets/` folder, including:
- ✅ CS2 by FaZe
- ✅ Valorant by FaZe
- ✅ CSGO by FaZe
- ✅ World of Warcraft

---

## 📦 Requirements (if running Python version)
- Python 3.7+
- `tkinter` (for GUI)
- `lxml` (optional, but recommended)

Install via:
```bash
pip install -r requirements.txt
```

---

## 🛠 Building an EXE (Optional)

If you'd like to build your own `.exe` version:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed converter.py
```

The final EXE will be located in the `dist/` folder.

---

## 🔄 License

MIT – free for personal and commercial use. Contributions welcome!