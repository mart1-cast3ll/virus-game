import enum

class Color(enum.Enum):
    RED     =   "Red"
    GREEN   =   "Green"
    BLUE    =   "Blue"
    YELLOW  =   "Yellow"
    MULTI   =   "Multicolor"

class CardType(enum.Enum):
    ORGAN       = "Organ"
    VIRUS       = "Virus"
    MEDICINE    = "Medicine"
    TREATMENT   = "Treatment"

class TreatmentType(enum.Enum):
    TRANSPLANT      = "Transplant"
    ORGAN_THIEF     = "Organ Thief"
    CONTAGION       = "Contagion"
    LATEX_GLOVE     = "Latex Glove"
    MEDICAL_ERROR   = "Medical Error"

class Card:
    def __init__(self, card_type: CardType, color: Color = None, treatment: TreatmentType = None):
        self.card_type = card_type
        self.color = color
        self.treatment = treatment
        
        if self.card_type == CardType.TREATMENT:
            if treatment is None:
                raise ValueError("Treatment card must have a treatment type.")
        else:
            self.treatment = None
            if self.color is None:
                raise ValueError(f"{self.card_type.value} card must have a color.")
        if self.card_type == CardType.TREATMENT:
            self.color = None

    def __repr__(self):
        if self.card_type == CardType.TREATMENT:
            return f"{self.treatment.value} card"
        elif self.card_type == CardType.ORGAN:
            return f"Organ ({self.color.value})"
        elif self.card_type == CardType.VIRUS:
            return f"Virus ({self.color.value})"
        elif self.card_type == CardType.MEDICINE:
            return f"Medicine ({self.color.value})"
        else:
            return "Unknown Card"
