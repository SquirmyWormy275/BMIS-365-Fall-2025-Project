#Wood Chopping Handicap Calculator Functions Dictionary and Library:

# Function Dictionary

'''| Function | Parameters | Purpose |
|:---|:---|:---|
| `competitor_menu` | `DataFrame comp_df`, `DataFrame selected_df`, `list selected_names` | **Menu (in `project_functions.py`; called from main):** print roster, select competitors (one-at-a-time Enter workflow), add competitor, remove competitor; returns updated `(comp_df, selected_df, selected_names)`. |
| `load_competitors_df` | *(none)* | Load the roster from Excel into a DataFrame; on error, print message and return empty DataFrame with expected columns. |
| `list_competitors` | `DataFrame df` | Print roster of competitors with name, country, and last handicap; if empty, print notice. |
| `add_competitor_to_excel` | *(none)* | Prompt for name/country/last_handicap, append a new row to the Excel roster (creating header if needed), save, and return the updated DataFrame; prints confirmations/errors. |
| `action_remove_competitor` | `DataFrame df` | Remove a competitor by exact name from the DataFrame and rewrite the Excel sheet; print confirmations or not-found message; return updated `df`. |
| `action_select_for_heat` | `DataFrame df`, `int max_select=8` | One-at-a-time selector for heat competitors (press Enter to finish); prevents duplicates; returns `(selected_df, selected_names_list)` and prints count/confirmations. |
| `wood_menu` | `dict wood_selection` | **Menu (in `project_functions.py`; called from main):** choose species, enter size (mm), enter **integer** quality (0–10); prints the standardized wood header after each change; returns updated `wood_selection`. |
| `load_wood_data` | *(none)* | Load wood species data from Excel into a DataFrame; on error, print message and return empty `["species","multiplier"]` DataFrame. |
| `select_wood_species` | `dict wood_selection`, `DataFrame wood_df=None` | Display species list, accept numeric choice, set `wood_selection["species"]`, and print the standardized wood header; handles invalid/empty data safely. |
| `enter_wood_size_mm` | `dict wood_selection` | Prompt for block diameter (mm), set `wood_selection["size_mm"]`, and print the standardized wood header; handles invalid numeric input. |
| `enter_wood_quality` | `dict wood_selection` | Prompt for wood quality as an integer 0–10 (blank = no change; clamps to [0,10]); set `wood_selection["quality"]`; print the standardized wood header. |
| `format_wood` | `dict ws` | Build and return `Selected Wood -> Species: X, Diameter: Y mm, Quality: Z`; also print “Wood selection updated: …”. |
| `view_handicaps_menu` | `DataFrame selected_df`, `dict wood_selection` | **Menu (in `project_functions.py`; called from main):** runs the handicap calculation pipeline for current selections and prints the compact start sheet; returns to menu loop after Enter. |
| `view_handicaps` | `DataFrame selected_df`, `dict wood_selection` | End-to-end calculation/display: build histories, choose baseline (300 mm if size ≥ 260 else 250), compute wood index, predict times, compute marks, print standardized wood header and compact `Name Mark X` lines in ascending mark order. |
| `_to_float_or_none` | `any v` | Utility: cast to `float` or return `None` on failure. |
| `_median` | `iterable nums` | Utility: median of a list (odd → middle value; even → average of two middles); returns `None` for empty. |
| `_load_wood_characteristics_df` | *(none)* | Load and normalize wood characteristics from Excel (species, density, janka, shear, MOR, MOE) with alias resolution; return standardized DataFrame. |
| `compute_species_multiplier` | `string species`, `dict species_index_map=None` | Compute species multiplier via geometric mean of ratios to Eastern White Pine (or dataset medians) using available characteristics; >1.0 harder/slower, <1.0 softer/faster. |
| `compute_quality_multiplier` | `int quality` | Map wood quality (0–10) to linear time multiplier (1.20 at 0 down to 0.80 at 10); parses/clamps, defaults to 5 on parse failure. |
| `compute_wood_index` | `float diameter_mm`, `float baseline_diameter_mm`, `int quality`, `string species=None`, `dict species_index_map=None` | Combine size factor, quality multiplier, and species multiplier into a composite wood index; size factor defaults to 1.0 if inputs invalid. |
| `predict_time` | `list[dict] records`, `float selected_wood_index`, `float baseline_diameter_mm`, `dict species_index_map=None` | Normalize each historical time by its own wood index, take median, then scale by `selected_wood_index`; return predicted seconds or `None` if no valid records. |
| `compute_marks` | `dict predicted_times` | Convert predictions to handicap marks: slowest gets 3; for each competitor `mark = 3 + ceil(slowest − time)` clamped to [3, 180]; ties allowed. |
'''

#Function Library

##Import Pandas, numpy, 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from math import ceil
from openpyxl import load_workbook

##file/sheet names (saved in the same directory as this script!!!!!!!!!!!!!!!!!!!!!!!!)
COMPETITOR_FILE  = "woodchopping.xlsx"
COMPETITOR_SHEET = "competitors"
WOOD_FILE        = "woodchopping.xlsx"
WOOD_SHEET       = "wood"


#MENU OPTION 1: COMPETITOR SELECTION MENU
''' Official will be presented with a list of competitors
    1. Select Competitors from the list
    2. Add competitors to the list
    3. Remove competitors from the list
    4. View selected competitors
    5. Return to Main Menu

    This is the first menu the judge will see. They will be able to select competitors from the existing roster
    or add/remove new competitors to the roster. The intent is not to just be able to select competitors for the current heat, but to be able to create
    a user-frindly interface where a judge can maintain and update a roster of competitors over time

    For V2 I want to find a way to be able to have the sheet update the 'most recent handicap' field based on the calculated handicap from the heat.
    I also want to find a way to update the three most recent times, or maybe just add additional times for each competitor based on the times recorded in the heat.

'''

## Competitor Selection Menu
def competitor_menu(comp_df, selected_df, selected_names):
    ''' Official will be presented with a list of competitors
        1. Select Competitors from the list
        2. Add competitors to the list
            (competitors added will be appended to the competitor CSV file)
            -Name
            -Country
            -Marker Type (Front, Mid, Back)
            -Times Recorded (3x)
                -Time (raw)
                -Wood Size
                -Wood Speceies
                -Most recent handicap (3 for novices)
        3. Remove competitors from the list
        4. View selected competitors
        5. Return to Main Menu
    '''
    while True:
        print("\n--- Competitor Menu ---")
        print("1) Print roster")
        print("2) Select competitors for heat")
        print("3) Add competitor to roster")
        print("4) Remove competitor from roster")
        print("5) Back to Main Menu")
        s = input("Choose an option: ").strip()

        if s == "1":
            print("\n--- Roster ---")
            list_competitors(comp_df)

        elif s == "2":
            selected_df, selected_names = action_select_for_heat(comp_df, max_select=8)

        elif s == "3":
            comp_df = add_competitor_to_excel()

        elif s == "4":
            comp_df = action_remove_competitor(comp_df)

        elif s == "5" or s == "":
            break
        else:
            print("Invalid selection. Try again.")
    return comp_df, selected_df, selected_names


##Load the roster from Excel  into a DataFrame.
'''Minimum data needed will be three times with the wood size in mm and the species of wood. 
Judge will also need to enter the last handicap to create a bench mark and a sanity check foe me when debugging.
If last handicap is unkown or not you are dealing with a novice competitor, enter 3.
Right now the jufge is only prompted for standing block times. 
In V2 I want to be able to select between standing block and underhand.'''

def load_competitors_df():
    try:
        df = pd.read_excel(COMPETITOR_FILE, sheet_name=COMPETITOR_SHEET)
        print("Roster loaded successfully from Excel.")
        return df
    except Exception as e:
        print(f"Error loading roster from Excel: {e}")
        return pd.DataFrame(columns=[
            "competitor_name","competitor_country","last_handicap",
            "timeOne","sizeOne","speciesOne",
            "timeTwo","sizeTwo","speciesTwo",
            "timeThree","sizeThree","speciesThree",
        ])

##Print a roster of competitors with name, country, and the last handicap listed in the Excel Roster
def list_competitors(df):
    if df.empty:
        print("No competitors currently in roster.")
        return
    print(df[["competitor_name","competitor_country","last_handicap"]])

## Prompt for name/country/last_handicap, append to Excel, and save
''' Add a new competitor to the roster and save to Excel. 
I want to be able to create a running list of competitors that can be added to over time. 
For V2, I want top be able to select between Standing Block and Underhand
'''

def add_competitor_to_excel():
    try:
        wb = load_workbook(COMPETITOR_FILE)
        if COMPETITOR_SHEET not in wb.sheetnames:
            ws = wb.create_sheet(COMPETITOR_SHEET)
            ws.append([
                "competitor_name","competitor_country","last_handicap",
                "timeOne","sizeOne","speciesOne",
                "timeTwo","sizeTwo","speciesTwo",
                "timeThree","sizeThree","speciesThree"
            ])
        else:
            ws = wb[COMPETITOR_SHEET]

        name = input("Enter competitor name: ").strip()
        country = input("Enter competitor country: ").strip()
        handicap = input("Enter last handicap (3 for novice): ").strip()

        ##Basic validation
        '''Need to make sure that excel file is working properly and the inputs are valid.'''

        if not name:
            print("Competitor name cannot be blank.")
            return pd.read_excel(COMPETITOR_FILE, sheet_name=COMPETITOR_SHEET)

        ws.append([
            name, country, handicap,
            None, None, None,
            None, None, None,
            None, None, None
        ])
        wb.save(COMPETITOR_FILE)
        wb.close()
        print("Competitor added successfully and saved to Excel.")
        return pd.read_excel(COMPETITOR_FILE, sheet_name=COMPETITOR_SHEET)
    except Exception as e:
        print(f"Error adding competitor: {e}")
        return pd.read_excel(COMPETITOR_FILE, sheet_name=COMPETITOR_SHEET)

##Remove a competitor by exact name and rewrite the Excel sheet.
'''This removes a competitor from the excel Roster. This does not remove them from any heats they may have been selected for.
The best way to remove from the heat is to simply restart the competitor selection process.'''

def action_remove_competitor(df):
    if df.empty:
        print("Roster is empty.")
        return df
    name = input("Enter competitor name to remove: ").strip()
    if name not in df["competitor_name"].values:
        print("Competitor not found.")
        return df
    df = df[df["competitor_name"] != name]
    try:
        wb = load_workbook(COMPETITOR_FILE)
        if COMPETITOR_SHEET in wb.sheetnames:
            ws = wb[COMPETITOR_SHEET]
            ws.delete_rows(2, ws.max_row)
            for _, row in df.iterrows():
                ws.append(row.tolist())
            wb.save(COMPETITOR_FILE)
            wb.close()
        print("Competitor removed successfully and Excel updated.")
    except Exception as e:
        print(f"Error updating Excel after removal: {e}")
    return df

##One-at-a-time selector for heat competitors
'''The judge will be able to select competitors one at a time for the current heat. from the available roster.
If you make an error finsish the roster selection and start over immediately. As a best practice,
I try and enter the competitors for a heat before I get into wood selection so that I can start over if needed.'''

def action_select_for_heat(df, max_select=8):
    if df.empty:
        print("Roster is empty.")
        return df.iloc[0:0], []

    print("\nAvailable competitors:")
    for i, name in enumerate(df["competitor_name"].tolist(), start=1):
        print(f"{i}) {name}")

    print("\nEnter competitor numbers one at a time. Press Enter with no input when finished.")
    idxs = []
    while len(idxs) < max_select:
        s = input(f"Select competitor #{len(idxs)+1}: ").strip()
        if s == "":
            break
        if not s.isdigit():
            print("Invalid input. Please enter a number.")
            continue
        idx = int(s) - 1
        if 0 <= idx < len(df):
            if idx in idxs:
                print("Competitor already selected.")
                continue
            idxs.append(idx)
            print(f"{df.iloc[idx]['competitor_name']} added to heat.")
        else:
            print("Invalid competitor number.")
    selected_df = df.iloc[idxs]
    selected_names = selected_df["competitor_name"].tolist()
    print(f"{len(selected_names)} competitors selected for the current heat.")
    return selected_df, selected_names


#MENU OPTION 2: WOOD CHARACTERISTICS MENU
''' Official will be presented with a list of wood characteristics:
    1. Select Wood Species from the list
    2. Enter Size in mm
    3. Enter wood quality 
    4. Return to Main Menu

    This menu will allow the judge to select the characteristics of the wood block being used in the heat and store the 
    selection for handicap calculation.
    Wood species available will be loaded from the wood sheet in the excel file.
'''

## Wood Characteristics Menu 
def wood_menu(wood_selection):
    ''' Official will be presented with a list of wood characteristics
        1. Select Wood Species from the list
        2. Enter Size in mm
        3. Enter wood quality 
        (0 for poor quality, 1-3 for soft, 4-7 for average firmness for species, 8-10 for above average firmness for species)
        4. Return to Main Menu
    '''
    while True:
        print("\n--- Wood Menu ---")
        print(f"Current: species={wood_selection.get('species')}, size_mm={wood_selection.get('size_mm')}, quality={wood_selection.get('quality')}")
        print("1) Select wood species")
        print("2) Enter size (mm)")
        print("3) Enter quality (0 for poor quality, 1-3 for soft wood, 4-7 for average firmness for species, 8-10 for above average firmness for species")
        print("4) Back to Main Menu")
        s = input("Choose an option: ").strip()

        if s == "1":
            wood_selection = select_wood_species (wood_selection, wood_df=None)

        elif s == "2":
            wood_selection = enter_wood_size_mm(wood_selection)

        elif s == "3":
            wood_selection = enter_wood_quality(wood_selection)

        elif s == "4" or s == "":
            break
        else:
            print("Invalid selection. Try again.")
    return wood_selection

## Load wood speciess data from excel into a DataFrame.
def load_wood_data():
    try:
        df = pd.read_excel(WOOD_FILE, sheet_name=WOOD_SHEET)
        print("Wood data loaded successfully.")
        return df
    except Exception as e:
        print(f"Error loading wood data: {e}")
        return pd.DataFrame(columns=["species","multiplier"])

##Display species list, accept numeric choice

def select_wood_species (wood_selection, wood_df=None):
    """Select wood species"""
    if wood_df is None:
        wood_df = load_wood_data()
    if wood_df.empty:
        print("No wood data available.")
        return wood_selection
    print("\nAvailable wood species:")
    for i, sp in enumerate(wood_df["species"].tolist(), start=1):
        print(f"{i}) {sp}")
    choice = input("Select species by number: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(wood_df):
            wood_selection["species"] = wood_df["species"].iloc[idx]
            print(format_wood(wood_selection))
        else:
            print("Invalid selection.")
    except Exception:
        print("Invalid input.")
    return wood_selection

## Enter block size in mm
def enter_wood_size_mm(wood_selection):
    """Enter block size in mm"""
    size = input("Enter block diameter in mm: ").strip()
    try:
        val = float(size)
        wood_selection["size_mm"] = val
        print(format_wood(wood_selection))
    except Exception:
        print("Invalid size input.")
    return wood_selection

##Prompt for quality (integer 0–10)
'''Higher quality means softer wood and a faster time. 
this needs to account for that because softer wood would favor the front marker, 
and firmer wood would favor the front marker. 
we want to avoid a situation where the front marker finishes (or is close to finishing) before the backmarker even starts. 
A "0" (or poor quality of wood) indicates that the wood is rotten, has knots, is too dry, or has other imperfections that would make it barely suitable for competition.'''

def enter_wood_quality(wood_selection):
    """Enter wood quality rating as an integer 0–10"""
    while True:
        s = input("Enter wood quality (integer 0–10): ").strip()
        if s == "":
            print("No change made to wood quality.")
            break
        try:
            val = int(s)
            if val < 0: val = 0
            if val > 10: val = 10
            wood_selection["quality"] = val
            print(format_wood(wood_selection))
            break
        except Exception:
            print("Invalid input. Please enter an integer between 0 and 10.")
    return wood_selection

##Header that displays current wood selection
def format_wood(ws):
    """Return formatted header for wood selection"""
    s = ws.get("species","—")
    d = ws.get("size_mm","—")
    q = ws.get("quality","—")
    header = f"Selected Wood -> Species: {s}, Diameter: {d} mm, Quality: {q}"
    print(f"Wood selection updated: {header}")
    return header



# MENU OPTION 3: VIEW HANDICAP MARKS
''' Official will be presented with the calculated handicap marks for each selected competitor in the heat
    1. View Handicap Marks
    2. Return to Main Menu
'''

## View Handicap Marks Menu
def view_handicaps_menu(selected_df, wood_selection):
    ''' Official will be presented with the calculated handicap marks for each selected competitor in the heat
        1. View Handicap Marks
        2. Return to Main Menu
    '''
    while True:
        print("\n--- View Handicap Marks ---")
        print("1) View handicap marks for current heat")
        print("2) Back to Main Menu")
        s = input("Choose an option: ").strip()

        if s == "1":
            if selected_df is None or selected_df.empty:
                print("\nNo competitors selected. Use Competitor Menu -> Select competitors for heat.")
                continue
            if not wood_selection.get("species") or not wood_selection.get("size_mm"):
                print("\nWood selection incomplete. Use Wood Menu to set species and size.")
                continue
            view_handicaps(selected_df, wood_selection)
            input("\n(Press Enter to return to the View Handicap Marks menu) ")

        elif s == "2" or s == "":
            break

        else:
            print("Invalid selection. Try again.")


def view_handicaps(selected_df, wood_selection):
    if selected_df.empty:
        print("No competitors selected.")
        return

    # Convert DataFrame to dictionary for computation
    histories = {}
    for _, row in selected_df.iterrows():
        name = row["competitor_name"]
        recs = []
        for n in [("timeOne","sizeOne","speciesOne"),("timeTwo","sizeTwo","speciesTwo"),("timeThree","sizeThree","speciesThree")]:
            t = row.get(n[0]); s = row.get(n[2]); d = row.get(n[1])
            if pd.isna(t): 
                continue
            recs.append({"time": t, "size": d, "species": s, "quality": wood_selection.get("quality",5)})
        histories[name] = recs

    baseline = 300 if wood_selection.get("size_mm",300) >= 260 else 250


    '''Compute the composite wood index (w_index) for the current heat using compute_wood_index().
    This combines three factors:

        1. Size factor = selected block diameter ÷ baseline diameter.

        2. Quality multiplier = computed from the entered wood quality (0-10).

        3. Species multiplier = derived from the wood density, Janka, shear, MOR, MOE).
        The result represents how “fast” or “slow” the selected wood will chop compared to the baseline.

    -Initialize an empty dictionary predicted = {} to store each competitor's predicted time on the selected wood.

    -Loop through each competitor history in histories.items() (each record containing up to three prior chopping times with their respective sizes, species, and quality).

    -Precint each competitor's time by calling predict_time(recs, w_index, baseline, None).

    -This normalizes all previous times back to the baseline wood, calculates the median normalized time, and scales that value by thwe wood_index to
     guestimate how long the competitor should take on the selected block.

    -Add predictions to the predictions dictionary as long as we can compute a valid predicted time.

    -Convert predicted times into handicap marks using compute_marks

    -The slowest predicted competitor gets mark 3, and all others get 3 + ceil(slowest_time − their_time), clamped between 3 and 180.

    -The difference between two marks equals the intended start delay in seconds.'''

    #Add in the wood index calculation
    w_index = compute_wood_index(
        wood_selection.get("size_mm",baseline),
        baseline,
        wood_selection.get("quality",5),
        wood_selection.get("species"),
        None)
    predicted = {}

    #Time prediction loop
    for name, recs in histories.items():
        pt = predict_time(recs, w_index, baseline, None)
        if pt is not None:
            predicted[name] = pt

    marks = compute_marks(predicted)

    header = f"Selected Wood -> Species: {wood_selection.get('species','?')}, Diameter: {wood_selection.get('size_mm','?')} mm, Quality: {wood_selection.get('quality','?')}"
    print(header)

    # make sure the characteristic for each species exist
    _char_df = _load_wood_characteristics_df()
    sp_key = str(wood_selection.get("species","")).strip().lower()
    has_char = (not _char_df.empty) and ((_char_df["species"] == sp_key).any())
    print(f"Species factors from characteristics: {'ON' if has_char else 'OFF'}")


    #Print the actual final handicap marks
    print("-" * len(header))
    print("Handicap marks calculated and displayed below.\n")
    for name, mark in sorted(marks.items(), key=lambda x: x[1]):
        print(f"{name} Mark {mark}")


# (Helpers used by handicap prediction and marks)

##Cast to float
def _to_float_or_none(v):
    try:
        return float(v)
    except:
        return None

#Find medium for historical times
'''Step 1: Sort the list ascending.
    Step 2: If the count (n) is odd, return the middle value as a float.
    Step 3: If n is even, return the average of the two middle values.'''
def _median(nums):
    s = sorted(nums)
    n = len(s)
    if n == 0:
        return None
    if n % 2 == 1:
        return float(s[n//2])
    return (float(s[n//2 - 1]) + float(s[n//2])) / 2.0

#Load wood characteristics data from excel
def _load_wood_characteristics_df():
    try:
        df = pd.read_excel(WOOD_FILE, sheet_name=WOOD_SHEET)
    except Exception:
        return pd.DataFrame()

    # normalize column names
    df.columns = [str(c).strip().lower() for c in df.columns]

    def pick(aliases):
        for a in aliases:
            if a in df.columns:
                return a
        return None

    c_species = pick(["species","wood","wood species"])
    c_density = pick(["density","density (kg/m3)","density (kg/m³)"])
    c_janka   = pick(["janka","janka_hardness","janka hardness","janka (lbf)","janka (n)"])
    c_shear   = pick(["shear","shear_force","shear force","shear parallel","shear (mpa)","shear (psi)"])
    c_mor     = pick(["mor","modulus of rupture","modulus_of_rupture"])
    c_moe     = pick(["moe","modulus of elasticity","modulus_of_elasticity"])

    if c_species is None:
        return pd.DataFrame()

    keep = [c for c in [c_species, c_density, c_janka, c_shear, c_mor, c_moe] if c is not None]
    out = df[keep].copy()
    out.rename(columns={c_species: "species"}, inplace=True)
    if c_density: out.rename(columns={c_density: "density"}, inplace=True)
    if c_janka:   out.rename(columns={c_janka:   "janka"}, inplace=True)
    if c_shear:   out.rename(columns={c_shear:   "shear"}, inplace=True)
    if c_mor:     out.rename(columns={c_mor:     "mor"}, inplace=True)
    if c_moe:     out.rename(columns={c_moe:     "moe"}, inplace=True)

    out["species"] = out["species"].astype(str).str.strip().str.lower()
    for col in ["density","janka","shear","mor","moe"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    return out

#Meat and Potatoes of wood species formula
def compute_species_multiplier(species, species_index_map=None):
    if species is None:
        return 1.0

    df = _load_wood_characteristics_df()
    if df.empty:
        return 1.0

    key = str(species).strip().lower()
    row = df[df["species"] == key]
    if row.empty:
        return 1.0

    # Eastern White Pine baseline
    ewp_key = "eastern white pine"
    if (df["species"] == ewp_key).any():
        base = df[df["species"] == ewp_key].iloc[0]
        base_vals = {
            "density": float(base["density"]) if ("density" in df.columns and pd.notna(base.get("density"))) else None,
            "janka":   float(base["janka"])   if ("janka"   in df.columns and pd.notna(base.get("janka")))   else None,
            "shear":   float(base["shear"])   if ("shear"   in df.columns and pd.notna(base.get("shear")))   else None,
            "mor":     float(base["mor"])     if ("mor"     in df.columns and pd.notna(base.get("mor")))     else None,
            "moe":     float(base["moe"])     if ("moe"     in df.columns and pd.notna(base.get("moe")))     else None,
        }
    else:
        base_vals = {
            "density": float(df["density"].median()) if "density" in df.columns else None,
            "janka":   float(df["janka"].median())   if "janka"   in df.columns else None,
            "shear":   float(df["shear"].median())   if "shear"   in df.columns else None,
            "mor":     float(df["mor"].median())     if "mor"     in df.columns else None,
            "moe":     float(df["moe"].median())     if "moe"     in df.columns else None,
        }

    sp = row.iloc[0]
    sp_vals = {
        "density": float(sp["density"]) if ("density" in df.columns and pd.notna(sp.get("density"))) else None,
        "janka":   float(sp["janka"])   if ("janka"   in df.columns and pd.notna(sp.get("janka")))   else None,
        "shear":   float(sp["shear"])   if ("shear"   in df.columns and pd.notna(sp.get("shear")))   else None,
        "mor":     float(sp["mor"])     if ("mor"     in df.columns and pd.notna(sp.get("mor")))     else None,
        "moe":     float(sp["moe"])     if ("moe"     in df.columns and pd.notna(sp.get("moe")))     else None,
    }

    ratios = []
    for col in ["density","janka","shear","mor","moe"]:
        sv = sp_vals.get(col)
        bv = base_vals.get(col)
        if (sv is not None) and (bv is not None) and (bv > 0):
            r = sv / bv
            if r > 0:
                ratios.append(r)

    if not ratios:
        return 1.0

    # geometric mean of available ratios
    prod = 1.0
    for r in ratios:
        prod *= r
    mult = prod ** (1.0 / len(ratios))
    return float(mult)

##Factor Quality of Wood
'''Equalize for wood quality to make the front/back marker competition fairer.
Higher quality means softer wood and a faster time. (1.20 at 0 down to 0.80 at 10)
 Formula: multiplier = 1.20 - ((1.20 - 0.80) * (quality / 10))'''
def compute_quality_multiplier(quality):
    try:
        q = int(quality)
    except Exception:
        q = 5
    if q < 0: q = 0
    if q > 10: q = 10
    slow = 1.20
    fast = 0.80
    return slow - ((slow - fast) * (q / 10.0))

# Compute Wood Index
''' Combine size, quality, and species multipliers into a single wood index.
    wood_index = (diameter_mm / baseline_mm if valid else 1.0) * quality_multiplier * species_multiplier
'''
def compute_wood_index(diameter_mm, baseline_diameter_mm, quality, species=None, species_index_map=None):
    d = _to_float_or_none(diameter_mm)
    b = _to_float_or_none(baseline_diameter_mm)
    if (d is None) or (b is None) or (b <= 0):
        size_factor = 1.0
    else:
        size_factor = d / b
    q_mult = compute_quality_multiplier(quality)
    s_mult = compute_species_multiplier(species, None)  # ignore species_index_map; we use measured characteristics
    return size_factor * q_mult * s_mult

# Predicts how long a competitor will take based on the wood selection for the heat
def predict_time(records, selected_wood_index, baseline_diameter_mm, species_index_map=None):
    normalized = []
    for r in records:
        t = _to_float_or_none(r.get("time"))
        if t is None:
            continue
        d = r.get("size")
        q = r.get("quality",5)
        s = r.get("species")
        w_index = compute_wood_index(d, baseline_diameter_mm, q, s, None)
        normalized.append(t / w_index)
    if not normalized:
        return None
    base = _median(normalized)
    return base * selected_wood_index

# Convert the predicted times into handicap marks
''' Steps:
 1. Find the slowest predicted time among the field (in seconds).
 2. For each competitor, compute a “gap” = slowest_time - competitor_time.
 3. Convert each gap to a mark as follows: mark = 3 + the gap rounded up to the next whole second (always round up).
 4. The difference between two marks equals the intended start separation in seconds (e.g., marks 3 and 11 mean the second athlete starts 8 seconds later).
 5. The upper limit is restricted to 180 seconds. Never go below 3.'''
def compute_marks(predicted_times):
    if not predicted_times:
        return {}
    slowest = max(predicted_times.values())
    marks = {}
    for name, t in predicted_times.items():
        gap = slowest - t
        raw = 3 + ceil(gap)
        if raw < 3: raw = 3
        if raw > 180: raw = 180
        marks[name] = int(raw)
    return marks