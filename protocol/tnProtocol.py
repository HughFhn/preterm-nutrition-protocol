from protocol.enumClass import AqueousSPN
from protocol.base import ProtocolBase
import pandas as pd

class TNProtocol(ProtocolBase):
    def __init__(self):
        super().__init__()
        self.tn_blocks = {
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
        self.table = self.create_tn_table()

    def get_row(self, aqueous_type, dol, enVal):
        dol_filter = self.normalize_dol(dol)
        row = self.table.loc[
            (self.table[('Aqueous SPN Product', 'Name')] == aqueous_type) &
            (self.table[('Patient Info', 'Day of Life')] == dol_filter) &
            (self.table.index.get_level_values('enVal') == enVal)
        ]
        if row.empty:
            raise ValueError(f"No matching PN row for {aqueous_type} and DOL {dol_filter} and EN {enVal}")
        return row.iloc[0]

    def normalize_dol(self, dol):
        if isinstance(dol, int):
            if dol <= 2:
                return f"dol{dol}"
            else:
                return "dol3+"
        else:
            return dol

    def add_ranges(self, t1, t2):
        return (t1[0]+t2, t1[1]+t2)

    def build_tn_table(self, block_data, en_value):
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

        total = []
        for aq, lip in zip(block_data['aq'], block_data['lipid_target']):
            total.append((aq[0] + lip + en_value, aq[1] + lip + en_value))

        df[('Patient Info', 'Total Fluid Volume (mL/kg/d)')] = total
        df['enVal'] = en_value

        return df

    def create_tn_table(self):
        spn_header = pd.MultiIndex.from_product(
            [['Aqueous SPN Product', 'Lipid SPN Product'],
             ['Name', 'Target Volume']],
            names=['Type', 'Value']
        )
        tnTable = pd.DataFrame(columns=spn_header)
        tnTable = pd.concat([
            self.build_tn_table(self.tn_blocks[k], int(k)) for k in self.tn_blocks
        ], ignore_index=True)
        tnTable.set_index('enVal', inplace=True)
        return tnTable

    def calculate_protocol_spn(self, row):
        aq = row[('Aqueous SPN Product', 'Target Volume')]
        lip = row[('Lipid SPN Product', 'Target Volume')]
        total = (aq[0] + lip, aq[1] + lip)
        return aq, lip, total

    def calculate_patient_spn(self, row):
        aq = row[('Aqueous SPN Product', 'Target Volume')]
        lip = row[('Lipid SPN Product', 'Target Volume')]

        aq_mL = (aq[0] * self.weight, aq[1] * self.weight)
        lip_mL = (lip * self.weight, lip * self.weight)
        total_mL = (aq_mL[0] + lip_mL[0], aq_mL[1] + lip_mL[1])

        return aq_mL, lip_mL, total_mL

    def display_results(self):
        tnRow = self.get_row(self.selected_cSPN.value, self.dol, self.en_volume)

        print('\n')
        print('=' * 135)
        print(self.table)
        print('=' * 135)
        print('\n')

        aq_protocol, lipid_protocol, total_protocol = self.calculate_protocol_spn(tnRow)
        aq_target, lipid_target, total_spn = self.calculate_patient_spn(tnRow)

        print("Protocol Targets (NOT weight factored):")
        print('=' * 80)
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
    tn_protocol = TNProtocol()
    tn_protocol.run()
