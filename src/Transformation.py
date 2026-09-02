"""Transformations PlantCV : extraction de caracteristiques d'une feuille."""

import argparse
import sys
from pathlib import Path

from utils.dataset import list_images
from utils.io_utils import read_image, write_image
from utils.plotting import plot_transformations
from utils.transform import TRANSFORMATIONS, build_mask, t_color_histogram

FLAGS = {
    "blur": "GaussianBlur",
    "mask": "Mask",
    "roi": "RoiObjects",
    "analyze": "AnalyzeObject",
    "pseudolandmarks": "Pseudolandmarks",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrait des caracteristiques d'une feuille via "
                    "PlantCV : image seule -> affichage, "
                    "-src/-dst -> traitement d'un dossier.",
        epilog="exemples:\n"
               "  %(prog)s ./data/images/Apple_healthy/image1.JPG\n"
               "  %(prog)s -src ./data/images/Apple_healthy "
               "-dst dst_directory --mask",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "image",
        nargs="?",
        help="image a transformer (mode affichage)",
    )
    parser.add_argument("-src", metavar="DIR", help="dossier source "
                        "(mode batch, avec -dst)")
    parser.add_argument("-dst", metavar="DIR", help="dossier destination "
                        "(mode batch, avec -src)")
    for flag, name in FLAGS.items():
        parser.add_argument(f"--{flag}", action="store_true",
                            help=f"transformation '{name}' uniquement")
    parser.add_argument("--histogram", action="store_true",
                        help="histogramme couleur uniquement")

    args = parser.parse_args()

    batch_mode = bool(args.src) or bool(args.dst)
    if bool(args.image) == batch_mode:
        parser.error("fournir soit une image, soit -src <dir> -dst <dir>")
    if batch_mode and not (args.src and args.dst):
        parser.error("-src et -dst sont requis ensemble")
    return args


def any_flag_set(args: argparse.Namespace) -> bool:
    return args.histogram or any(getattr(args, flag) for flag in FLAGS)


def selected_transformations(args: argparse.Namespace) -> list[str]:
    """Noms des transformations d'image demandees (hors histogramme).
    Aucun flag du tout => toutes."""
    if not any_flag_set(args):
        return list(TRANSFORMATIONS)
    return [name for flag, name in FLAGS.items() if getattr(args, flag)]


def transform_one(
    path: Path,
    names: list[str],
    with_histogram: bool,
) -> tuple:
    """Applique les transformations demandees a une image.
    Renvoie (original, {nom: image}, histogramme_ou_None)."""
    img = read_image(path)
    mask = build_mask(img)
    results = {name: TRANSFORMATIONS[name](img, mask) for name in names}
    histogram = t_color_histogram(img, mask) if with_histogram else None
    return img, results, histogram


def run_display(args: argparse.Namespace) -> None:
    """Mode image unique : affiche les transformations demandees."""
    path = Path(args.image)
    names = selected_transformations(args)
    with_histogram = args.histogram or not any_flag_set(args)
    img, results, histogram = transform_one(path, names, with_histogram)
    plot_transformations(img, results, histogram, path.name)


def run_batch(args: argparse.Namespace) -> None:
    """Mode dossier : reproduit l'arborescence source sous -dst, une
    image par transformation demandee. L'histogramme n'est pas
    sauvegarde en mode batch (pas de cible image evidente pour des
    donnees, pas une transformation d'image)."""
    src, dst = Path(args.src), Path(args.dst)
    names = selected_transformations(args)

    for class_name, paths in list_images(src).items():
        for path in paths:
            img = read_image(path)
            mask = build_mask(img)
            for name in names:
                out = TRANSFORMATIONS[name](img, mask)
                write_image(
                    dst / class_name / f"{path.stem}_{name}{path.suffix}",
                    out,
                )


def run(args: argparse.Namespace) -> None:
    if args.image:
        run_display(args)
    else:
        run_batch(args)


def main() -> int:
    try:
        run(parse_args())
    except (OSError, ValueError, NotADirectoryError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
