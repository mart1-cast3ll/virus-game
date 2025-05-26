# Virus! Card Game
**What is Virus!?**

Virus! is a fun and fast-paced card game where players compete to be the first to build a healthy body with four different organs. During the game, players can infect opponents' organs, cure infections, immunize their own, and use special treatment cards to change the course of the match.

---

## 🎲 How to Play

- Each player starts with 3 cards in hand.
- On your turn, you can:
  - Play one card (organ, virus, medicine, or treatment).
  - Or discard one or more cards and draw until you have 3.
- The goal is to be the first player to have 4 healthy (uninfected) organs.
- You can attack others with viruses or steal organs using treatment cards.
- Some cards allow you to protect your organs or force everyone to discard their hand.

---

### 🎯 Objective

Be the first player to have **4 healthy organs** in front of you (organs that are not infected).

---

### 🃏 Types of Cards

#### 1. Organs

- Colors: Red, Green, Blue, Yellow, and Multicolor.
- You can only have **one organ of each color**.
- Multicolor organs count as any color but also interact with all viruses and medicines.

#### 2. Viruses

- Can be played on opponents' organs of the same color.
- A multicolor virus infects any organ.
- A second virus on the same organ destroys it (send to discard pile).
- You **cannot** infect an **immunized organ**.

#### 3. Medicines

- Can be played on your own organs.
- One medicine protects (vaccinates) the organ.
- Two medicines **immunize** the organ (cannot be infected or destroyed).
- A medicine removes a virus **if played on the same organ and color**.

#### 4. Treatment Cards

| Card          | Effect                                                             |
| ------------- | ------------------------------------------------------------------ |
| Transplant    | Swap two organs between any two players (even yourself).           |
| Organ Thief   | Steal an unprotected organ from another player.                    |
| Contagion     | Spread a virus from one of your infected organs to another player. |
| Latex Glove   | All other players discard their hand and skip their next turn.     |
| Medical Error | Swap your entire body (organs) with another player.                |

---

### 🔁 Turn Overview

On your turn:

1. Play **one card** from your hand, or
2. Discard **one or more cards**, then draw up to 3.
3. At the end of your turn, draw cards until you have 3 cards in hand.

You must always **draw up to 3** cards after your action.

---

### 💥 Additional Rules

- You cannot place an organ if you already have one of the same color.
- You cannot use a virus on an immunized organ.
- You cannot apply medicine to an opponent's organ.
- If the deck runs out, reshuffle the discard pile.
- All actions must respect card colors, unless using a multicolor card.

---

The game ends immediately when one player has 4 healthy organs. That player wins!

## 🚀 How to Run the Game

1. Open the project in **Visual Studio Code**.
2. Make sure `pygame` is installed:
   ```bash
   pip install pygame
   ```
3. Use this `launch.json` file to run `main.py` with the debugger:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python Debugger: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

4. Open `main.py`, press `F5`, or click the green play button in VS Code.

---
