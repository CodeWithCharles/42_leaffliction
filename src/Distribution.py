"""Analyse de la distribution."""

import argparse
import sys
from pathlib import Path

from utils.dataset import count_images_per_class
from utils.plotting import plot_distribution


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Affiche la répartition des images par classe "
                    "sous forme de camembert et d'histogramme.",
    )
    parser.add_argument(
        "directory",
        help="répertoire à analyser (ex: ./data/images)",
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        help="ecrit la figure dans un fichier au lieu de l'afficher",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> None:
    root = Path(args.directory)
    counts = count_images_per_class(root)
    plot_distribution(counts, root.name, save_path=args.save)


def main() -> int:
    try:
        run(parse_args())
    except (OSError, ValueError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
