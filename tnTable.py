import pandas as pd
# See all columns and rows:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

from enum import Enum

# ============================================================
# Get PN row based on cSPN type and DOL
def get_row(table, aqueous_type, dol, enVal):
    dol_filter = normalize_dol(dol)
    row = table.loc[
        (table[('Aqueous SPN Product', 'Name')] == aqueous_type) &
        (table[('Patient Info', 'Day of Life')] == dol_filter) &
        (table.index.get_level_values('enVal') == enVal)
    ]
    if row.empty:
        raise ValueError(f"No matching PN row for {aqueous_type} and DOL {dol_filter} and EN {enVal}")
    return row.iloc[0]  # Return a single row as Series

# Used as dol is now a string
def normalize_dol(dol):
    if isinstance(dol, int):
        if dol <= 2:
            return f"dol{dol}"
        else:
            return "dol3+"
    else:
        return dol

# Function to add tuple ranges to show min and max total vals
def add_ranges(t1, t2):
    return (t1[0]+t2, t1[1]+t2)

# Function to build table using dict and assign enVal to it
def build_tn_table(block_data, en_value):
    # Ensure dol, cspn, aq, lipid_name, lipid_target are all lists
    for key in ['dol', 'cspn', 'aq', 'lipid_name', 'lipid_target']:
        if not isinstance(block_data[key], list):
            block_data[key] = [block_data[key]]

    df = pd.DataFrame({
        ('Patient Info', 'Day of Life'): block_data['dol'],
        ('Aqueous SPN Product', 'Name'): block_data['cspn'],
        ('Aqueous SPN Product', 'Target Volume'): block_data['aq'],
        ('Lipid SPN Product', 'Name'): block_data['lipid_name'],
        ('Lipid SPN Product', 'Target Volume'): block_data['lipid_target'],
    })

    # Calculate total fluid volume
    total = []
    for aq, lip in zip(block_data['aq'], block_data['lipid_target']):
        total.append((aq[0] + lip + en_value, aq[1] + lip + en_value))

    df[('Patient Info', 'Total Fluid Volume (mL/kg/d)')] = total
    df['enVal'] = en_value

    return df


#============================================

# TN raw data
tn_blocks = {
    "40": {
        "dol": ['dol2', 'dol3+'],
        "cspn": ['cSPN1', 'cSPN2'],
        "aq": [(45,70), (55,100)],
        "lipid_name": ['SMOFlipid with vits', 'SMOFlipid with vits'],
        "lipid_target": [12, 18],
    },
    "50": {
        "dol": ['dol2', 'dol3+'],
        "cspn": ['cSPN1', 'cSPN2'],
        "aq": [(40,70), (50,95)],
        "lipid_name": ['SMOFlipid with vits', 'SMOFlipid with vits'],
        "lipid_target": [12, 18],
    },
    "60": {
        "dol": ['dol2', 'dol3+'],
        "cspn": ['cSPN1', 'cSPN2'],
        "aq": [(40,65), (45,90)],
        "lipid_name": ['SMOFlipid with vits', 'SMOFlipid with vits'],
        "lipid_target": [12, 12],
    },
    "70": {
        "dol": ['dol3+'],
        "cspn": ['cSPN2'],
        "aq": [(40,85)],
        "lipid_name": ['SMOFlipid with vits'],
        "lipid_target": [12],
    },
    "80": {
        "dol": ['Fortify EBM'],
        "cspn": ['cSPN2'],
        "aq": [(40,75)],
        "lipid_name": ['SMOFlipid with vits'],
        "lipid_target": [12],
    },
    "90": {
        "dol": ['Fortify EBM'],
        "cspn": ['cSPN2'],
        "aq": [(30,65)],
        "lipid_name": ['SMOFlipid with vits'],
        "lipid_target": [12],
    },
    "100": {
        "dol": ['Fortify EBM'],
        "cspn": ['cSPN2'],
        "aq": [(20,55)],
        "lipid_name": ['SMOFlipid with vits'],
        "lipid_target": [12],
    },
    "110": {
        "dol": ['Fortify EBM'],
        "cspn": ['cSPN2'],
        "aq": [(10,45)],
        "lipid_name": ['SMOFlipid with vits'],
        "lipid_target": [12],
    },
    "120": {
        "dol": ['Stop SPN unless clinically indicated'],
        "cspn": [''],
        "aq": [(0,0)],
        "lipid_name": [''],
        "lipid_target": [0],
    }
}

# ============================================================
# Create a multi-level header for SPN products
spn_header = pd.MultiIndex.from_product(
    [['Aqueous SPN Product', 'Lipid SPN Product'],
     ['Name', 'Target Volume']],
    names=['Type', 'Value']
)

tnTable = pd.DataFrame(columns=spn_header)

tnTable = pd.concat([
    build_tn_table(tn_blocks[k], int(k)) for k in tn_blocks
], ignore_index=True)

# Set MultiIndex
tnTable.set_index('enVal', inplace=True)

# ============================================================

# Enum class for the SPN type
class AqueousSPN(Enum):
    CSPN1 = "cSPN1"
    CSPN2 = "cSPN2"

# === Application ===

# Ask user for info
en_volume = int(input("Please enter EN Volume in mL: "))
dol = int(input("Please enter Day Of Life: "))

# After assessing the dol and en vol, one of these will be true and operations on that table will happen
pnPhase = False
tnPhase = False
valid = False

#cSPN assign based on dol
if dol < 0:
    print("\nInvalid day of life")
    dol = int(input("Please enter Day of Life: "))
    
elif dol <= 2:
    selected_cSPN = AqueousSPN.CSPN1 # cSPN1
    
else:
    selected_cSPN = AqueousSPN.CSPN2 # cSPN2

# Check basic edge cases and selects which table to use
while valid != True:

    if en_volume > 120:
        print("\nStop SPN unless clinically indicated")
        en_volume = int(input("Please enter EN Volume in mL: "))

    elif en_volume < 0:
        print("\nCannot be less than zero")
        en_volume = int(input("Please enter EN Volume in mL: "))
        
    elif en_volume >= 40 and dol >= 2:
        tnPhase = True
        valid = True
        
    elif en_volume > 0 and en_volume < 40:
        pnPhase = True
        valid = True

weight = float(input("Please enter weight in kg: "))

# ==========================================================
tnRow = get_row(tnTable, selected_cSPN.value, dol, en_volume)
print(tnTable)

print('=' * 80)
print(f"User Inputs -> EN Volume: {en_volume}, DOL: {dol}, Weight: {weight}, SPN Type: {selected_cSPN.value}\n")
print(f"This is the result of the input\n{tnRow}")
print('=' * 80)
print('\n')
