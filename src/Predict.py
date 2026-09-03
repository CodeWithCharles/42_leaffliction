"""Predit la maladie d'une feuille a partir d'un modele entraine, ou
evalue ce modele sur un repertoire de validation (accuracy + matrice de
confusion)."""

import argparse
import sys
from pathlib import Path

import numpy as np

from utils.dataset import list_images
from utils.io_utils import read_image
from utils.learnings import load_learnings, preprocess_image
from utils.plotting import plot_confusion_matrix, plot_prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predit la classe d'une image, ou evalue le modele "
                    "sur un repertoire de validation.",
        epilog="exemples:\n"
               "  %(prog)s ./data/images/Apple_rust/'image (1).JPG'\n"
               "  %(prog)s --evaluate validation_directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "image",
        nargs="?",
        help="image a classifier (mode prediction)",
    )
    parser.add_argument(
        "--evaluate",
        metavar="DIR",
        help="repertoire organise par classe a evaluer (mode evaluation)",
    )
    parser.add_argument(
        "--model",
        metavar="ZIP",
        default="learnings.zip",
        help="zip d'apprentissages produit par Train.py "
             "(defaut: %(default)s)",
    )
    args = parser.parse_args()
    if bool(args.image) == bool(args.evaluate):
        parser.error("fournir soit une image, soit --evaluate <dir>")
    return args


def predict_image(
    model,
    class_names: list[str],
    config: dict,
    img: np.ndarray,
) -> tuple[str, float, np.ndarray]:
    """Applique exactement le pretraitement de l'entrainement, predit,
    renvoie la classe, la confiance et l'image pretraitee (pour
    l'affichage)."""
    prepped = preprocess_image(img, config)
    probs = model.predict(prepped[np.newaxis, ...], verbose=0)[0]
    idx = int(np.argmax(probs))
    return class_names[idx], float(probs[idx]), prepped


def evaluate(
    model,
    class_names: list[str],
    config: dict,
    directory: Path,
) -> None:
    """Parcourt `directory` (une classe = un sous-dossier, cf.
    `utils.dataset`), predit chaque image, affiche l'accuracy globale et
    la matrice de confusion."""
    classes = list_images(directory)
    unknown = set(classes) - set(class_names)
    if unknown:
        raise ValueError(
            f"classes absentes du modele: {sorted(unknown)}")

    y_true: list[int] = []
    y_pred: list[int] = []
    for class_name, paths in classes.items():
        true_idx = class_names.index(class_name)
        for path in paths:
            predicted, _, _ = predict_image(
                model, class_names, config, read_image(path))
            y_true.append(true_idx)
            y_pred.append(class_names.index(predicted))

    accuracy = np.mean(np.array(y_true) == np.array(y_pred))
    total = len(y_true)
    print(f"accuracy: {accuracy:.4f} ({total} images)")
    plot_confusion_matrix(y_true, y_pred, class_names)


def run(args: argparse.Namespace) -> None:
    model, class_names, config = load_learnings(Path(args.model))

    if args.evaluate:
        evaluate(model, class_names, config, Path(args.evaluate))
        return

    path = Path(args.image)
    original = read_image(path)
    predicted, confidence, prepped = predict_image(
        model, class_names, config, original)
    print(f"classe predite: {predicted} (confiance: {confidence:.1%})")
    plot_prediction(original, prepped, predicted, confidence)


def main() -> int:
    try:
        run(parse_args())
    except (OSError, ValueError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
