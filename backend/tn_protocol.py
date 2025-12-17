from backend.enumClass import AqueousSPN
from backend.statusClass import SPNStatus
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
                "lipid_min": [12, 18],
                "lipid_max": [12, 18],
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
                "lipid_min": [12, 18],
                "lipid_max": [12, 18],
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
                "lipid_min": [12, 12],
                "lipid_max": [12, 12],
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
                "lipid_min": [12],
                "lipid_max": [12],
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
                "lipid_min": [12],
                "lipid_max": [12],
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
                "lipid_min": [12],
                "lipid_max": [12],
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
                "lipid_min": [12],
                "lipid_max": [12],
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
                "lipid_min": [12],
                "lipid_max": [12],
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
                "lipid_min": [0],
                "lipid_max": [0],
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
        """
        Normalize DOL to match protocol table format
        Per PDF: EN 40-69 has DOL 2 and 3+ options
                 EN 70+ only has "3+" or "Fortify EBM" entries
        """
        if isinstance(dol, int):
            # For EN ranges 40-69, distinguish between DOL 2 and 3+
            if self.en_volume < 70:
                if dol == 2:
                    return 2
                elif dol >= 3:
                    return "3+"
            # For EN ranges 70+, all DOLs map to "Fortify EBM" or "3+"
            else:
                # Check what DOL value exists in the table for this EN range
                en_bucket = self.get_en_bucket(self.en_volume)
                if en_bucket == 70:
                    return "3+"  # EN 70-79 uses "3+"
                else:
                    return "Fortify EBM"  # EN 80+ uses "Fortify EBM"
        return dol

    def build_tn_table(self, block_data, en_value):
        """Build a section of the TN table for a specific EN value range"""
        for key in ['dol', 'cspn', 'aq_target', 'aq_min', 'aq_max', 'lipid_name', 'lipid_target', 'lipid_min', 'lipid_max', 'total_target']:
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
            ('Lipid SPN Product', 'Min Volume'): block_data['lipid_min'],
            ('Lipid SPN Product', 'Max Volume'): block_data['lipid_max'],
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
        """
        Calculate patient-specific Fluid volumes
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

        # ===== Step 1: Allocate lipid first =====
        lipid_alloc = lip_target
        if lipid_alloc < lip_min:
            lipid_status = "BELOW_MINIMUM"
        elif lipid_alloc < lip_target:
            lipid_status = "PARTIAL"
        else:
            lipid_status = "TARGET_MET"

        # ===== Step 2: Allocate aqueous =====
        aqueous_alloc = aq_target
        if aqueous_alloc < aq_min:
            aqueous_status = "BELOW_MINIMUM"
        elif aqueous_alloc < aq_target:
            aqueous_status = "PARTIAL"
        else:
            aqueous_status = "TARGET_MET"

        # ===== Step 3: Calculate total SPN and TFI =====
        total_spn_per_kg = aqueous_alloc + lipid_alloc
        total_tfi_per_kg = total_spn_per_kg + en
        aqueous_ml = aqueous_alloc * wt
        lipid_ml = lipid_alloc * wt
        total_spn_ml = total_spn_per_kg * wt
        total_tfi_ml = total_tfi_per_kg * wt

        # ===== Step 4: Overall status =====
        if lipid_status == "BELOW_MINIMUM" or aqueous_status == "BELOW_MINIMUM":
            overall_status = "BELOW_MINIMUM"
        elif lipid_status == "PARTIAL" or aqueous_status == "PARTIAL":
            overall_status = "PARTIAL"
        else:
            overall_status = "TARGET_MET"

        # ===== Step 5: Return results =====
        return {
            "aqueous_per_kg": aqueous_alloc,
            "lipid_per_kg": lipid_alloc,
            "aqueous_ml_day": aqueous_ml,
            "lipid_ml_day": lipid_ml,
            "total_spn_ml": total_spn_ml,
            "total_tfi_per_kg": total_tfi_per_kg,
            "total_tfi_ml": total_tfi_ml,
            "lipid_status": lipid_status,
            "aqueous_status": aqueous_status,
            "status": overall_status
        }

    def display_results(self):
        """Display the calculation results"""
        tnRow = self.get_row()

        print('\n')
        print('=' * 135)
        print(self.table)
        print('=' * 135)
        print('\n')

        aq_target, aq_min, aq_max, lip_target, total_target = self.calculate_protocol_spn(tnRow)
        patient = self.calculate_patient_spn(tnRow)

        print("\n" + "="*80)
        print("PROTOCOL TARGETS (mL/kg/day)")
        print("="*80)
        print(f"Inputs: EN={self.en_volume}, TFI={self.tfi}, DOL={self.dol}, Weight={self.weight}kg, cSPN={self.selected_cSPN.value}")
        print(f"\nAqueous Target: {aq_target} (min: {aq_min}, max: {aq_max})")
        print(f"Lipid Target: {lip_target}")
        print(f"Total Fluid Target: {total_target}")
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
    tn_protocol = TNProtocol()
    tn_protocol.run()