"""Split train/validation - AVANT toute augmentation.

Augmenter puis splitter fait fuir des quasi-doublons (une image et sa
version flippee) des deux cotes de la frontiere train/validation :
l'accuracy mesuree devient artificiellement haute et ne veut plus rien
dire. Ce module ne travaille donc que sur les images originales."""

import random
import shutil
from pathlib import Path

from utils.dataset import list_images

SPLIT_SEED = 42


def split_dataset(
    root: Path,
    val_ratio: float = 0.2,
) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    """Separe chaque classe de `root` en train/validation.

    Deterministe (SPLIT_SEED, independante de BALANCE_SEED) : le split ne
    doit jamais bouger d'un run a l'autre, sous peine d'invalider une
    comparaison entre deux entrainements. Au moins une image par classe
    part en validation."""
    classes = list_images(root)
    rng = random.Random(SPLIT_SEED)
    train: dict[str, list[Path]] = {}
    val: dict[str, list[Path]] = {}

    for name, paths in classes.items():
        shuffled = list(paths)
        rng.shuffle(shuffled)
        n_val = max(1, round(len(shuffled) * val_ratio))
        val[name] = sorted(shuffled[:n_val])
        train[name] = sorted(shuffled[n_val:])

    return train, val


def materialize(classes: dict[str, list[Path]], dst: Path) -> None:
    """Copie chaque classe telle quelle vers `dst/<classe>/`, sans
    augmentation. Sert a poser le split de validation sur le disque pour
    `image_dataset_from_directory`."""
    for name, paths in classes.items():
        class_dst = dst / name
        class_dst.mkdir(parents=True, exist_ok=True)
        for path in paths:
            shutil.copy2(path, class_dst / path.name)
