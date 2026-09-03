# Prochains petits pas

> Dans l'ordre. On ne passe à l'étape suivante que quand la précédente est validée.

## Immédiat — clôture Phase 1

- [ ] Créer `.flake8` avec `extend-exclude = .venv` (D-011)
- [ ] Newline finale dans `src/utils/plotting.py` (W292)
- [ ] `git add -A` — `dataset.py` et `plotting.py` n'étaient pas suivis
- [ ] `flake8 .` vert

## Phase 2 — `Augmentation.py`

Deux usages du même code, dans cet ordre :

- [x] **2.1** `src/utils/augment.py` — signatures d'abord, 6 fonctions de même
      signature `(np.ndarray) -> np.ndarray`, plus le dict `AUGMENTATIONS`.
      Noms imposés (D-004) : `Flip, Rotate, Skew, Shear, Crop, Distortion`.
      **Contrainte clé** : toute sortie a la même taille que l'entrée.
- [x] **2.2** Mode démo — 1 image en argument → 6 fichiers
      `<nom>_<Type>.JPG` + affichage des 7 vignettes
- [x] **2.3** Mode équilibrage — `--balance <src> --dst augmented_directory`,
      cible = classe majoritaire, **énumération déterministe** des paires
      (D-006), `seed(42)` — validé sur dataset synthétique cette session
- [ ] **2.4** Vérification : relancer `Distribution.py` sur `augmented_directory/`
      → les 8 barres doivent être strictement égales — **à faire sur le vrai
      dataset**, absent de la machine durant l'implémentation

### Critères de sortie Phase 2

- [x] Les 6 fichiers produits, nommés exactement comme le sujet p.6
- [ ] `augmented_directory/` équilibré, prouvé via `Distribution.py` sur le
      **vrai** dataset (prouvé sur synthétique uniquement pour l'instant)
- [x] Deux exécutions successives → dataset identique (seed + `sorted`),
      vérifié par comparaison de hash sur un dataset synthétique
- [x] `flake8 .` vert

## Immédiat — clôture Phase 3 (implémentée cette session)

- [ ] Valider visuellement le masque (`build_mask`, canal `a` LAB + Otsu) sur
      3-4 classes d'Apple **et** de Grape une fois `data/images/` disponible
      — non testé sur le vrai dataset, seulement sur une image synthétique
      (cf. `docs/part3-transformation.md`, section "Limites connues").
- [ ] Lancer le mode batch sur ~50 images réelles (pas de crash, pas de
      fuite mémoire) — testé seulement sur 2 images synthétiques.

## Immédiat — avant tout entraînement réel (bloquant Phase 4)

- [ ] **Dédupliquer `data/images/`** : chaque classe est actuellement en 2×
      (mêmes contenus, noms différents — cf. D-014, `.ai/state.md`). Lancer
      `Train.py` sans nettoyer risque une fuite de données entre train et
      validation.

## Immédiat — clôture Phase 4 (implémentée cette session)

- [ ] Lancer `python src/Train.py ./data/images --dst learnings.zip` sur le
      vrai dataset (dédupliqué) et observer accuracy/temps d'entraînement
      réels — seulement validé sur un dataset synthétique minuscule (3
      classes, 2 époques) cette session.
- [ ] `python src/Predict.py --evaluate <validation_directory>` sur le vrai
      set de validation → confirmer accuracy > 90 % sur ≥ 100 images
      (critère de sortie du sujet).
- [ ] `python src/Predict.py <image jamais vue>` → vérifier l'affichage
      côte à côte original/prétraitée et la classe annoncée.
- [ ] Décompresser `learnings.zip` ailleurs et relancer `Predict.py` dessus
      → confirmer que le zip est bien autosuffisant.
- [ ] Comparaison A/B (RGB brut vs image masquée Phase 3) de D-009, si
      l'accuracy plafonne sous 90 % avec l'option A actuelle.

### Critères de sortie Phase 4

- [x] `flake8 .` vert
- [x] Split train/validation sur les originaux, avant augmentation —
      démontrable en lisant `utils/data_prep.py` + `Train.py::prepare_data`
- [x] `class_names.json` sauvegardé et rechargé — ordre partagé entre train
      et predict
- [ ] Validation ≥ 100 images, accuracy > 90 %, matrice de confusion
      affichée — **à mesurer sur le vrai dataset**
- [ ] `predict.py` fonctionne sur une image jamais vue à l'entraînement —
      à confirmer sur le vrai dataset
- [ ] Le zip est autosuffisant, décompressé ailleurs — à confirmer

## Plus tard

- **Phase 5** — zip, `signature.txt`, soutenance
- Question non tranchée : renommer `Train.py`/`Predict.py` en minuscules (D-010)
