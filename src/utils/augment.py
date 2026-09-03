"""Six augmentations deterministes, à taille d'image constante."""

import random
import shutil
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from utils.io_utils import read_image, write_image


# Parametres fixes
ROTATION_ANGLE = 25.0
SHEAR_FACTOR = 0.25
SKEW_FACTOR = 0.20
CROP_RATIO = 0.80
DISTORTION_STRENGTH = 0.25


def flip(img: np.ndarray) -> np.ndarray:
    """Miroir horizontal."""
    return cv2.flip(img, 1)


def rotate(img: np.ndarray) -> np.ndarray:
    """Rotation d'un angle fixe, coins remplis par replication du bord."""
    height, width = img.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, ROTATION_ANGLE, 1.0)
    return cv2.warpAffine(img, matrix, (width, height),
                          borderMode=cv2.BORDER_REPLICATE)


def skew(img: np.ndarray) -> np.ndarray:
    """Transformation perspective : bascule le plan de l'image."""
    height, width = img.shape[:2]
    offset = width * SKEW_FACTOR
    source = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    target = np.float32([[offset, 0], [width - offset, 0],
                         [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(source, target)
    return cv2.warpPerspective(img, matrix, (width, height),
                               borderMode=cv2.BORDER_REPLICATE)


def shear(img: np.ndarray) -> np.ndarray:
    """Cisaillement affine horizontal."""
    height, width = img.shape[:2]
    matrix = np.float32([[1.0, SHEAR_FACTOR, -SHEAR_FACTOR * height / 2],
                        [0.0, 1.0, 0.0]])
    return cv2.warpAffine(img, matrix, (width, height),
                          borderMode=cv2.BORDER_REPLICATE)


def crop(img: np.ndarray) -> np.ndarray:
    """Recadrage centré (~80 %) puis retour à la taille d'origine."""
    height, width = img.shape[:2]
    new_h, new_w = int(height * CROP_RATIO), int(width * CROP_RATIO)
    top, left = (height - new_h) // 2, (width - new_w) // 2
    cropped = img[top:top + new_h, left:left + new_w]
    return cv2.resize(cropped, (width, height),
                      interpolation=cv2.INTER_LINEAR)


def distortion(img: np.ndarray) -> np.ndarray:
    """Distorsion barrel : éloigne les pixels du centre proportionnellement
    au carré de leur distance."""
    height, width = img.shape[:2]
    ys, xs = np.indices((height, width), dtype=np.float32)
    norm_x = (xs - width / 2) / (width / 2)
    norm_y = (ys - height / 2) / (height / 2)
    radius_sq = norm_x ** 2 + norm_y ** 2
    factor = 1.0 + DISTORTION_STRENGTH * radius_sq
    map_x = norm_x * factor * (width / 2) + width / 2
    map_y = norm_y * factor * (height / 2) + height / 2
    return cv2.remap(img, map_x, map_y,
                     interpolation=cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REPLICATE)


AUGMENTATIONS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "Flip": flip,
    "Rotate": rotate,
    "Skew": skew,
    "Shear": shear,
    "Crop": crop,
    "Distortion": distortion,
}

BALANCE_SEED = 42


def balance_classes(classes: dict[str, list[Path]], dst: Path) -> None:
    """Copie chaque classe vers `dst`, puis genere des images augmentees
    pour amener chaque classe deficitaire au niveau de la classe
    majoritaire (jamais l'inverse : la majoritaire n'est jamais
    augmentee, sinon on ne converge jamais).

    Selection deterministe : toutes les paires (image, augmentation)
    possibles sont enumerees, melangees avec une graine fixe, et les
    premieres sont retenues - jamais de tirage avec remise (cf.
    .ai/decisions.md, D-006). Utilisee par `Augmentation.py --balance`
    et par `Train.py` (uniquement sur le split train, jamais sur la
    validation - cf. .ai/decisions.md, split avant augmentation)."""
    target = max(len(paths) for paths in classes.values())
    random.seed(BALANCE_SEED)

    for class_name, paths in classes.items():
        class_dst = dst / class_name
        class_dst.mkdir(parents=True, exist_ok=True)
        for path in paths:
            shutil.copy2(path, class_dst / path.name)

        deficit = target - len(paths)
        if deficit <= 0:
            continue

        pairs = [(path, name) for path in paths for name in AUGMENTATIONS]
        if deficit > len(pairs):
            raise ValueError(
                f"'{class_name}': {deficit} images a generer pour "
                f"seulement {len(pairs)} paires (image, augmentation) "
                "possibles"
            )
        random.shuffle(pairs)

        for index, (path, aug_name) in enumerate(pairs[:deficit]):
            img = read_image(path)
            out = AUGMENTATIONS[aug_name](img)
            out_name = f"{path.stem}_{aug_name}_{index}{path.suffix}"
            write_image(class_dst / out_name, out)
