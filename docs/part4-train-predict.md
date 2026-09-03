# Partie 4 — `Train.py` + `Predict.py`

CNN Keras/TensorFlow entraine **from scratch** (pas de transfer learning,
cf. `.ai/decisions.md`, D-009 : l'objectif est de comprendre chaque couche,
pas d'obtenir le meilleur score possible). Historique de la decision et
pieges connus : `.ai/roadmap.md` (Phase 4).

## Usage

```bash
# Entraine sur un dataset organise par classes, sauvegarde le resultat
python src/Train.py ./data/images --dst learnings.zip

# Reglages optionnels
python src/Train.py ./data/images --dst learnings.zip \
    --val-ratio 0.2 --epochs 30 --batch-size 32 --work-dir train_workdir

# Predit la classe d'une image (affiche original + image pretraitee)
python src/Predict.py "./data/images/Apple_rust/image (1).JPG" --model learnings.zip

# Evalue le modele sur un repertoire de validation : accuracy + matrice
# de confusion
python src/Predict.py --evaluate validation_directory --model learnings.zip

python src/Train.py -h
python src/Predict.py -h
```

Regle CLI (meme convention que `Augmentation.py`/`Transformation.py`) :
`image` **XOR** `--evaluate <dir>` sur `Predict.py`.

## Pipeline de donnees (`utils/data_prep.py`, `utils/augment.py`)

**Ordre impose, c'est le point le plus important de cette phase :**

1. `split_dataset` separe chaque classe en train/validation **sur les
   images originales**, avant tout traitement (`SPLIT_SEED = 42`,
   independante de `BALANCE_SEED`). Au moins une image par classe part en
   validation ; `Train.py` refuse de continuer si le total validation
   descend sous 100 images (`VAL_MIN_IMAGES`).
2. Seul le split **train** est augmente/equilibre, via
   `utils.augment.balance_classes` — la meme fonction que
   `Augmentation.py --balance` (aucune duplication de logique, cf.
   `docs/part2-augmentation.md`).
3. Le split **validation** est copie tel quel (`materialize`), jamais
   augmente.

Pourquoi cet ordre et pas l'inverse : augmenter puis splitter fait
atterrir une image et sa quasi-copie (flip, rotation...) de part et
d'autre de la frontiere train/validation. Le modele "reconnait" alors une
image qu'il a vue sous une autre forme, l'accuracy mesuree grimpe
artificiellement, et ne veut plus rien dire — le sujet previent
explicitement que des resultats "suspects" seront challenges en
soutenance.

`Train.py` materialise les deux splits sur disque sous `--work-dir`
(defaut `train_workdir/`, gitignore) :

```
train_workdir/
├── augmented_directory/   # train, equilibre - c'est ce qui part dans le zip
├── validation/            # validation, non augmente
└── best.keras             # meilleur checkpoint pendant l'entrainement
```

## Pretraitement (`utils/learnings.py`, `utils/model.py`)

Option **A** du roadmap : image RGB brute, redimensionnee `128x128`,
normalisee en `[0, 1]`. Pas de masque (option B) ni de 4e canal (option C)
— a essayer seulement si l'accuracy plafonne sous 90 %, cf.
`.ai/decisions.md`.

`utils.learnings.preprocess_image` est **la seule fonction** qui decrit ce
pretraitement, partagee par `Train.py` (via `image_dataset_from_directory`
+ normalisation manuelle) et `Predict.py` : un ecart entre les deux
effondre l'accuracy a l'inference sans erreur visible (piege explicitement
note dans le roadmap).

## Architecture (`utils/model.py::build_cnn`)

```
Input (128, 128, 3)
→ Conv2D(32, 3x3, relu)  → BatchNorm → MaxPool(2x2)
→ Conv2D(64, 3x3, relu)  → BatchNorm → MaxPool(2x2)
→ Conv2D(128, 3x3, relu) → BatchNorm → MaxPool(2x2)
→ Flatten → Dropout(0.5)
→ Dense(128, relu) → Dropout(0.3)
→ Dense(n_classes, softmax)
```

- **Conv2D** : filtres locaux appris — contours, textures, taches de
  maladie. Chaque couche combine les motifs de la precedente en motifs
  plus complexes (32 → 64 → 128 filtres).
- **BatchNorm** : renormalise les activations entre les couches, stabilise
  et accelere l'entrainement.
- **MaxPool** : sous-echantillonne (garde le maximum local) — reduit le
  cout de calcul et rend la detection tolerante a une petite translation
  du motif dans l'image.
- **Dropout** : eteint aleatoirement des neurones a l'entrainement,
  empeche le reseau de se reposer sur un seul chemin — limite
  l'overfitting.
- **Softmax final** : transforme les logits en probabilites qui somment a
  1 sur les classes.

Loss `sparse_categorical_crossentropy` (labels entiers, pas de one-hot),
`Adam(1e-3)`. `EarlyStopping(patience=5, restore_best_weights=True)` +
`ModelCheckpoint` pour ne pas surentrainer.

## Format du zip (`utils/learnings.py`)

```
learnings.zip
├── model.keras            # poids + architecture (Keras 3, cf. D-007)
├── class_names.json       # ordre des classes fige — CRITIQUE
├── config.json            # img_size, val_ratio, seed, pretraitement
└── augmented_directory/   # images de train augmentees, telles qu'utilisees
```

`class_names.json` est sauvegarde dans l'ordre alphabetique de
`split_dataset` (meme convention que `list_images`). Sans lui, `Predict.py`
associerait un index a la mauvaise classe — c'est le bug n°1 annonce par le
roadmap. `save_learnings`/`load_learnings` sont les deux seules fonctions
qui savent lire/ecrire ce format ; ne pas le reconstruire a la main
ailleurs.

## `Predict.py --evaluate`

Parcourt un repertoire organise par classes (`utils.dataset.list_images`),
predit chaque image avec exactement le pretraitement d'entrainement,
affiche l'accuracy globale et une matrice de confusion normalisee par
ligne (rappel par classe, `utils.plotting.plot_confusion_matrix`). C'est
la preuve a montrer en soutenance pour le critere ">90 % sur ≥100 images".

## Limites connues / a valider

- Pipeline valide de bout en bout (train → save → load → predict →
  evaluate) sur un dataset synthetique minuscule (3 classes, images
  unies bruitees) — **pas encore sur le vrai dataset**, ni sur un nombre
  d'epoques suffisant pour juger de l'accuracy reelle.
- **`data/images/` local est duplique en 2x** au moment de l'ecriture
  (chaque classe a exactement 2 fois son effectif attendu, meme contenu
  sous des noms differents — verifie par hash MD5). Lancer `Train.py`
  dessus sans dedupliquer risque de faire atterrir un doublon (nom
  different, contenu identique) des deux cotes du split train/validation,
  ce qui fausserait l'accuracy mesuree exactement comme le piege
  "augmenter avant split" decrit plus haut. **A nettoyer avant tout run
  d'entrainement reel** — non fait dans cette session, cf.
  `.ai/next-steps.md`.
- `--epochs 30` par defaut avec `EarlyStopping` n'a pas ete mesure sur le
  vrai dataset : temps d'entrainement et accuracy finale restent a
  observer avant de clore la phase.
- Choix A (RGB brut) n'a pas encore ete compare a B (image masquee, phase
  3) comme le prevoit D-009 — a faire si l'accuracy plafonne sous 90 %.
