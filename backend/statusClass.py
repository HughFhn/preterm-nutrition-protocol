# status class for status type
from enum import Enum

class SPNStatus(Enum):
    TARGET_MET = "Target Met"                     # Both lipid and aqueous meet protocol targets
    PARTIAL = "Between Minimum and Target"       # One or both volumes above minimum but below target
    BELOW_MINIMUM = "Below Minimum Requirement" # Either lipid or aqueous is below minimum
    ABOVE = "Above Requirements"