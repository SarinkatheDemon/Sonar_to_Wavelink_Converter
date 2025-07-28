import sqlite3
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import json

TYPE_MAPPING = {
    "highPass": "0.0",
    "lowShelving": "1.0",
    "peakingEQ": "2.0",
    "highShelving": "3.0",
    "lowPass": "4.0"
}

def db_to_xml_gain(g):
    return 0.9673 * (2 ** (g / 5.8420))

def create_wavelink_xml(preset_name, filters):
    preset = ET.Element("Preset")
    ET.SubElement(preset, "Info", Name=preset_name)
    params = ET.SubElement(preset, "Parameters")

    for i, f in enumerate(filters, 1):
        band_prefix = f"Band {i} Filter"
        gain_converted = round(db_to_xml_gain(float(f["gain"])), 6)

        ET.SubElement(params, "PARAM", id=f"{band_prefix} Bypass", value="0.0")
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Frequency", value=str(float(f["frequency"])))
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Gain", value=str(gain_converted))
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Quality", value=str(float(f.get("qFactor", 1.0))))
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Type", value=f["type"])
        ET.SubElement(params, "PARAM", id=f"{band_prefix} Visible", value="1.0")

    return minidom.parseString(ET.tostring(preset)).toprettyxml(indent="  ")

def fix_and_parse_json(data_str):
    try:
        # Fix JSON-like formatting
        fixed = re.sub(r'(?<=\{|,)\s*([a-zA-Z0-9_]+)\s*:', r'"\1":', data_str)
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        fixed = fixed.replace("true", "true").replace("false", "false").replace("null", "null")
        return json.loads(fixed)
    except:
        return {}

def extract_filters_with_type(data_str):
    try:
        parsed = fix_and_parse_json(data_str)
        eq = parsed.get("parametricEQ", {})
        if not eq.get("enabled", False):
            return []
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

def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def select_directory(title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)

def main():
    db_path = select_file("Select your SteelSeries Sonar database.db", [("SQLite DB", "*.db"), ("All Files", "*.*")])
    if not db_path:
        messagebox.showerror("Error", "No database selected.")
        return

    out_dir = select_directory("Select output folder")
    if not out_dir:
        messagebox.showerror("Error", "No output folder selected.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, data FROM configs WHERE name IS NOT NULL AND TRIM(name) != '';")
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("No Presets", "No valid presets found in this database.")
            return

        name_count = {}

        for name, data in rows:
            filters = extract_filters_with_type(data)
            if not filters:
                continue

            base_name = "".join(c for c in name if c.isalnum() or c in " _-").rstrip()
            count = name_count.get(base_name, 0)
            filename = f"{base_name}.xml" if count == 0 else f"{base_name}_{count+1}.xml"
            name_count[base_name] = count + 1

            xml = create_wavelink_xml(name, filters)
            with open(Path(out_dir) / filename, "w", encoding="utf-8") as f:
                f.write(xml)

        messagebox.showinfo("Done", f"Export complete. Files written to:\n{out_dir}")

    except Exception as e:
        messagebox.showerror("Unexpected Error", str(e))

if __name__ == "__main__":
    main()
