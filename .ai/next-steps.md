# Prochains petits pas

> Dans l'ordre. On ne passe à l'étape suivante que quand la précédente est validée.

## Phases 1 à 5 — toutes validées ✅

Validées sur le vrai dataset le 2026-09-23 (cf. D-015 et D-016).

- [x] Phase 1 — `Distribution.py`
- [x] Phase 2 — `augmented_directory/` équilibré à 1640 par classe, prouvé
      via `Distribution.py` sur le **vrai** dataset, déterminisme confirmé
- [x] Phase 3 — masque contrôlé visuellement sur Apple **et** Grape, batch
      sans crash ni fuite mémoire
- [x] Phase 4 — **93,98 %** sur 1444 images de validation
- [x] Phase 5 — zip figé, `signature.txt` générée

### Critères de sortie Phase 4 — tous atteints

- [x] `flake8 .` vert
- [x] Split train/validation sur les originaux, avant augmentation —
      **prouvé empiriquement** : intersection vide entre les 10 496 entrées
      du train et les 1444 de validation
- [x] `class_names.json` sauvegardé et rechargé
- [x] Validation ≥ 100 images (1444)
- [x] **Accuracy > 90 %** → 93,98 %
- [x] `Predict.py` sur une image jamais vue
- [x] Zip autosuffisant, décompressé ailleurs

## Immédiat — le seul geste restant

- [ ] **Commiter** : `signature.txt` n'est pas encore suivi par git.

```bash
git add signature.txt src/Train.py .ai/
git commit -m "Validation sur le vrai dataset + signature.txt"
```

Vérifier avant de pousser que `git status` ne montre **aucune** image,
aucun zip, aucun modèle.

## Questions encore ouvertes (à trancher avant le rendu)

- **Casse des noms** : le sujet écrit `train.[extension]` /
  `predict.[extension]` en minuscules (p.9), le repo a `Train.py` /
  `Predict.py`. Ouverte depuis D-010. Sur un filesystem sensible à la casse,
  un correcteur qui tape `./predict.py` échoue.
  ⚠️ Renommer **ne touche pas au zip**, donc n'invalide pas la signature.
- **`en.subject_leaffliction.pdf` commité** à la racine, alors que le sujet
  demande « only your programs and the signature.txt » (p.11).
- **`--save` pour la matrice de confusion** : `plot_confusion_matrix`
  accepte `save_path`, `evaluate()` ne le lui passe jamais. Sans `$DISPLAY`,
  pas de fichier récupérable pour archiver la preuve du > 90 %.

## Préparation de la soutenance (roadmap 5.4)

Les réponses sont dans `.ai/decisions.md`. Les points les plus susceptibles
d'être challengés :

- **Pourquoi le split avant augmentation ?** → sinon une image et sa version
  flippée tombent de part et d'autre : fuite, accuracy artificielle. Preuve
  disponible : intersection vide train/validation (D-016).
- **Sur quel set l'accuracy a-t-elle été mesurée ?** → 1444 images
  originales jamais augmentées, jamais vues à l'entraînement. 93,98 %.
- **Commenter la matrice de confusion** → la pire classe est `Apple_scab`
  (81,7 % de rappel), confondue avec `Apple_Black_rot` et `Apple_healthy` :
  trois affections du même pommier. Aucune confusion entre pommier et vigne,
  contrairement au premier modèle sous-entraîné.
- **Pourquoi `monitor="val_accuracy"` ?** → la `val_loss` remonte quand le
  réseau devient sur-confiant alors que l'accuracy progresse encore ; et la
  courbe est très bruitée (0,51 → 0,88 → 0,59 → 0,94), d'où patience 8.
- **Que fait une convolution / un max pooling / un dropout ?** → docstring
  de `utils/model.py::build_cnn`.
- **Comment le masque est-il construit ?** → canal `a` de LAB + Otsu, cf.
  D-013.
