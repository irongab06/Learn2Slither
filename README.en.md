# Learn2Slither

*[Version française](README.md)*

A Snake game played by an artificial intelligence. The snake only sees what lies
in the four directions from its head, and it learns on its own, by trial and
error, to go after green apples and avoid red ones, walls and its own body.
Learning relies on a **Deep Q-Network** (DQN) written with PyTorch.

Project made as part of the 42 curriculum.

## Contents

1. [Installation](#installation)
2. [Running the program](#running-the-program)
3. [Project layout](#project-layout)
4. [The game](#the-game)
5. [What the snake sees](#what-the-snake-sees)
6. [The agent and the neural network](#the-agent-and-the-neural-network)
7. [Provided models](#provided-models)
8. [Training your own model](#training-your-own-model)
9. [Known limits](#known-limits)

## Installation

```sh
git clone git@github.com:irongab06/Learn2Slither.git
cd Learn2Slither
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `pygame` (display), `torch` (neural network), `numpy`, `flake8`
(code style). Tested with Python 3.12, on macOS and Linux.

The first line of `requirements.txt` points to the PyTorch **CPU** index: on
Linux, `pip` therefore installs the build without CUDA (~900 MB installed
instead of several GB), which is enough since everything runs on the processor.

### On a 42 workstation (Linux)

`venv` is not available there: the environment is created with `virtualenv`,
**from the project folder**.

```sh
cd Learn2Slither
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Since the *home* quota is small, it is better to clone the project inside the
goinfre.

Every command is run **from the project root**, either with `python snake.py`
or `python -m src.main` (both are equivalent; `snake.py` is just a shortcut
to `src/main.py`).

## Running the program

```sh
python -m src.main -h
```

| option | default | role |
|---|---|---|
| `-sessions N` | 100 | number of games to play |
| `-load PATH` | — | load a model at start |
| `-save PATH` | — | save the model at the end |
| `-visual on/off` | `on` | Pygame window, or terminal only |
| `-speed MS` | 200 | delay between two moves, in milliseconds |
| `-dontlearn` | — | the agent plays without learning (evaluation) |
| `-step-by-step` | — | one move per press of **Space** or **→** |
| `-grid-size N` | 10 | board size, from 5 to 15 |
| `-menu` | — | open the graphical menu (model and board-size selection) |

Options can be combined in any order.

### Examples

Watch the best model play three games:

```sh
python -m src.main -load models/best.pth -sessions 3 -dontlearn
```

Study a game move by move:

```sh
python -m src.main -load models/best.pth -sessions 1 -dontlearn -step-by-step
```

Evaluate the model over 100 games without display (a few seconds):

```sh
python -m src.main -visual off -load models/best.pth -sessions 100 -dontlearn
```

A summary is printed at the end: best game, mean final length, and how many
games reached 35.

Train a new model without display and save it:

```sh
python -m src.main -visual off -sessions 10000 -save models/my_model.pth
```

Open the graphical menu:

```sh
python -m src.main -menu
```

Play on an 8 × 8 board with the same model:

```sh
python -m src.main -load models/best.pth -sessions 1 -dontlearn -grid-size 8
```

In visual mode, the terminal prints at every move the snake's vision and the
chosen action. In both modes, every game ends with a line such as:

```
Game over, final length = 31, max length = 32, max duration = 254
```

## Project layout

```
src/
├── main.py              entry point: option parsing, launch
├── session.py           game loop without display (run_sessions)
├── environment/         the game rules
│   ├── board.py         the board (size, valid cells)
│   ├── snake.py         the snake (body, direction, movement)
│   ├── apple.py         an apple (position, colour)
│   └── environment.py   one game: state, rewards, game over
├── state/
│   └── vision.py        encoding of the vision for the network
├── agent/
│   ├── dqn.py           the neural network
│   └── agent.py         the agent: action choice, memory, learning
└── gui/
    ├── renderer.py      the Pygame window: menu, game, statistics
    ├── grid_renderer.py drawing of the board, snake and apples
    ├── button.py        a clickable button
    ├── selection_panel.py  an image panel
    └── ui_layout.py     button positions
models/                  trained models (.pth files)
assets/images/           interface images
```

The game (`environment`), the agent (`agent`) and the display (`gui`) are
independent: `session.py` and `renderer.py` are the two ways of running them
together, one in the terminal, the other in a window.

## The game

- 10 × 10 board by default.
- Two green apples and one red apple, placed at random. When an apple is eaten,
  a new one of the same colour appears.
- The snake starts with 3 cells, placed at random.
- Green apple: the snake grows by 1. Red apple: it shrinks by 1.
- Game over: wall, collision with its own body, or length down to 0.
- A snake never moves backwards: if the agent asks for the direction opposite to
  the current one, the order is ignored and the snake keeps going straight.

Rewards are defined at the top of `environment.py`:

| event | reward |
|---|---|
| green apple | `+1` |
| red apple | `-0.5` |
| a move without eating | `-0.005` |
| death | `-2` |

I added one safety rule: after `size × size` moves without a green apple (100
moves on 10 × 10), the game is stopped with the same penalty as a death. Without
it, a poorly trained agent can circle forever. Those stops are reported as
`Partie arretee` instead of `Game over`.

## What the snake sees

The agent receives **only** what the snake sees from its head, in the four
directions, up to the wall. This is what the terminal prints at every move:

```
      W
      0
      0
W00G00H00SW
      S
      0
      W
```

`W` wall, `H` head, `S` body, `G` green apple, `R` red apple, `0` empty cell.

For the network, `vision.py` turns each cell into a vector of 5 values (one per
possible symbol, *one-hot* encoding). Each direction is padded to 25 cells, which
gives a fixed-size input: 4 directions × 25 cells × 5 values = **500 numbers**.
Nothing else is passed to the agent: no apple position outside the cross, no
board size, no snake direction.

## The agent and the neural network

### The network (`dqn.py`)

A fully connected network, deliberately simple:

```
500 inputs  →  128 neurons (ReLU)  →  128 neurons (ReLU)  →  4 outputs
```

The 4 outputs are the **Q-values**: for the received vision, an estimate of how
good each of the actions `up`, `down`, `left`, `right` is. Playing means picking
the action with the highest Q-value.

### Learning (`agent.py`)

At every move the agent stores the transition `(vision, action, reward, next
vision, game over)` in a memory of 100,000 entries, then samples 64 transitions
at random and corrects the network on them. Sampling from the past instead of
learning only from the last move prevents the network from forgetting what it
learned a few games earlier.

The target of each correction is the Q-learning equation:

```
target = reward + gamma × Q_target(next vision, best action)
```

with `gamma = 0.99`. Two classic details to stabilise learning:

- **Double DQN**: the main network picks the best next action, but a frozen copy
  of the network (the *target network*, resynchronised every 100 steps) gives its
  value. This limits the DQN's tendency to overestimate.
- **Huber loss** (`SmoothL1Loss`) and the Adam optimiser (`lr = 0.0005`).

### Exploring

To discover new situations, the agent sometimes plays at random: with
probability `epsilon`, the action is drawn at random instead of following the
network. `epsilon` starts at 1 (everything random) and decreases linearly to
0.01 over the first 30,000 moves. In `-dontlearn` mode, `epsilon` is 0: the
model plays exactly what it knows.

### Saving

A model (`.pth`) holds the network weights, `epsilon` and the exploration
progress — enough to play again, or to resume a training.

## Provided models

| file | training | mean final length |
|---|---|---|
| `models/1_sessions.pth` | 1 game | 3 — plays at random, dies within a few moves |
| `models/10_sessions.pth` | 10 games | 3 |
| `models/100_sessions.pth` | 100 games | 3 — already avoids walls, but does not eat |
| `models/best.pth` | 10,000 games | **≈ 27** |

`best.pth`, measured over 300 games without learning (10 × 10 board): mean final
length ≈ 27, median 27, **99% of games reach 10**, about a third exceed 30 and
10 to 15% exceed 35. Best game observed: 48.

With the same file on other boards, the snake plays well from 5 × 5 to 10 × 10,
and exceeds length 7 on every size up to 15 × 15.

## Training your own model

```sh
python -m src.main -visual off -sessions 10000 -save models/my_model.pth
```

Expect about fifty minutes for 10,000 games. The terminal prints one line per
game (moves played, max length, number of network updates, epsilon). The first
~4,000 games mostly fill the memory: the snake plays almost at random, and the
level jumps once `epsilon` reaches its floor.

Without `-save`, the training is lost when the command ends. To watch a training
live:

```sh
python -m src.main -load models/best.pth -sessions 3
```

## Known limits

- The model was trained on 10 × 10 only: its vision covers up to 10 cells per
  direction, so beyond 10 × 10 it plays, but noticeably worse.
- Performance varies a lot from one game to the next (from 3 to 48 for the same
  model): judging a model takes a series of games, not a single one.
