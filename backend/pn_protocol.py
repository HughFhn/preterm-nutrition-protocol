import pandas as pd
from backend.enumClass import AqueousSPN
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
        aq_target = row[('Aqueous SPN Product', 'Target Volume')]
        aq_min = row[('Aqueous SPN Product', 'Min Volume')]
        aq_max = row[('Aqueous SPN Product', 'Max Volume')]
        lip_target = row[('Lipid SPN Product', 'Target Volume')]
        
        aq_target_ml = aq_target * self.weight
        aq_min_ml = aq_min * self.weight
        aq_max_ml = aq_max * self.weight
        
        lip_target_ml = lip_target * self.weight
        
        total_target_ml = aq_target_ml + lip_target_ml
        
        return aq_target_ml, aq_min_ml, aq_max_ml, lip_target_ml, total_target_ml

    def display_results(self):
        print('\n')
        print('='*135)
        print(self.table)
        print('='*135)
        print('\n')
        
        pnRow = self.get_row()
        
        aq_target, aq_min, aq_max, lip_target, total_target = self.calculate_protocol_spn(pnRow)
        aq_target_ml, aq_min_ml, aq_max_ml, lip_target_ml, total_target_ml = self.calculate_patient_spn(pnRow)
        
        print("Protocol Targets (NOT weight factored):")
        print('=' * 80)
        print(f"User Inputs -> EN Volume: {self.en_volume}, DOL: {self.dol}, Weight: {self.weight}, SPN Type: {self.selected_cSPN.value}\n")
        print(f"Aqueous SPN Target (mL/kg/day): {aq_target} (min: {aq_min}, max: {aq_max})")
        print(f"Lipid SPN Target (mL/kg/day):   {lip_target}")
        print(f"Total SPN Volume (mL/kg/day):   {total_target}")
        print('=' * 80)
        print('\n')

        print("Patient-Specific Targets (weight factored):")
        print('=' * 80)
        print(f"User Inputs -> EN Volume: {self.en_volume}, DOL: {self.dol}, Weight: {self.weight}, SPN Type: {self.selected_cSPN.value}\n")
        print(f"Aqueous SPN Target (mL/day): {aq_target_ml} (min: {aq_min_ml}, max: {aq_max_ml})")
        print(f"Lipid SPN Target (mL/day):   {lip_target_ml}")
        print(f"Total SPN Volume (mL/day):   {total_target_ml}")
        print('=' * 80)
        print('\n')

if __name__ == '__main__':
    pn_protocol = PNProtocol()
    pn_protocol.run()