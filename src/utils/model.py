"""Architecture du CNN. Entraine from scratch (pas de transfer learning,
cf. .ai/decisions.md) - l'objectif du sujet est de comprendre chaque
couche, pas d'obtenir le meilleur score."""

from tensorflow import keras
from tensorflow.keras import layers

IMG_SIZE = (128, 128)


def build_cnn(
    input_shape: tuple[int, int, int], n_classes: int
) -> keras.Model:
    """Trois blocs conv/batchnorm/pool qui montent en profondeur (32 -> 64
    -> 128 filtres) pendant que le pooling reduit la resolution spatiale,
    suivis d'une tete dense avec dropout pour limiter l'overfitting.

    - Conv2D : apprend des filtres locaux (contours, textures, taches de
      maladie) : chaque couche combine les motifs de la precedente en
      motifs plus complexes.
    - BatchNorm : renormalise les activations entre les couches, stabilise
      et accelere l'entrainement.
    - MaxPool : sous-echantillonne (garde le maximum local), reduit le
      cout de calcul et rend la detection tolerante a une petite
      translation du motif.
    - Dropout : eteint aleatoirement des neurones a l'entrainement,
      empeche le reseau de se reposer sur un seul chemin de neurones
      (overfitting).
    - Softmax final : transforme les logits en probabilites qui somment a
      1 sur les `n_classes`.
    """
    model = keras.Sequential([
        keras.Input(shape=input_shape),

        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),

        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),

        layers.Conv2D(128, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),

        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(n_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
