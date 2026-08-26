"""6 augmentations d'une image ou equilibre un dataset"""

import argparse
import sys
from pathlib import Path

import numpy as np

from utils.augment import AUGMENTATIONS
from utils.io_utils import read_image, write_image
from utils.plotting import plot_augmentations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Applqiue six augmentations a une image ou equilibre "
                    "un dataset en generant les images manquantes.",
        epilog="exemples:\n"
               "  %(prog)s ./data/images/Apple_rust/'image (1).JPG'\n"
               "  %(prog)s --balance ./data/images --dst augmented_directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "image",
        nargs="?",
        help="image a augmenter (mode demo)",
    )
    parser.add_argument(
        "--balance",
        metavar="SRC",
        help="repertoire du dataset a equilibrer (mode equilibrage)",
    )
    parser.add_argument(
        "--dst",
        metavar="DST",
        default="augmented_directory",
        help="destination du mode equilibrage (defaut: %(default)s)",
    )
    args = parser.parse_args()
    if bool(args.image) == bool(args.balance):
        parser.error("fournir soit une image, soit --balance <dir>")
    return args


def augment_image(
    path: Path,
    dst_dir: Path,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Applique les six augmentations et ecrit les fichiers resultants.
    Renvoie l'image d'origine et le dict des versions augmentees."""
    img = read_image(path)
    results = {name: fn(img) for name, fn in AUGMENTATIONS.items()}
    for name, out in results.items():
        write_image(dst_dir / f"{path.stem}_{name}{path.suffix}", out)
    return img, results


def run(args: argparse.Namespace) -> None:
    """Aiguille vers le mode demo ou le mode equilibrage."""
    if args.balance:
        raise NotImplementedError("mode equilibrage - etape 2.3")

    path = Path(args.image)
    original, augmented = augment_image(path, Path.cwd())
    plot_augmentations(original, augmented, path.name)


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
