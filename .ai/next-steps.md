# Prochains petits pas

> Dans l'ordre. On ne passe à l'étape suivante que quand la précédente est validée.

## Immédiat — clôture Phase 1

- [ ] Créer `.flake8` avec `extend-exclude = .venv` (D-011)
- [ ] Newline finale dans `src/utils/plotting.py` (W292)
- [ ] `git add -A` — `dataset.py` et `plotting.py` n'étaient pas suivis
- [ ] `flake8 .` vert

## Phase 2 — `Augmentation.py`

Deux usages du même code, dans cet ordre :

- [ ] **2.1** `src/utils/augment.py` — signatures d'abord, 6 fonctions de même
      signature `(np.ndarray) -> np.ndarray`, plus le dict `AUGMENTATIONS`.
      Noms imposés (D-004) : `Flip, Rotate, Skew, Shear, Crop, Distortion`.
      **Contrainte clé** : toute sortie a la même taille que l'entrée.
- [ ] **2.2** Mode démo — 1 image en argument → 6 fichiers
      `<nom>_<Type>.JPG` + affichage des 7 vignettes
- [ ] **2.3** Mode équilibrage — `--balance <src> --dst augmented_directory`,
      cible = 1640, **énumération déterministe** des paires (D-006), `seed(42)`
- [ ] **2.4** Vérification : relancer `Distribution.py` sur `augmented_directory/`
      → les 8 barres doivent être strictement égales

### Critères de sortie Phase 2

- [ ] Les 6 fichiers produits, nommés exactement comme le sujet p.6
- [ ] `augmented_directory/` équilibré, prouvé via `Distribution.py`
- [ ] Deux exécutions successives → dataset identique (seed + `sorted`)
- [ ] `flake8 .` vert

## Plus tard

- **Phase 3** — `Transformation.py`, PlantCV **v4** (D-007)
- **Phase 4** — `train.py` + `predict.py`, avec la comparaison A/B de D-009
- **Phase 5** — zip, `signature.txt`, soutenance
- Question non tranchée : renommer `Train.py`/`Predict.py` en minuscules (D-010)
