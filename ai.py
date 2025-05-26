import random
from cards import CardType, Color, TreatmentType

def ai_take_turn(game, player):
    """Decide and perform an action for the AI player."""
    p = player 

    def play(card, **kwargs):
        success, message = game.play_card(p, card, **kwargs)
        return success, message

    my_healthy = p.count_healthy_organs()
    if my_healthy >= 3:
        have_colors = set(p.body.keys())
        needed_colors = [c for c in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.MULTI] if c not in have_colors]
        if my_healthy == 3:  
            for card in p.hand:
                if card.card_type == CardType.ORGAN and card.color in needed_colors:
                    success, msg = play(card)
                    if success:
                        return msg
        for organ_color, placed in p.body.items():
            if placed.is_infected():
                for card in p.hand:
                    if card.card_type == CardType.MEDICINE:
                        virus_card = placed.virus_cards[0]
                        if card.color == Color.MULTI or virus_card.color == Color.MULTI or card.color == virus_card.color:
                            if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                                success, msg = play(card, target_color=organ_color)
                                if success:
                                    return msg

    opponents = [op for op in game.players if op is not p]
    opponents.sort(key=lambda op: op.count_healthy_organs(), reverse=True)
    top_opponent = opponents[0] if opponents else None
    opp_healthy = top_opponent.count_healthy_organs() if top_opponent else 0

    if top_opponent and opp_healthy >= 3:
        for card in p.hand:
            if card.card_type == CardType.VIRUS:
                target_player = top_opponent
                target_color = None
                for col, placed in top_opponent.body.items():
                    if placed.is_infected() and not placed.is_immunized():
                        if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                            target_color = col
                            break
                if target_color:
                    success, msg = play(card, target_player=target_player, target_color=target_color)
                    if success:
                        return msg
                for col, placed in top_opponent.body.items():
                    if placed.is_healthy() and not placed.is_immunized() and not placed.is_vaccinated():
                        if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                            target_color = col
                            break
                if target_color:
                    success, msg = play(card, target_player=target_player, target_color=target_color)
                    if success:
                        return msg
                for col, placed in top_opponent.body.items():
                    if placed.is_vaccinated() and not placed.is_immunized():
                        if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                            target_color = col
                            break
                if target_color:
                    success, msg = play(card, target_player=target_player, target_color=target_color)
                    if success:
                        return msg
        for card in p.hand:
            if card.card_type == CardType.TREATMENT:
                if card.treatment == TreatmentType.ORGAN_THIEF:
                    for col, placed in top_opponent.body.items():
                        if not placed.is_immunized() and placed.is_healthy() and col not in p.body:
                            success, msg = play(card, target_player=top_opponent, target_color=col)
                            if success:
                                return msg
                elif card.treatment == TreatmentType.TRANSPLANT:
                    for my_col, my_placed in p.body.items():
                        if my_placed.is_infected() and not my_placed.is_immunized():
                            for op_col, op_placed in top_opponent.body.items():
                                if op_placed.is_healthy() and not op_placed.is_immunized():
                                    if op_col not in p.body and my_col not in top_opponent.body:
                                        success, msg = play(card, player1=p, color1=my_col, player2=top_opponent, color2=op_col)
                                        if success:
                                            return msg
                elif card.treatment == TreatmentType.LATEX_GLOVE:
                    next_index = (game.current_player_index + 1) % len(game.players)
                    if opp_healthy >= 3 and game.players[next_index] is top_opponent:
                        success, msg = play(card)
                        if success:
                            return msg
                elif card.treatment == TreatmentType.MEDICAL_ERROR:
                    if opp_healthy > my_healthy:
                        success, msg = play(card, target_player=top_opponent)
                        if success:
                            return msg

    for card in p.hand:
        if card.card_type == CardType.MEDICINE:
            for organ_color, placed in p.body.items():
                if placed.is_infected():
                    virus_card = placed.virus_cards[0]
                    if card.color == Color.MULTI or virus_card.color == Color.MULTI or card.color == virus_card.color:
                        if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                            success, msg = play(card, target_color=organ_color)
                            if success:
                                return msg

    for card in p.hand:
        if card.card_type == CardType.ORGAN and card.color not in p.body:
            success, msg = play(card)
            if success:
                return msg

    for card in p.hand:
        if card.card_type == CardType.MEDICINE:
            for organ_color, placed in p.body.items():
                if placed.is_vaccinated() and not placed.is_immunized():
                    existing_med = placed.medicine_cards[0] if placed.medicine_cards else None
                    if placed.card.color == Color.MULTI:
                        if existing_med and existing_med.color == card.color:
                            continue
                    if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                        success, msg = play(card, target_color=organ_color)
                        if success:
                            return msg
            for organ_color, placed in p.body.items():
                if not placed.is_vaccinated() and not placed.is_immunized():
                    if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                        success, msg = play(card, target_color=organ_color)
                        if success:
                            return msg

    for card in p.hand:
        if card.card_type == CardType.VIRUS:
            for op in opponents:
                for col, placed in op.body.items():
                    if not placed.is_immunized():
                        if placed.is_healthy() and not placed.is_vaccinated():
                            if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                                success, msg = play(card, target_player=op, target_color=col)
                                if success:
                                    return msg
                        if placed.is_infected():
                            if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                                success, msg = play(card, target_player=op, target_color=col)
                                if success:
                                    return msg
                        if placed.is_vaccinated():
                            if card.color == Color.MULTI or placed.card.color == Color.MULTI or card.color == placed.card.color:
                                success, msg = play(card, target_player=op, target_color=col)
                                if success:
                                    return msg

    for card in p.hand:
        if card.card_type == CardType.TREATMENT:
            if card.treatment == TreatmentType.ORGAN_THIEF:
                for op in opponents:
                    for col, placed in op.body.items():
                        if col not in p.body and not placed.is_immunized():
                            success, msg = play(card, target_player=op, target_color=col)
                            if success:
                                return msg
            elif card.treatment == TreatmentType.CONTAGION:
                if any(placed.is_infected() for placed in p.body.values()):
                    success, msg = play(card)
                    if success:
                        return msg
            elif card.treatment == TreatmentType.LATEX_GLOVE:
                if random.random() < 0.1: 
                    success, msg = play(card)
                    if success:
                        return msg
            elif card.treatment == TreatmentType.MEDICAL_ERROR:
                for op in opponents:
                    if op.count_healthy_organs() > my_healthy:
                        success, msg = play(card, target_player=op)
                        if success:
                            return msg
            elif card.treatment == TreatmentType.TRANSPLANT:
                if top_opponent and len(p.body) < len(top_opponent.body):
                    for op_col, op_placed in top_opponent.body.items():
                        if not op_placed.is_immunized():
                            for my_col, my_placed in p.body.items():
                                if not my_placed.is_immunized():
                                    if op_col not in p.body and my_col not in top_opponent.body:
                                        success, msg = play(card, player1=p, color1=my_col, player2=top_opponent, color2=op_col)
                                        if success:
                                            return msg

    discard_candidates = []
    for card in p.hand:
        if card.card_type == CardType.ORGAN and card.color in p.body:
            discard_candidates.append(card)
        elif card.card_type == CardType.MEDICINE:
            organ_exists = any((card.color == Color.MULTI or organ.card.color == card.color or organ.card.color == Color.MULTI) for organ in p.body.values())
            if not organ_exists:
                discard_candidates.append(card)
        elif card.card_type == CardType.VIRUS:
            color = card.color
            exists = False
            for op in opponents:
                for col in op.body.keys():
                    if color == Color.MULTI or col == color or col == Color.MULTI:
                        exists = True
                        break
                if exists:
                    break
            if not exists:
                discard_candidates.append(card)
    if discard_candidates:
        for dc in discard_candidates:
            if dc in p.hand:
                p.hand.remove(dc)
                game.discard_pile.append(dc)
        return f"{p.name} discarded {len(discard_candidates)} card(s)."
    else:
        if p.hand:
            card = random.choice(p.hand)
            p.hand.remove(card)
            game.discard_pile.append(card)
            return f"{p.name} discarded a card."
    return f"{p.name} passes (no action)."
