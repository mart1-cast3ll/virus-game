from cards import Card, Color

class PlacedOrgan:
    def __init__(self, organ_card: Card):
        self.card = organ_card
        self.virus_cards = []       
        self.medicine_cards = []    
    def is_healthy(self) -> bool:
        return len(self.virus_cards) == 0
    def is_immunized(self) -> bool:
        return len(self.medicine_cards) >= 2
    def is_vaccinated(self) -> bool:
        return len(self.medicine_cards) == 1 and not self.is_immunized()
    def is_infected(self) -> bool:
        return len(self.virus_cards) >= 1
    def __repr__(self):
        status = []
        if self.is_immunized():
            status.append("immunized")
        elif self.is_vaccinated():
            status.append("vaccinated")
        if self.is_infected():
            status.append("infected")
        status_str = (" (" + ", ".join(status) + ")") if status else ""
        return f"{self.card.color.value} Organ{status_str}"

class Player:
    def __init__(self, name: str, is_human: bool = False):
        self.name = name
        self.is_human = is_human
        self.hand = []        
        self.body = {}        
        self.skip_turn = False 
    def count_healthy_organs(self) -> int:
        
        return sum(1 for organ in self.body.values() if organ.is_healthy())
    def add_organ_to_body(self, organ_card: Card) -> bool:
        """Place an organ card onto this player's body. Returns True if successful, False if not allowed (duplicate color)."""
        if organ_card.color in self.body:
            
            return False
        self.body[organ_card.color] = PlacedOrgan(organ_card)
        return True
    def remove_organ_from_body(self, color: Color) -> PlacedOrgan:
        """Remove the organ of the given color from the body and return the PlacedOrgan (or None if not present)."""
        return self.body.pop(color, None)
    def __repr__(self):
        return f"Player({self.name}, Hand={len(self.hand)} cards, Body organs={len(self.body)})"
