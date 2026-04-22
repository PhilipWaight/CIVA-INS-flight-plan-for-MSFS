# CIVA INS Flight Plan Processor for MSFS

CIVA_flightplan.py is a Python-based utility for **MSFS 2020/2024** 
that automates the entry of flight plan waypoints into the **CIVA INS** navigation unit,
specifically for the **DC Designs Concorde**. The aircraft will fly under FMC control 
if a full flight plan is loaded, and INS selected, but this loses the realism of Concorde navigation.

The CIVA INS unit had an attached ADEU
card reader that was able to load 9 waypoints, thus automated load as well as individual waypoint entry 
was a part of normal operations.
 
CIVA_flightplan.py parses standard `.pln` files, chunks them into up to 9 waypoint phases, and generates mouse-macro sequences for **Macro Commander**.

There are 2 parts to this utility. The primary goal was to split a large flight plan into CIVA readable chunks,
while preserving the structure of departure , arrival and intermediate waypoints required for EFB use.

The utility emulates a pilot, co-pilot 
or flight engineer keying the required waypoints manually. Entry of a single waypoint is 17 keystrokes
on the CIVA unit, thus requiring the use of automation, but through the standard INS interface. 

A calibration script CIVA_calibrate.py allows the button positions to be recorded once for your preferred view and monitor 
and saved for use with each new flight plan.

Use of the free tool **Macro Commander**: This is a windows tool which I have used reliably in **MSFS**
for improving the user experience in the MSFS UI. As an example, importing a flight plan from a disk file,
or restoring a second monitor when it is dropped during a VR session. Any similar automation tool has some risk in its use.
Please read the "Notes and Warnings" and be prepared to familiarise yourself with this tool.


## ⚠️ Notes and Warnings

1.  Clipboard Usage: The script uses a global hotkey to feed data into your clipboard. 
    If you prefer manual handling, press ESC in the CMD window 
    to exit the cycler. You can always find the raw macro text files in the {flight plan}/phases folder.
    
2.  Emergency Stop: A 9-waypoint phase will contain over 1,000 lines of commands. 
    
    If the macro runs out of sequence or is triggered by mistake, 
    press `Shift + Esc` to bring up the Macro Commander interrupt dialogue.
    It is recommended to practice `Shift + Esc` during first use.
    
    `Ctrl + Alt + Del` remains your last resort for a system override.
    
3.  Target Focus: Output is targeted specifically at the MSFS process using the `<if_win>` and
    `<win_activate>` **Macro Commander** commands, included in each of the phase macros. 
    The macro should exit if the simulator is not running. It 
    forces it to be the active, focused window before running the body of the commands.
    You should ensure MSFS is running full screen and maximised.
    
4.  Macro timing: The calibrate script requests and outputs a wait time between mouse clicks.
    This serves several purposes: 
    1. ensures the macro runs at optimal speed. This will be faster than your button position clicks; 
    2. ensures it is not so fast as to fail with inherent responsiveness in the UI to contend with. 
    
    Also there is some satisfaction in watching the key inputs, so this is definitely a user choice. 
    100ms is recommended and 50ms works in testing.
    
5.  It is understood that during the CIVA load, no mouse or keyboard activity is possible. This process
    only takes a minute.

6.  This software is at beta development status.

## Development

    This project was developed through a collaborative process between the author (aged 72) and Google Gemini (2 years 4 months).
    Role: Gemini assisted in architecting specific functions, optimizing logic and providing encouragement and emotional support.
    Oversight: All AI-generated code was manually reviewed, refactored, and tested to ensure it meets project needs.


## Terminology
    
    INS     - Inertial Navigation System
    Flight plan
    Waypoint
    NoProc  - an export form from **Simbrief** omitting SID and STAR details.
			  Noproc version is preferred for CIVA_flightplan as all
              waypoints have a <WorldPosition> tag
    Phase - Each set of up to 9 waypoints for input to the CIVA unit
    Leg   - The path between consecutive waypoints.


## ✈️ Features

- **Smart Parsing**: Extracts Waypoint name, Latitude, Longitude, and Elevation from MSFS XML flight plans.
- **CIVA Logic**: Coordinate formatting (CDDMMS / CDDDMMS) and rounds seconds to the INS-required single digit.
- **Clipboard Cycler**: Uses a global hotkey (`F9`) to feed macro phases into the clipboard 
					during flight setup. Paste into the phase templates and save for in-flight use.							
- **On-Screen Feedback**: Includes audio beeps and console counters to track your progress while tabbed into the sim.
- **Custom Calibration**: Uses an external `.txt` file in macro format for mouse coordinates, 
					allowing rerecording to match screen resolution and saved cockpit view.
- ** Portability **: This utility could be used in other MSFS aircraft and possibly in other simulators.

## 🛠️ Requirements

- **Python 3.10+**
- **Macro Commander** (Basic-free or Pro current version 2.8.5) running during flight to 
   action each CIVA load. Suggest use of the download option from the web site and install, rather than
   the Microsoft Store version, as the Store version  hasnt been tested.
   [Download Macro Commander Basic 2.8.5 from Website](https://www.macro-commander.com/download)
- **External Libraries**: `pyperclip`, `pynput`, `keyboard`
- **CIVA_calibrate.py** script running from a CMD window during CIVA button identification in MSFS.
- **CIVA_flightplan.py** script running during flight plan setup only from a CMD window
- **Fplans folder** where you normally direct generated flight plans from **Simbrief**, or similar.
                    A sub-folder, `\phases` will be created for the generated plans.
- **Run as Administrator** The CMD window requires elevated execution to permit a global hotkey to be available
  in other applications. F9 (or user keyed alternative) is used to copy the next phase prior to pasting into Macro Commander.
- **MSFS** 
  The `Cockpit Interaction System` Flight Interface setting must be set to `Lock`. Single scroll on
  the waypoint selector fails if `Legacy` is used.
  If the `FMC` display is visible next to the INS, 
  the `Auto-Man` switch must be set to `Man` to operate under `INS`. This should be done every flight.

## 🚀 Installation & Setup

1. **Download** this repository to a project folder of your choice.

2. **Install Dependencies**:
   Open a CMD prompt in the folder and run:
      py -m pip install -r requirements.txt

3. Start MSFS and Macro Commander

	1.  Open the `CIVAkeypush.macros` macro group file and note the individual macros named
		`phase 1` to 7. [A `calibration` macro was used in an early dev version to record button locations].
        The assigned activation hotkeys are `ctrl + shift + 1` through 9. Change to your preferred
        hotkeys as needed. The hotkey for each phase should be a compound key combination
        dissimilar to other shortcut keys to avoid inadvertent use.

    2.  In MSFS, zoom to the CIVA unit with your saved view. 
        
> [!TIP]
>       See the project: Videos\CalibrationTest.mkv video.

4. Calibrate: 

	1. Note that `CIVAinsCalibration.txt` is a saved copy of the `Calibration` button locations
		to be read by `CIVA_flightplan.py` . 

	2. Create a view in MSFS (Chase Plane is a good option here) that shows the pilot CIVA INS 
	   filling 70% of screen or better. Ensure the view is repeatable.

	3. Start a CMD window and run `run_calibrate.bat` file from the project folder.
	   Follow the prompts and click on each button and selector in turn.
	   	   
	4. The 2,4,6,8 buttons provide the cardinal directions N, W, S, E and only need 
	   recording once.

> [!NOTE] 
>   5. The effective use of the rotary waypoint selector requires
>      a `{move to selector}{mouse click}{mouse wheel forward}{mouse click}`
>      sequence to prevent a stray mouse wheel movement changing the screen view.
>      This is handled by the calibrate script.
>      


## 📖 How to setup each flight plan

> [!TIP]
> See project file 'Videos\FlightPlanProcess.mkv' for an example of running steps 1-5

    MSFS doesn't need to be running for this setup.

1.  Start a CMD window and run run_civa.bat file from the project folder containing all the project files
    including your version of CIVAinsCalibration.txt.

2.  Select your MSFS .pln flight plan when prompted.

3.  The script will generate a /phases folder containing the split flight plan parts.

4.  Transfer to the saved macro template phase macro:

    1.  Tab to the CMD window and press `F9` to copy the first phase to the clipboard.
    
    2.  Tab into Macro Commander and click on macro `Phase 1` in the top macro list window. 
        Delete any existing macro content from the editor window.

	3.  Paste into your Macro Commander editor window for the selected phase.
        [The following step is a less intuitive requirement of Macro Commander:]
	    **Click on the phase macro list in the top window to transfer the contents of the macro body** 
        and `Save`.

	4.  Repeat from step i. for subsequent phases (a beep will confirm each successful copy).

5.  Press ESC in the command window to finish and close the CMD window. 

6.  Close Macro Commander and check it remains active in the windows toolbar 
    for triggering each phase during flight. 
    
## 📖 How to load each flight plan phase in MSFS

1.  Prerequisites for manual waypoint entry are:

	  1. Cold and dark checklist including Mode Selector Unit (MSU) to NAV or start with aircraft running.

      2. The CIVA INS (C/DU) on .

      3. Eight position `data selector` set to `WAY PT`

      4. `Waypoint/DME` selector set to zero. **This must be set manually.**

2.  If you choose to load phase 1 from the EFB in the world map, and use the CIVA `Remote` 
    flight plan load step, the procedure during flight is:

	1.  Check the CIVA device for the last waypoint.

	2.  When the last segment is active, switch to `Trk Hld` to allow INS editing.
        Note the `Alert` button should light as the waypoint is approaching. The
        correct function of the INS unit including the Alert light and other significant improvements 
        can be found in the addon:
        "https://flightsim.to/addon/94824/dc-designs-concorde-systems-enhancement"

	3.  Set the CIVA view, ensure waypoint selector is 0, data selector is `WayPt`. 
	    Hit the hotkey `Ctrl + Shift + 2` and watch  the points load.
	    A message box appears to show each waypoint name, position and elevation.

	4.  Click `Wy Pt Chg` button and select 0 to 1. The From-To should change.

	5.  Clear `Trk Hld` and hit `INS` on the AP panel.

2.  If you are using CIVA manual load for all phases, 
	follow from step 2.iii for the first phase with `Ctrl + Shift + 1` and from step 2.ii for subsequent phases.
	 
	
## 📁 Project Structure

1.  CIVA_calibrate.py: The calibrate logic.
    CIVA_flightplan.py: The main Python logic for flight plan split and macro generation. 

2.  CIVAkeypush.macros: Binary file containing phase macro templates.

3.  CIVAinsCalibration.txt: Exported macro text file for button mouse coordinates and timings.

4.  run_calibrate.bat and run_civa.bat: Windows batch launcher.

5.  requirements.txt: List of required Python modules.

6.  LICENSE.txt

7.  `Videos` folder for setup and use assistance.

8.  `tests\EGLLKJFK_MFS_NoProc_18Apr26.pln`: 

    A sample classic **Simbrief** flight plan used for testing.
    Modified as some original waypoints no longer exist. 
    This departure was used by Concorde as it allowed acceleration to supersonic flight phase over 
    the Bristol Channel. The CPT3F departure has been expanded in the "Selected Route" section 
    of the Simbrief edit page, although the VOR navigation departure is more interesting and typical. 

```
EGLL D255G D259K WOD D100H CPT/F060 KENET UNZIB/F150 D149T/F280 BHD57 LESLU/F500 
5041N01500W 5050N02000W 5030N03000W 4916N04000W 4703N05000W 4610N05300W 4414N06000W 
4246N06500W 4200N06700W 4044N06955W 4027N07230W CAMRN KJFK
```
    This should be placed in the flight plans Simbrief export folder.

> [!NOTE] 
>   Simbrief does not recognise Concorde performance data and produces erroneous altitude predictions.
>   A workaround is to use the wypt/Fnnn syntax to advise departure restriction, supersonic acceleration points
>   and expected cruise altitude waypoint altitudes. It seems to calculate a TOD with these minimal inputs.
>   To assist vertical profile planning, these altitudes will be displayed alongside the waypoint name
>   in the onscreen message attached to each phase.
    
## 🚀 Roadmap
- [x] Add usage videos
- [x] Replace manual calibration record step with script prompted button capture
- [ ] Test in FSS B727
- [x] The required timing changes could be applied to the calibration file commands by the script.
- [x] The raw calibration file could be parsed and updated automatically removing the 'Annotate' step
- [ ] Add a popup message or a kneepad note or similar to name waypoints as the `from-to` selector progresses.
      This may require an app such as Spad.Next monitor the next waypoint id.
- [ ] Add a warning as the last waypoint becomes the active destination
- [ ] The 9 waypoint entry has so far been very reliable in testing. A single waypoint entry option could be considered.
- [ ] An option to push a set of named waypoints on the fly for a diversion would be appealing, with a lookup to find the 
      coordinates. This could involve some interaction with the EFB.
- [ ] The Macro Commander Pro version has an `<Include>` text file option which would simplify the setup of each flight plan
      considerably. Include replaces the macro content with the file commands and runs them.


## ⚖️ License

This project is licensed under the MIT License.