# main.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import game as virus_game
from cards import CardType, Color, TreatmentType

class VirusGameGUI:
    def __init__(self, root, num_players=4):
        self.root = root
        self.root.title("Virus! Card Game")
        self.game = virus_game.Game(num_players=num_players)
        self.current_turn_label = tk.Label(root, text="")
        self.current_turn_label.pack(pady=5)
        self.players_frame = tk.Frame(root)
        self.players_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.player_frames = []
        for player in self.game.players:
            frame = tk.Frame(self.players_frame, bd=2, relief=tk.GROOVE, padx=5, pady=5)
            frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
            name_label = tk.Label(frame, text=player.name)
            name_label.pack(anchor=tk.W)
            body_frame = tk.Frame(frame)
            body_frame.pack(anchor=tk.W)
            hand_frame = tk.Frame(frame)
            hand_frame.pack(anchor=tk.W, pady=2)
            if player.is_human:
                tk.Label(hand_frame, text="Your hand:").pack(side=tk.LEFT)
            else:
                tk.Label(hand_frame, text=f"Hand: {len(player.hand)} cards").pack(side=tk.LEFT)
            self.player_frames.append({
                "player": player,
                "frame": frame,
                "name_label": name_label,
                "body_frame": body_frame,
                "hand_frame": hand_frame
            })
        self.log_text = tk.Text(root, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        self.selected_card = None
        self.update_ui()
        self.start_turn()

    def update_ui(self):
        """Refresh the GUI to reflect the current game state (players' organs, hand cards, etc.)"""
        current_player = self.game.players[self.game.current_player_index]
        self.current_turn_label.config(text=f"Turn: {current_player.name}")
        for pf in self.player_frames:
            player = pf["player"]
            if player is current_player:
                pf["name_label"].config(font=("Arial", 10, "bold"))
            else:
                pf["name_label"].config(font=("Arial", 10, "normal"))
            for widget in pf["body_frame"].winfo_children():
                widget.destroy()
            for color, placed in player.body.items():
                organ_text = f"{color.value} organ"
                status_icons = ""
                if placed.is_immunized():
                    status_icons += "💉💉"   
                elif placed.is_vaccinated():
                    status_icons += "💉"     
                if placed.is_infected():
                    status_icons += "🦠"     
                label_text = organ_text + ((" " + status_icons) if status_icons else "")
                organ_label = tk.Label(pf["body_frame"], text=label_text, bd=1, relief=tk.SOLID, padx=2, pady=2)
                organ_label.pack(side=tk.LEFT, padx=2)
            for widget in pf["hand_frame"].winfo_children():
                if isinstance(widget, tk.Button):
                    widget.destroy()
            if player.is_human:
                for card in player.hand:
                    if card.card_type == CardType.ORGAN:
                        btn_text = f"Organ ({card.color.value})"
                    elif card.card_type == CardType.VIRUS:
                        btn_text = f"Virus ({card.color.value})"
                    elif card.card_type == CardType.MEDICINE:
                        btn_text = f"Medicine ({card.color.value})"
                    elif card.card_type == CardType.TREATMENT:
                        btn_text = f"{card.treatment.value}"
                    else:
                        btn_text = str(card)
                    btn = tk.Button(pf["hand_frame"], text=btn_text)
                    btn.pack(side=tk.LEFT, padx=2)
                    btn.config(command=lambda c=card: self.on_card_clicked(c))
                discard_btn = tk.Button(pf["hand_frame"], text="Discard...")
                discard_btn.pack(side=tk.LEFT, padx=5)
                discard_btn.config(command=self.on_discard_clicked)
            else:
                pf["hand_frame"].winfo_children()[0].config(text=f"Hand: {len(player.hand)} cards")
        self.root.update_idletasks()

    def log(self, message):
        """Append a message to the log text area."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def on_card_clicked(self, card):
        """Handle when the human player clicks a card in their hand to play it."""
        current_player = self.game.players[self.game.current_player_index]
        if not current_player.is_human:
            return 
        if card.card_type == CardType.ORGAN:
            success, msg = self.game.play_card(current_player, card)
            if not success:
                messagebox.showerror("Invalid Move", msg)
                return
            self.log(msg)
            self.end_turn()
        elif card.card_type == CardType.VIRUS:
            options = []
            for op in self.game.players:
                for col, placed in op.body.items():
                    if op == current_player:
                        pass
                    if placed.is_immunized():
                        continue
                    if card.color != Color.MULTI and placed.card.color != Color.MULTI and card.color != placed.card.color:
                        continue
                    if placed.is_infected() and placed.card.color == Color.MULTI:
                        existing = placed.virus_cards[0]
                        if existing.color == card.color:
                            continue
                    status = "healthy"
                    if placed.is_infected():
                        status = "infected"
                    elif placed.is_vaccinated():
                        status = "vaccinated"
                    desc = f"{op.name}'s {placed.card.color.value} organ ({status})"
                    options.append((op, col, desc))
            if not options:
                messagebox.showwarning("No Targets", "No valid targets for this virus.")
                return
            choice = simpledialog.askstring("Choose target", 
                "Enter the number of the target for the virus:\n" + 
                "\n".join(f"{i+1}. {opt[2]}" for i, opt in enumerate(options)))
            if not choice:
                return  
            try:
                idx = int(choice.strip()) - 1
                if idx < 0 or idx >= len(options):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid target number.")
                return
            target_player, target_color, desc = options[idx]
            success, msg = self.game.play_card(current_player, card, target_player=target_player, target_color=target_color)
            if not success:
                messagebox.showerror("Invalid Move", msg)
                return
            self.log(msg)
            self.end_turn()
        elif card.card_type == CardType.MEDICINE:
            options = []
            for col, placed in current_player.body.items():
                if placed.is_immunized():
                    continue 
                if card.color != Color.MULTI and placed.card.color != Color.MULTI and card.color != placed.card.color:
                    continue
                if placed.is_infected():
                    virus_card = placed.virus_cards[0]
                    if card.color != Color.MULTI and virus_card.color != Color.MULTI and card.color != virus_card.color:
                        continue
                    status = "infected"
                elif placed.is_vaccinated():
                    if placed.card.color == Color.MULTI and placed.medicine_cards:
                        if placed.medicine_cards[0].color == card.color:
                            continue  
                    status = "vaccinated"
                else:
                    status = "healthy"
                options.append((col, f"{placed.card.color.value} organ ({status})"))
            if not options:
                messagebox.showwarning("No Targets", "No valid organ to use this medicine on.")
                return
            choice = simpledialog.askstring("Choose organ", 
                "Enter the number of your organ to use the medicine on:\n" + 
                "\n".join(f"{i+1}. {desc}" for i, (_, desc) in enumerate(options)))
            if not choice:
                return
            try:
                idx = int(choice.strip()) - 1
                if idx < 0 or idx >= len(options):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
                return
            target_color, desc = options[idx]
            success, msg = self.game.play_card(current_player, card, target_color=target_color)
            if not success:
                messagebox.showerror("Invalid Move", msg)
                return
            self.log(msg)
            self.end_turn()
        elif card.card_type == CardType.TREATMENT:
            tret = card.treatment
            if tret == TreatmentType.TRANSPLANT:
                all_organs = []
                for op in self.game.players:
                    for col, placed in op.body.items():
                        if placed.is_immunized():
                            continue  
                        all_organs.append((op, col, f"{op.name}'s {placed.card.color.value} organ"))
                if not all_organs:
                    messagebox.showerror("Transplant", "No organs available to swap.")
                    return
                choice1 = simpledialog.askstring("Transplant", 
                    "Enter the number for the first organ to swap:\n" + 
                    "\n".join(f"{i+1}. {desc}" for i, (*_, desc) in enumerate(all_organs)))
                if not choice1:
                    return
                try:
                    idx1 = int(choice1.strip()) - 1
                    assert 0 <= idx1 < len(all_organs)
                except Exception:
                    messagebox.showerror("Invalid Input", "Invalid selection.")
                    return
                op1, col1, desc1 = all_organs[idx1]
                all_organs2 = [(op, col, desc) for (op, col, desc) in all_organs if op is not op1]
                if not all_organs2:
                    messagebox.showerror("Transplant", "No valid second organ to swap with the first selection.")
                    return
                choice2 = simpledialog.askstring("Transplant", 
                    f"First chosen: {desc1}\nEnter the number for the second organ to swap:\n" + 
                    "\n".join(f"{i+1}. {desc}" for i, (*_, desc) in enumerate(all_organs2)))
                if not choice2:
                    return
                try:
                    idx2 = int(choice2.strip()) - 1
                    assert 0 <= idx2 < len(all_organs2)
                except Exception:
                    messagebox.showerror("Invalid Input", "Invalid selection for second organ.")
                    return
                op2, col2, desc2 = all_organs2[idx2]
                success, msg = self.game.play_card(current_player, card, player1=op1, color1=col1, player2=op2, color2=col2)
                if not success:
                    messagebox.showerror("Transplant Failed", msg)
                    return
                self.log(msg)
                self.end_turn()
            elif tret == TreatmentType.ORGAN_THIEF:
                options = []
                for op in self.game.players:
                    if op is current_player:
                        continue
                    for col, placed in op.body.items():
                        if placed.is_immunized():
                            continue
                        if col in current_player.body:
                            continue
                        options.append((op, col, f"{op.name}'s {placed.card.color.value} organ"))
                if not options:
                    messagebox.showwarning("Organ Thief", "No organ available to steal.")
                    return
                choice = simpledialog.askstring("Organ Thief", 
                    "Enter the number of an organ to steal:\n" + 
                    "\n".join(f"{i+1}. {desc}" for i, (*_, desc) in enumerate(options)))
                if not choice:
                    return
                try:
                    idx = int(choice.strip()) - 1
                    assert 0 <= idx < len(options)
                except Exception:
                    messagebox.showerror("Invalid Input", "Invalid selection.")
                    return
                target_player, target_color, desc = options[idx]
                success, msg = self.game.play_card(current_player, card, target_player=target_player, target_color=target_color)
                if not success:
                    messagebox.showerror("Move Failed", msg)
                    return
                self.log(msg)
                self.end_turn()
            elif tret == TreatmentType.CONTAGION:
                success, msg = self.game.play_card(current_player, card)
                if not success:
                    messagebox.showerror("Error", msg)
                    return
                self.log(msg)
                self.end_turn()
            elif tret == TreatmentType.LATEX_GLOVE:
                if messagebox.askyesno("Latex Glove", "This will force all other players to discard their hand and skip their next turn. Proceed?"):
                    success, msg = self.game.play_card(current_player, card)
                    if not success:
                        messagebox.showerror("Error", msg)
                        return
                    self.log(msg)
                    self.end_turn()
            elif tret == TreatmentType.MEDICAL_ERROR:
                options = [op for op in self.game.players if op is not current_player]
                if not options:
                    messagebox.showwarning("Medical Error", "No other player to swap with.")
                    return
                choice = simpledialog.askstring("Medical Error",
                    "Enter the number of a player to swap bodies with:\n" + 
                    "\n".join(f"{i+1}. {op.name}" for i, op in enumerate(options)))
                if not choice:
                    return
                try:
                    idx = int(choice.strip()) - 1
                    assert 0 <= idx < len(options)
                except Exception:
                    messagebox.showerror("Invalid Input", "Invalid selection.")
                    return
                target_player = options[idx]
                success, msg = self.game.play_card(current_player, card, target_player=target_player)
                if not success:
                    messagebox.showerror("Move Failed", msg)
                    return
                self.log(msg)
                self.end_turn()

    def on_discard_clicked(self):
        """Handle the human clicking the Discard... button to discard cards."""
        current_player = self.game.players[self.game.current_player_index]
        if not current_player.is_human:
            return
        if not current_player.hand:
            return
        choice = simpledialog.askstring("Discard", 
            "Enter the card numbers to discard (e.g., 1,3 to discard cards 1 and 3):\n" +
            "\n".join(f"{i+1}. {self.card_to_text(card)}" for i, card in enumerate(current_player.hand)))
        if not choice:
            return
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip()]
        except:
            messagebox.showerror("Invalid Input", "Please enter valid card numbers separated by commas.")
            return
        indices = sorted(set(indices), reverse=True)
        if any(i < 0 or i >= len(current_player.hand) for i in indices):
            messagebox.showerror("Invalid Input", "One or more indices are out of range.")
            return
        discarded_count = 0
        for i in indices:
            card = current_player.hand[i]
            current_player.hand.pop(i)
            self.game.discard_pile.append(card)
            discarded_count += 1
        if discarded_count > 0:
            self.log(f"{current_player.name} discarded {discarded_count} card(s).")
            self.end_turn()

    def card_to_text(self, card):
        """Helper to get text description of a card (for discard prompts)."""
        if card.card_type == CardType.ORGAN:
            return f"Organ ({card.color.value})"
        elif card.card_type == CardType.VIRUS:
            return f"Virus ({card.color.value})"
        elif card.card_type == CardType.MEDICINE:
            return f"Medicine ({card.color.value})"
        elif card.card_type == CardType.TREATMENT:
            return f"{card.treatment.value}"
        else:
            return str(card)

    def start_turn(self):
        """Begin the current player's turn. Handle skip logic or AI decision if needed."""
        current_player = self.game.players[self.game.current_player_index]
        if current_player.skip_turn:
            current_player.skip_turn = False
            while len(current_player.hand) < 3:
                card = self.game._draw_from_deck()
                if not card:
                    break
                current_player.hand.append(card)
            self.log(f"{current_player.name} skips their turn and draws {len(current_player.hand)} card(s).")
            self.end_turn(skipped=True)
            return
        if not current_player.is_human:
            self.root.after(500, self.ai_turn_action)
        self.update_ui()

    def end_turn(self, skipped=False):
        """End the current player's turn: draw up to 3, check victory, and pass to next player."""
        current_player = self.game.players[self.game.current_player_index]
        if not skipped:
            while len(current_player.hand) < 3:
                card = self.game._draw_from_deck()
                if not card:
                    break
                current_player.hand.append(card)
            if current_player.is_human:
                drawn = 3 - len(current_player.hand)  
                if drawn > 0:
                    self.log(f"You draw {drawn} card(s).")

        winner = self.game.check_victory()
        if winner:
            self.update_ui()
            self.log(f"*** {winner.name} wins the game! ***")
            messagebox.showinfo("Game Over", f"{winner.name} has won the game!")
            return
        self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
        self.start_turn()

    def ai_turn_action(self):
        """Call the AI logic for the current AI player's turn and handle the result."""
        current_player = self.game.players[self.game.current_player_index]
        if current_player.is_human:
            return
        import ai
        action_desc = ai.ai_take_turn(self.game, current_player)
        self.log(action_desc)
        self.end_turn()

def main():
    root = tk.Tk()
    num = simpledialog.askinteger("Players", "Enter number of players (2-8):", minvalue=2, maxvalue=8, parent=root)
    if num is None:
        num = 4  
    app = VirusGameGUI(root, num_players=num)
    root.mainloop()

if __name__ == "__main__":
    main()
