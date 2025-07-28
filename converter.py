import sqlite3
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil

# Mapping für Filtertypen
TYPE_MAPPING = {
    "highPass": "0.0",
    "lowShelving": "1.0",
    "peakingEQ": "2.0",
    "highShelving": "3.0",
    "lowPass": "4.0"
}

# Gain-Umrechnung dB → XML-Wert
def db_to_xml_gain(g):
    return 0.9673 * (2 ** (g / 5.8420))

# XML-Exportfunktion
def create_wavelink_xml(preset_name, filters, position):
    preset = ET.Element("Preset")
    info = ET.SubElement(preset, "Info", Name=preset_name)
    params = ET.SubElement(preset, "Parameters")

    for i, f in enumerate(filters, 1):
        band_prefix = f"Band {i} Filter"
        gain_converted = round(db_to_xml_gain(float(f["gain"])), 6)

        ET.SubElement(params, "PARAM", id=f"{band_prefix} Bypass", value="0.0")
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Frequency", value=str(float(f["frequency"])))
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Gain", value=str(gain_converted))
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Quality", value=str(float(f["qFactor"])))
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Type", value=f["type"])
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Visible", value="1.0")

    return minidom.parseString(ET.tostring(preset)).toprettyxml(indent="  ")

# EQ-Filter aus JSON extrahieren
def extract_filters_with_type(json_str):
    try:
        parsed = json.loads(json_str)
        eq = parsed.get("parametricEQ", {})
        filters = []
        for i in range(1, 11):
            f = eq.get(f"filter{i}")
            if f and f.get("enabled", False):
                filters.append({
                    "filter": f"filter{i}",
                    "frequency": f.get("frequency"),
                    "gain": f.get("gain"),
                    "qFactor": f.get("qFactor"),
                    "type": TYPE_MAPPING.get(f.get("type"), "2.0")
                })
        return filters
    except:
        return []

# GUI für Dateiauswahl
def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def select_directory(title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)

def main():
    db_path = select_file("Select your SteelSeries Sonar database.db", [("SQLite DB", "*.db"), ("Alle Dateien", "*.*")])
    if not db_path:
        messagebox.showerror("Error", "No database selected.")
        return

    out_dir = select_directory("Select output folder")
    if not out_dir:
        messagebox.showerror("Error", "No output folder selected.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, data FROM configs WHERE name IS NOT NULL AND TRIM(name) != '' AND vad = 1 GROUP BY name;")
    rows = cursor.fetchall()

    presets = []
    for name, data in rows:
        filters = extract_filters_with_type(data)
        if filters:
            presets.append({"name": name, "filters": filters})

    for i, preset in enumerate(presets, start=10):
        xml = create_wavelink_xml(preset["name"], preset["filters"], i)
        safe_name = "".join(c for c in preset["name"] if c.isalnum() or c in " _-").rstrip()
        with open(Path(out_dir) / f"{safe_name}.xml", "w", encoding="utf-8") as f:
            f.write(xml)

    messagebox.showinfo("Done", f"{len(presets)} Presets successfully exported to: {out_dir}")

if __name__ == "__main__":
    main()