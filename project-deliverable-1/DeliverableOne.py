#Import Pandas, numpy, 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from math import ceil
from openpyxl import load_workbook

#Import Functions from project_functinos.py
import project_functions as FL

# file/sheet names (saved in the same directory as this script!!!!!!!!!!!!!!!!!!!!!!!!)
COMPETITOR_FILE  = "woodchopping.xlsx"
COMPETITOR_SHEET = "competitors"
WOOD_FILE        = "woodchopping.xlsx"
WOOD_SHEET       = "wood"

#Load Competitor and Wood Data from Excel
'''Read the xlsx file containing data. 
Sheet "competitors" contains competitor data
Sheet "wood" contains wood species data'''
try:
    comp_df = FL.load_competitors_df()
except Exception as e:
    print(f"Error loading roster from Excel: {e}")
    comp_df = pd.DataFrame(columns=[
        "competitor_name","competitor_country","last_handicap",
        "timeOne","sizeOne","speciesOne",
        "timeTwo","sizeTwo","speciesTwo",
        "timeThree","sizeThree","speciesThree",
    ])

#Wood Selection Dictionary
wood_selection = {"species": None, "size_mm": None, "quality": None}

# If a formatter exists in FL, alias to it (no local logic kept here)
format_wood = getattr(FL, "format_wood", lambda ws: f"species={ws.get('species') or '—'}, size_mm={ws.get('size_mm') or '—'}, quality={ws.get('quality') or '—'}")

# Selected competitors state
selected_df = comp_df.iloc[0:0].copy()
selected_names = []

## Competitor Selection Menu
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

## Wood Characteristics Menu
''' Official will be presented with a list of wood characteristics
    1. Select Wood Species from the list
    2. Enter Size in mm
    3. Enter wood quality 
    (0 for poor quality, 1-3 for soft, 4-7 for average firmness for species, 8-10 for above average firmness for species)
    4. Return to Main Menu
'''

## View Handicap Marks
''' Official will be presented with the calculated handicap marks for each selected competitor in the heat
    1. View Handicap Marks
    2. Return to Main Menu
'''

## Main Menu
''' Official will enter the menu and be presented with two options
1. Competitor Selection Menu
2. Wood Characteristics Menu
3. View Handicap Marks
create a loop that will allow the official to return to the main menu after completing tasks in sub-menus
run menu as a function to allow for easy return to main menu
'''
while True:
    print("\nWelcome to the Wood Chopping Handicap Management System")
    print("Please select an option from the Main Menu:")
    print("1. Competitor Selection Menu")
    print("2. Wood Characteristics Menu")
    print("3. View Handicap Marks")
    print("4. Reload roster from Excel")
    print("5. Exit")
    menu_choice = input("Enter your choice (1-5): ").strip()

    if menu_choice == '1':
        # Calls into functions library; returns updated state
        comp_df, selected_df, selected_names = FL.competitor_menu(comp_df, selected_df, selected_names)

    elif menu_choice == '2':
        # Calls into functions library; returns updated wood selection
        wood_selection = FL.wood_menu(wood_selection)

    elif menu_choice == '3':
        # Calls into functions library; displays handicaps
        FL.view_handicaps_menu(selected_df, wood_selection)

    elif menu_choice == '4':
        try:
            comp_df = FL.load_competitors_df()
            print("Roster reloaded from Excel.")
        except Exception as e:
            print(f"Failed to reload roster: {e}")

    elif menu_choice == '5' or menu_choice == '':
        print("Goodbye.")
        break

    else:
        print("Invalid selection. Try again.")