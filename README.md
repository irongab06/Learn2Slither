# Learn2Slither

*[English version](README.en.md)*

Un Snake joué par une intelligence artificielle. Le serpent ne voit que ce qui se
trouve dans les quatre directions depuis sa tête, et il apprend seul, par essais et
erreurs, à aller chercher les pommes vertes, éviter les rouges, les murs et son
propre corps. L'apprentissage repose sur un **Deep Q-Network** (DQN) écrit avec
PyTorch.

Projet réalisé dans le cadre du cursus 42.

## Sommaire

1. [Installation](#installation)
2. [Lancer le programme](#lancer-le-programme)
3. [Organisation du projet](#organisation-du-projet)
4. [Le jeu](#le-jeu)
5. [La vision du serpent](#la-vision-du-serpent)
6. [L'agent et le réseau de neurones](#lagent-et-le-réseau-de-neurones)
7. [Les modèles fournis](#les-modèles-fournis)
8. [Entraîner son propre modèle](#entraîner-son-propre-modèle)
9. [Limites connues](#limites-connues)

## Installation

```sh
git clone git@github.com:irongab06/Learn2Slither.git
cd Learn2Slither
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dépendances : `pygame` (affichage), `torch` (réseau de neurones),
`flake8` (norme). Testé avec Python 3.12.

Toutes les commandes se lancent **depuis la racine du projet** avec
`python -m src.main` (les imports partent de `src`).

## Lancer le programme

```sh
python -m src.main -h
```

| option | défaut | rôle |
|---|---|---|
| `-sessions N` | 100 | nombre de parties à jouer |
| `-load CHEMIN` | — | charge un modèle au départ |
| `-save CHEMIN` | — | sauvegarde le modèle à la fin |
| `-visual on/off` | `on` | fenêtre Pygame, ou terminal seul |
| `-speed MS` | 200 | délai entre deux coups, en millisecondes |
| `-dontlearn` | — | l'agent joue sans apprendre (évaluation) |
| `-step-by-step` | — | un coup par appui sur **Espace** ou **→** |
| `-grid-size N` | 10 | taille du plateau, de 5 à 15 |
| `-menu` | — | ouvre le menu graphique (choix du modèle, taille du plateau) |

Les options se combinent dans n'importe quel ordre.

### Exemples

Regarder le meilleur modèle jouer trois parties :

```sh
python -m src.main -load models/best.pth -sessions 3 -dontlearn
```

Étudier une partie coup par coup :

```sh
python -m src.main -load models/best.pth -sessions 1 -dontlearn -step-by-step
```

Évaluer le modèle sur 100 parties sans affichage (quelques secondes) :

```sh
python -m src.main -visual off -load models/best.pth -sessions 100 -dontlearn
```

À la fin, un bilan indique la meilleure partie, la longueur finale moyenne et le
nombre de parties ayant atteint 35.

Entraîner un nouveau modèle sans affichage et le sauvegarder :

```sh
python -m src.main -visual off -sessions 10000 -save models/mon_modele.pth
```

Ouvrir le menu graphique :

```sh
python -m src.main -menu
```

Jouer sur un plateau de 8 × 8 avec le même modèle :

```sh
python -m src.main -load models/best.pth -sessions 1 -dontlearn -grid-size 8
```

En mode visuel, le terminal affiche à chaque coup la vision du serpent puis
l'action choisie. Dans les deux modes, chaque partie se termine par une ligne :

```
Game over, final length = 31, max length = 32, max duration = 254
```

## Organisation du projet

```
src/
├── main.py              point d'entrée : lecture des options, lancement
├── session.py           boucle de jeu sans affichage (run_sessions)
├── environment/         les règles du jeu
│   ├── board.py         le plateau (taille, cases valides)
│   ├── snake.py         le serpent (corps, direction, déplacement)
│   ├── apple.py         une pomme (position, couleur)
│   └── environment.py   une partie : état, récompenses, fin de partie
├── state/
│   └── vision.py        encodage de la vision pour le réseau
├── agent/
│   ├── dqn.py           le réseau de neurones
│   └── agent.py         l'agent : choix de l'action, mémoire, apprentissage
└── gui/
    ├── renderer.py      la fenêtre Pygame : menu, partie, statistiques
    ├── grid_renderer.py dessin du plateau, du serpent et des pommes
    ├── button.py        un bouton cliquable
    ├── selection_panel.py  un panneau d'image
    └── ui_layout.py     positions des boutons
models/                  les modèles entraînés (fichiers .pth)
assets/images/           les images de l'interface
```

Le jeu (`environment`), l'agent (`agent`) et l'affichage (`gui`) sont
indépendants : `session.py` et `renderer.py` sont les deux façons de les faire
tourner ensemble, l'une dans le terminal, l'autre dans une fenêtre.

## Le jeu

- Plateau de 10 × 10 par défaut.
- Deux pommes vertes et une pomme rouge, placées au hasard. Quand une pomme est
  mangée, une nouvelle de la même couleur apparaît.
- Le serpent démarre avec 3 cases, placé au hasard.
- Pomme verte : le serpent grandit de 1. Pomme rouge : il rétrécit de 1.
- Fin de partie : mur, collision avec son propre corps, ou longueur tombée à 0.
- Un serpent ne recule jamais : si l'agent demande la direction opposée à celle
  en cours, l'ordre est ignoré et le serpent continue tout droit.

Les récompenses sont définies en tête de `environment.py` :

| événement | récompense |
|---|---|
| pomme verte | `+1` |
| pomme rouge | `-0.5` |
| un coup sans rien manger | `-0.005` |
| mort | `-2` |

J'ai ajouté une règle de sécurité : après `taille × taille` coups sans pomme
verte (100 coups sur 10 × 10), la partie est arrêtée avec la même pénalité que la
mort. Sans elle, un agent peu entraîné peut tourner en rond indéfiniment. Ces
arrêts sont signalés par `Partie arretee` au lieu de `Game over`.

## La vision du serpent

L'agent ne reçoit **que** ce que le serpent voit depuis sa tête, dans les quatre
directions, jusqu'au mur. C'est ce qui est affiché dans le terminal à chaque coup :

```
      W
      0
      0
W00G00H00SW
      S
      0
      W
```

`W` mur, `H` tête, `S` corps, `G` pomme verte, `R` pomme rouge, `0` case vide.

Pour le réseau, `vision.py` transforme chaque case en un vecteur de 5 valeurs
(une par symbole possible, codage *one-hot*). Chaque direction est complétée à 25
cases, ce qui donne une entrée de taille fixe : 4 directions × 25 cases × 5
valeurs = **500 nombres**. Rien d'autre n'est transmis à l'agent : ni la position
des pommes hors de la croix, ni la taille du plateau, ni la direction du serpent.

## L'agent et le réseau de neurones

### Le réseau (`dqn.py`)

Un réseau entièrement connecté, volontairement simple :

```
500 entrées  →  128 neurones (ReLU)  →  128 neurones (ReLU)  →  4 sorties
```

Les 4 sorties sont les **Q-values** : pour la vision reçue, une estimation de la
qualité de chacune des actions `up`, `down`, `left`, `right`. Jouer, c'est
choisir l'action dont la Q-value est la plus grande.

### Apprendre (`agent.py`)

À chaque coup, l'agent mémorise la transition `(vision, action, récompense,
vision suivante, fin de partie)` dans une mémoire de 100 000 entrées, puis tire
64 transitions au hasard et corrige le réseau dessus. Tirer dans le passé plutôt
que d'apprendre sur le dernier coup seulement évite que le réseau n'oublie ce
qu'il a appris quelques parties plus tôt.

La cible de chaque correction est l'équation de Q-learning :

```
cible = récompense + gamma × Q_cible(vision suivante, meilleure action)
```

avec `gamma = 0.99`. Deux détails classiques pour stabiliser l'apprentissage :

- **Double DQN** : le réseau principal choisit la meilleure action suivante, mais
  c'est une copie figée du réseau (le *réseau cible*, resynchronisée tous les
  100 pas) qui en donne la valeur. Ça limite la tendance du DQN à surestimer.
- **Perte de Huber** (`SmoothL1Loss`) et optimiseur Adam (`lr = 0.0005`).

### Explorer

Pour découvrir de nouvelles situations, l'agent joue parfois au hasard : avec une
probabilité `epsilon`, l'action est tirée au sort au lieu de suivre le réseau.
`epsilon` démarre à 1 (tout au hasard) et descend linéairement jusqu'à 0.01 au
cours des 30 000 premiers coups. En mode `-dontlearn`, `epsilon` vaut 0 : le
modèle joue exactement ce qu'il sait.

### Sauvegarder

Un modèle (`.pth`) contient les poids du réseau, `epsilon` et l'avancement de
l'exploration — de quoi rejouer, ou reprendre un entraînement.

## Les modèles fournis

| fichier | entraînement | longueur finale moyenne |
|---|---|---|
| `models/1_sessions.pth` | 1 partie | 3 — joue au hasard, meurt en quelques coups |
| `models/10_sessions.pth` | 10 parties | 3 |
| `models/100_sessions.pth` | 100 parties | 3 — évite déjà les murs, mais ne mange pas |
| `models/best.pth` | 10 000 parties | **≈ 27** |

`best.pth`, mesuré sur 300 parties sans apprentissage (plateau 10 × 10) :
longueur finale moyenne ≈ 27, médiane 27, **99 % des parties atteignent 10**,
environ un tiers dépassent 30 et 10 à 15 % dépassent 35. Meilleure partie
observée : 48.

Avec le même fichier sur d'autres plateaux, le serpent joue bien de 5 × 5 à
10 × 10, et dépasse la longueur 7 sur toutes les tailles jusqu'à 15 × 15.

## Entraîner son propre modèle

```sh
python -m src.main -visual off -sessions 10000 -save models/mon_modele.pth
```

Compter une cinquantaine de minutes pour 10 000 parties. Le terminal affiche une
ligne par partie (coups joués, longueur max, nombre de mises à jour du réseau,
epsilon). Les ~4 000 premières parties servent surtout à remplir la mémoire :
le serpent y joue quasiment au hasard, et le niveau monte d'un coup quand
`epsilon` atteint son plancher.

Sans `-save`, l'entraînement est perdu à la fin de la commande. Pour voir un
entraînement en direct :

```sh
python -m src.main -load models/best.pth -sessions 3
```

## Limites connues

- Le modèle a été entraîné uniquement en 10 × 10 : sa vision couvre jusqu'à 10
  cases par direction, donc au-delà de 10 × 10 il joue, mais nettement moins bien.
- Les performances varient fortement d'une partie à l'autre (de 3 à 48 pour le
  même modèle) : pour juger un modèle, il faut une série de parties, pas une seule.
