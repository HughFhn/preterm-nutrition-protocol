import pandas as pd
from backend.enumClass import AqueousSPN
from backend.statusClass import SPNStatus
from backend.base import ProtocolBase

class PNProtocol(ProtocolBase):
    def __init__(self):
        super().__init__()
        self.table = self.create_pn_table()

    def create_pn_table(self):
        spn_header = pd.MultiIndex.from_product(
            [['Aqueous SPN Product', 'Lipid SPN Product'],
             ['Name', 'Target Volume', 'Min Volume', 'Max Volume']],
            names=['Type', 'Value']
        )

        # Create DataFrame for PN Phase and fill clinical protocol
        pnTable = pd.DataFrame(columns=spn_header)
        pnTable[('Aqueous SPN Product', 'Name')] = ['cSPN1', 'cSPN1', 'cSPN2', 'cSPN2']
        pnTable[('Lipid SPN Product', 'Name')] = 'SMOFlipid with vits'

        # Fill in target volumes (mL/kg/d) from switch case
        pnTable[('Aqueous SPN Product', 'Target Volume')] = [65, 80, 95, 105]
        pnTable[('Aqueous SPN Product', 'Min Volume')] = [65, 65, 75, 75]
        pnTable[('Aqueous SPN Product', 'Max Volume')] = [65, 90, 120, 120]
        
        # ADD LIPID MIN/MAX COLUMNS
        pnTable[('Lipid SPN Product', 'Target Volume')] = [6, 12, 18, 18]
        pnTable[('Lipid SPN Product', 'Min Volume')] = [6, 12, 18, 18]
        pnTable[('Lipid SPN Product', 'Max Volume')] = [6, 12, 18, 18]

        # Add regular columns for EN feed, Day of Life, and Total SPN Volume
        pnTable[('Patient Info', 'EN Feed Volume (mL)')] = "<40"
        pnTable[('Patient Info', 'Day of Life')] = [1, 2, 3, "4+"]

        # Calculate Total SPN Volume
        pnTable[('Patient Info', 'Total SPN Volume (mL/kg/d)')] = [71, 92, 113, 123]

        # Reorder columns: Patient Info first, SPN products after
        patient_cols = [col for col in pnTable.columns if col[0] == 'Patient Info']
        spn_cols = [col for col in pnTable.columns if col[0] != 'Patient Info']

        return pnTable[patient_cols + spn_cols]

    def get_row(self):
        dol_filter = '4+' if self.dol >= 4 else self.dol
        row = self.table.loc[
            (self.table[('Aqueous SPN Product', 'Name')] == self.selected_cSPN.value) &
            (self.table[('Patient Info', 'Day of Life')] == dol_filter)
        ]
        
        if row.empty:
            raise ValueError(f'No matching PN row for {self.selected_cSPN.value} and DOL {dol_filter}')
        return row.iloc[0]

    def calculate_protocol_spn(self, row):
        aq_target = row[('Aqueous SPN Product', 'Target Volume')]
        aq_min = row[('Aqueous SPN Product', 'Min Volume')]
        aq_max = row[('Aqueous SPN Product', 'Max Volume')]
        
        lip_target = row[('Lipid SPN Product', 'Target Volume')]
        
        total_target = row[('Patient Info', 'Total SPN Volume (mL/kg/d)')]
        
        return aq_target, aq_min, aq_max, lip_target, total_target
    
    def calculate_patient_spn(self, row):
        """
        Calculate patient-specific SPN volumes based on protocol targets.
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
        wt = self.weight             # kg

        # ===== STEP 1: Available resources =====

        print("\n--- INPUTS ---")
        print(f"EN: {en} mL/kg/d")
        print(f"Patient Weight: {wt} kg")

        print("\n--- CONSTRAINTS ---")
        print(f"Aqueous min / target / max: {aq_min} / {aq_target} / {aq_max}")
        print(f"Lipid min / target / max: {lip_min} / {lip_target} / {lip_max}")

        # ===== STEP 2: Allocate lipid first (priority) =====
        lipid_alloc = lip_target
        
        # Check if we met lipid minimum
        lipid_status = SPNStatus.TARGET_MET
        if lipid_alloc < lip_min:
            lipid_status = SPNStatus.BELOW_MINIMUM
        elif lipid_alloc < lip_target:
            lipid_status = SPNStatus.PARTIAL

        # ===== STEP 3: Allocate aqueous =====
        aqueous_alloc = aq_target
        aqueous_status = SPNStatus.TARGET_MET
        if aqueous_alloc < aq_min:
            aqueous_status = SPNStatus.BELOW_MINIMUM
        elif aqueous_alloc < aq_target:
            aqueous_status = SPNStatus.PARTIAL

        # ===== STEP 4: Calculate total SPN and TFI =====
        total_spn_per_kg = aqueous_alloc + lipid_alloc
        total_spn_ml = total_spn_per_kg * wt
        aqueous_ml = aqueous_alloc * wt
        lipid_ml = lipid_alloc * wt
        total_tfi = total_spn_per_kg + en

        print("\n--- FINAL SPN ALLOCATION (mL/kg/day) ---")
        print(f"Aqueous allocated: {aqueous_alloc} mL/kg/d ({aqueous_status})")
        print(f"Lipid allocated: {lipid_alloc} mL/kg/d ({lipid_status})")
        print(f"Total SPN per kg: {total_spn_per_kg} mL/kg/d")
        print(f"Total TFI per kg (EN + SPN): {total_tfi} mL/kg/d")

        print("\n--- PATIENT VOLUMES (mL/day) ---")
        print(f"Aqueous: {aqueous_ml:.2f} mL/day")
        print(f"Lipid: {lipid_ml:.2f} mL/day")
        print(f"Total SPN: {total_spn_ml:.2f} mL/day")

        # Combine statuses into a single overall status
        if lipid_status == SPNStatus.BELOW_MINIMUM or aqueous_status == SPNStatus.BELOW_MINIMUM:
            overall_status = SPNStatus.BELOW_MINIMUM
        elif lipid_status == SPNStatus.PARTIAL or aqueous_status == SPNStatus.PARTIAL:
            overall_status = SPNStatus.PARTIAL
        else:
            overall_status = SPNStatus.TARGET_MET

        return {
            "aqueous_per_kg": aqueous_alloc,
            "lipid_per_kg": lipid_alloc,
            "aqueous_ml_day": aqueous_ml,
            "lipid_ml_day": lipid_ml,
            "total_spn_ml": total_spn_ml,
            "total_tfi_per_kg": total_spn_per_kg + en, 
            "lipid_status": str(lipid_status),
            "aqueous_status": str(aqueous_status),
            "status": str(overall_status)
        }

    def display_results(self):
        """Display calculation results"""
        print('\n')
        print('='*135)
        print(self.table)
        print('='*135)
        print('\n')
        
        pnRow = self.get_row()
        
        aq_target, aq_min, aq_max, lip_target, total_target = self.calculate_protocol_spn(pnRow)
        patient = self.calculate_patient_spn(pnRow)
        
        print("\n" + "="*80)
        print("PROTOCOL TARGETS (mL/kg/day)")
        print("="*80)
        print(f"Inputs: EN={self.en_volume}, TFI={self.tfi}, DOL={self.dol}, Weight={self.weight}kg, cSPN={self.selected_cSPN.value}")
        print(f"\nAqueous Target: {aq_target} (min: {aq_min}, max: {aq_max})")
        print(f"Lipid Target: {lip_target}")
        print(f"Total SPN Target: {total_target}")
        print("="*80)

        print("\n" + "="*80)
        print("PATIENT-SPECIFIC VOLUMES")
        print("="*80)
        print(f"Aqueous: {patient['aqueous_per_kg']:.2f} mL/kg/d  →  {patient['aqueous_ml_day']:.2f} mL/day")
        print(f"Lipid:   {patient['lipid_per_kg']:.2f} mL/kg/d  →  {patient['lipid_ml_day']:.2f} mL/day")
        print(f"Total:   {patient['aqueous_per_kg'] + patient['lipid_per_kg']:.2f} mL/kg/d  →  {patient['total_spn_ml']:.2f} mL/day")
        print(f"\nStatus: {patient['status']}")
        print("="*80)
        print('\n')

if __name__ == '__main__':
    pn_protocol = PNProtocol()
    pn_protocol.run()