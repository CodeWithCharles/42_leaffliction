"""Helpers matplotlib pour la visualisation du dataset."""

import os
import matplotlib
import matplotlib.pyplot as plt


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
