"""Lecture + ecriture d'images.
La seule couche au courant de la convention BGR d'OpenCV.
Le reste est en RGB car on est pas des animaux."""

from pathlib import Path

import cv2
import numpy as np


def read_image(path: Path) -> np.ndarray:
    """Charge une image et la renvoie en RGB."""
    img = cv2.imread(str(path))
    if img is None:
        raise OSError(f"image illisible: '{path}'")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def write_image(path: Path, img: np.ndarray) -> None:
    """Ecrit une image RGB.
    Cree les dossiers parents si necessaire."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR)):
        raise OSError(f"ecriture impossible: '{path}'")
