import pandas as pd
from protocol.enumClass import AqueousSPN

class ProtocolBase:
    def __init__(self):
        self.en_volume = 0
        self.dol = 0
        self.weight = 0
        self.selected_cSPN = None
        self.pnPhase = False
        self.tnPhase = False
        self.table = None

    def get_user_inputs(self):
        self.en_volume = int(input("Please enter EN Volume in mL: "))
        self.dol = int(input("Please enter Day Of Life: "))
        self.weight = float(input("Please enter weight in kg: "))

    def determine_phase(self):
        if self.dol < 0:
            print("\nInvalid day of life")
            return

        if self.en_volume > 120:
            print("\nStop SPN unless clinically indicated")
            return
        
        if self.en_volume < 0:
            print("\nCannot be less than zero")
            return

        if self.dol <= 2:
            self.selected_cSPN = AqueousSPN.CSPN1
        else:
            self.selected_cSPN = AqueousSPN.CSPN2

        if self.en_volume >= 40 and self.dol >= 2:
            self.tnPhase = True
        elif self.en_volume < 40:
            self.pnPhase = True

    def get_row(self):
        raise NotImplementedError("This method should be implemented by a subclass.")

    def calculate_protocol_spn(self):
        raise NotImplementedError("This method should be implemented by a subclass.")

    def calculate_patient_spn(self):
        raise NotImplementedError("This method should be implemented by a subclass.")

    def display_results(self):
        raise NotImplementedError("This method should be implemented by a subclass.")

    def run(self):
        self.get_user_inputs()
        self.determine_phase()
        if self.pnPhase or self.tnPhase:
            self.display_results()
