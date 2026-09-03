# Partie 2 — `Augmentation.py`

Six augmentations d'une image (sujet IV.2, p.6), et équilibrage du dataset à
partir des mêmes fonctions. Historique de la décision et pièges connus :
`.ai/roadmap.md` (Phase 2) et `.ai/decisions.md` (D-004, D-006).

## Usage

```bash
# Une image -> 6 fichiers <nom>_<Type>.JPG dans le dossier courant
# + affichage des 7 vignettes (original + 6 augmentations)
python src/Augmentation.py "./data/images/Apple_rust/image (1).JPG"

# Un dataset déséquilibré -> équilibré vers la classe majoritaire,
# copié + complété sous augmented_directory/
python src/Augmentation.py --balance ./data/images --dst augmented_directory

python src/Augmentation.py -h
```

Règle : `image` **XOR** `--balance <dir>` — toute autre combinaison est
rejetée proprement par `argparse` (`parser.error`, code de sortie 2).
`--dst` est optionnel en mode équilibrage (défaut : `augmented_directory`).

## Les 6 augmentations (`utils/augment.py`)

| # | Nom (`AUGMENTATIONS`) | Technique |
|---|---|---|
| 1 | `Flip` | miroir horizontal |
| 2 | `Rotate` | rotation d'angle fixe (25°), bord répliqué |
| 3 | `Skew` | transformation perspective (bascule le plan) |
| 4 | `Shear` | cisaillement affine horizontal |
| 5 | `Crop` | recadrage centré (~80 %) puis retour à la taille d'origine |
| 6 | `Distortion` | distorsion barrel (éloignement radial du centre) |

Contrainte commune à toutes : signature homogène `(np.ndarray) -> np.ndarray`
et **même taille en sortie qu'en entrée** — c'est ce qui permet de les mettre
dans un dict et de les appliquer génériquement, en mode démo comme en mode
équilibrage.

## Mode équilibrage (`Augmentation.py::balance_dataset`)

1. `list_images(src)` regroupe les images par classe (réutilise la Phase 1,
   `utils/dataset.py`) ; la cible est l'effectif de la **classe majoritaire**.
2. Pour chaque classe : les originaux sont copiés tels quels
   (`shutil.copy2`, pas de réencodage) vers `dst/<classe>/`.
3. Si la classe est déficitaire (`deficit = cible - effectif > 0`) : toutes
   les paires `(image, augmentation)` possibles sont énumérées
   (`effectif × 6` paires), mélangées avec `random.seed(42)`, et les
   `deficit` premières sont retenues et écrites sous
   `<original>_<Type>_<index>.JPG`.
4. La classe majoritaire n'est **jamais** augmentée (`deficit <= 0` → rien
   de plus) — sinon l'équilibrage ne converge jamais.

**Pourquoi une énumération déterministe plutôt qu'un tirage aléatoire**
(D-006) : sur le vrai dataset, `Apple_rust` (275 originaux) doit produire
1365 images sur 1650 paires possibles, soit 83 % de l'espace disponible — un
tirage avec remise aurait un taux de collision élevé et pourrait ne jamais
converger. Énumérer puis mélanger garantit zéro doublon en un seul passage,
et `random.seed(42)` rend le résultat reproductible d'une exécution à
l'autre — nécessaire puisque `signature.txt` (Phase 5) est le sha1 du
contenu exact du zip livré.

Si une classe demande plus d'images que de paires disponibles
(`deficit > effectif × 6`), `balance_dataset` lève un `ValueError` explicite
plutôt que de produire des doublons silencieusement — situation qui ne se
produit pas sur le dataset connu mais qui doit échouer proprement sur un
autre.

## Limites connues / à valider

- Testé sur un dataset **synthétique** (classes déséquilibrées générées pour
  l'occasion) : comptes strictement égaux en sortie, deux exécutions
  successives produisent des fichiers identiques (comparaison de hash), et
  le cas d'erreur (déficit trop grand) échoue proprement. **Pas encore
  vérifié sur le vrai dataset**, absent de cette machine au moment de
  l'implémentation.
- Reste à faire une fois `data/images/` disponible : lancer
  `python src/Augmentation.py --balance data/images --dst
  augmented_directory` puis `python src/Distribution.py
  augmented_directory` pour confirmer que les 8 classes ont des effectifs
  strictement égaux (critère de sortie Phase 2, cf. `.ai/next-steps.md`).
