import pandas as pd
import numpy as np
from enum import Enum

# Enum class for the SPN type
class AqueousSPN(Enum):
    CSPN1 = "cSPN1"
    CSPN2 = "cSPN2"

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


# Create a multi-level header for SPN products
spn_header = pd.MultiIndex.from_product(
    [['Aqueous SPN Product', 'Lipid SPN Product'],
     ['Name', 'Target Volume']],
    names=['Type', 'Value']
)

# Create a DataFrame with random values for SPN products
pnTable = pd.DataFrame(
    columns=spn_header
)

# Fill in product names
pnTable[('Aqueous SPN Product', 'Name')] = ['cSPN1', 'cSPN1', 'cSPN2', 'cSPN2']
pnTable[('Lipid SPN Product', 'Name')] = 'SMOFlipid with vits'

# Fill in target volumes (mL/kg/d)
pnTable[('Aqueous SPN Product', 'Target Volume')] = [(65,65), (65,90), (75,120), (75,120)]
pnTable[('Lipid SPN Product', 'Target Volume')] = [(6,12), (12,18), (18,24), (18,24)]

# Add regular columns for EN feed, Day of Life, and Total SPN Volume
pnTable[('Patient Info', 'EN Feed Volume (mL)')] = "<40"
pnTable[('Patient Info', 'Day of Life')] = [1, 2, 3, "4+"]

# Function to add tuple ranges to show min and max total vals
def add_ranges(t1, t2):
    return (t1[0]+t2[0], t1[1]+t2[1])

# Calculate Total SPN Volume as a tuple range
pnTable[('Patient Info', 'Total SPN Volume (mL/kg/d)')] = [
    add_ranges(aq, lip) for aq, lip in zip(
        pnTable[('Aqueous SPN Product', 'Target Volume')],
        pnTable[('Lipid SPN Product', 'Target Volume')]
    )
]

# Reorder columns: Patient Info first, SPN products after
patient_cols = [col for col in pnTable.columns if col[0] == 'Patient Info']
spn_cols = [col for col in pnTable.columns if col[0] != 'Patient Info']
pnTable = pnTable[patient_cols + spn_cols]

print('='*135)
print(pnTable)
print('='*135)

# Operate on user input and use table to show target val
print(f'\nUsers inputs: \nEN Volume: {en_volume} \nDOL: {dol} \nWeight: {weight} \nAqueous Type: {selected_cSPN.value}')

if pnPhase:
    # Use a display-friendly DOL for filtering, without changing original dol
    dol_filter = '4+' if dol >= 4 else dol

    # Filter table by Aqueous SPN type and Day of Life
    pnRow = pnTable.loc[
        (pnTable[('Aqueous SPN Product', 'Name')] == selected_cSPN.value) &
        (pnTable[('Patient Info', 'Day of Life')] == dol_filter)
    ]

    # Check if any row matched
    if pnRow.empty:
        raise ValueError(f"No matching SPN row found for {selected_cSPN.value} and DOL {dol_filter}")

    # pnRow now contains the correct row
    print(pnRow)
    
else: # TN not done yet
    print('Not done yet')