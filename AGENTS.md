# Learn2Slither - Contexte et consignes de travail

Derniere mise a jour : 2026-09-30.

Ce fichier resume les decisions utiles de la conversation. Il ne constitue pas
une transcription complete ni une preuve que toutes les fonctionnalites sont
terminees. Relire le code avant de proposer une modification : il peut avoir
evolue depuis cette mise a jour. Le sujet local fait reference pour les exigences.

## Collaboration avec l'utilisateur

- Repondre en francais, simplement, avec des explications courtes et concretes.
- L'utilisateur apprend Python, Pygame et le reinforcement learning en codant.
  Il veut comprendre son propre code et pouvoir l'expliquer a la correction.
- Avancer une fonction ou une notion a la fois. Expliquer les parametres,
  les coordonnees et les boucles avec de petits exemples.
- Preferer des `if`, `elif`, `for`, `while` explicites aux constructions compactes
  ou aux abstractions difficiles a comprendre. Introduire les nouveaux concepts.
- Quand il dit "regarde", lire son code et commenter sans le reecrire.
  Quand il dit "fais-le", "mets-le" ou equivalent, implementer la demande.
- Respecter les demandes "sans code", "juste le debut" et les tests temporaires.
  Retirer uniquement les ajouts de test lorsqu'il demande de revenir en arriere.
- Ne pas ajouter de grosses fonctionnalites ou refactorisations sans rapport
  avec l'etape demandee. Ne pas ecraser les modifications de l'utilisateur.
- Verifier dans le PDF avant d'affirmer une exigence. Des conseils precedents
  etaient errones ; les corrections importantes sont consignees ci-dessous.
- Actualiser ce contexte lors des decisions importantes, sans y accumuler chaque
  petit echange. Les demandes recentes de l'utilisateur priment sur ce resume.

## Sujet et exigences verifiees

Source : `learn2slither.en.subject.pdf`, version 1.1, a la racine.
Les numeros suivants sont les pages imprimees, pas les indices du lecteur PDF.

### Obligatoire

- Page 5 : plateau 10 x 10, deux pommes vertes et une pomme rouge aleatoires.
- Le serpent commence avec trois segments contigus places aleatoirement.
  Un depart toujours au meme endroit ne respecte pas cette consigne.
- Pomme verte : longueur +1, puis remplacement par une pomme verte.
- Pomme rouge : longueur -1, puis remplacement par une pomme rouge.
- Fin de partie : mur, collision avec soi-meme ou longueur nulle.
  Un serpent d'une seule case peut continuer ; deux cases = tete et queue.
- Page 7 : vision en croix depuis la tete jusqu'aux murs, dans les quatre
  directions. Conserver les cases vides et les elements au-dela des pommes
  et segments. Ne pas reduire arbitrairement chaque direction au premier objet.
- Symboles : `W` mur, `H` tete, `S` corps, `G` pomme verte, `R` pomme rouge,
  `0` case vide. L'agent ne doit pas recevoir d'informations hors de cette vision.
- Page 8 : quatre actions absolues `UP`, `LEFT`, `DOWN`, `RIGHT`.
  Ne pas revenir a trois actions relatives "tout droit / tourner gauche / droite".
  Dans le code actuel, les chaines sont en minuscules.
- Afficher graphiquement le plateau, et dans le terminal la vision et l'action.
- Page 5 : vitesse configurable avec au moins une vitesse lisible par un humain,
  ainsi qu'un mode pas-a-pas. Une seule vitesse fixe ne suffit pas.
- Pas-a-pas : l'utilisateur declenche une action de l'IA a la fois ; il ne choisit
  pas la direction. Le mode manuel au clavier n'est pas exige.
- Pages 10-11 : apprendre une fonction Q, via Q-table ou reseau de neurones.
  Le DQN est autorise, mais pas impose. Aucune limite de couches n'est specifiee.
- Gerer exploration, apprentissage, export/import de l'etat d'apprentissage et
  un mode sans apprentissage. L'entrainement peut etre sans affichage ni terminal.
- Choisir le nombre de sessions par argument de lancement.
- Pages 13-14 : entrainer avant la correction et livrer les modeles de 1, 10,
  100 sessions et le meilleur modele dans `models/`. Viser une longueur d'au
  moins 10 et une bonne survie. Une session n'est pas un epoch de reseau.
- Page 4 : respecter flake8 ; le projet n'est pas encore conforme partout.

### Bonus et choix du projet

- Page 15 : longueurs finales plus elevees (15, 20, 25, 30, 35), interface
  soignee (lobby, configuration, resultats/statistiques...), plateau variable.
- Les nombres 15 a 35 ci-dessus concernent la longueur du serpent, pas la grille.
- Le plateau variable doit etre configurable par arguments, et les memes modeles
  entraines doivent pouvoir jouer sur les differentes tailles.
- Les boutons de selection de taille sont possibles en complement des arguments.
- Le sujet ne fixe pas de taille minimale/maximale pour ce bonus.
  Tailles retenues pour le projet : 10, 15, 20 et 25 ; choix personnel,
  pas une limite officielle du sujet.
- Idee de menu : `1`, `10`, `100`, `Best`, `Bonus`. `Bonus` chargerait le meilleur
  modele et permettrait le choix de grille ; ce n'est pas encore implemente.
- Ne pas garantir qu'un modele entraine uniquement en 10 x 10 sera performant
  ailleurs : compatibilite de l'entree et generalisation doivent etre testees.
- Charger un modele specialise different pour chaque taille ne suffit pas pour
  ce bonus. Garder le meme modele et ses poids lorsque la taille change.
  Entrainement sur plusieurs tailles propose pour favoriser la generalisation,
  puis evaluation sans apprentissage sur chaque taille ; rien de cela n'est code.
- Les bonus ne sont evalues que si tout l'obligatoire est correct.

## Architecture et etat actuel

### Moteur : `src/environment/`

- `board.py` : `Board(grid_size)`, `is_inside((x, y))` verifie les bornes.
  Pas de matrice persistante necessaire pour l'etat actuel du moteur.
- `snake.py` : `body` est une liste de tuples, tete en `body[0]`, queue en
  `body[-1]`. Pas de classe par segment. `direction` est un tuple `(dx, dy)`.
- `left/right/up/down()` affectent directement la direction. Ne pas bloquer les
  demi-tours de l'agent : le moteur applique l'action et detecte la collision.
  Le sujet ne demande pas d'annuler automatiquement les actions opposees.
- `move(next_head_position, grow)` insere la tete et retire la queue sauf croissance.
  `shrink()` retire un segment supplementaire pour la pomme rouge.
- `apple.py` : `Apple(position, apple_type)`, type `green` ou `red`.
- `environment.py` : `Environment(grid_size=10)` assemble le moteur.
  `reset()` recree le serpent et les pommes pour une nouvelle partie.
- `random_snake()` cree une tete aleatoire avec deux segments en dessous et une
  direction initiale vers le haut. Le choix d'une marge de depart a ete discute.
  Le code actuel tire x avec `randrange(2, grid_size - 1)` et y avec
  `randrange(2, grid_size - 2)` : la queue peut donc atteindre la derniere ligne.
  Ne pas annoncer une marge uniforme inexistante ; revisiter si necessaire.
- `_create_random_apple()` evite le serpent et les autres pommes.
  `get_apple_at(position)` renvoie une pomme ou `None`.
- `step(action)` renvoie `(reward, done)` : mouvement -0.1, verte +1,
  rouge -1, defaite -10. Ce sont nos reglages, pas des constantes du sujet.
- `get_state()` retourne un dictionnaire `up/down/left/right`, contenant chacun
  une liste de symboles du plus proche au plus lointain, terminee par `W`.
  La tete n'est pas incluse dans ces listes puisqu'elles commencent a cote d'elle.
- `display_vision()` affiche cette vision en croix avec `H` au centre ; l'ordre
  de `up` et `left` est inverse pour l'affichage. Elle ne deplace pas le serpent.

### Affichage : `src/gui/`

- `renderer.py` : `Renderer` gere fenetre, pages, evenements et affichage.
  Pages actuelles : `menu`, `game_setup`, `game`.
- `_create_grid(size_grid)` cree `GridRenderer` et `Environment` de meme taille.
- La selection d'un modele memorise son nom et ouvre actuellement une grille
  10 x 10. Aucun fichier de modele n'est charge, le DQN n'existe pas encore.
  Le bouton Bonus n'est pas encore relie a un parcours fonctionnel.
- `update_game(action)` appelle le moteur, stocke reward/done et bloque apres
  defaite. Elle n'est actuellement appelee par aucun agent ou timer dans `run()`.
  Le serpent immobile dans l'interface est donc attendu a ce stade.
- `grid_renderer.py` : grille cyan, cadre translucide, pommes et serpent.
  `draw_snake(screen, body, direction)` dessine une image par case.
- `get_head_image(direction)` oriente la tete ; `get_body_image(previous_position,
  position, next_position)` choisit droit/coude ; `get_tail_image(previous_position,
  position)` oriente la queue. Ces methodes sont du rendu, pas du moteur.
- Conversion : pixel_x = rect.left + x * cell_size, idem pour y.
  Dans Pygame, y augmente vers le bas. Une rotation positive est antihoraire.
- Une tete seule et une tete avec queue sont deja gerees par les conditions.
- Images conservees : `head_up.png`, `tail_down.png`, `body_vertical.png`,
  `body_corner_top_right.png`, `Green_apple.png`, `Red_apple.png`.
  Le coude source relie le haut a la droite. Assets dans `assets/images/`.
- Conserver le theme futuriste/neon et les placements regles par l'utilisateur.
  `ui_layout.py` contient les positions individuelles des boutons ; ne pas les
  remplacer par un espacement uniforme ou un redesign non demande.
- `button.py` et `selection_panel.py` gerent les images des boutons et panneaux.

### Fonctionnalites volontairement retirees

- Mode manuel, commandes clavier et timer de deplacement retires a sa demande.
- Une animation fluide complexe avait ete ajoutee (interpolation, decoupage des
  images, points de raccord). Elle fonctionnait mais etait trop difficile a
  comprendre : retiree a sa demande. Garder l'affichage case par case.
- Ne pas restaurer `_draw_moving_snake`, `_clip_path_end`, les snapshots de
  positions/pommes ou les autres helpers d'animation sans nouvelle demande.
- Les serpents fixes de demonstration ont ete retires. Utiliser le vrai moteur.
- `clock.tick(60)` limite encore l'affichage ; ce n'est pas la vitesse du serpent.
- Pour l'IA avec affichage, un timer pourra etre remis plus tard, avec vitesse
  configurable. Pour entrainer sans affichage, ne pas attendre de timer.

## Encodage de la vision termine

- `src/state/vision.py` contient deux fonctions, sans classe.
- `encode_symbol(symbol)` implemente le one-hot suivant, dans cet ordre precis :
  `S` -> [1,0,0,0,0], `G` -> [0,1,0,0,0], `R` -> [0,0,1,0,0],
  `0` -> [0,0,0,1,0], `W` -> [0,0,0,0,1]. Conserver ce mapping.
  Le symbole vide est le chiffre zero sous forme de chaine, pas la lettre O
  (reverifie dans le PDF). Un symbole inconnu declenche `ValueError`.
- `encode_vision(vision)` recoit le dictionnaire complet de `get_state()`.
  Elle parcourt les directions dans l'ordre fixe `up`, `down`, `left`, `right`,
  puis les symboles de chaque direction, du plus proche au mur inclus.
- `extend()` ajoute les cinq nombres directement a une seule liste plate.
  Apres chaque rayon, `25 - len(vision[direction])` groupes de cinq zeros sont
  ajoutes : chaque direction occupe 25 emplacements, soit 125 nombres.
  Resultat : 4 * 25 * 5 = 500 valeurs pour toutes les tailles prevues.
- Le remplissage [0,0,0,0,0] signifie absence de donnee APRES le mur ; ce n'est
  ni une vraie case vide ni une information sur des cases derriere le mur.
  La tete reste implicite, elle n'est pas encodee comme symbole du rayon.
- Tests temporaires executes avec l'utilisateur : affichage des cinq encodages
  corrects et vraie vision d'Environment en 10 x 10 et 25 x 25, 500 valeurs
  dans les deux cas. 15 et 20 sont compatibles, mais pas testes lors de ces essais.
  Ces tests ne constituent pas une verification exhaustive du contenu encode.
- Le bloc `if __name__ == "__main__":` de demonstration a ensuite ete retire
  par l'utilisateur. Ne pas le restaurer sans demande.
- Limite connue : aucun controle des rayons depassant 25 symboles. Dans ce cas,
  la fonction renverrait trop de valeurs ; valider la limite avant integration.

## Decision DQN et prochaine etape

- Architecture de depart choisie : 500 -> 128 -> 128 -> 4.
  Deux couches cachees de 128 neurones ; quatre sorties Q, pas des probabilites.
- ReLU dans les couches cachees, sortie lineaire. Taille d'entree : 500.
  C'est une base a tester, pas une garantie de resultat.
- `src/main.py` etait vide lors de la derniere lecture ; l'encodage est termine.
  Aucun reseau, replay buffer, entrainement ou chargement DQN n'est implemente.
- L'utilisateur a choisi PyTorch le 2026-09-30. `torch` est ajoute aux
  dependances. Utiliser son calcul automatique des gradients, mais implementer
  notre logique DQN. Prochaine etape : construire le reseau progressivement,
  en expliquant chaque partie avant de coder tout un agent.
- L'ordre des directions d'entree est fixe ; il reste a formaliser le mapping
  entre les quatre indices de sortie et les actions absolues du moteur.
- Notions deja expliquees : poids, biais, activation, deux couches cachees,
  exploration et cible DQN `r + gamma * max Q_cible(etat_suivant, action)` ;
  pour une transition terminale, la cible est seulement `r`.
- Reseau cible evoque, mais framework, loss, optimiseur, replay, epsilon et gamma
  restent a choisir et expliquer, sauf le framework : PyTorch est choisi.
- Exemples consultes : https://github.com/leogaudin/Learn2Slither
  (13 -> 42 -> 42 -> 3) et https://github.com/sungyongcho/Learn2Slither
  (24 -> 256 -> 128 -> 3), d'apres leurs README. Ils utilisent trois actions
  relatives : ne pas recopier cette difference avec notre sujet.

## Reste a faire et limites connues

- Construire le DQN avec PyTorch progressivement avec l'utilisateur.
- Ajouter la boucle d'entrainement, les sauvegardes et l'evaluation sans apprentissage.
- Brancher l'agent a l'affichage, a la vision/action dans le terminal et au pas-a-pas.
- Ajouter les arguments de lancement : sessions, vitesse, taille bonus,
  chargement/sauvegarde, affichage, sans apprentissage, pas-a-pas.
  Les noms comme `--speed` ou `--grid-size` sont des exemples, pas deja disponibles.
- `_create_random_apple()` peut boucler sans fin s'il n'y a plus de case libre.
- Le tirage initial suppose une grille assez grande ; valider les tailles acceptees.
- Apres longueur nulle, `get_state()` ne peut pas lire `body[0]`. Prevoir le
  traitement des etats terminaux avant de brancher la collecte pour le DQN.
- `step()` ne valide pas encore les actions inconnues et n'a pas son propre
  verrou de fin de partie. Le futur pilote doit respecter `done`.
- Collision actuelle : toute position dans `body` est bloquante avant mouvement,
  y compris la queue qui pourrait se liberer. Ne pas changer cette regle sans
  examiner le comportement voulu et le sujet.
- Flake8 signale encore tabulations, espaces et quelques lignes longues.
  Ne pas annoncer la conformite ni lancer un reformatage global hors demande.
- Des tests ponctuels du moteur et du rendu Pygame sans fenetre ont ete executes,
  mais il n'existe pas encore de suite de regression complete ni de scores DQN.

## Lancement et portabilite

Depuis la racine du depot, avec les dependances installees dans un venv local :

```sh
python -m pip install -r requirements.txt
python -m src.gui.renderer
python -m flake8 src
```

`requirements.txt` contient actuellement pygame, numpy, flake8 et torch.
Utiliser `python -m src.gui.renderer`, pas `python src/gui/renderer.py`, pour
resoudre les imports depuis `src`. Recreer le venv sur chaque ordinateur.
Pour des verifications graphiques sans fenetre : `SDL_VIDEODRIVER=dummy` et
`SDL_AUDIODRIVER=dummy` peuvent etre utilises pour le processus de test.

Pour lire le sujet, utiliser un lecteur PDF ou `pdftotext` si disponible.
Sur le Mac d'origine, PDFKit via `osascript -l JavaScript` a permis d'extraire
le texte et de voir les schemas. Ne pas supposer ces outils presents ailleurs.

Ce fichier doit etre versionne et transfere avec le depot pour servir sur un
autre ordinateur. Il transmet ce resume aux assistants compatibles avec
`AGENTS.md`, pas l'historique integral de la conversation. Ne pas faire de commit
ou de push sans demande. Pour le fonctionnement du fichier :
https://developers.openai.com/codex/guides/agents-md
