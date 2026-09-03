"""Extraction de caracteristiques via PlantCV (v4.11.3).

Une fonction par transformation, signature homogene (img, mask) -> image,
sauf `build_mask` (le point d'entree du pipeline) et `t_color_histogram`
(produit des donnees a tracer, pas une image).
"""

from typing import Callable

import cv2
import numpy as np
from plantcv import plantcv as pcv

# Mode batch : pas de fichiers de debug parasites (cf. .ai/roadmap.md,
# Phase 3, "Pieges").
pcv.params.debug = None

FILL_SIZE = 200
CLOSING_KSIZE = 5

# Les 9 canaux que `pcv.analyze.color(..., colorspaces="all")` enregistre
# dans `pcv.outputs.observations`, dans l'ordre de la legende du sujet
# (Figure IV.7).
COLOR_CHANNELS = (
    "blue", "blue-yellow", "green", "green-magenta",
    "hue", "lightness", "red", "saturation", "value",
)


def build_mask(img: np.ndarray) -> np.ndarray:
    """Construit un masque binaire de la feuille.

    Pipeline : canal 'a' de LAB (vert<->magenta, le plus discriminant
    feuille/fond gris de ce dataset) -> seuillage Otsu -> suppression du
    bruit -> fermeture des petits trous.
    """
    gray = pcv.rgb2gray_lab(rgb_img=img, channel="a")
    binary = pcv.threshold.otsu(gray_img=gray, object_type="dark")
    filled = pcv.fill(bin_img=binary, size=FILL_SIZE)
    kernel = np.ones((CLOSING_KSIZE, CLOSING_KSIZE), dtype=np.uint8)
    return cv2.morphologyEx(filled, cv2.MORPH_CLOSE, kernel)


def t_gaussian_blur(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Flou gaussien applique au masque (met en evidence les contours)."""
    blurred = pcv.gaussian_blur(img=mask, ksize=(5, 5))
    return cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)


def t_masked(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Image d'origine avec le fond efface (mis en blanc)."""
    return pcv.apply_mask(img=img, mask=mask, mask_color="white")


def t_roi_objects(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Objets retenus dans une ROI (rectangle plein cadre) : masque en
    vert, bordure de la ROI en bleu."""
    height, width = mask.shape[:2]
    roi = pcv.roi.rectangle(img=img, x=0, y=0, h=height, w=width)
    filtered = pcv.roi.filter(mask=mask, roi=roi, roi_type="partial")

    result = img.copy()
    result[filtered > 0] = (0, 255, 0)
    cv2.rectangle(result, (0, 0), (width - 1, height - 1), (0, 0, 255), 5)
    return result


def t_analyze_object(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Contour et axe principal de l'objet detecte."""
    return pcv.analyze.size(img=img.copy(), labeled_mask=mask)


def t_pseudolandmarks(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Points de repere le long des axes x et y de la feuille."""
    top_x, bottom_x, center_x = pcv.homology.x_axis_pseudolandmarks(
        img=img, mask=mask)
    top_y, bottom_y, center_y = pcv.homology.y_axis_pseudolandmarks(
        img=img, mask=mask)

    result = img.copy()
    groups = (
        (top_x, (255, 0, 0)), (bottom_x, (255, 0, 255)),
        (center_x, (0, 0, 255)),
        (top_y, (0, 165, 255)), (bottom_y, (0, 255, 0)),
        (center_y, (255, 255, 0)),
    )
    for points, color in groups:
        for point in points:
            if isinstance(point, str):
                continue
            x, y = int(point[0][0]), int(point[0][1])
            cv2.circle(result, (x, y), 3, color, -1)
    return result


def t_color_histogram(
    img: np.ndarray,
    mask: np.ndarray,
) -> dict[str, list[float]]:
    """Proportion de pixels (%) par intensite, une serie par canal.

    Renvoie un dict {nom_du_canal: liste_de_256_valeurs}, pret a etre
    trace (cf. `plotting.plot_transformations`).
    """
    pcv.outputs.clear()
    pcv.analyze.color(rgb_img=img, labeled_mask=mask, colorspaces="all")
    # `analyze.color` cle ses observations sur "<sample_label>_<n_objet>"
    # (ex. "default_1") plutot que sur `sample_label` seul.
    observations = next(iter(pcv.outputs.observations.values()))
    return {
        name: observations[f"{name}_frequencies"]["value"]
        for name in COLOR_CHANNELS
    }


TRANSFORMATIONS: dict[str, Callable[[np.ndarray, np.ndarray], np.ndarray]] = {
    "GaussianBlur": t_gaussian_blur,
    "Mask": t_masked,
    "RoiObjects": t_roi_objects,
    "AnalyzeObject": t_analyze_object,
    "Pseudolandmarks": t_pseudolandmarks,
}
