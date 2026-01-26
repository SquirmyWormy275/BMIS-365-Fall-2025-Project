# Woodchopping Handicap Calculator

## Executive Summary
In the sport of woodchopping, there are two types of races that can occur. The first type of race is called a 'Championship' race and occurs when all competitors start at the same time on the mark of 'Go.' The second type of race more common in Australia and New Zealand is a handicapped race. A properly handicapped race allows competitors of all ability levels to have roughly the same chance of winning the race. The idea is that it keeps top-tier competitors from growing complacent, and allows newer compeitors the potential to win large amounts of money that would allow them to invest in better equipment and travel to more competitions. In Australia, the purses on prestigious handicap races can reach into the tens of thousands of dollars. The tangibility of the handicap 'marks' also allows for unbelievably lucrative sports betting to occur, and many venues make a significant portion of thier revenue through the proceeds. In the United States, there is currently no handicapping system. This forces mid-tier competitors to compete at a loss for years on end, and allows for top-tier competitors to grow complacent. While the Australians have a good framework for handicapping, it is largely subjective. Given the stakes and the amount of money involved, this system becomes highly political. According to the Australian Axemen Assosciation's Competition Rulebook, handicapping is determined by tht following means:

"12. Competitors in Events conducted in heats or divisions shall be handicapped at the
 discretion of the Committee or, if appointed, the Handicapper.
13. Handicaps will be determined based on form, inherent ability and performances and such
other information as may be deemed by the Committee, or Handicapper, to be relevant. "

In a perfectly handicapped system, all of the competitors should sever their blocks at the same time. Since the Australian's have over 150 years of experience handicapping competitors, they are usually fairly accurate at determining marks. Having a more objective system that accurately considers the various factors that impact the time to sever the block would eliminate the guesswork and bias inherhent to the handicapper, and would allow the system to be implemented in countries that lack the instituitonal knowledge. This system would hopefully help eliminate the common practices of "foxing" or "laying down", where competitors perform deliberately poorly in order to get their handicap lowered prior to a bigger race. In short, a proper handicap calculator would create fairer competition, more exciting races for the spectators, and better distribution of purses.'''


## Statement of Scope
  **Project objectives:** This project will allow a judge to add or remove competitors from a master excel sheet, select competitors from that master roster for a heat, and accurately calcualte handicap marks for competitors of any ability level. As long as there three doceumented times with the noted wood species and size, the most novice competitor will have an equal shot at winning a handicap race against the best in the world. The formula works with two main components. The first componenet is the competitor spread. By using past data, we can predict what a future competitors time to completion will be. The second piece of the formula involves wood. By accounting for factors like Janka Hardness and Shear force, we can have a pretty accurate model of how an axe will behave in wood of varrying firmness. By accounting for the wood quality and characteristics, we can avoid a scenario where the wood is so soft that a frontmarker finishes before the back marker even starts. By combining the predicted time and the wood characteristics, we can ensure that judges have a quick, easily readable way to create heats with competitors of all abilities.

**Value add:** American Timbersports athletes and officials will have the ability to easily and accurately implement a handicap system without a century-plus of institutional knowledge. Competitive events and organizations will be able to accurately calculate handicaps for competitors, and adjust handicap marks in a competition objectively based on a competitor's performace. This app will allow for a fairer and more equitable competition wherever implemented.

## Inputs, Processes, and Outputs


### Step 1: Load Libraries
* **Description:** Import core libraries used 
* **Inputs:** None for this step.  
* **Processes:** Import `pandas`, `numpy`, `matplotlib`, `sys`, `math.ceil`, and `openpyxl`.  
* **Outputs:** None for this step; proceed to **Step 2**.


### Step 2: Load Competitor Roster
* **Description:** Read the competitor roster from Excel into memory.  
* **Inputs:** `woodchopping.xlsx`, sheet `"competitors"`.  
* **Processes:** Attempt to load into a DataFrame; on failure, build an empty DataFrame with the expected columns and print a descriptive message.  
* **Outputs:** `comp_df` is available in memory; proceed to **Step 3**.


### Step 3: Initialize Program State
* **Description:** Create clean placeholders for the session.  
* **Inputs:** None for this step.  
* **Processes:** Initialize `wood_selection = {species: None, size_mm: None, quality: None}`; create empty `selected_df` and `selected_names`.  
* **Outputs:** Internal state ready; proceed to **Step 4**.


### Step 4: Welcome Message
* **Description:** Display "Welcome to the Woodchopping Handicap Calcualtor"
* **Inputs:** None for this step.  
* **Processes:** Print greeting and prepare to show the main menu options.  
* **Outputs:** display message; proceed to **Step 5**.


### Step 5: Main Menu Selection
* **Description:** Present the primary navigation loop to for the main menu  
* **Inputs:** A number from **1–5** entered by the official.  
* **Processes:** Evaluate the choice and route accordingly.  
* **Outputs:**  
  * For Option 1: **Competitor Selection Menu**, go to **Step 6**.  
  * For Option 2: **Wood Characteristics Menu**, go to **Step 10**.  
  * For Option 3: **View Handicap Marks**, go to **Step 13**.  
  * For Option 4: **Reload Roster**, go to **Step 18**.  
  * For Option 5: **Exit**, go to **Step 19**.

### Step 6: Competitor Menu — View Roster
* **Description:** Show `competitor_name`, `competitor_country`, and `last_handicap` for each entry.  
* **Inputs:** None beyond `comp_df` already in memory.  
* **Processes:** Print a compact roster or a message if the roster is empty.  
* **Outputs:** Returns to **Step 6** (Competitor Menu). If “Back” is chosen, return to **Step 5**.

### Step 7: Competitor Menu — Select Competitors (one-at-a-time)
* **Description:** Build the heat field using the Enter-to-finish workflow (max 8).  
* **Inputs:** A sequence of numeric entries; blank **Enter** to finish.  
* **Processes:** Validate indices; prevent duplicates; cap selections at eight; acknowledge each addition.  
* **Outputs:** Updates `selected_df` and `selected_names`; return to **Step 6**. If “Back” is chosen, return to **Step 5**.

### Step 8: Competitor Menu — Add Competitor
* **Description:** Append a new competitor to the Excel roster.  
* **Inputs:** Name, country, last handicap (prompted).  
* **Processes:** Create header if needed; append a row; save workbook; reload roster to keep memory in sync.  
* **Outputs:** Updated `comp_df`; return to **Step 6**. If “Back” is chosen, return to **Step 5**.

### Step 9: Competitor Menu — Remove Competitor
* **Description:** Remove a competitor by exact name and rewrite the Excel sheet.  
* **Inputs:** Exact competitor name (prompted).  
* **Processes:** Filter DataFrame; rewrite rows under the header; save; print confirmations or “not found”.  
* **Outputs:** Updated `comp_df`; return to **Step 6**. If “Back” is chosen, return to **Step 5**.

### Step 10: Wood Menu — Select Species
* **Description:** Choose the wood species for the current heat from the wood sheet.  
* **Inputs:** Numeric choice corresponding to a listed species.  
* **Processes:** Load species list; set `wood_selection["species"]`; print standardized wood header.  
* **Outputs:** Return to **Step 10** (Wood Menu). If “Back” is chosen, return to **Step 5**.

### Step 11: Wood Menu — Enter Size (mm)
* **Description:** Specify the block diameter in millimeters.  
* **Inputs:** Numeric diameter in mm.  
* **Processes:** Parse number; update `wood_selection["size_mm"]`; print standardized wood header.  
* **Outputs:** Return to **Step 10**. If “Back” is chosen, return to **Step 5**.

### Step 12: Wood Menu — Enter Quality (0–10 integer)
* **Description:** Capture the wood quality rating for the heat.  
* **Inputs:** Integer **0–10** (blank leaves prior value).  
* **Processes:** Clamp to **[0, 10]**; update `wood_selection["quality"]`; print standardized wood header.  
* **Outputs:** Return to **Step 10**. If “Back” is chosen, return to **Step 5**.

### Step 13: View Handicaps — Preconditions Check
* **Description:** Ensure selections exist before computing marks.  
* **Inputs:** `selected_df` and `wood_selection`.  
* **Processes:** Verify that at least one competitor is selected and that species and size are set; print guidance if anything is missing.  
* **Outputs:**  
  * If competitors are missing, go to **Step 6**.  
  * If wood species/size is missing, go to **Step 10**.  
  * If all required inputs exist, go to **Step 14**.

### Step 14: Compute Wood Index
* **Description:** Produce a composite multiplier from size, quality, and species characteristics.  
* **Inputs:** `wood_selection.size_mm`, `wood_selection.quality`, `wood_selection.species`; wood characteristics from Excel; baseline diameter (**300 mm** if size ≥ 260 else **250 mm**).  
* **Processes:** Compute size factor; compute quality multiplier (**1.20** at 0 down to **0.80** at 10); compute species multiplier via characteristics; multiply to get the wood index.  
* **Outputs:** Wood index for the heat; proceed to **Step 15**.

### Step 15: Predict Competitor Times
* **Description:** Estimate each competitor’s finish time on the selected wood.  
* **Inputs:** Up to three historical records per competitor (time, size, species), the wood index from **Step 14**, and the baseline diameter.  
* **Processes:** Normalize historical times to baseline using each record’s own index; take the median; scale by the current wood index.  
* **Outputs:** Dictionary of predicted times by competitor; proceed to **Step 16**.

### Step 16: Convert Predictions to Handicap Marks
* **Description:** Convert predicted seconds into start marks per the handicap rules.  
* **Inputs:** Predicted times from **Step 15**.  
* **Processes:** Identify the slowest predicted time; for each competitor compute `gap = slowest − time`; `mark = 3 + ceil(gap)`; clamp to **[3, 180]**; ties allowed.  
* **Outputs:** Integer marks per competitor; proceed to **Step 17**.

### Step 17: Print Start Sheet
* **Description:** Display the standardized wood header and the compact list of marks.  
* **Inputs:** Marks and the selected wood header.  
* **Processes:** Print header; indicate whether species characteristics were applied (ON/OFF); list “`Name Mark X`” in ascending mark order.  
* **Outputs:** Printed start sheet; return to **Step 13** (View Handicaps menu). Choosing “Back” there returns to **Step 5**.

### Step 18: Reload Roster (Optional, listed as Main Menu Option 4)
* **Description:** Refresh the in-memory roster from the Excel file.  
* **Inputs:** Selection of the reload option from the main menu.  
* **Processes:** Re-run the roster load and replace `comp_df`; handle errors safely.  
* **Outputs:** Confirmation or error message; return to **Step 5**.

### Step 19: Exit Program
* **Description:** End the session.  
* **Inputs:** Selection of “Exit” from the main menu.  
* **Processes:** Break the main loop and finalize.  
* **Outputs:** “Goodbye.” printed; program terminates.
