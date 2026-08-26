"""6 augmentations d'une image."""

import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Affiche la répartition des images par classe "
                    "sous forme de camembert et d'histogramme.",
    )
    parser.add_argument(
        "directory",
        help="répertoire à analyser (ex: ./data/images)",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> None:
    raise NotImplementedError("Phase 1")


def main() -> int:
    try:
        run(parse_args())
    except NotImplementedError as exc:
        print(f"Non implémenté: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
