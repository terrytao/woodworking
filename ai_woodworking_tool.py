# AI-Powered Woodworking Assistant - Web App Version
# Streamlit app to generate SVG + G-code from part list or text prompt

import svgwrite
import uuid
import os
import streamlit as st
import re

# Core logic for SVG + G-code generation
def generate_table_design(parts, svg_filename="cut_layout.svg", gcode_filename="cut_output.gcode"):
    dwg = svgwrite.Drawing(svg_filename, size=("48in", "96in"), viewBox="0 0 1920 960")
    
    x, y = 0, 0
    spacing = 20

    for part in parts:
        qty = part.get("qty", 1)
        width = part["width"]
        height = part["height"]
        label = part["part"]

        for _ in range(qty):
            dwg.add(dwg.rect(insert=(x, y), size=(width, height), fill="none", stroke="black", stroke_width=2))
            dwg.add(dwg.text(label, insert=(x + 5, y + 15), font_size="12px", fill="black"))
            x += width + spacing
            if x > 1800:
                x = 0
                y += max(height, 60) + spacing

    dwg.save()

    with open(gcode_filename, "w") as f:
        f.write(f"; G-code generated for job {uuid.uuid4()}\n")
        for part in parts:
            for _ in range(part.get("qty", 1)):
                f.write(f"G1 X{x} Y{y} ; Cutting {part['part']}\n")

    return svg_filename, gcode_filename

# Parse simple prompts like "2x2 foot table with four 28-inch legs"
def parse_prompt(prompt):
    parts = []
    match_table = re.search(r"(\d+(\.\d+)?)x(\d+(\.\d+)?)\s*ft.*table", prompt)
    if match_table:
        w_ft = float(match_table.group(1))
        h_ft = float(match_table.group(3))
        width = int(w_ft * 240)  # approx. pixels per foot
        height = int(h_ft * 240)
        parts.append({"part": "Tabletop", "qty": 1, "width": width, "height": height})

    match_legs = re.search(r"four (\d+)-inch legs", prompt)
    if match_legs:
        height = int(match_legs.group(1))
        parts.append({"part": "Leg", "qty": 4, "width": 60, "height": height})

    return parts if parts else None

# Streamlit UI
st.title("🪚 AI-Powered Cut List Generator")

option = st.selectbox("Choose input mode", ["Coffee Table", "Custom", "Prompt"])

if option == "Coffee Table":
    cut_list = [
        {"part": "Tabletop", "qty": 1, "width": 480, "height": 480},
        {"part": "Leg", "qty": 4, "width": 60, "height": 400},
        {"part": "Apron Long", "qty": 2, "width": 420, "height": 80},
        {"part": "Apron Short", "qty": 2, "width": 300, "height": 80},
    ]
elif option == "Custom":
    part_name = st.text_input("Part name", "Custom Part")
    qty = st.number_input("Quantity", 1)
    width = st.number_input("Width (px)", 100)
    height = st.number_input("Height (px)", 100)
    cut_list = [{"part": part_name, "qty": qty, "width": width, "height": height}]
elif option == "Prompt":
    prompt = st.text_area("Describe your furniture (e.g., '2x2 foot table with four 28-inch legs')")
    cut_list = parse_prompt(prompt)
    if cut_list is None:
        st.warning("Could not understand prompt. Try again with clearer dimensions and terms.")

if st.button("Generate Cut Files") and cut_list:
    svg_file, gcode_file = generate_table_design(cut_list)
    with open(svg_file, "rb") as f:
        st.download_button("Download SVG", f, file_name="layout.svg")
    with open(gcode_file, "rb") as f:
        st.download_button("Download G-code", f, file_name="output.gcode")
