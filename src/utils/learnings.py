"""Format du zip livre par Train.py et consomme par Predict.py.

Les deux scripts DOIVENT partager cette couche : un pretraitement ou un
ordre de classes qui diverge entre train et predict fait s'effondrer
l'accuracy a l'inference sans aucune erreur visible (cf. .ai/roadmap.md,
pieges Phase 4)."""

import json
import shutil
import zipfile
from pathlib import Path

import cv2
import numpy as np
from tensorflow import keras

MODEL_FILENAME = "model.keras"
CLASS_NAMES_FILENAME = "class_names.json"
CONFIG_FILENAME = "config.json"
AUGMENTED_DIRNAME = "augmented_directory"


def preprocess_image(img: np.ndarray, config: dict) -> np.ndarray:
    """RGB brut, redimensionne, normalise en [0, 1] - exactement le
    pretraitement applique aux images d'entrainement (choix A du
    roadmap : pas de masque, le CNN apprend ses features seul)."""
    width, height = config["img_size"]
    resized = cv2.resize(
        img, (width, height), interpolation=cv2.INTER_LINEAR)
    return resized.astype(np.float32) / 255.0


def save_learnings(
    model: keras.Model,
    class_names: list[str],
    config: dict,
    augmented_dir: Path,
    dst_zip: Path,
) -> None:
    """Empaquette le modele, l'ordre des classes, la config de
    pretraitement et les images augmentees dans un zip autosuffisant."""
    staging = dst_zip.parent / f".{dst_zip.stem}_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    model.save(staging / MODEL_FILENAME)
    (staging / CLASS_NAMES_FILENAME).write_text(
        json.dumps(class_names, indent=2))
    (staging / CONFIG_FILENAME).write_text(json.dumps(config, indent=2))
    shutil.copytree(augmented_dir, staging / AUGMENTED_DIRNAME)

    dst_zip.parent.mkdir(parents=True, exist_ok=True)
    if dst_zip.exists():
        dst_zip.unlink()
    with zipfile.ZipFile(dst_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging))

    shutil.rmtree(staging)


def load_learnings(
    zip_path: Path,
) -> tuple[keras.Model, list[str], dict]:
    """Charge model.keras + class_names.json + config.json depuis le zip
    produit par `save_learnings`."""
    extract_dir = zip_path.parent / f".{zip_path.stem}_extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(extract_dir)

    try:
        model = keras.models.load_model(extract_dir / MODEL_FILENAME)
        class_names = json.loads(
            (extract_dir / CLASS_NAMES_FILENAME).read_text())
        config = json.loads((extract_dir / CONFIG_FILENAME).read_text())
    finally:
        shutil.rmtree(extract_dir)

    return model, class_names, config
