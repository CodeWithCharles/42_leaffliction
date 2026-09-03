"""Entraine un CNN a reconnaitre la maladie d'une feuille et sauvegarde
les apprentissages (modele + classes + config + images augmentees) dans
un zip autosuffisant, consomme par Predict.py."""

import argparse
import shutil
import sys
from pathlib import Path

import tensorflow as tf
from tensorflow import keras

from utils.augment import balance_classes
from utils.data_prep import split_dataset, materialize
from utils.learnings import save_learnings
from utils.model import IMG_SIZE, build_cnn

VAL_MIN_IMAGES = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entraine un CNN sur un dataset organise en "
                    "sous-repertoires par classe, et sauvegarde le "
                    "resultat dans un zip.",
        epilog="exemple:\n"
               "  %(prog)s ./data/images --dst learnings.zip",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "directory",
        help="dataset a utiliser (ex: ./data/images)",
    )
    parser.add_argument(
        "--dst",
        metavar="ZIP",
        default="learnings.zip",
        help="zip de sortie (defaut: %(default)s)",
    )
    parser.add_argument(
        "--work-dir",
        metavar="DIR",
        default="train_workdir",
        help="repertoire de travail pour le split et l'augmentation "
             "(defaut: %(default)s)",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2,
        help="proportion d'images originales reservees a la validation "
             "(defaut: %(default)s)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="nombre maximal d'epoques, EarlyStopping peut arreter "
             "avant (defaut: %(default)s)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="taille de batch (defaut: %(default)s)",
    )
    return parser.parse_args()


def prepare_data(
    directory: Path,
    work_dir: Path,
    val_ratio: float,
) -> tuple[Path, Path, list[str]]:
    """Split train/val sur les originaux, augmente UNIQUEMENT le train,
    materialise la validation telle quelle. Renvoie les deux repertoires
    et la liste des classes (ordre alphabetique fige)."""
    train_paths, val_paths = split_dataset(directory, val_ratio)

    n_val = sum(len(paths) for paths in val_paths.values())
    if n_val < VAL_MIN_IMAGES:
        raise ValueError(
            f"seulement {n_val} images de validation ({VAL_MIN_IMAGES} "
            "minimum exiges) - augmenter --val-ratio ou le dataset"
        )

    if work_dir.exists():
        shutil.rmtree(work_dir)
    train_dir = work_dir / "augmented_directory"
    val_dir = work_dir / "validation"

    balance_classes(train_paths, train_dir)
    materialize(val_paths, val_dir)

    return train_dir, val_dir, sorted(train_paths)


def load_dataset(
    directory: Path,
    class_names: list[str],
    batch_size: int,
    shuffle: bool,
) -> tf.data.Dataset:
    """Charge un repertoire en dataset TF, redimensionne, normalise en
    [0, 1] - le meme pretraitement que `utils.learnings.preprocess_image`
    applique a l'inference (cf. sa docstring)."""
    dataset = keras.utils.image_dataset_from_directory(
        directory,
        labels="inferred",
        label_mode="int",
        class_names=class_names,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=42,
    )
    return dataset.map(lambda x, y: (x / 255.0, y))


def run(args: argparse.Namespace) -> None:
    directory = Path(args.directory)
    work_dir = Path(args.work_dir)

    train_dir, val_dir, class_names = prepare_data(
        directory, work_dir, args.val_ratio)

    train_ds = load_dataset(
        train_dir, class_names, args.batch_size, shuffle=True)
    val_ds = load_dataset(
        val_dir, class_names, args.batch_size, shuffle=False)

    model = build_cnn((*IMG_SIZE, 3), len(class_names))
    callbacks = [
        keras.callbacks.EarlyStopping(
            patience=5, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(
            str(work_dir / "best.keras"), save_best_only=True),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
        shuffle=False,  # deja fait par image_dataset_from_directory
    )

    val_accuracy = history.history["val_accuracy"][-1]
    print(f"accuracy de validation (derniere epoque): {val_accuracy:.4f}")

    config = {
        "img_size": list(IMG_SIZE),
        "val_ratio": args.val_ratio,
        "seed": 42,
        "preprocessing": "rgb_resized_normalized",
    }
    save_learnings(model, class_names, config, train_dir, Path(args.dst))
    print(f"apprentissages sauvegardes dans '{args.dst}'")


def main() -> int:
    try:
        run(parse_args())
    except (OSError, ValueError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
