import argparse
from pathlib import Path

from src.agent.agent import Agent
from src.session import run_sessions
from src.gui.renderer import Renderer


def main():
	parser = argparse.ArgumentParser(description="Learn2Slither")

	parser.add_argument("-sessions", type=int, default=100)
	parser.add_argument("-load", type=str, default=None)
	parser.add_argument("-save", type=str, default=None)
	parser.add_argument("-visual", choices=["on", "off"], default="on")
	parser.add_argument("-speed", type=int, default=200)
	parser.add_argument("-dontlearn", action="store_true")
	parser.add_argument("-step-by-step", action="store_true")
	parser.add_argument("-grid-size", type=int, default=10)

	args = parser.parse_args()

	if args.sessions < 1:
		print("Erreur : -sessions doit etre au moins 1.")
		return
	if args.grid_size < 5 or args.grid_size > 25:
		print("Erreur : -grid-size doit etre entre 5 et 25.")
		return
	if args.load is not None and not Path(args.load).is_file():
		print(f"Erreur : modele introuvable : {args.load}")
		return
	if args.dontlearn and args.save is not None:
		print("Erreur : -save n'a pas de sens avec -dontlearn.")
		return
	agent = Agent()
	if args.load is not None:
		agent.load(args.load)
	if args.dontlearn:
		agent.epsilon = 0.0
		agent.network.eval()
	if args.visual == "off":
		run_sessions(
			args.sessions,
			agent,
			learn=not args.dontlearn,
			save_path=args.save,
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
		if args.save is not None:
			agent.save(args.save)


if __name__ == "__main__":
	main()
