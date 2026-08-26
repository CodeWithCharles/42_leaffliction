# Leaffliction — Roadmap de réalisation

> **Destinataire** : agent de code travaillant en mode `collab-pairing-mentor`.
> **Règle du mode** : l'agent **ne code pas à la place de Charles**. Il guide, découpe en petits pas, donne les signatures et le code en markdown dans la réponse, puis review. Le seul dossier où l'agent écrit sur le disque est `.ai/`.
> **Langage imposé** : Python 3. **Norme** : `flake8` (alias `norminette_python`).

---

## 0. Contexte du projet

Projet 42 « Leaffliction » (Computer Vision). Objectif final : un classifieur capable de reconnaître la maladie d'une feuille à partir d'une photo, avec **> 90 % d'accuracy** sur un set de validation d'**au moins 100 images**.

Le sujet impose **4 programmes** :

| # | Programme | Rôle |
|---|-----------|------|
| 1 | `Distribution.py` | Analyse du dataset → pie chart + bar chart par type de plante |
| 2 | `Augmentation.py` | 6 augmentations d'une image ; sert aussi à équilibrer le dataset |
| 3 | `Transformation.py` | ≥ 6 transformations d'extraction de caractéristiques (PlantCV) |
| 4 | `train.py` + `predict.py` | Entraînement CNN + prédiction sur une image |

Livrables Git : **uniquement le code + `signature.txt`**. Le dataset et le modèle entraîné sont livrés à part (`.zip`), jamais commités.

### Décisions techniques actées

- **Partie 4** : CNN **Keras/TensorFlow entraîné from scratch** (pas de transfer learning). Objectif pédagogique : comprendre chaque couche.
- **Partie 3** : `plantcv` (recommandé par le sujet).
- **Partie 2** : augmentations écrites à la main avec `Pillow` / `numpy` / `opencv` — pas de dépendance à une lib d'augmentation « magique », c'est plus défendable en soutenance.

---

## 1. Découpage global

```
Phase 0  — Setup projet & dataset                       (~1 h)
Phase 1  — Distribution.py                              (~2-3 h)
Phase 2  — Augmentation.py + équilibrage du dataset     (~4-5 h)
Phase 3  — Transformation.py                            (~5-6 h)
Phase 4  — train.py + predict.py                        (~6-8 h)
Phase 5  — Packaging, signature.txt, préparation defense (~2 h)
```

Chaque phase se termine par une **checkpoint review** de l'agent mentor, et une mise à jour de `.ai/state.md`, `.ai/decisions.md`, `.ai/next-steps.md`.

---

## Phase 0 — Setup projet & dataset

### Objectif
Avoir un environnement reproductible, une arborescence propre, et le dataset accessible **hors du repo Git**.

### Petits pas

**0.1 — Environnement virtuel**
- `python3 -m venv .venv` + `source .venv/bin/activate`
- Dépendances à figer dans `requirements.txt` :
  `numpy`, `pillow`, `matplotlib`, `opencv-python`, `plantcv`, `scikit-learn`, `tensorflow` (ou `tensorflow-cpu`), `flake8`
- ⚠️ `plantcv` est lourd et sensible aux versions — l'installer **en premier** et laisser pip résoudre `numpy`/`opencv` autour. Si conflit avec TensorFlow, prévoir **deux venv séparés** (`.venv-cv` pour parties 1-3, `.venv-ml` pour partie 4) et le documenter dans `.ai/decisions.md`.

**0.2 — Arborescence cible**

```
42_leaffliction/
├── .ai/                     # contexte de session (versionné)
├── Distribution.py          # exécutables à la racine (attendu par le sujet)
├── Augmentation.py
├── Transformation.py
├── train.py
├── predict.py
├── utils/                   # code partagé
│   ├── __init__.py
│   ├── dataset.py           # parcours de répertoires, comptage
│   ├── io_utils.py          # lecture/écriture image, validation de chemins
│   └── plotting.py          # helpers matplotlib
├── requirements.txt
├── signature.txt            # généré en Phase 5
└── .gitignore
```

**0.3 — `.gitignore`**
Doit exclure : `.venv/`, `__pycache__/`, `*.zip`, `images/`, `augmented_directory/`, `transformed_directory/`, `*.h5`, `*.keras`, `dst_*/`.
❗ Le dataset dans le repo = **note 0**.

**0.4 — Récupérer le dataset**
Archive `leaves.zip` / `images.zip` fournie par l'école. Décompresser **en dehors** du repo (ex. `~/goinfre/leaffliction_data/`) et pointer dessus par chemin. Structure attendue :

```
images/
├── Apple/
│   ├── Apple_healthy/
│   ├── Apple_scab/
│   ├── Apple_Black_rot/
│   └── Apple_rust/
└── Grape/
    ├── Grape_healthy/
    ├── Grape_Black_rot/
    ├── Grape_Esca/
    └── Grape_spot/
```

**0.5 — Convention de code partagée (à décider maintenant, pas plus tard)**
- Toute entrée utilisateur passe par `argparse`.
- Aucune fonction ne `sys.exit()` en profondeur : on lève une exception, le `main()` l'attrape et affiche un message propre. Le sujet sanctionne un crash brutal.
- Un `if __name__ == "__main__":` par exécutable, avec un `main()` isolé et testable.
- `flake8 .` doit être vert **à chaque fin d'étape**, pas à la fin du projet.

### Critères de validation Phase 0
- [ ] `flake8 .` passe sur un squelette vide
- [ ] `python -c "import plantcv, tensorflow"` fonctionne
- [ ] `git status` ne montre aucune image
- [ ] `.ai/decisions.md` contient le choix venv unique vs double

---

## Phase 1 — `Distribution.py`

### Objectif
Programme qui prend **un répertoire** en argument, parcourt ses sous-répertoires, compte les images par classe, et affiche **un pie chart + un bar chart**, avec les noms de classes tirés des noms de dossiers.

```
$> python Distribution.py ./images/Apple
```

### Petits pas

**1.1 — `utils/dataset.py` : le parcours (structure d'abord)**

Signatures à poser **avant** d'implémenter :

```
def is_image_file(path: Path) -> bool
def count_images_per_class(root: Path) -> dict[str, int]
def list_images(root: Path) -> dict[str, list[Path]]
```

- `count_images_per_class` renvoie `{nom_du_sous_dossier: nombre}`.
- Extensions acceptées : `.jpg`, `.jpeg`, `.png`, `.JPG` (le dataset 42 est en `.JPG` majuscule — piège classique).
- Décider : parcours **1 niveau** de sous-dossiers, ou récursif ? → recommandation : récursif mais la **classe = dossier parent direct de l'image**. Ça rend le programme tolérant à `./images` comme à `./images/Apple`.

**1.2 — Gestion d'erreurs**
- Chemin inexistant, chemin qui n'est pas un dossier, dossier vide, aucune image trouvée → message clair, code retour ≠ 0, pas de traceback.

**1.3 — `utils/plotting.py` : les graphiques**

```
def plot_distribution(counts: dict[str, int], title: str) -> None
```

- Une figure, deux subplots (`plt.subplots(1, 2)`) : pie à gauche, bar à droite.
- Le pie affiche les pourcentages (`autopct='%1.1f%%'`).
- **Même couleur pour une même classe** entre les deux graphes → construire une liste de couleurs indexée sur les classes triées, la passer aux deux appels.
- Titre = nom du répertoire analysé (`root.name`).

**1.4 — `Distribution.py` : l'assemblage**
- `argparse` avec un argument positionnel `directory`.
- Ajouter un flag optionnel `--save <path>` pour dumper le PNG (pratique en soutenance quand il n'y a pas de serveur X).

### Pièges
- Ne pas hardcoder les noms de classes : le sujet insiste sur la récupération depuis le nom des dossiers, et le programme doit marcher sur **tous** les répertoires du dataset.
- Matplotlib sur VM sans display : prévoir `matplotlib.use("Agg")` conditionnel si `DISPLAY` absent.

### Critères de validation Phase 1
- [ ] Fonctionne sur `./images/Apple` et sur `./images/Grape`
- [ ] Fonctionne aussi si on pointe `./images` (2 plantes)
- [ ] Message propre sur chemin invalide
- [ ] `flake8` vert
- [ ] Les chiffres affichés correspondent à un `find <dir> -type f | wc -l` manuel

---

## Phase 2 — `Augmentation.py` + équilibrage

### Objectif
Deux usages du même code :
1. **Mode démo (imposé par le sujet)** : une image en argument → affiche et sauvegarde **6 versions augmentées**, nommées `<nom_original>_<Type>.JPG`.
2. **Mode équilibrage** : générer assez d'images pour que **toutes les classes aient le même effectif**, résultat dans `augmented_directory/`.

```
$> python Augmentation.py ./images/Apple/Apple_healthy/image1.JPG
$> ls
image1_Flip.JPG image1_Rotate.JPG image1_Skew.JPG
image1_Shear.JPG image1_Crop.JPG image1_Distortion.JPG
```

### Petits pas

**2.1 — Module `utils/augment.py` : signatures d'abord**

Une fonction par transformation, **toutes de même signature** — c'est ce qui permet de les mettre dans un dict et d'itérer proprement :

```
def flip(img: np.ndarray) -> np.ndarray
def rotate(img: np.ndarray) -> np.ndarray
def skew(img: np.ndarray) -> np.ndarray
def shear(img: np.ndarray) -> np.ndarray
def crop(img: np.ndarray) -> np.ndarray
def distortion(img: np.ndarray) -> np.ndarray

AUGMENTATIONS: dict[str, Callable[[np.ndarray], np.ndarray]]
```

Détails d'implémentation attendus :
- **Flip** : miroir horizontal.
- **Rotate** : angle aléatoire (ou fixe) ~±25°, en remplissant les coins (bord répliqué ou fond blanc — à choisir et documenter).
- **Skew / Shear** : transformation affine ou perspective via `cv2.warpAffine` / `cv2.warpPerspective`.
- **Crop** : recadrage centré ou aléatoire (~80 % de l'image) **puis redimensionnement à la taille d'origine** — sinon les images sortent de tailles hétérogènes.
- **Distortion** : distorsion barrel/pincushion ou remap élastique.
- ⚠️ **Toutes les sorties doivent avoir la même taille que l'entrée.** C'est la contrainte qui simplifie toute la Phase 4.

**2.2 — Mode démo**
- Sauvegarde à côté de l'image source (le sujet montre un `ls` dans le dossier courant — sauvegarder dans le **répertoire courant** est le comportement le plus proche de l'exemple ; le documenter).
- Affichage : une figure matplotlib avec les 7 vignettes (original + 6).

**2.3 — Mode équilibrage** (flag `--balance <src> --dst augmented_directory`)
- Compter les classes (réutilise `count_images_per_class` de la Phase 1 — pas de duplication de code).
- Cible = effectif de la **classe majoritaire**.
- Pour chaque classe déficitaire : copier les originaux, puis tirer des images au hasard et leur appliquer une augmentation au hasard jusqu'à atteindre la cible.
- **Seed fixe** (`random.seed(42)`) pour que le dataset soit reproductible — indispensable, la `signature.txt` dépend du contenu exact du zip.
- Noms de fichiers uniques et déterministes : `<original>_<Type>_<index>.JPG`.

**2.4 — Vérification**
Relancer `Distribution.py` sur `augmented_directory/` : les barres doivent être **parfaitement égales**. C'est la meilleure preuve visuelle en soutenance.

### Pièges
- Ne pas augmenter la **classe majoritaire** (sinon on ne converge jamais).
- Ne pas augmenter une image déjà augmentée (partir toujours des originaux).
- Attention aux noms de fichiers avec espaces (`image (1).JPG`) : toujours passer par `pathlib`, jamais par concaténation de strings shell.

### Critères de validation Phase 2
- [ ] Les 6 fichiers attendus sont produits, exactement nommés comme dans le sujet
- [ ] `augmented_directory/` a des classes équilibrées, vérifié via `Distribution.py`
- [ ] Deux exécutions successives donnent le même dataset (seed)
- [ ] `flake8` vert

---

## Phase 3 — `Transformation.py`

### Objectif
≥ 6 transformations d'extraction de caractéristiques via **PlantCV**. Deux modes :
- **chemin vers une image** → affichage des transformations ;
- **`-src <dir> -dst <dir>`** → sauvegarde de toutes les transformations dans le répertoire de destination.

```
$> python Transformation.py ./images/Apple/Apple_healthy/image1.JPG
$> python Transformation.py -src Apple/Apple_healthy/ -dst dst_directory --mask
$> python Transformation.py -h        # usage obligatoire
```

### Les 6 transformations du sujet

| # | Nom | Fonction PlantCV principale |
|---|-----|-----------------------------|
| 1 | Original | — |
| 2 | Gaussian blur | `pcv.gaussian_blur` |
| 3 | Mask | seuillage + `pcv.apply_mask` |
| 4 | ROI objects | `pcv.roi.rectangle` + filtrage des objets |
| 5 | Analyze object | `pcv.analyze.size` (forme, surface, périmètre) |
| 6 | Pseudolandmarks | `pcv.homology.x_axis_pseudolandmarks` / `y_axis_...` |
| 7 | Color histogram | `pcv.analyze.color` |

### Petits pas

**3.1 — Pipeline de segmentation d'abord**
Avant toute transformation, il faut un **masque de feuille fiable**. Séquence recommandée :
1. Convertir en LAB ou HSV, garder le canal qui sépare le mieux feuille/fond (souvent `a` de LAB ou `s` de HSV).
2. `pcv.threshold.binary` (ou Otsu) → masque binaire.
3. `pcv.fill` pour supprimer le bruit, `pcv.closing`/`dilate` pour boucher les trous.
4. Contrôler visuellement sur **3-4 images de classes différentes** avant de continuer. Un masque raté fausse toutes les transformations suivantes.

**3.2 — Structure du module `utils/transform.py`**

Même logique que la Phase 2 : une fonction par transformation, signature homogène.

```
def build_mask(img: np.ndarray) -> np.ndarray
def t_gaussian_blur(img, mask) -> np.ndarray
def t_masked(img, mask) -> np.ndarray
def t_roi_objects(img, mask) -> np.ndarray
def t_analyze_object(img, mask) -> np.ndarray
def t_pseudolandmarks(img, mask) -> np.ndarray
def t_color_histogram(img, mask) -> Figure

TRANSFORMATIONS: dict[str, Callable]
```

**3.3 — CLI avec `argparse`**
Le sujet insiste sur un `-h` utile. Arguments attendus :
- positionnel optionnel : `image`
- `-src`, `-dst`
- flags de sélection : `--blur`, `--mask`, `--roi`, `--analyze`, `--pseudolandmarks`, `--histogram` (aucun flag = toutes)
- Règle : `image` **XOR** (`-src` + `-dst`). Rejeter proprement les combinaisons invalides.

**3.4 — Mode batch**
- Reproduire l'arborescence source dans `-dst`.
- Nommage : `<nom>_<Transformation>.JPG`.
- ⚠️ `plt.close()` après chaque figure en mode batch, sinon fuite mémoire et crash sur gros dossier.

### Pièges
- PlantCV change d'API entre versions majeures (`pcv.analyze_object` → `pcv.analyze.size`, gestion des `objects`/`hierarchy` supprimée en v4). **Épingler la version dans `requirements.txt`** et noter laquelle dans `.ai/decisions.md`.
- `pcv.params.debug` doit rester à `None` en batch, sinon PlantCV écrit des dizaines de fichiers parasites.

### Critères de validation Phase 3
- [ ] Les 7 vues du sujet s'affichent pour une image
- [ ] Le masque est propre sur les 4 classes d'Apple **et** les 4 de Grape
- [ ] Mode batch sur ~50 images sans crash ni fuite mémoire
- [ ] `-h` documente clairement chaque option
- [ ] `flake8` vert

---

## Phase 4 — `train.py` + `predict.py`

### Objectif
Entraîner un CNN à reconnaître la maladie. Contraintes du sujet :
- `train.py <dir>` : parcourt les sous-dossiers, augmente/modifie les images, **sauvegarde l'apprentissage**, produit un `.zip` contenant **les apprentissages + les images augmentées**.
- `predict.py <image>` : affiche l'**image originale + l'image transformée**, et annonce la maladie.
- Split train/validation, **accuracy > 90 %** sur au moins **100 images de validation**.

### Petits pas

**4.1 — Préparer les données (`utils/data_prep.py`)**

Ordre imposé, et c'est le point le plus important du projet :

1. **Split AVANT augmentation.** Séparer les originaux en train (~80 %) / validation (~20 %).
2. **Augmenter uniquement le train** (réutilise Phase 2).
3. Le set de validation ne contient **que des images originales, jamais vues**.

> ❗ Si on augmente puis qu'on split, une image et sa version flippée peuvent tomber de part et d'autre → **fuite de données**, accuracy artificiellement à 99 %, et le sujet prévient explicitement que des résultats « suspects » seront challengés en soutenance.

4. Vérifier que le set de validation contient **≥ 100 images**. Si non, ajuster le ratio.

**4.2 — Décider du prétraitement d'entrée** (choix d'architecture à trancher explicitement)

| Option | Description | Trade-off |
|--------|-------------|-----------|
| A | Image RGB brute redimensionnée (128×128 ou 256×256) | Simple, le CNN apprend seul ses features. **Recommandé.** |
| B | Image masquée (fond supprimé, Phase 3) | Supprime le bruit de fond, mais dépend de la qualité du masque |
| C | RGB + masque en 4ᵉ canal | Meilleur des deux, plus complexe |

Recommandation : **A d'abord**, mesurer, et n'essayer B que si l'accuracy plafonne sous 90 %. Documenter le résultat des deux dans `.ai/decisions.md` — c'est une excellente réponse en soutenance.

Normalisation : pixels en `[0, 1]` (`/255.0`), taille fixe, `class_names` **triés alphabétiquement** et sauvegardés avec le modèle.

**4.3 — Architecture du CNN (structure d'abord, puis implémentation)**

Point de départ raisonnable, à faire évoluer :

```
Input (128, 128, 3)
→ Conv2D(32, 3x3, relu) → BatchNorm → MaxPool(2x2)
→ Conv2D(64, 3x3, relu) → BatchNorm → MaxPool(2x2)
→ Conv2D(128, 3x3, relu) → BatchNorm → MaxPool(2x2)
→ Flatten → Dropout(0.5)
→ Dense(128, relu) → Dropout(0.3)
→ Dense(n_classes, softmax)
```

- Loss : `sparse_categorical_crossentropy` (labels entiers) — ou `categorical_crossentropy` si one-hot. **Choisir une convention et s'y tenir.**
- Optimizer : `Adam(1e-3)`.
- Callbacks : `EarlyStopping(patience=5, restore_best_weights=True)` + `ModelCheckpoint`.
- L'agent mentor doit **expliquer chaque couche** avant que Charles l'écrive : rôle de la convolution, du pooling, du dropout, du softmax.

**4.4 — Sauvegarde des « apprentissages »**

Le zip livré doit contenir tout ce qui est nécessaire pour rejouer une prédiction :

```
learnings.zip
├── model.keras            # poids + architecture
├── class_names.json       # ordre des classes (CRITIQUE)
├── config.json            # taille d'entrée, prétraitement, seed
└── augmented_directory/   # images augmentées
```

> ❗ `class_names.json` est le bug n°1 de ce projet : sans lui, `predict.py` associe l'index 2 à la mauvaise maladie et personne ne comprend pourquoi.

**4.5 — `predict.py`**
1. Charger le zip / le modèle + `class_names.json`.
2. Charger l'image, appliquer **exactement** le même prétraitement que l'entraînement.
3. Prédire → classe + probabilité.
4. Afficher côte à côte : **image originale** et **image transformée** (masque ou version prétraitée), avec la classe prédite en dessous. Le sujet le demande explicitement.

**4.6 — Mesurer honnêtement**
Ajouter un mode `--evaluate <validation_dir>` qui parcourt tout le set de validation et affiche accuracy globale + **matrice de confusion**. C'est ce qu'il faut pouvoir montrer pour prouver le > 90 %.

### Pièges
- Ordre des classes non figé entre `train` et `predict` → prédictions décalées.
- Prétraitement divergent entre `train` et `predict` (redimensionnement, normalisation) → accuracy qui s'effondre à l'inférence.
- Entraîner sur `augmented_directory/` sans avoir vérifié qu'il ne contient pas les images de validation.
- Ne pas confondre les classes des **deux plantes** : décider si on entraîne un modèle par plante ou un modèle unique à 8 classes. → recommandation : **un modèle unique**, plus simple à défendre, et `Distribution.py` montre déjà les 8 classes.

### Critères de validation Phase 4
- [ ] Validation ≥ 100 images, accuracy > 90 %, matrice de confusion affichée
- [ ] `predict.py` fonctionne sur une image jamais vue à l'entraînement
- [ ] Le zip est autosuffisant : décompressé ailleurs, `predict.py` marche
- [ ] Pas de fuite train/validation, démontrable en lisant le code
- [ ] `flake8` vert

---

## Phase 5 — Packaging, `signature.txt`, soutenance

### Petits pas

**5.1 — Constituer le zip final**
Il contient le dataset augmenté + les apprentissages. Le zipper **une seule fois** — chaque re-zip change le hash.

**5.2 — Générer `signature.txt`**
```
sha1sum directory.zip > signature.txt
```
Le fichier contient le hash SHA1 du `.zip`. ❗ Si le hash du zip présenté en soutenance ne correspond pas à `signature.txt` → **note 0**. Donc : geler le zip, générer la signature, ne plus jamais toucher au zip.

**5.3 — Nettoyer le repo**
Vérifier avec `git ls-files` qu'il ne contient **que** : les `.py`, `utils/`, `requirements.txt`, `signature.txt`, `.gitignore`, `.ai/`. Aucune image, aucun modèle, aucun zip.

**5.4 — Répétition de soutenance**
Questions à savoir traiter sans hésiter :
- Pourquoi le split avant augmentation ?
- Que fait concrètement une couche de convolution ? un max pooling ? un dropout ?
- Comment le masque est-il construit, et que se passe-t-il s'il rate ?
- Sur quel set l'accuracy a-t-elle été mesurée, et combien d'images ?
- Montrer la matrice de confusion et commenter les classes qui se confondent.

### Critères de validation Phase 5
- [ ] `sha1sum` du zip == contenu de `signature.txt`
- [ ] `git ls-files` propre
- [ ] `flake8 .` vert sur tout le repo
- [ ] Les 4 programmes tournent depuis un clone frais + le zip

---

## 2. Règles de collaboration pour l'agent mentor

1. **Une phase à la fois, une étape à la fois.** Ne pas donner la Phase 2 tant que la Phase 1 n'est pas validée.
2. **Structure avant implémentation** : d'abord les signatures et le contrat de chaque fonction, Charles valide, puis le corps.
3. **Le code est donné en markdown dans la réponse**, jamais écrit dans les fichiers du repo. Seul `.ai/` est modifiable par l'agent.
4. **Expliquer le « pourquoi » de chaque choix** avant le « comment » — c'est un projet d'apprentissage, et la soutenance porte sur la compréhension.
5. **Review après chaque étape** : findings priorisés d'abord, résumé bref ensuite.
6. **Mettre à jour `.ai/state.md`, `.ai/decisions.md`, `.ai/next-steps.md`** en fin de chaque phase et en fin de session.
7. **`flake8` est un gate, pas une formalité** : une étape n'est pas terminée si la norme ne passe pas.

---

## 3. Ordre de démarrage recommandé

> Prochaine action : **Phase 0, étape 0.1** — créer le venv et résoudre l'installation de `plantcv` + `tensorflow`. C'est le point de friction le plus probable du projet ; le régler à froid maintenant évite de le découvrir en Phase 3.
