## Function Dictionary

| Function | Parameters | Purpose |
|:---|:---|:---|
| `load_competitors_df` | *(none)* | Load the roster from Excel into a DataFrame; on error, print message and return empty DataFrame with expected columns. |
| `list_competitors` | `DataFrame df` | Print roster of competitors with name, country, and last handicap; if empty, print notice. |
| `add_competitor_to_excel` | *(none)* | Prompt for name/country/last_handicap, append a new row to the Excel roster (creating header if needed), save, and return the updated DataFrame; prints confirmations/errors. |
| `action_remove_competitor` | `DataFrame df` | Remove a competitor by exact name from the DataFrame and rewrite the Excel sheet; print confirmations or not-found message; return updated `df`. |
| `action_select_for_heat` | `DataFrame df`, `int max_select=8` | One-at-a-time selector for heat competitors (press Enter to finish); prevents duplicates; returns `(selected_df, selected_names_list)` and prints count/confirmations. |
| `load_wood_data` | *(none)* | Load wood species data from Excel into a DataFrame; on error, print message and return empty `["species","multiplier"]` DataFrame. |
| `select_wood_species` | `dict wood_selection`, `DataFrame wood_df=None` | Display species list, accept numeric choice, set `wood_selection["species"]`, and print the standardized wood header; handles invalid/empty data safely. |
| `enter_wood_size_mm` | `dict wood_selection` | Prompt for block diameter (mm), set `wood_selection["size_mm"]`, and print the standardized wood header; handles invalid numeric input. |
| `enter_wood_quality` | `dict wood_selection` | Prompt for wood quality as an integer 0–10 (blank = no change; clamps to [0,10]), set `wood_selection["quality"]`, and print the standardized wood header. |
| `format_wood` | `dict ws` | Build and return `Selected Wood -> Species: X, Diameter: Y mm, Quality: Z`; also print “Wood selection updated: …”. |
| `_to_float_or_none` | `any v` | Utility: cast to `float` or return `None` on failure. |
| `_median` | `iterable nums` | Utility: median of a list (odd → middle value; even → average of two middles); returns `None` for empty. |
| `compute_quality_multiplier` | `int quality` | Map wood quality (0–10) to linear time multiplier (1.20 at 0 down to 0.80 at 10); parses/clamps, defaults to 5 on parse failure. |
| `_load_wood_characteristics_df` | *(none)* | Load and normalize wood characteristics from Excel (species, density, janka, shear, MOR, MOE) with alias resolution; return standardized DataFrame. |
| `compute_species_multiplier` | `string species`, `dict species_index_map=None` | Compute species multiplier via geometric mean of ratios to Eastern White Pine (or dataset medians) using available characteristics; >1.0 harder/slower, <1.0 softer/faster. |
| `compute_wood_index` | `float diameter_mm`, `float baseline_diameter_mm`, `int quality`, `string species=None`, `dict species_index_map=None` | Combine size factor, quality multiplier, and species multiplier into a composite wood index; size factor defaults to 1.0 if inputs invalid. |
| `predict_time` | `list[dict] records`, `float selected_wood_index`, `float baseline_diameter_mm`, `dict species_index_map=None` | Normalize each historical time by its own wood index, take median, then scale by `selected_wood_index`; return predicted seconds or `None` if no valid records. |
| `compute_marks` | `dict predicted_times` | Convert predictions to handicap marks: slowest gets 3; for each competitor `mark = 3 + ceil(slowest − time)` clamped to [3, 180]; ties allowed. |
| `view_handicaps` | `DataFrame selected_df`, `dict wood_selection` | End-to-end calculation/display: build histories, choose baseline (300mm if size ≥ 260 else 250), compute wood index, predict times, compute marks, print standardized wood header and compact `Name Mark X` lines in ascending mark order. |
| `pick` | `list[str] aliases` | Helper to normalize multiple input aliases into one canonical choice string. |
| `competitor_menu` | *(none)* | **Menu (in `DeliverableOne.py`):** list competitors, select for heat (one-at-a-time Enter workflow), add competitor, remove competitor; updates `comp_df`/`selected_df` and prints confirmations. |
| `wood_menu` | *(none)* | **Menu (in `DeliverableOne.py`):** choose species, enter size (mm), enter **integer** quality (0–10); prints the standardized wood header after each change. |
| `view_handicaps_menu` | *(none)* | **Menu (in `DeliverableOne.py`):** runs the handicap calculation pipeline for current selections and prints the compact start sheet. |
