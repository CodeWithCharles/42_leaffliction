"""Parcours et comptage d'un dataset d'images organisé par répertoires."""

from pathlib import Path

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png"})


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def list_images(root: Path) -> dict[str, list[Path]]:
    """Parcourt `root` et regroupe les images par classes.

    La classe d'une image est le nom de son repertoire parent direct.
    Le dict et chaque liste de path sont tries.
    """
    if not root.is_dir():
        raise NotADirectoryError(f"'{root}' n'est pas un repertoire")

    groups: dict[str, list[Path]] = {}
    for path in sorted(root.rglob("*")):
        if is_image_file(path):
            groups.setdefault(path.parent.name, []).append(path)

    if not groups:
        raise ValueError(f"aucune image trouvee dans '{root}'")

    return {name: groups[name] for name in sorted(groups)}


def count_images_per_class(root: Path) -> dict[str, int]:
    return {name: len(paths) for name, paths in list_images(root).items()}
