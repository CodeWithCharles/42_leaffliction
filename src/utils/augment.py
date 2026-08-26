"""Six augmentations deterministes, à taille d'image constante."""

from typing import Callable

import cv2
import numpy as np


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
