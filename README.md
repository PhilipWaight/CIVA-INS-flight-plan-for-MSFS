# CIVA INS Flight Plan Processor for MSFS

A Python-based utility for **MSFS 2020/2024** that automates the entry of flight plan waypoints into the **CIVA INS** navigation unit,
specifically for the **DC Designs Concorde**.  
It parses standard `.pln` files, chunks them into 7-9 waypoint legs, and generates mouse-macro sequences for **Macro Commander**.

There are 2 parts to this utility. The primary goal was to split a large flight plan into CIVA readable chunks,
while preserving the structure of departure , arrival and intermediate waypoints required for EFB use.
If the Concorde supported EFB plan import from the cockpit, this would be sufficient.

As this aircraft requires flight plan loading from the world map, the scope extended to emulate a co-pilot 
or flight engineer keying the required waypoints manually. This required the use of a macro record
and playback tool as there are insufficient LVars available to achieve this using an external controls and interface
tool such as **Spad.Next**. 
A calibration macro concept means the button positions can be recorded once for your preferred view and monitor 
and saved for use with each new flight plan.

Use of the free tool **Macro Commander**: This is a windows tool which I have used reliably in **MSFS**
for improving the user experience in the MSFS UI. As an example, importing a flight plan from a disk file,
or restoring a second monitor when it is dropped during a VR session. Any similar automation tool has some risk in its use.
Please read the "Notes and Warnings" and be prepared to familiarise yourself with this tool.


## ⚠️ Notes and Warnings

1.  Clipboard Usage: The script uses a global hotkey to feed data into your clipboard. 
    If you experience hotkey conflicts or prefer manual handling, press ESC in the CMD window 
    to exit the cycler. You can always find the raw macro text files in the /legs folder.
    
2.  Emergency Stop: A 9-waypoint leg will contain over 1,000 lines of commands. 
    
    If the macro runs out of sequence or is triggered by mistake, 
    press `Shift + Esc` to bring up the Macro Commander interrupt dialogue.
    It is recommended to practice `Shift + Esc` during first use.
    
    `Ctrl + Alt + Del` remains your last resort for a system override.
    
3.  Target Focus: Output is targeted specifically at the MSFS process using the `<if_win>` and
    `<win_activate>` **Macro Commander** commands, included in each of the leg macros. 
    The macro should exit if the simulator is not running and 
    forces it to be the active, focused window before running the body of the commands.
    You should ensure MSFS is running full screen and maximised.
    
4.  Macro timing: The **Annotate the calibration file** setup section, refers to adjusting wait time
    in the calibration macro. This serves several purposes: to ensure the macro runs at optimal speed
    which will be faster than your deliberate recording to position the clicks accurately; to make sure 
    it is not so fast as to fail with inherent responsiveness in any UI to contend with. Also there is some
    satisfaction in watching the key inputs, so this is definitely a user choice. 200msecs is recommended.
    
5.  This software is at beta development status.

## Development

    This project was developed through a collaborative process between the author and Google Gemini.
    
    Role: Gemini assisted in architecting specific functions and optimizing logic.
    
    Oversight: All AI-generated code was manually reviewed, refactored, and tested to ensure it meets project standards.


## Terminology
    
    INS     - Inertial Navigation System
    Flight plan
    Waypoint
    NoProc  - an export form from **Simbrief** omitting SID and STAR details.
			  Noproc version is preferred for CIVA_flightplan as all
              waypoints have a <WorldPosition> tag
    Leg     - Each set of up to 9 waypoints for input to the CIVA unit form a leg
    Segment - The path between consecutive waypoints.


## ✈️ Features

- **Smart Parsing**: Automatically extracts Latitude, Longitude, and Elevation from MSFS XML flight plans.
- **CIVA Logic**: Coordinate formatting (CDDMMS / CDDDMMS) and rounds seconds to the INS-required single digit.
- **Clipboard Cycler**: Uses a global hotkey (`Ctrl + Shift + N`) to feed macro legs into the clipboard 
					during flight setup. Paste into the leg templates and save for in-flight use.							
- **On-Screen Feedback**: Includes audio beeps and console counters to track your progress while tabbed into the sim.
- **Custom Calibration**: Uses an external `.txt` file in macro format for mouse coordinates, 
					allowing rerecording to match screen resolution and saved cockpit view.

## 🛠️ Requirements

- **Python 3.10+**
- **Macro Commander** (Basic-free or Pro) running during initial setup and during flight to 
   action each CIVA load. Suggest use of the download option from the web site and install, rather than
   the Microsoft Store version, as the Store version  hasnt been tested.
- **External Libraries**: `pyperclip`, `keyboard`
- **CIVA_flightplan.py** script running during flight plan setup only from a CMD window
- **Fplans folder** where you normally direct generated flight plans from **Simbrief**, or similar.
                    A sub-folder, `\legs` will be created for the generated plans.

## 🚀 Installation & Setup

1. **Download** this repository to a folder of your choice.

2. **Install Dependencies**:
   Open a CMD prompt in the folder and run:
      py -m pip install -r requirements.txt

3. Start MSFS and Macro Commander

	1. Open the `CIVAkeypush.macro` macro group file and note the individual macros named
		leg1 to 7, and calibration.

	2. In MSFS, zoomed to the CIVA unit, you can run the provided calibration template `Shift+Ctrl+0` 
		if you have a 4K  monitor to show mouse moves and clicks. 
		Once you have recorded your own calibration, you can check your result using this hotkey.

4. Calibrate: 

	1. Note that `CIVAinsCalibration.txt` is a saved copy of the `Calibration` macro 
		(copy and paste as no export), read by `CIVA_flightplan.py` . 

	2. Create a view in MSFS (Chase Plane is a good option here) that shows the pilot CIVA INS 
	   filling 70% of screen or better. Ensure the view is repeatable.

	3. The required button pushes start with a single scroll of the `waypoint selector` 
	   from current to next (eg 0 to 1), followed by button pushes
       on each of the `Insert` and `0` to `9` buttons.
	   
	   Prior to each mouse move to the next button, 
	   a unique marker character should be keyed to identify this button.
	   eg., W for waypoint selector, I for insert, and 0-9.
	   The output will appear as:
	   
		W<mm>(1499,657,456)<#>
		<mlbd><#>
		<wx>(456,0)<#>
		<mlbu><#> ...	   
		
		which becomes the following after the annotation step 5
		
		<#> waypoint selector
		<mm>(1499,657,200)<#>
		<mlbd><#>
		<wx>(200,0)<#>
		<mlbu><#> ...	   
	   
	   The project file and macro includes all the buttons in anticipation of future use.
	   
	4. The 2,4,6,8 buttons provide the cardinal directions N, W, S, E and only need 
	   recording once.

	5. Important note: The effective use of the rotary waypoint selector requires
       a {marker key}{move to selector}{mouse click}{mouse wheel forward}{mouse click}
       sequence to prevent a stray mouse wheel movement changing the screen view.
       This is the reason the 'waypoint select' button contains multiple clicks
       but every other button has only 1 click.
	   You will need to follow this rule when recording the scroll. In testing
	   a single <mwheel_f> command worked well. If your mouse wheel has notched scroll option, this makes it easier.

	6. Prerequisites for manual waypoint entry are:

		1. Cold and dark checklist including Mode Selector Unit (MSU) to NAV

		2. The CIVA INS (C/DU) on.

		3. Eight position `data selector` set to `WAY PT`

		4. `Waypoint/DME` selector set to zero, although only a requirement for flight plan load.

	7. `Record` the macro with content as described in point 3: 
		Right click on the calibration macro line in the top macro list and click `record macro`. 
		In the dialogue steps, `desktop macro`,
		keyboard, mouse, absolute coordinates, UNCHECK record mouse movements to ensure
		no redundant intermediate data, CHECK record timing information, track the windows is NO.
		`Record Now` displays a start/stop dialogue. After `STOP`, the recorded steps 
		are displayed in the editor window.

	8. `Playback` the recorded macro to ensure accurate result for each button.

	9. Save the macro. This requires 2 steps (always):

		1. Click on the Calibration macro line in the top window. to transfer the edit window

		2. Click `File > Save'
	
5.  Annotate the calibration file:

	1.  The calibration macro file needs to be annotated with '<#> waypoint selector' .. 
        '<#> insert', '<#> 0' etc comments to denote the next block of wait , mouse move 
        and mouse click commands. This has to be a manual edit to replace each marker character. 
        Check the txt file for format.
        This step can be performed in the editor window, with convenient double click 
        on a command to check the arguments.

	2.  The parsing of this file uses comment lines so avoid extraneous comments beyond the header.

	3.  The `<wx>(567,0)<#>` wait first argument and <mm> last argument lines  
	    need to be edited to a preferred wait time. 200msec
	    is recommended but 100 might provide a faster and still reliable result.
			<#> insert
			<wx>(200,0)<#>
			<mm>(1873,497,200)<#>
			<mlbd><#>
			<wx>(200,0)<#>
			<mlbu><#>	   

	4.  Other commands 'could' be added to this file as long as the mouse position at button push 
	    is preserved.
	   
5.	Export (copy/paste) the calibration file to the project file CIVAinsCalibration.txt


## 📖 How to Use for each flight plan

1.  Run the run_civa.bat file from the project folder containing all the project files
    including your version of CIVAinsCalibration.txt.

2.  Select your exported MSFS .pln flight plan when prompted.

3.  The script will generate a /legs folder containing the split flight plan parts.

4.  Transfer to a saved macro per leg with activation hotkey:

    1.  Tab into Macro Commander and click on macro `Leg 1`. Delete any existing macro content.

	2.  Press `Ctrl + Shift + N` to copy the first leg. If this conflicts with existing shortcuts,
	    alter in the script file. Note: This hotkey is created by `CIVA_flightplan.py`

	3.  Paste into your Macro Commander editor window of the leg number macro. 
	    Click on the leg macro list in the top window to transfer the contents and `Save`.

	4.  Repeat for subsequent legs (a beep will confirm each successful copy).

5.  Press ESC in the command window to finish and close the CMD window. 

6.  Close Macro Commander and check it remains active in the windows toolbar 
    for triggering each leg during flight. 

7.  If you choose to load leg 1 from the EFB in the world map, the procedure during flight is:

	1.  Check the device for the last waypoint. This will be the destination.

	2.  When the last segment is active, switch to `Trk Hld` to allow INS editing.

	3.  Set the CIVA view, ensure waypoint selector is 0, data selector is `WayPt`. 
	    Hit the hotkey `Ctrl+Shift+2` and watch  the points load.
	    As the points load a message box appears to show the first waypoint name.

	4.  CLick `Wy Pt Chg` button and select 0 to 1. The From-To should change.

	5.  Clear `Trk Hld` and hit `INS` on the AP panel.

8.  If you are using CIVA manual load for all legs, 
	follow 7.3 for the first leg with `Ctrl+Shift+1`
	 
	
## 📁 Project Structure

1.  CIVA_flightplan.py: The main Python logic.

2.  CIVAkeypush.macro leg and calibration templates.

3.  CIVAinsCalibration.txt: Sample exported macro file for button mouse coordinates and timings.

4.  run_civa.bat: Windows batch launcher.

5.  requirements.txt: List of required Python modules.

6.  LICENSE.txt

7.  EGLLKJFK_MFS_NoProc_18Apr26.pln: 
    A sample classic **Simbrief** flight plan used for testing.
    Modified as some original waypoints no longer exist. 
    This departure was used by Concorde as it allowed acceleration to supersonic flight phase over 
    the Bristol Channel. The CPT3F departure has been expanded in the "Selected Route" section 
    of the Simbrief edit page, although the VOR navigation departure is more interesting and typical. 
        EGLL D255G D259K WOD D100H CPT KENET UNZIB D149T BHD57 LESLU 
        5041N01500W 5050N02000W 5030N03000W 4916N04000W 4703N05000W 4610N05300W 4414N06000W 
        4246N06500W 4200N06700W 4044N06955W 4027N07230W CAMRN KJFK
    This should be placed in the flight plans Simbrief export folder.

## ⚖️ License

This project is licensed under the MIT License.