import pandas as pd
from backend.enumClass import AqueousSPN

class ProtocolBase:
    def __init__(self):
        self.en_volume = 0
        self.dol = 0
        self.weight = 0
        self.tfi = 120  # Default total fluid intake (mL/kg/d)
        self.selected_cSPN = None
        self.pnPhase = False
        self.tnPhase = False
        self.table = None

    def get_user_inputs(self):
        self.en_volume = int(input("Please enter EN Volume in mL/kg/d: "))
        self.dol = int(input("Please enter Day Of Life: "))
        self.weight = float(input("Please enter weight in kg: "))
        self.tfi = int(input("Please enter Total Fluid Intake (TFI) in mL/kg/d [default 120]: ") or "120")
    
    def determine_phase(self):
        """
        Determine which phase based on EN volume and DOL
        Per PDF protocol:
        - PN Phase: EN < 40 mL/kg/d (any DOL)
        - TN Phase: EN >= 40 mL/kg/d AND DOL >= 2
        - DOL 1 should never be in TN phase
        """
        if self.dol < 1:
            print("\nInvalid day of life (must be >= 1)")
            return
        
        if self.en_volume > 120:
            print("\nStop SPN unless clinically indicated")
            return
        
        if self.en_volume < 0:
            print("\nEN volume cannot be less than zero")
            return

        if self.dol <= 2:
            self.selected_cSPN = AqueousSPN.CSPN1
        else:
            self.selected_cSPN = AqueousSPN.CSPN2
        
        # Determine phase
        if self.en_volume < 40:
            # PN Phase: EN < 40 mL/kg/d
            self.pnPhase = True
        elif self.en_volume >= 40 and self.dol >= 2:
            # TN Phase: EN >= 40 AND DOL >= 2
            self.tnPhase = True
        elif self.en_volume >= 40 and self.dol == 1:
            # Edge case: DOL 1 with high EN - clinically unusual
            print("\nWarning: DOL 1 with EN >= 40 mL/kg/d is clinically unusual.")
            print("Treating as PN Phase per protocol.")
            self.pnPhase = True
        else:
            print("\nInvalid combination of EN volume and DOL")
            return
    
    def get_row(self):
        raise NotImplementedError("This method should be implemented by a subclass.")
    
    def calculate_protocol_spn(self, row):
        raise NotImplementedError("This method should be implemented by a subclass.")
    
    def calculate_patient_spn(self, row):
        raise NotImplementedError("This method should be implemented by a subclass.")
    
    def display_results(self):
        raise NotImplementedError("This method should be implemented by a subclass.")
    
    def run(self):
        self.get_user_inputs()
        self.determine_phase()
        if self.pnPhase or self.tnPhase:
            self.display_results()