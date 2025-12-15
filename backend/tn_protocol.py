from backend.enumClass import AqueousSPN
from backend.base import ProtocolBase
import pandas as pd

class TNProtocol(ProtocolBase):
    def __init__(self):
        super().__init__()
        # TN Phase data matching the clinical protocol from PDF
        # EN volume ranges map to specific recommendations
        self.tn_blocks = {
            40: {
                "dol": [2, "3+"],
                "cspn": ['cSPN1', 'cSPN2'],
                "aq_target": [60, 95],
                "aq_min": [45, 55],
                "aq_max": [70, 100],
                "lipid_name": ['SMOFlipid with vits', 'SMOFlipid with vits'],
                "lipid_target": [12, 18],
                "total_target": [112, 153],
            },
            50: {
                "dol": [2, "3+"],
                "cspn": ['cSPN1', 'cSPN2'],
                "aq_target": [55, 85],
                "aq_min": [40, 50],
                "aq_max": [70, 95],
                "lipid_name": ['SMOFlipid with vits', 'SMOFlipid with vits'],
                "lipid_target": [12, 18],
                "total_target": [117, 153],
            },
            60: {
                "dol": [2, "3+"],
                "cspn": ['cSPN1', 'cSPN2'],
                "aq_target": [50, 80],
                "aq_min": [40, 45],
                "aq_max": [65, 90],
                "lipid_name": ['SMOFlipid with vits', 'SMOFlipid with vits'],
                "lipid_target": [12, 12],
                "total_target": [122, 152],
            },
            70: {
                "dol": ["3+"],
                "cspn": ['cSPN2'],
                "aq_target": [70],
                "aq_min": [40],
                "aq_max": [85],
                "lipid_name": ['SMOFlipid with vits'],
                "lipid_target": [12],
                "total_target": [152],
            },
            80: {
                "dol": ["Fortify EBM"],
                "cspn": ['cSPN2'],
                "aq_target": [60],
                "aq_min": [40],
                "aq_max": [75],
                "lipid_name": ['SMOFlipid with vits'],
                "lipid_target": [12],
                "total_target": [152],
            },
            90: {
                "dol": ["Fortify EBM"],
                "cspn": ['cSPN2'],
                "aq_target": [50],
                "aq_min": [30],
                "aq_max": [65],
                "lipid_name": ['SMOFlipid with vits'],
                "lipid_target": [12],
                "total_target": [152],
            },
            100: {
                "dol": ["Fortify EBM"],
                "cspn": ['cSPN2'],
                "aq_target": [40],
                "aq_min": [20],
                "aq_max": [55],
                "lipid_name": ['SMOFlipid with vits'],
                "lipid_target": [12],
                "total_target": [152],
            },
            110: {
                "dol": ["Fortify EBM"],
                "cspn": ['cSPN2'],
                "aq_target": [30],
                "aq_min": [10],
                "aq_max": [45],
                "lipid_name": ['SMOFlipid with vits'],
                "lipid_target": [12],
                "total_target": [152],
            },
            120: {
                "dol": ['Stop SPN unless clinically indicated'],
                "cspn": [''],
                "aq_target": [0],
                "aq_min": [0],
                "aq_max": [0],
                "lipid_name": [''],
                "lipid_target": [0],
                "total_target": [0],
            }
        }
        self.table = self.create_tn_table()

    def get_en_bucket(self, en_volume):
        """Determine which EN volume bucket the value falls into"""
        if 40 <= en_volume < 50:
            return 40
        elif 50 <= en_volume < 60:
            return 50
        elif 60 <= en_volume < 70:
            return 60
        elif 70 <= en_volume < 80:
            return 70
        elif 80 <= en_volume < 90:
            return 80
        elif 90 <= en_volume < 100:
            return 90
        elif 100 <= en_volume < 110:
            return 100
        elif 110 <= en_volume < 120:
            return 110
        elif en_volume >= 120:
            return 120
        return None

    def get_row(self):
        en_bucket = self.get_en_bucket(self.en_volume)
        dol_filter = self.normalize_dol(self.dol)
        
        row = self.table.loc[
            (self.table[('Aqueous SPN Product', 'Name')] == self.selected_cSPN.value) &
            (self.table[('Patient Info', 'Day of Life')] == dol_filter) &
            (self.table.index.get_level_values('enVal') == en_bucket)
        ]
        
        if row.empty:
            raise ValueError(f"No matching TN row for {self.selected_cSPN.value} and DOL {dol_filter} and EN {en_bucket}")
        return row.iloc[0]

    def normalize_dol(self, dol):
        """Normalize DOL to match protocol table format"""
        if isinstance(dol, int):
            if dol == 2:
                return 2
            elif dol >= 3:
                return "3+"
        return dol

    def build_tn_table(self, block_data, en_value):
        """Build a section of the TN table for a specific EN value range"""
        for key in ['dol', 'cspn', 'aq_target', 'aq_min', 'aq_max', 'lipid_name', 'lipid_target', 'total_target']:
            if not isinstance(block_data[key], list):
                block_data[key] = [block_data[key]]

        df = pd.DataFrame({
            ('Patient Info', 'Day of Life'): block_data['dol'],
            ('Aqueous SPN Product', 'Name'): block_data['cspn'],
            ('Aqueous SPN Product', 'Target Volume'): block_data['aq_target'],
            ('Aqueous SPN Product', 'Min Volume'): block_data['aq_min'],
            ('Aqueous SPN Product', 'Max Volume'): block_data['aq_max'],
            ('Lipid SPN Product', 'Name'): block_data['lipid_name'],
            ('Lipid SPN Product', 'Target Volume'): block_data['lipid_target'],
            ('Patient Info', 'Total Fluid Volume (mL/kg/d)'): block_data['total_target'],
        })

        df['enVal'] = en_value
        return df

    def create_tn_table(self):
        """Create the complete TN protocol table"""
        spn_header = pd.MultiIndex.from_product(
            [['Aqueous SPN Product', 'Lipid SPN Product'],
             ['Name', 'Target Volume', 'Min Volume', 'Max Volume']],
            names=['Type', 'Value']
        )
        tnTable = pd.DataFrame(columns=spn_header)
        tnTable = pd.concat([
            self.build_tn_table(self.tn_blocks[k], k) for k in self.tn_blocks
        ], ignore_index=True)
        tnTable.set_index('enVal', inplace=True)
        return tnTable

    def calculate_protocol_spn(self, row):
        """Calculate protocol-level SPN values (mL/kg/d)"""
        aq_target = row[('Aqueous SPN Product', 'Target Volume')]
        aq_min = row[('Aqueous SPN Product', 'Min Volume')]
        aq_max = row[('Aqueous SPN Product', 'Max Volume')]
        
        lip_target = row[('Lipid SPN Product', 'Target Volume')]
        
        total_target = row[('Patient Info', 'Total Fluid Volume (mL/kg/d)')]
        
        return aq_target, aq_min, aq_max, lip_target, total_target

    def calculate_patient_spn(self, row):
        """Calculate patient-specific SPN values (mL/d) factoring in weight"""
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
        """Display the calculation results"""
        tnRow = self.get_row()

        print('\n')
        print('=' * 135)
        print(self.table)
        print('=' * 135)
        print('\n')

        aq_target, aq_min, aq_max, lip_target, total_target = self.calculate_protocol_spn(tnRow)
        aq_target_ml, aq_min_ml, aq_max_ml, lip_target_ml, total_target_ml = self.calculate_patient_spn(tnRow)

        print("Protocol Targets (NOT weight factored):")
        print('=' * 80)
        print(f"User Inputs -> EN Volume: {self.en_volume}, DOL: {self.dol}, Weight: {self.weight}, SPN Type: {self.selected_cSPN.value}\n")
        print(f"Aqueous SPN Target (mL/kg/day): {aq_target} (min: {aq_min}, max: {aq_max})")
        print(f"Lipid SPN Target (mL/kg/day):   {lip_target}")
        print(f"Total Fluid Volume (mL/kg/day): {total_target}")
        print('=' * 80)
        print('\n')

        print("Patient-Specific Targets (weight factored):")
        print('=' * 80)
        print(f"User Inputs -> EN Volume: {self.en_volume}, DOL: {self.dol}, Weight: {self.weight}, SPN Type: {self.selected_cSPN.value}\n")
        print(f"Aqueous SPN Target (mL/day): {aq_target_ml:.2f} (min: {aq_min_ml:.2f}, max: {aq_max_ml:.2f})")
        print(f"Lipid SPN Target (mL/day):   {lip_target_ml:.2f}")
        print(f"Total SPN Volume (mL/day):   {total_target_ml:.2f}")
        print('=' * 80)
        print('\n')

if __name__ == '__main__':
    tn_protocol = TNProtocol()
    tn_protocol.run()