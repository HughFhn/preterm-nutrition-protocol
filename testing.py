import pandas as pd
from enum import Enum

# === Functions ===

# Function to add tuple ranges to show min and max total vals
def add_ranges(t1, t2):
    return (t1[0]+t2[0], t1[1]+t2[1])

# Get PN row based on cSPN type and DOL
def get_pn_row(table, aqueous_type, dol):
    dol_filter = '4+' if dol >= 4 else dol
    row = table.loc[
        (table[('Aqueous SPN Product', 'Name')] == aqueous_type) &
        (table[('Patient Info', 'Day of Life')] == dol_filter)
    ]
    if row.empty:
        raise ValueError(f"No matching PN row for {aqueous_type} and DOL {dol_filter}")
    return row.iloc[0]  # Return a single row as Series
 
# Calculate patient-specific SPN target volumes
def calculate_patient_spn(row, weight):
    # Extract protocol ranges directly from the row
    aq_target = row[('Aqueous SPN Product', 'Target Volume')]
    lipid_target = row[('Lipid SPN Product', 'Target Volume')]
    
    # Total SPN range = sum of tuples
    total_spn = (aq_target[0] + lipid_target[0], aq_target[1] + lipid_target[1])
    
    return aq_target, lipid_target, total_spn

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

# Create a multi-level header for SPN products
spn_header = pd.MultiIndex.from_product(
    [['Aqueous SPN Product', 'Lipid SPN Product'],
     ['Name', 'Target Volume']],
    names=['Type', 'Value']
)

# === Create daframe ===

# Create DataFrame and fill clinical protocol
pnTable = pd.DataFrame(columns=spn_header)
pnTable[('Aqueous SPN Product', 'Name')] = ['cSPN1', 'cSPN1', 'cSPN2', 'cSPN2']
pnTable[('Lipid SPN Product', 'Name')] = 'SMOFlipid with vits'

# Fill in target volumes (mL/kg/d)
pnTable[('Aqueous SPN Product', 'Target Volume')] = [(65,65), (65,90), (75,120), (75,120)]
pnTable[('Lipid SPN Product', 'Target Volume')] = [(6,12), (12,18), (18,24), (18,24)]

# Add regular columns for EN feed, Day of Life, and Total SPN Volume
pnTable[('Patient Info', 'EN Feed Volume (mL)')] = "<40"
pnTable[('Patient Info', 'Day of Life')] = [1, 2, 3, "4+"]

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

print('\n')
print('='*135)
print(pnTable)
print('='*135)
print('\n')

# === Grab volumes and totals based on input info ===

if pnPhase:
    pnRow = get_pn_row(pnTable, selected_cSPN.value, dol)
    aq_target, lipid_target, total_spn = calculate_patient_spn(pnRow, weight)

    print('='*80)
    print(f"Users inputs: EN Volume: {en_volume}, DOL: {dol}, Weight: {weight}, Aqueous Type: {selected_cSPN.value}")
    print(f"Aqueous SPN Target (mL/day): {aq_target}")
    print(f"Lipid SPN Target (mL/day): {lipid_target}")
    print(f"Total SPN Volume (mL/day): {total_spn}")
    print(f"")
    print('='*80)
    print('\n')

else:
    print('TN Phase not implemented yet')
