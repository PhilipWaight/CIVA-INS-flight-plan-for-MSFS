#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox
import re
# glob for targeted cleanup of previous plan macros from 
# flightplan\LEGS folder
import glob
# clipboard cycler for legs macro files...
import keyboard
import pyperclip
import time
# facilitate clipboard actions with beep prompt
import winsound

__author__ = "Philip Waight with assistance from Gemini"
__version__ = "1.0.0"
__status__ = "Beta"  #  "Production", "Dev", "Beta"


"""
CIVA INS Flight Plan Processor

DEPENDENCIES:
    - CIVAinsCalibration.txt : Required in the same directory. 
                               Macro Commander syntax file
                               contains mouse command and coordinate mappings.
    - CIVAkeypush.macro
    - requirements.txt       : Run 'pip install -r requirements.txt' 
                               to install keyboard and pyperclip.


This script emulates co-pilot manual entry of waypoint coordinates to the civa ins
using 'Macro Commander' hotkey triggered macro files.

See README.md for detailed setup instructions

"""

def clean_filename(name):
    """Removes characters not allowed in Windows filenames."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def get_icao(wp_node):
    """Extracts the ICAOIdent text from a waypoint node."""
    icao_node = wp_node.find(".//ICAOIdent")
    return icao_node.text if icao_node is not None else "UNK"

def get_global_icao(container, tag_name):
    """Finds ICAO in global nodes like DepartureID or DestinationID."""
    # First search for direct child, then deep search
    node = container.find(f".//{tag_name}")
    if node is not None:
        # If it has children (like DepartureDetails), look for ICAOIdent
        icao_child = node.find(".//ICAOIdent")
        if icao_child is not None: 
            return icao_child.text
        # Otherwise return the text of the node itself (like DepartureID)
        return node.text
    return None

def process_flight_plan():
    global target_exe
    print(f"--- CIVA INS Flight Plan Processor v{__version__} ---")    
    root = tk.Tk()
    root.withdraw()
    #This is a Macro Commander macro captured from a record session and annotated
    # It should be saved with, for example, a CTRL-SHIFT-0 hotkey
    # to allow for a quick check of saved CIVA INS MSFS view or after other changes
    # it also needs to be a txt file on disk for access from this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    calibration_path = os.path.join(script_dir, "CIVAinsCalibration.txt")

    # capture target exe to ensure directed macro output enabled
    if messagebox.askyesno("Microsoft Flight Simulator Edition", 
        "Is the target application Microsoft Flight Simulator 2024? (Otherwise 2020 is assumed)"):
        target_exe = "flightsimulator2024.exe"
    else:
        target_exe = "flightsimulator.exe"

    source_path = filedialog.askopenfilename(
        title="Select Flight Plan file, Simbrief NoProc version preferred",
        filetypes=[("Flight Plan", "*.pln"), ("XML Files", "*.xml")]
    )
    
    if not source_path: 
        return
        
    include_icao = messagebox.askyesno("Flightplan Filename Option", 
        "Include Departure/Arrival ICAOs in the filename?\n\nFormat: root_FROM_TO_plnXX.pln")

    try:
        # Use a parser that preserves some structure but we will re-indent
        tree = ET.parse(source_path)
        xml_root = tree.getroot()
        fp_container = xml_root.find(".//FlightPlan.FlightPlan")

        # Extract Global ICAO info for naming
        dep_id = get_global_icao(xml_root, "DepartureID") or "DEP"
        dest_id = get_global_icao(xml_root, "DestinationID") or "ARR"

        header_nodes, waypoint_nodes, footer_nodes = [], [], []
        found_first_wp = found_footer_start = False

        for child in fp_container:
            tag = child.tag.split('}')[-1].lower()
            if "arrivaldetails" in tag or "approachdetails" in tag:
                found_footer_start = True
            
            if "atcwaypoint" in tag:
                waypoint_nodes.append(child)
                found_first_wp = True
            elif found_footer_start:
                footer_nodes.append(child)
            elif not found_first_wp:
                header_nodes.append(child)
            else:
                footer_nodes.append(child)

        source_dir = os.path.dirname(source_path)
        base_name, ext = os.path.splitext(os.path.basename(source_path))
        target_dir = os.path.join(source_dir, "legs")
         
        os.makedirs(target_dir, exist_ok=True)
        # Clean up only the specific CIVA leg files from previous runs
        # This looks for any file matching "CIVA_Leg_###.txt"
        old_civa_files = glob.glob(os.path.join(target_dir, "CIVA_Leg_[0-9][0-9][0-9].txt"))
        for f_path in old_civa_files:
            try:
                os.remove(f_path)
            except OSError:
                pass # Ignore if file is locked or already gone

        # 2. Load calibration data once at the start
        # (Assumes parse_civa_calibration function is defined above)
        calibration_data = parse_civa_calibration(calibration_path)

        chunk_size = 7
        total_chunks = (len(waypoint_nodes) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(waypoint_nodes), chunk_size):
            leg_num = (i // chunk_size) + 1
            current_chunk = waypoint_nodes[i : i + chunk_size]
            
            # Name logic per your request
            from_name = dep_id if leg_num == 1 else get_icao(current_chunk[0])
            to_name = dest_id if leg_num == total_chunks else get_icao(current_chunk[-1])
            
            from_clean, to_clean = clean_filename(from_name), clean_filename(to_name)
            
            if include_icao:
                new_filename = f"{base_name}_{from_clean}_{to_clean}_pln{leg_num:03d}{ext}"
            else:
                new_filename = f"{base_name}_pln{leg_num:03d}{ext}"
            
            output_path = os.path.join(target_dir, new_filename)
            
            # Rebuild XML
            new_root = ET.Element(xml_root.tag, xml_root.attrib)
            for child in xml_root:
                if "FlightPlan.FlightPlan" not in child.tag:
                    new_root.append(ET.fromstring(ET.tostring(child)))

            new_fp = ET.SubElement(new_root, "FlightPlan.FlightPlan")
            for node in header_nodes: 
                new_fp.append(ET.fromstring(ET.tostring(node)))
            for wp in current_chunk: 
                new_fp.append(ET.fromstring(ET.tostring(wp)))
            for node in footer_nodes: 
                new_fp.append(ET.fromstring(ET.tostring(node)))

            # Write current_chunk <WorldPosition> tags
            save_leg_macro(leg_num, current_chunk, calibration_data, target_dir)
            
            # Apply clean indentation (standardized human readable)
            if hasattr(ET, 'indent'):
                ET.indent(new_root, space="    ", level=0)

            # Write to file
            with open(output_path, "wb") as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                ET.ElementTree(new_root).write(f, encoding="utf-8", xml_declaration=False)
            
            print(f"Leg {leg_num:03d}: {from_name} -> {to_name}")

        messagebox.showinfo("Success", f"Split into {total_chunks} legs.\nFiles saved to /legs folder.")
 
        # Collect all generated leg file paths for clipboard output
        generated_legs = []
        for j in range(1, total_chunks + 1):
            # Matches your naming logic
            pattern = f"CIVA_Leg_{j:03d}.txt"
            generated_legs.append(os.path.join(target_dir, pattern))
            
        print("Default hotkey to copy next leg to clipbboard is F9.")
        choice = input("Press ENTER to keep F9, or type a new key (e.g. f11): ").strip().lower()
        chosen_key = choice if choice else "f9"
            
        start_clipboard_cycler(generated_legs, chosen_key)
 
    except Exception as e:
        messagebox.showerror("Error", f"Processing failed: {e}")

def parse_civa_calibration(file_path):
    """
    Parses a CIVA INS calibration file into a dictionary.
    Keys: Button names (e.g., 'hold', '1', 'insert')
    Values: List of macro command strings
    """
    calibration_map = {}
    current_button = None

    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                
                # Skip empty lines
                if not clean_line:
                    continue

                # Check for the button header <#>
                if clean_line.startswith("<#>"):
                    # Extract the name after <#> and normalize to lowercase
                    current_button = clean_line[3:].strip().lower()
                    calibration_map[current_button] = []
                
                # If we are within a button block, add the command to its list
                elif current_button is not None:
                    calibration_map[current_button].append(clean_line)

        return calibration_map

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}


def save_leg_macro(leg_num, current_chunk, calibration_data, target_dir):
    """
    current_chunk: A list of ElementTree nodes (<ATCWaypoint>)
    leg_num: The sequential number of the leg (1, 2, 3...)
    """
    filename = f"CIVA_Leg_{leg_num:03d}.txt"
    file_path = os.path.join(target_dir, filename)
    
    with open(file_path, 'w') as f:
        f.write(f"<#> CIVA AUTO-LOADER LEG {leg_num:03d}\n")
        # Ensure macro output is directed to the target MSFS app        
        f.write(f'<if_win>("Executable:{target_exe}","OPEN")\n')
        f.write(f'  <win_activate>("Executable:{target_exe}")\n')

        for wp_node in current_chunk:
            # Find the text inside the <WorldPosition> tag for this node
            # This handles the namespace if present or simple tags if not
            world_pos_string = wp_node.findtext("WorldPosition")
            waypoint_id      = wp_node.get("id") or "UNK"
            
            if world_pos_string:
                # Passes the string "N20° 42' 38.02",W68° 7' 31.01",+039000.00"
                write_waypoint_macro(waypoint_id, world_pos_string, calibration_data, f)
            else:
                f.write(f"<#> WARNING: No WorldPosition found for a waypoint in Leg {leg_num}\n")
                
        f.write(f"<#> End of Leg {leg_num:03d}\n")
        # Close Directed macro output check        
        f.write("<else>\n")
        f.write(f'  <msg>(500,500,"Error:Cant find {target_exe} window","%_vRunningMacroName%",1,0,0,1,33%,33%)\n')
        f.write("<endif>\n")        


def write_waypoint_macro(waypoint_id, world_pos_tag, calibration_data, out_file):
    """
    Parses a MSFS WorldPosition string and writes the macro command sequence.
    Sequence: {waypoint selector}{insert}{longitude}{insert}{latitude}{insert}
    """
    # Regex for N38° 44' 55.31",W90° 22' 12.09",+000617.00
    coord_pattern = r"([NS])(\d+)°\s*(\d+)'\s*(\d+\.?\d*)\",([EW])(\d+)°\s*(\d+)'\s*(\d+\.?\d*)\""
    # add to coord pattern to retrieve elevation... ,\+?(-?\d+\.?\d*)
    match = re.search(coord_pattern, world_pos_tag)
    
    if not match:
        out_file.write(f"<#> ERROR: Invalid coordinate format: {world_pos_tag}\n")
        return

    lat_card, lat_d, lat_m, lat_s, lon_card, lon_d, lon_m, lon_s = match.groups()

    # Cardinal Mapping: N=2, S=8, E=6, W=4
    card_map = {'N': '2', 'S': '8', 'E': '6', 'W': '4'}

    # 1. Format Longitude: CDDDMMS (e.g. W90° 22' 12" -> 4 090 22 1)
    lon_s_digit = str(int(float(lon_s)) // 10)
    lon_sequence = card_map[lon_card] + lon_d.zfill(3) + lon_m.zfill(2) + lon_s_digit

    # 2. Format Latitude: CDDMMS (e.g. N38° 44' 55" -> 2 38 44 5)
    lat_s_digit = str(int(float(lat_s)) // 10)
    lat_sequence = card_map[lat_card] + lat_d.zfill(2) + lat_m.zfill(2) + lat_s_digit

    def push_button(name):
        """Writes the lines from the calibration array for a specific button."""
        lines = calibration_data.get(str(name).lower(), [])
        if not lines:
            out_file.write(f"<#> WARNING: Button '{name}' not found in calibration!\n")
        for line in lines:
            out_file.write(f"{line}\n")

    # --- START MACRO OUTPUT ---
    out_file.write(f"<#> World pos tag: {world_pos_tag}\n")
    out_file.write(f"<#> Waypoint Entry: {lat_card}{lat_d}{lat_m}{lat_s} / {lon_card}{lon_d}{lon_m}{lon_s}'\n")
    out_file.write(f"<#> Encoded: '{lat_sequence}' / '{lon_sequence}'\n")
    # Write onscreen message indicating WP name and pos
    out_file.write(f'<msg>(10,10, "WP: {waypoint_id} Pos: {world_pos_tag}", "World pos tag", 10, 10, 0, 20%, 10%)\n')
 
    # 1. Increment Waypoint Selector
    push_button("waypoint selector")
    
    # 2. Enter Latitude
    push_button("insert")
    for digit in lat_sequence:
        push_button(digit)
    
    # 3. Enter Longitude
    push_button("insert")
    for digit in lon_sequence:
        push_button(digit)
        
    # 4. Final confirmation
    push_button("insert")

    out_file.write("<#> End Waypoint Entry\n")
        

def start_clipboard_cycler(leg_files, chosen_key):
    state = {"index": 0}
    total = len(leg_files)

    # Renamed to be generic
    def on_hotkey_pressed(event):
        if state["index"] < total:
            try:
                file_path = leg_files[state["index"]]
                with open(file_path, 'r') as f:
                    pyperclip.copy(f.read())
                
                state["index"] += 1
                print(f"-> [{state['index']}/{total}] COPIED: {os.path.basename(file_path)}")
                winsound.Beep(1000, 100)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("All legs completed! Press ESC to exit.")
            winsound.Beep(600, 150)

    # Pass the variable 'chosen_key' here instead of a hardcoded string
    keyboard.on_press_key(chosen_key, on_hotkey_pressed)

    print("\n" + "="*50)
    print("      CIVA CLIPBOARD CYCLER ACTIVE")
    print(f" Hotkey: [ {chosen_key.upper()} ]") # Shows the user their choice
    print(" [ ESC ] - Exit")
    print("="*50)

    # The "Keep-Alive" loop
    try:
        while True:
            if keyboard.is_pressed('esc'):
                break
            time.sleep(0.2) # A longer sleep is fine and saves Windows resources
    finally:
        keyboard.unhook_all()
        print("\n[ESC] detected. Hotkeys released.")
        

if __name__ == "__main__":
    process_flight_plan()
