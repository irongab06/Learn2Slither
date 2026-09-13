# learn2slither

Projet d'apprentissage par renforcement autour du jeu Snake.

L'objectif est d'entrainer un agent avec un DQN (Deep Q-Network) pour apprendre a survivre, chercher les pommes et maximiser son score.

## Architecture

- `src/environment/` contient les regles du jeu : plateau, serpent, pommes, collisions et score.
- `src/state/` transforme l'etat du jeu en observation utilisable par l'agent.
- `src/gui/` gere l'affichage avec `pygame`, sans porter la logique du jeu.
- `src/main.py` servira de point d'entree pour lancer une partie, un entrainement ou une evaluation.

## Stack

- Python
- pygame
- numpy
