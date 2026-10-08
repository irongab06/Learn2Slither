import argparse
from pathlib import Path

import pygame

from src.agent.agent import Agent
from src.session import run_sessions
from src.gui.renderer import Renderer


def parse_arguments():
    parser = argparse.ArgumentParser(description="Learn2Slither")
    parser.add_argument(
        "-sessions", type=int, default=100,
        help="nombre de parties a jouer (defaut : 100)",
    )
    parser.add_argument(
        "-load", type=str, default=None,
        help="modele a charger au depart",
    )
    parser.add_argument(
        "-save", type=str, default=None,
        help="fichier ou sauvegarder le modele a la fin",
    )
    parser.add_argument(
        "-visual", choices=["on", "off"], default="on",
        help="fenetre Pygame (on) ou terminal seul (off)",
    )
    parser.add_argument(
        "-speed", type=int, default=200,
        help="delai entre deux coups, en millisecondes (defaut : 200)",
    )
    parser.add_argument(
        "-dontlearn", action="store_true",
        help="jouer sans apprendre (evaluation d'un modele)",
    )
    parser.add_argument(
        "-step-by-step", action="store_true",
        help="un coup par appui sur Espace ou Fleche droite",
    )
    parser.add_argument(
        "-grid-size", type=int, default=10,
        help="taille du plateau, de 5 a 15 (defaut : 10)",
    )
    parser.add_argument(
        "-menu", action="store_true",
        help="ouvrir le menu graphique",
    )
    return parser.parse_args()


def check_arguments(args):
    if args.sessions < 1:
        print("Erreur : -sessions doit etre au moins 1.")
        return False
    if args.grid_size < 5 or args.grid_size > 15:
        print("Erreur : -grid-size doit etre entre 5 et 15.")
        return False
    if args.load is not None and not Path(args.load).is_file():
        print(f"Erreur : modele introuvable : {args.load}")
        return False
    if args.dontlearn and args.save is not None:
        print("Erreur : -save n'a pas de sens avec -dontlearn.")
        return False
    if args.save is not None:
        # On verifie le chemin maintenant, pas apres 50 minutes d'entrainement.
        save_path = Path(args.save)
        if save_path.is_dir():
            print(f"Erreur : {args.save} est un dossier, pas un fichier.")
            return False
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            print(f"Erreur : impossible de creer le dossier de {args.save}")
            return False
    return True


def build_agent(args):
    agent = Agent()
    if args.load is not None:
        try:
            agent.load(args.load)
        except Exception:
            print(f"Erreur : {args.load} n'est pas un modele valide.")
            return None
    if args.dontlearn:
        agent.epsilon = 0.0
        agent.network.eval()
    return agent


def save_model(agent, path):
    try:
        agent.save(path)
    except (OSError, RuntimeError):
        print(f"Erreur : impossible d'ecrire le modele dans {path}")
        return False
    print(f"Modele sauvegarde dans {path}")
    return True


def run(args, agent):
    try:
        if args.visual == "off":
            run_sessions(
                args.sessions,
                agent,
                learn=not args.dontlearn,
                grid_size=args.grid_size,
            )
        else:
            renderer = Renderer(
                agent,
                sessions=args.sessions,
                learn=not args.dontlearn,
                speed=args.speed,
                step_by_step=args.step_by_step,
                grid_size=args.grid_size,
            )
            renderer.run()
    except KeyboardInterrupt:
        # Ctrl+C : on s'arrete proprement, et on sauvegarde quand meme.
        print("\nArret demande par l'utilisateur.")
        pygame.quit()
    if args.save is not None:
        save_model(agent, args.save)


def run_menu(args):
    # Le menu choisit lui-meme le modele : pas d'agent a construire ici.
    renderer = Renderer(
        sessions=args.sessions,
        speed=args.speed,
        step_by_step=args.step_by_step,
    )
    try:
        renderer.run()
    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur.")
        pygame.quit()


def main():
    args = parse_arguments()
    if not check_arguments(args):
        return
    if args.menu:
        run_menu(args)
        return
    agent = build_agent(args)
    if agent is None:
        return
    run(args, agent)


if __name__ == "__main__":
    main()
