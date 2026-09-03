"""Helpers matplotlib pour la visualisation du dataset."""

import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix as sk_confusion_matrix


# Si pas de serveur X (VM, ou SSH), on bascule sur un
# backend hors ecran.
if not os.environ.get("DISPLAY"):
    plt.switch_backend("Agg")


def build_palette(labels: list[str]) -> list[tuple]:
    cmap = matplotlib.colormaps["tab10"]
    return [cmap(i % cmap.N) for i in range(len(labels))]


def plot_distribution(
    counts: dict[str, int],
    title: str,
    save_path: str | None = None,
) -> None:
    """Camembert et histo de la repartition.
    Les couleurs sont partagees entre les graphs.
    save_path si on veut les figures sur le disque."""
    labels = list(counts)
    values = [counts[name] for name in labels]
    colors = build_palette(labels)

    fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle(f"{title} class distribution", fontsize=16)

    ax_pie.pie(values, labels=labels, colors=colors,
               autopct="%1.1f%%", startangle=90)
    ax_pie.axis("equal")

    ax_bar.bar(labels, values, color=colors)
    ax_bar.set_ylabel("nombre d'images")
    ax_bar.set_xticks(range(len(labels)))
    ax_bar.set_xticklabels(labels, rotation=45, ha="right")

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=100)
        plt.close(fig)
    else:
        plt.show()


def plot_augmentations(
    original: np.ndarray,
    augmented: dict[str, np.ndarray],
    title: str,
    save_path: str | None = None,
) -> None:
    """Affiche l'original et ses augmenations sur le meme plot."""
    total = len(augmented) + 1
    fig, axes = plt.subplots(1, total, figsize=(3.0 * total, 3.6))
    fig.suptitle(title, fontsize=14)

    axes[0].imshow(original)
    axes[0].set_title("Original")
    axes[0].axis("off")

    for ax, (name, img) in zip(axes[1:], augmented.items()):
        ax.imshow(img)
        ax.set_title(name)
        ax.axis("off")

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=90)
        plt.close(fig)
    else:
        plt.show()


def plot_prediction(
    original: np.ndarray,
    preprocessed: np.ndarray,
    predicted_class: str,
    confidence: float,
    save_path: str | None = None,
) -> None:
    """Affiche l'image originale et sa version pretraitee (celle
    consommee par le modele), avec la classe predite en titre."""
    fig, (ax_orig, ax_prep) = plt.subplots(1, 2, figsize=(8, 4.5))
    fig.suptitle(
        f"{predicted_class}  ({confidence:.1%})", fontsize=14)

    ax_orig.imshow(original)
    ax_orig.set_title("Original")
    ax_orig.axis("off")

    ax_prep.imshow(preprocessed)
    ax_prep.set_title("Pretraitee (entree du modele)")
    ax_prep.axis("off")

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=100)
        plt.close(fig)
    else:
        plt.show()


def plot_confusion_matrix(
    y_true: list[int],
    y_pred: list[int],
    class_names: list[str],
    save_path: str | None = None,
) -> None:
    """Matrice de confusion normalisee par ligne (rappel par classe)."""
    matrix = sk_confusion_matrix(
        y_true, y_pred, labels=range(len(class_names)))
    normalized = matrix / matrix.sum(axis=1, keepdims=True).clip(min=1)

    fig, ax = plt.subplots(figsize=(1.0 * len(class_names) + 2, 8))
    im = ax.imshow(normalized, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("predit")
    ax.set_ylabel("reel")
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            ax.text(j, i, matrix[i, j], ha="center", va="center",
                    color="white" if normalized[i, j] > 0.5 else "black")
    fig.colorbar(im, ax=ax, label="rappel")
    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=100)
        plt.close(fig)
    else:
        plt.show()


def plot_transformations(
    original: np.ndarray,
    images: dict[str, np.ndarray],
    histogram: dict[str, list[float]] | None,
    title: str,
    save_path: str | None = None,
) -> None:
    """Affiche l'original, les images transformees, et l'histogramme
    couleur (si fourni) sur une meme figure."""
    tiles = {"Original": original, **images}
    n_cols = min(4, len(tiles))
    n_rows = -(-len(tiles) // n_cols)  # ceil
    extra_row = 1 if histogram else 0

    fig = plt.figure(figsize=(3.2 * n_cols, 3.6 * n_rows + 3.5 * extra_row))
    fig.suptitle(title, fontsize=14)
    grid = fig.add_gridspec(n_rows + extra_row, n_cols)

    for i, (name, img) in enumerate(tiles.items()):
        ax = fig.add_subplot(grid[i // n_cols, i % n_cols])
        ax.imshow(img)
        ax.set_title(name)
        ax.axis("off")

    if histogram:
        ax_hist = fig.add_subplot(grid[n_rows, :])
        colors = build_palette(list(histogram))
        for (channel, values), color in zip(histogram.items(), colors):
            ax_hist.plot(values, label=channel, color=color)
        ax_hist.set_xlabel("pixel intensity")
        ax_hist.set_ylabel("proportion of pixels (%)")
        ax_hist.legend(fontsize=8)

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=90)
        plt.close(fig)
    else:
        plt.show()
