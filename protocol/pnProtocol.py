import pandas as pd
from protocol.enumClass import AqueousSPN
from protocol.base import ProtocolBase

class PNProtocol(ProtocolBase):
    def __init__(self):
        super().__init__()
        self.table = self.create_pn_table()

    # Function to add tuple ranges to show min and max total vals
    def add_ranges(self, t1, t2):
        return (t1[0]+t2[0], t1[1]+t2[1])

# Create a multi-level header for SPN products
    def create_pn_table(self):
        spn_header = pd.MultiIndex.from_product(
        [['Aqueous SPN Product', 'Lipid SPN Product'],
        ['Name', 'Target Volume']],
        names=['Type', 'Value']
    )

# === Create dataframe ===

        # Create DataFrame for PN Phase and fill clinical protocol
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
            self.add_ranges(aq, lip) for aq, lip in zip(
                pnTable[('Aqueous SPN Product', 'Target Volume')],
                pnTable[('Lipid SPN Product', 'Target Volume')]
            )
        ]

        # Reorder columns: Patient Info first, SPN products after
        patient_cols = [col for col in pnTable.columns if col[0] == 'Patient Info']
        spn_cols = [col for col in pnTable.columns if col[0] != 'Patient Info']

        return pnTable[patient_cols + spn_cols]

    def get_row(self):
        dol_filter = '4+' if self.dol >= 4 else self.dol
        row = self.table.loc[
            (self.table[('Aqueous SPN Product', 'Name')] == self.selected_cSPN.value) &
            (self.table[('Aqueous SPN Product', 'Name')] == self.selected_cSPN.value) &
            (self.table[('Patient Info', 'Day of Life')] == dol_filter)
        ]
        
        if row.empty:
            raise ValueError(f'No matching PN row for {self.selected_cSPN.value} and DOL {dol_filter}')
        return row.iloc[0]

    def calculate_protocol_spn(self, row):
        aq = row[('Aqueous SPN Product', 'Target Volume')]
        lip = row[('Lipid SPN Product', 'Target Volume')]
        total = (aq[0] + lip[0], aq[1] + lip[1])
        return aq, lip, total
    
    def calculate_patient_spn(self, row):
        aq = row[('Aqueous SPN Product', 'Target Volume')]
        lip = row[('Lipid SPN Product', 'Target Volume')]
        
        aq_ml = (aq[0] * self.weight, aq[1] * self.weight)
        lip_ml = (lip[0] * self.weight, lip[1] * self.weight)
        total_ml = (aq_ml[0] + lip_ml[0], aq_ml[1] + lip_ml[1])
        
        return aq_ml, lip_ml, total_ml


    # Display final results
    def display_results(self):
        
        print('\n')
        print('='*135)
        print(self.table)
        print('='*135)
        print('\n')
        
        pnRow = self.get_row()
        
        aq_protocol, lipid_protocol, total_protocol = self.calculate_protocol_spn(pnRow)
        aq_target, lipid_target, total_spn = self.calculate_patient_spn(pnRow)
        
        print(f"User Inputs -> EN Volume: {self.en_volume}, DOL: {self.dol}, Weight: {self.weight}, SPN Type: {self.selected_cSPN.value}\n")
        print(f"Aqueous SPN Target (mL/kg/day): {aq_protocol}")
        print(f"Lipid SPN Target (mL/kg/day):   {lipid_protocol}")
        print(f"Total SPN Volume (mL/kg/day):   {total_protocol}")
        print('=' * 80)
        print('\n')

        print("Patient-Specific Targets (weight factored):")
        print('=' * 80)
        print(f"User Inputs -> EN Volume: {self.en_volume}, DOL: {self.dol}, Weight: {self.weight}, SPN Type: {self.selected_cSPN.value}\n")
        print(f"Aqueous SPN Target (mL/day): {aq_target}")
        print(f"Lipid SPN Target (mL/day):   {lipid_target}")
        print(f"Total SPN Volume (mL/day):   {total_spn}")
        print('=' * 80)
        print('\n')

if __name__ == '__main__':
    pn_protocol = PnProtocol()
    pn_protocol.run()
    