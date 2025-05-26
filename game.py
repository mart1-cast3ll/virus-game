import random
from cards import Card, CardType, Color, TreatmentType
from players import Player, PlacedOrgan
import ai

class Game:
    def __init__(self, num_players: int = 4):
        if num_players < 2 or num_players > 8:
            raise ValueError("Number of players must be between 2 and 8.")

        self.players = []
        self.players.append(Player("You", is_human=True))
        for i in range(2, num_players+1):
            self.players.append(Player(f"AI {i}"))

        self.deck = []
        self.discard_pile = []
        self._create_deck()
        random.shuffle(self.deck)

        for _ in range(3):
            for player in self.players:
                card = self._draw_from_deck()
                if card:
                    player.hand.append(card)

        self.current_player_index = 0

    def _create_deck(self):
        """Create the deck of 68 playing cards (base game)."""
        for color in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]:
            for _ in range(5):
                self.deck.append(Card(CardType.ORGAN, color))
        self.deck.append(Card(CardType.ORGAN, Color.MULTI))

        for color in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]:
            for _ in range(4):
                self.deck.append(Card(CardType.VIRUS, color))
        self.deck.append(Card(CardType.VIRUS, Color.MULTI))

        for color in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.MULTI]:
            for _ in range(4):
                self.deck.append(Card(CardType.MEDICINE, color))

        for _ in range(2):
            self.deck.append(Card(CardType.TREATMENT, treatment=TreatmentType.TRANSPLANT))
        for _ in range(3):
            self.deck.append(Card(CardType.TREATMENT, treatment=TreatmentType.ORGAN_THIEF))
        for _ in range(3):
            self.deck.append(Card(CardType.TREATMENT, treatment=TreatmentType.CONTAGION))
        self.deck.append(Card(CardType.TREATMENT, treatment=TreatmentType.LATEX_GLOVE))
        self.deck.append(Card(CardType.TREATMENT, treatment=TreatmentType.MEDICAL_ERROR))

    def _draw_from_deck(self) -> Card:
        """Draw one card from the deck. Recycle the discard pile into a new deck if needed."""
        if not self.deck:
            if not self.discard_pile:
                return None

            self.deck = list(reversed(self.discard_pile))
            self.discard_pile.clear()
        return self.deck.pop()

    def check_victory(self):
        """Check if any player has 4 or more healthy organs (win condition)."""
        for player in self.players:
            if player.count_healthy_organs() >= 4:
                return player
        return None

    def play_card(self, player: Player, card: Card, **kwargs):
        """
        Apply the effect of a card played by the given player.
        kwargs may include target_player, target_color, etc., depending on card.
        Returns (success: bool, message: str).
        """
        if card not in player.hand:
            return (False, "Card not in hand.")
        player.hand.remove(card)

        if card.card_type == CardType.ORGAN:
            if card.color in player.body:
                player.hand.append(card)  
                return (False, "You already have an organ of that color.")
            player.add_organ_to_body(card)  
            winner = self.check_victory()
            if winner:
                return (True, f"{winner.name} wins by completing the body!")
            return (True, f"Organ {card.color.value} placed on {player.name}'s body.")

        elif card.card_type == CardType.VIRUS:
            target_player: Player = kwargs.get('target_player')
            target_color: Color = kwargs.get('target_color')
            if target_player is None or target_color is None:
                player.hand.append(card)
                return (False, "No target specified for virus.")
            placed = target_player.body.get(target_color)
            if placed is None:
                player.hand.append(card)
                return (False, "Target organ not found.")

            if placed.is_immunized():
                player.hand.append(card)
                return (False, "Target organ is immunized and cannot be infected.")

            if card.color != Color.MULTI and placed.card.color != Color.MULTI and card.color != placed.card.color:
                player.hand.append(card)
                return (False, "Virus color does not match target organ color.")

            if placed.is_infected() and placed.card.color == Color.MULTI:

                existing_virus = placed.virus_cards[0]
                if existing_virus.color == card.color:

                    player.hand.append(card)
                    return (False, "Need a virus of a different color to destroy a multicolor organ.")

            if not placed.is_infected():

                if placed.is_vaccinated():
                    med_card = placed.medicine_cards.pop()
                    self.discard_pile.append(med_card)
                    self.discard_pile.append(card)
                    result_msg = f"{player.name} played a virus on {target_player.name}'s vaccinated {placed.card.color.value} organ, destroying the vaccine."
                else:
                    placed.virus_cards.append(card)
                    result_msg = f"{player.name} infected {target_player.name}'s {placed.card.color.value} organ with a virus."
            else:
                existing_virus = placed.virus_cards.pop()  
                removed = target_player.remove_organ_from_body(target_color)  

                self.discard_pile.append(removed.card)
                for med in removed.medicine_cards:
                    self.discard_pile.append(med)
                self.discard_pile.append(existing_virus)
                self.discard_pile.append(card)
                result_msg = f"{player.name} destroyed {target_player.name}'s {removed.card.color.value} organ with a second virus!"

            winner = self.check_victory()
            if winner:
                return (True, f"{winner.name} wins by having 4 healthy organs!")
            return (True, result_msg)

        elif card.card_type == CardType.MEDICINE:
            target_color: Color = kwargs.get('target_color')
            target_player: Player = kwargs.get('target_player', player)  
            if target_color is None:
                player.hand.append(card)
                return (False, "No target organ specified for medicine.")
            placed = target_player.body.get(target_color)
            if placed is None:
                player.hand.append(card)
                return (False, "Target organ not found.")
            if target_player is not player:
                player.hand.append(card)
                return (False, "Can only use medicine on your own organs.")
            if placed.is_immunized():
                player.hand.append(card)
                return (False, "Target organ is already immunized.")
            if card.color != Color.MULTI and placed.card.color != Color.MULTI and card.color != placed.card.color:
                player.hand.append(card)
                return (False, "Medicine color does not match target organ color.")

            if placed.is_infected():
                virus_card = placed.virus_cards[0]
                if card.color != Color.MULTI and virus_card.color != Color.MULTI and card.color != virus_card.color:
                    player.hand.append(card)
                    return (False, "Medicine color does not match the virus color.")

                placed.virus_cards.pop()
                self.discard_pile.append(virus_card)
                self.discard_pile.append(card)
                result_msg = f"{player.name} cured their {placed.card.color.value} organ of a virus."
            else:
                if placed.is_vaccinated():
                    if placed.card.color == Color.MULTI:
                        if placed.medicine_cards and placed.medicine_cards[0].color == card.color:
                            player.hand.append(card)
                            return (False, "Need a different color medicine to immunize a multicolor organ.")
                    placed.medicine_cards.append(card)
                    result_msg = f"{player.name} immunized their {placed.card.color.value} organ! It is now protected."
                else:
                    placed.medicine_cards.append(card)
                    result_msg = f"{player.name} vaccinated their {placed.card.color.value} organ."
            winner = self.check_victory()
            if winner:
                return (True, f"{winner.name} wins by having 4 healthy organs!")
            return (True, result_msg)

        elif card.card_type == CardType.TREATMENT:
            tret = card.treatment
            self.discard_pile.append(card)
            if tret == TreatmentType.TRANSPLANT:
                p1: Player = kwargs.get('player1')
                c1: Color = kwargs.get('color1')
                p2: Player = kwargs.get('player2')
                c2: Color = kwargs.get('color2')
                if not p1 or not p2 or c1 is None or c2 is None:
                    return (False, "Targets not specified for transplant.")
                placed1 = p1.body.get(c1)
                placed2 = p2.body.get(c2)
                if placed1 is None or placed2 is None:
                    return (False, "Chosen organs not found.")
                if placed1.is_immunized() or placed2.is_immunized():
                    return (False, "Cannot transplant immunized organs.")

                if c2 in p1.body and c2 != c1:
                    return (False, f"{p1.name} would end up with two {c2.value} organs.")
                if c1 in p2.body and c1 != c2:
                    return (False, f"{p2.name} would end up with two {c1.value} organs.")

                organ1 = p1.remove_organ_from_body(c1)
                organ2 = p2.remove_organ_from_body(c2)
                p1.body[c2] = organ2
                p2.body[c1] = organ1
                result_msg = f"{player.name} swapped {p1.name}'s {organ1.card.color.value} organ with {p2.name}'s {organ2.card.color.value} organ."
            elif tret == TreatmentType.ORGAN_THIEF:
                target_player: Player = kwargs.get('target_player')
                target_color: Color = kwargs.get('target_color')
                if not target_player or target_color is None:
                    return (False, "Target not specified for organ thief.")
                placed = target_player.body.get(target_color)
                if placed is None:
                    return (False, "Target organ not found.")
                if placed.is_immunized():
                    return (False, "Cannot steal an immunized organ.")
                if target_color in player.body:
                    return (False, "You already have that color organ.")

                stolen = target_player.remove_organ_from_body(target_color)
                player.body[target_color] = stolen
                result_msg = f"{player.name} stole {target_player.name}'s {stolen.card.color.value} organ!"
            elif tret == TreatmentType.CONTAGION:

                for organ_color, placed in list(player.body.items()):
                    if placed.is_infected():
                        virus_card = placed.virus_cards[0]  
                        target_found = False
                        for other in self.players:
                            if other is player:
                                continue

                            for tgt_color, tgt_placed in other.body.items():
                                if tgt_placed.is_immunized() or tgt_placed.is_infected() or tgt_placed.is_vaccinated():
                                    continue  
                                if virus_card.color == Color.MULTI or tgt_placed.card.color == Color.MULTI or tgt_placed.card.color == virus_card.color:
                                    tgt_placed.virus_cards.append(virus_card)  
                                    target_found = True

                                    result = f"{player.name} spread a virus to {other.name}'s {tgt_placed.card.color.value} organ."
                                    break
                            if target_found:
                                break
                        if target_found:
                            placed.virus_cards.pop(0)
                result_msg = f"{player.name} spread viruses to other players' organs."
            elif tret == TreatmentType.LATEX_GLOVE:
                for other in self.players:
                    if other is player:
                        continue

                    for card_to_discard in other.hand:
                        self.discard_pile.append(card_to_discard)
                    other.hand.clear()

                    other.skip_turn = True
                result_msg = f"{player.name} played Latex Glove! All other players must discard their hand and skip their next turn."
            elif tret == TreatmentType.MEDICAL_ERROR:

                target_player: Player = kwargs.get('target_player')
                if not target_player or target_player is player:
                    return (False, "Target player not specified or invalid for medical error.")

                player.body, target_player.body = target_player.body, player.body
                result_msg = f"{player.name} swapped all organs with {target_player.name}!"
            else:
                return (False, "Unknown treatment.")

            winner = self.check_victory()
            if winner:
                return (True, f"{winner.name} wins by completing the body!")
            return (True, result_msg)

        else:
            return (False, "Cannot play this card.")
