import pandas as pd

row = pd.Series({
    
    ('Aqueous SPN Product', 'Target Volume'): 80,   # mL/kg/day
    ('Aqueous SPN Product', 'Min Volume'): 45,      # mL/kg/day
    ('Aqueous SPN Product', 'Max Volume'): 90,      # mL/kg/day
    
    ('Lipid SPN Product', 'Target Volume'): 12,     # mL/kg/day
    ('Lipid SPN Product', 'Min Volume'): 12,      # mL/kg/day
    ('Lipid SPN Product', 'Max Volume'): 12,      # mL/kg/day
})

def calculate_patient_spn(self, row):
    """
    STARTER FUNCTION - fill in the logic yourself
    All variables you need are exposed and printed.
    """

    # ===== Protocol constraints (mL/kg/day) =====
    aq_target = row[('Aqueous SPN Product', 'Target Volume')]
    aq_min = row[('Aqueous SPN Product', 'Min Volume')]
    aq_max = row[('Aqueous SPN Product', 'Max Volume')]

    lip_target = row[('Lipid SPN Product', 'Target Volume')]
    lip_min = row[('Lipid SPN Product', 'Min Volume')]
    lip_max = row[('Lipid SPN Product', 'Max Volume')]

    # ===== Patient inputs =====
    en = self.en_volume          # mL/kg/day
    tfi = self.tfi               # mL/kg/day
    wt = self.weight             # kg

    # ===== STEP 1: Available fluid for SPN =====
    available_spn = tfi - en
    available_spn = max(0, tfi - en)

    print("\n--- INPUTS ---")
    print(f"EN: {en}")
    print(f"TFI: {tfi}")
    print(f"Available for SPN: {available_spn}")

    print("\n--- CONSTRAINTS ---")
    print(f"Aqueous min / target / max: {aq_min} / {aq_target} / {aq_max}")
    print(f"Lipid target: {lip_target}")

    # ===== STEP 2: Allocate lipid (YOU decide how) =====
    lipid_alloc = min(lip_target, lip_max, available_spn)

    if lipid_alloc < lip_min:
        status = "Below lipid minimum"

    print("\n--- AFTER LIPID ---")
    print(f"Lipid allocated: {lipid_alloc}")

    # ===== STEP 3: Remaining fluid =====
    remaining = available_spn - lipid_alloc

    print(f"Remaining fluid: {remaining}")

    # ===== STEP 4: Allocate aqueous (YOU decide how) =====
    
    if remaining >= aq_target:
        status = "Good"
        aqueous_alloc = aq_target
    
    elif aq_min <= remaining and remaining < aq_target:
        status = "Between minimum and target"
        aqueous_alloc = remaining
    
    elif remaining < aq_min:
        status = "Below minimum requirement"
        aqueous_alloc = remaining
         
    print("\n--- FINAL SPN (mL/kg/day) ---")
    print(f"Aqueous allocated: {aqueous_alloc}")
    print(f"Lipid allocated: {lipid_alloc}")
    print(f"Status: {status}")

    # ===== STEP 5: Convert to patient volumes =====
    aqueous_ml = aqueous_alloc * wt
    lipid_ml = lipid_alloc * wt
    total_spn_ml = aqueous_ml + lipid_ml

    print("\n--- PATIENT VOLUMES (mL/day) ---")
    print(f"Aqueous: {aqueous_ml}")
    print(f"Lipid: {lipid_ml}")
    print(f"Total SPN: {total_spn_ml}")

    return {
        "aqueous_per_kg": aqueous_alloc,
        "lipid_per_kg": lipid_alloc,
        "aqueous_ml_day": aqueous_ml,
        "lipid_ml_day": lipid_ml,
        "total_spn_ml": total_spn_ml,
        "status": status
    }

class DummySelf:
    def __init__(self):
        self.en_volume = 60    # mL/kg/day
        self.tfi = 120         # mL/kg/day
        self.weight = 0.9      # kg

self = DummySelf()

result = calculate_patient_spn(self, row)

print(result)
