en_volume = int(input("Please enter EN Volume in mL: "))
dol = int(input("Please enter Day Of Life: "))
weight = float(input("Please enter weight in kg: "))

match (en_volume, dol):

    case (ev, d) if ev < 40 and d == 1:
        cspn_type = "cSPN1"
        target_a = 65
        min_a = 65
        max_a = 65
        target_l = 6
        target_total = 71

    case (ev, d) if ev < 40 and d == 2:
        cspn_type = "cSPN1"
        target_a = 80
        min_a = 65
        max_a = 90
        target_l = 12
        target_total = 92

    case (ev, d) if ev < 40 and d == 3:
        cspn_type = "cSPN2"
        target_a = 95
        min_a = 75
        max_a = 120
        target_l = 18
        target_total = 113

    case (ev, d) if ev < 40 and d >= 4:
        cspn_type = "cSPN2"
        target_a = 105
        min_a = 75
        max_a = 120
        target_l = 18
        target_total = 123

    case (ev, d) if 40 <= ev < 50 and d == 2:
        cspn_type = "cSPN1"
        target_a = 60
        min_a = 45
        max_a = 70
        target_l = 12
        target_total = 112

    case (ev, d) if 40 <= ev < 50 and d >= 3:
        cspn_type = "cSPN2"
        target_a = 95
        min_a = 55
        max_a = 100
        target_l = 18
        target_total = 153

    case (ev, d) if 50 <= ev < 60 and d == 2:
        cspn_type = "cSPN1"
        target_a = 55
        min_a = 40
        max_a = 70
        target_l = 12
        target_total = 117

    case (ev, d) if 50 <= ev < 60 and d >= 3:
        cspn_type = "cSPN2"
        target_a = 85
        min_a = 50
        max_a = 95
        target_l = 18
        target_total = 153

    case (ev, d) if 60 <= ev < 70 and d == 2:
        cspn_type = "cSPN1"
        target_a = 50
        min_a = 40
        max_a = 65
        target_l = 12
        target_total = 122

    case (ev, d) if 60 <= ev < 70 and d >= 3:
        cspn_type = "cSPN2"
        target_a = 80
        min_a = 45
        max_a = 90
        target_l = 12
        target_total = 152

    case (ev, d) if 70 <= ev < 80:
        cspn_type = "cSPN2"
        target_a = 70
        min_a = 40
        max_a = 85
        target_l = 12
        target_total = 152

    case (ev, d) if 80 <= ev < 90:
        cspn_type = "cSPN2"
        target_a = 60
        min_a = 40
        max_a = 75
        target_l = 12
        target_total = 152

    case (ev, d) if 90 <= ev < 100:
        cspn_type = "cSPN2"
        target_a = 50
        min_a = 30
        max_a = 65
        target_l = 12
        target_total = 152

    case (ev, d) if 100 <= ev < 110:
        cspn_type = "cSPN2"
        target_a = 40
        min_a = 20
        max_a = 55
        target_l = 12
        target_total = 152

    case (ev, d) if 110 <= ev < 120:
        cspn_type = "cSPN2"
        target_a = 30
        min_a = 10
        max_a = 45
        target_l = 12
        target_total = 152

    case (ev, d) if ev >= 120:
        cspn_type = None  # prevents crashing later
        print("Stop SPN unless clinically indicated")

if en_volume < 120:
    print("CPSN Type: ", cspn_type)
    print("Target Aqueous SPN Volume:", target_a, "with a minimum of", min_a, "and a maximum of", max_a)
    print("Target Lipid SPN Volume: ", target_l)
    print("Target Total Fluid Volume: ", target_total)
