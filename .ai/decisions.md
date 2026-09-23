# Journal des décisions

> Journal append-only : on n'efface pas une décision, on en ajoute une nouvelle
> qui la remplace en le disant explicitement.

---

## D-001 — Langage, norme, architecture générale
**Date** : 2026-08-26 · **Statut** : acté (hérité du roadmap)

- Python 3, norme `flake8` (le sujet impose la norme si on choisit Python, p.4).
- Partie 4 : CNN **Keras/TensorFlow from scratch**, pas de transfer learning.
  Objectif pédagogique : pouvoir expliquer chaque couche en soutenance.
- Partie 3 : `plantcv` (explicitement recommandé par le sujet, p.7).
- Partie 2 : augmentations écrites à la main (`Pillow` / `numpy` / `opencv`),
  pas de lib d'augmentation clé en main — plus défendable en soutenance.
- Un modèle **unique à 8 classes**, pas un modèle par plante.

---

## D-002 — `.gitignore` : `data/` ignoré, `.ai/` versionné
**Date** : 2026-08-26 · **Statut** : acté

Le `.gitignore` initial contenait uniquement `.ai/`, soit l'inverse du besoin.

**Pourquoi** : le sujet p.11 est catégorique — livrer le dataset dans le repo Git
est interdit et vaut 0. `data/` contient 7221 images dans le repo, donc un
`git add .` non protégé est fatal. À l'inverse, `.ai/` est le contexte de session :
il doit être poussé pour permettre de reprendre le travail sur un autre poste.

**Exception** : `.ai/leaffliction.pdf` reste ignoré (3,4 Mo, c'est le sujet fourni
par l'école, pas un livrable).

---

## D-003 — Parcours récursif, classe = dossier parent direct de l'image
**Date** : 2026-08-26 · **Statut** : acté

Le sujet (p.5, p.9) et le roadmap supposent une arborescence à 2 niveaux
(`Apple/apple_healthy/`). Le dataset réel est **plat** (`images/Apple_healthy/`).

**Décision** : parcours récursif, la classe d'une image est le **nom de son dossier
parent direct**.

**Pourquoi** : c'est la seule règle qui fonctionne sur les deux arborescences sans
branchement conditionnel. Le programme marche donc aussi bien sur `data/images`
que sur un `./Apple` à 2 niveaux si le correcteur en présente un — ce que le sujet
exige explicitement (« Your program must work with all the directory in the data set »).

---

## D-004 — Noms des augmentations : on suit le `ls`, pas la figure
**Date** : 2026-08-26 · **Statut** : acté

Le sujet se contredit en page 6 :
- la **figure** annonce `Rotation, Blur, Contrast, Scaling, Illumination, Projective`
- le **`ls`** juste en dessous montre `_Flip, _Rotate, _Skew, _Shear, _Crop, _Distortion`

**Décision** : suivre le `ls` — donc `Flip, Rotate, Skew, Shear, Crop, Distortion`.

**Pourquoi** : le `ls` est la sortie littérale que le correcteur va reproduire
au clavier pendant l'évaluation. La liste à puces en haut de la page p.6
(« examples of techniques you can use ») confirme ces 6 noms-là.

---

## D-005 — Un seul venv, `tensorflow-cpu`
**Date** : 2026-08-26 · **Statut** : acté, à réévaluer si conflit

Le roadmap (§0.1) prévoyait de basculer sur deux venv séparés (`.venv-cv` /
`.venv-ml`) en cas de conflit `plantcv` ↔ `tensorflow`.

**Décision** : commencer par **un seul venv**, avec `tensorflow-cpu`.

**Pourquoi** : la machine n'a que **3,3 Go libres** (93 % de remplissage). Deux venv
dupliquent numpy, opencv et scipy, ce qui rend l'échec disque plus probable que
le conflit de versions qu'on cherchait à éviter. On ne split que si un conflit
réel se manifeste, et on le documentera ici.

**Ordre d'installation** : `plantcv` en premier (c'est lui le plus contraint sur
numpy/opencv), on laisse pip résoudre autour, puis `tensorflow-cpu`.

**Résultat (2026-08-26)** : ✅ aucun conflit. Un seul venv suffit, la décision
tient. Le venv pèse 2,4 Go et il reste 4,9 Go libres — deux venv auraient été
très serrés. Versions obtenues en D-007.

---

## D-007 — Versions figées de l'environnement
**Date** : 2026-08-26 · **Statut** : acté

| Paquet | Version | Conséquence sur le code |
|---|---|---|
| plantcv | **4.11.3** | **API v4** |
| tensorflow-cpu | 2.21.0 | Keras 3 → format `.keras` |
| numpy | **2.4.6** | numpy **2.x** |
| opencv-python | 4.11.0.86 | — |
| matplotlib | 3.11.1 | — |
| scikit-learn | 1.9.0 | pour la matrice de confusion (Phase 4) |
| pillow | 12.3.0 | — |
| scipy | 1.15.3 | tiré par plantcv |
| flake8 | 7.3.0 | la norme |

**Deux implications à ne pas oublier :**

1. **PlantCV v4** — l'API a changé depuis la v3, et la majorité des exemples en
   ligne sont encore en v3. En v4 : `pcv.analyze.size(...)`, `pcv.analyze.color(...)`.
   Les fonctions `pcv.find_objects()` / `pcv.analyze_object()` et toute la gestion
   manuelle `objects` + `hierarchy` **n'existent plus** : le masque binaire suffit.
   Si un exemple trouvé en ligne mentionne `find_objects`, il est périmé.

2. **numpy 2.x** — les alias `np.float`, `np.int`, `np.bool` ont été supprimés.
   Un snippet qui les utilise lèvera `AttributeError`. Utiliser `float`, `int`,
   `bool` natifs ou `np.float64` / `np.int64`.

**Note portabilité** : `tensorflow-cpu` n'est pas publié pour macOS ARM (Mac M1/M2).
Si le projet doit tourner sur une telle machine, remplacer par `tensorflow`.
Documenté ici pour ne pas être surpris en soutenance si le poste change.

---

## D-008 — Arborescence : `src/` pour la logique, exécutables à la racine
**Date** : 2026-08-26 · **Statut** : ⚠️ **REMPLACÉ par D-010** — conservé pour l'historique

Charles souhaitait ranger le code source dans `src/` (au lieu de `utils/` prévu au
roadmap) et les exécutables dans `cli/`.

**`utils/` → `src/`** : accepté sans réserve, c'est plus conventionnel.

**`cli/`** : bloque techniquement. Quand on lance `python cli/Distribution.py`,
Python place le **répertoire du script** en `sys.path[0]` — donc `cli/`, jamais la
racine. Le répertoire courant n'est pas ajouté au path pour un script. Résultat :
`from src.dataset import ...` lève `ModuleNotFoundError: No module named 'src'`.
Vérifié expérimentalement le 2026-08-26.

S'ajoute une contrainte du sujet : les programmes y sont invoqués **depuis la
racine** (`./Distribution.[extension] ./Apple`, p.5 et p.9).

| Option | Invocation | Verdict |
|---|---|---|
| **A** — exécutables racine + `src/` | `python Distribution.py <dir>` | ✅ natif, conforme |
| B — `cli/` + `sys.path.insert()` | idem | 5 hacks dupliqués |
| C — `cli/` + `python -m cli.Distribution` | non conforme au sujet | ✗ |

**Décision : option A.** Les 5 fichiers racine restent des **coquilles minces**
(argparse + un appel) ; toute la logique vit dans `src/`. La séparation CLI/logique
voulue par Charles est donc préservée — portée par la finesse des fichiers plutôt
que par un dossier supplémentaire.

Arborescence retenue :

```
42_leaffliction/
├── Distribution.py  Augmentation.py  Transformation.py
├── train.py         predict.py            ← coquilles minces
├── src/
│   ├── __init__.py
│   ├── dataset.py       # parcours, comptage
│   ├── io_utils.py      # lecture/écriture image, validation de chemins
│   ├── plotting.py      # helpers matplotlib
│   ├── augment.py       # Phase 2
│   ├── transform.py     # Phase 3
│   └── data_prep.py     # Phase 4
├── requirements.txt  signature.txt  .gitignore
└── .ai/
```

---

## D-009 — Phase 3 : comparaison A/B pour justifier l'extraction de features
**Date** : 2026-08-26 · **Statut** : acté, à réaliser en Phase 4

Des collègues ayant fait le projet ont soutenu que les CNN récents rendent la
Phase 3 (extraction manuelle de caractéristiques) inutile, et l'ont démontré en
comparant **un ancien modèle et un modèle récent**.

**Le fond est juste** : avant les CNN, classifier une image imposait d'extraire des
features à la main (descripteurs de forme, histogrammes de couleur, SIFT, HOG) pour
nourrir un classifieur classique — c'est exactement ce que produit
`Transformation.py`. Un CNN apprend cette hiérarchie seul depuis les pixels bruts.

**Ce que ça ne change pas** : `Transformation.py` reste un **livrable obligatoire**
(sujet IV.3). L'argument sert en soutenance, il ne dispense pas d'implémenter.

**Correction méthodologique** : comparer « ancien modèle » et « nouveau modèle »
change *deux* variables à la fois (architecture **et** prétraitement) — l'écart
mesuré n'est attribuable à aucune des deux. On garde donc la **même architecture**
et on ne fait varier que le **prétraitement**, ce qui est déjà le plan A/B du
roadmap §4.2 :

- **A** : RGB brut redimensionné
- **B** : image masquée, réutilisant le masque de la Phase 3

Une seule variable, écart interprétable, et deux entraînements du même modèle au
lieu de deux modèles à concevoir. Résultats des deux runs à consigner ici.

---

## D-006 — Équilibrage : énumération déterministe, pas tirage aléatoire
**Date** : 2026-08-26 · **Statut** : acté, à appliquer en Phase 2

Le roadmap (§2.3) proposait de « tirer des images au hasard et leur appliquer une
augmentation au hasard » jusqu'à atteindre la cible.

**Problème** : la cible est 1640 (Apple_healthy). Apple_rust n'a que 275 originaux,
il faut donc générer 1365 images alors que 6 augmentations n'offrent que
275 × 6 = 1650 paires `(image, augmentation)` distinctes. On consomme **83 %** de
l'espace disponible : un tirage avec remise produit un taux de collision énorme
et peut ne jamais converger.

**Décision** : énumérer toutes les paires `(image, augmentation)`, les shuffler
avec `random.seed(42)`, et prendre les N premières.

**Pourquoi** : garantit zéro doublon, converge en un passage, et reste
reproductible — ce qui est indispensable puisque `signature.txt` est le sha1 du
zip et dépend du contenu exact.

---

## D-010 — Arborescence retenue : tout dans `src/`, exécutables inclus
**Date** : 2026-08-26 · **Statut** : acté (remplace D-008)

Décision de Charles, après que le risque a été exposé (cf. D-008) : les exécutables
vivent dans `src/`, le code partagé dans `src/utils/`.

```
42_leaffliction/
├── requirements.txt  signature.txt  .gitignore
├── .ai/
└── src/
    ├── Distribution.py  Augmentation.py  Transformation.py
    ├── Train.py  Predict.py
    └── utils/
        ├── __init__.py
        ├── dataset.py    # parcours, comptage
        ├── plotting.py   # helpers matplotlib
        ├── augment.py    # Phase 2
        ├── transform.py  # Phase 3
        └── data_prep.py  # Phase 4
```

**Invocation** : `python src/Distribution.py ./data/images`

**Forme des imports** : `from utils.dataset import ...`
Ça fonctionne parce que Python place le répertoire du script en `sys.path[0]` —
donc `src/` — et que `utils/` est un sous-package de `src/`. Aucun bricolage de
`sys.path` n'est nécessaire. `src/` lui-même n'a pas besoin d'être un package
(pas de `src/__init__.py`) : c'est un répertoire de scripts, pas un module importé.

**Écart assumé avec le sujet** : le sujet invoque `./Distribution.[extension]`
depuis la racine (p.5, p.9). Il faudra préfixer par `src/`. Justification de
Charles : la notation `[extension]` montre que ces lignes sont des exemples
schématiques, pas une spécification littérale du chemin. Risque jugé acceptable.

**Point resté ouvert** : `Train.py` / `Predict.py` sont capitalisés alors que le
sujet p.9 nomme ces deux programmes `train.[extension]` et `predict.[extension]`
en minuscules (les trois autres sont bien capitalisés dans le sujet). Question de
nom de programme, distincte de celle de l'emplacement. Non tranché.

---

## D-011 — `.flake8` : exclure `.venv`, ne pas toucher au reste
**Date** : 2026-08-26 · **Statut** : acté

`flake8 .` scanne `.venv/` : la liste d'exclusion par défaut de flake8
(`.git`, `__pycache__`, `.tox`, `.eggs`, …) **ne contient pas `.venv`**. Résultat
constaté : 54 Mo de sortie, des milliers d'erreurs dans PIL, numpy & co.

**Fix** — fichier `.flake8` à la racine :

```ini
[flake8]
extend-exclude = .venv
```

`extend-exclude` **ajoute** aux exclusions par défaut ; `exclude` les **remplace**
(on perdrait `.git` et `__pycache__`).

**Ce qu'on ne fait PAS** : toucher à `max-line-length`. On reste aux **79 colonnes**
par défaut. La distinction est nette et défendable en soutenance — exclure `.venv`
écarte du code tiers qui n'est pas le nôtre, relever la limite de ligne assouplirait
la norme elle-même.

---

## D-012 — matplotlib : API colormaps et bascule de backend
**Date** : 2026-08-26 · **Statut** : acté

**Colormaps** : sur matplotlib 3.11, `matplotlib.cm.get_cmap()` lève
`AttributeError` (supprimé en 3.9). La forme valide est
`matplotlib.colormaps["tab10"]`. La majorité des exemples en ligne utilisent
encore la forme supprimée.

**Backend sans écran** : on utilise `plt.switch_backend("Agg")` **après** les
imports, plutôt que le canonique `matplotlib.use("Agg")` **avant** d'importer
pyplot. Raison : la forme canonique impose un import en milieu de fichier, donc un
`# noqa: E402` pour flake8. `switch_backend` est une API publique et laisse les
imports groupés en tête de fichier.

**Cohérence des couleurs entre le camembert et l'histogramme** : elle repose sur le
fait que `labels`, `values` et `colors` sont construits dans le **même ordre** à
partir de la même liste, et que `build_palette` indexe sur la **position** et non
sur le nom. Comme `dataset.py` renvoie déjà un dict trié, la chaîne complète est
déterministe.

---

## D-013 — Phase 3 : masque LAB-a/Otsu, histogramme sur index, pas d'histogramme en batch
**Date** : 2026-09-02 · **Statut** : acté, implémenté

**Session menée en implémentation directe** (mode confirmé par Charles pour
cette session, dérogation ponctuelle au mode mentor pas-à-pas d'`AGENTS.md`).

**Masque** : canal `a` de LAB (vert↔magenta) + `pcv.threshold.otsu(...,
object_type="dark")`, puis `pcv.fill(size=200)` + `pcv.closing(kernel=5x5)`.
C'est l'approche standard des tutoriels PlantCV pour un fond gris/blanc
uniforme. Vérifiée fonctionnellement sur une image synthétique (ellipse verte
sur fond gris) — **pas encore sur le vrai dataset**, absent de la machine au
moment de l'implémentation. Cf. `.ai/next-steps.md`.

**Histogramme couleur (`t_color_histogram`)** : `pcv.analyze.color(...,
colorspaces="all")` stocke ses résultats dans `pcv.outputs.observations`,
sous une clé `"<sample_label>_<n>"` (ex. `"default_1"`), pas sous
`sample_label` seul — on prend `next(iter(...))` plutôt que de supposer la
clé. Chaque canal (`blue, blue-yellow, green, green-magenta, hue, lightness,
red, saturation, value`) est ensuite tracé contre son **indice de position**
et non son unité physique réelle (`hue` n'a que 180 valeurs pour une plage de
0-359°, les autres canaux en ont 256) — simplification assumée pour avoir un
seul axe des abscisses malgré 3 unités différentes dans les données brutes.

**Histogramme non sauvegardé en mode batch** : ce n'est pas une image mais
des données à tracer, sans destination `<nom>_<Type>.JPG` naturelle. Les
autres transformations (image → image) sont sauvegardées normalement.

**Fermeture morphologique via `cv2.morphologyEx`, pas `pcv.closing`** :
`pcv.closing` délègue à `skimage.morphology.binary_closing`, qui émet un
`FutureWarning` (dépréciée depuis skimage 0.26, suppression prévue en 0.28).
Remplacée par `cv2.morphologyEx(..., cv2.MORPH_CLOSE, kernel)` — même
opération, sans dépendance à une API tierce en sursis. Vérifié : plus aucun
`FutureWarning` levé (testé avec `-W error::FutureWarning`).

---

## D-014 — Phase 4 : split avant augmentation, format du zip, choix A
**Date** : 2026-09-03 · **Statut** : acté, implémenté

**Session menée en implémentation directe** (mode confirmé par Charles pour
cette session — même dérogation qu'en D-013 — via une demande explicite
répétée après refus de la question de clarification sur le dataset dupliqué,
cf. limite ci-dessous).

**Split train/validation** (`utils/data_prep.py::split_dataset`) : sur les
images **originales**, avant tout appel à `balance_classes` — jamais
l'inverse (fuite de données sinon, cf. `.ai/roadmap.md` Phase 4, pièges).
Graine dédiée `SPLIT_SEED = 42`, indépendante de `BALANCE_SEED` (déjà
utilisée par la Phase 2) pour ne pas coupler les deux tirages aléatoires. Au
moins 1 image par classe part en validation ; `Train.py` refuse de continuer
si le total validation < 100 (`VAL_MIN_IMAGES`).

**Réutilisation Phase 2** : la logique d'équilibrage de
`Augmentation.py::balance_dataset` a été extraite vers
`utils/augment.py::balance_classes(classes: dict, dst: Path)` — `Train.py`
l'appelle directement sur le split train (un dict déjà en mémoire) sans
repasser par le disque ; `Augmentation.py` devient un wrapper fin qui
appelle `list_images` puis `balance_classes`. Aucune logique dupliquée.

**Format du zip** (`utils/learnings.py`) : `model.keras` + `class_names.json`
(ordre alphabétique, critique) + `config.json` (taille d'image, ratio de
split, seed, description du prétraitement) + `augmented_directory/` (le
train augmenté). `save_learnings`/`load_learnings` sont les deux seules
fonctions qui connaissent ce format — `Predict.py` ne le reconstruit jamais
à la main, pour éviter la divergence train/predict que le roadmap identifie
comme le piège n°1 du projet.

**Prétraitement retenu : option A** (RGB brut, redimensionné 128×128,
normalisé `[0, 1]`) — recommandation du roadmap, à ne remettre en cause que
si l'accuracy plafonne sous 90 % (comparaison avec l'option B, masque Phase
3, non faite cette session — cf. D-009).

**Architecture** : 3 blocs Conv2D(32→64→128)/BatchNorm/MaxPool, puis
Flatten/Dropout(0.5)/Dense(128)/Dropout(0.3)/Dense(softmax). `Adam(1e-3)`,
`sparse_categorical_crossentropy`, `EarlyStopping(patience=5)` +
`ModelCheckpoint`. Point de départ du roadmap, non encore ajusté sur le vrai
dataset.

**`--evaluate` placé sur `Predict.py`**, pas `Train.py` : le roadmap (4.6)
ne tranche pas explicitement, mais `Predict.py` a déjà toute la logique de
chargement du zip et de prétraitement — l'y ajouter évite de dupliquer
`load_learnings` dans les deux scripts.

**Limite non résolue cette session** : `data/images/` local s'est révélé
**dupliqué en 2×** (mêmes contenus, noms différents — vérifié par hash MD5,
chaque classe a exactement 2× l'effectif attendu). Question posée à Charles
(dédupliquer / ré-extraire / ignorer pour l'instant) — refusée sans réponse
alternative, et la demande "réalise la partie 4" a été répétée telle
quelle. Interprété comme instruction d'avancer sans bloquer davantage.
**Le dataset n'a pas été nettoyé** : lancer `Train.py` dessus tel quel
risque de faire atterrir un doublon des deux côtés du split train/validation
(même piège que "augmenter avant split", cf. `docs/part4-train-predict.md`,
section limites). Pipeline validé uniquement sur données synthétiques.

---

## D-015 — Validation sur le vrai dataset : les 3 premières phases passent, le modèle est sous-entraîné
**Date** : 2026-09-23 · **Statut** : acté

Première session où **tout tourne sur le vrai `data/images/`** (7221 images,
8 classes). Les limites de D-013 et D-014 (validation uniquement sur données
synthétiques) sont donc levées, sauf mention contraire ci-dessous.

**Le dataset dupliqué en 2× signalé en D-014 n'existe plus.** Recomptage :
chaque classe est à son effectif nominal (Apple_rust 275, Apple_healthy 1640,
etc.). Le blocage « dédupliquer avant tout entraînement » est caduc — il ne
reste rien à nettoyer.

**Phase 2 validée** : `Augmentation.py --balance data/images --dst
augmented_directory` produit 13 120 images, **1640 par classe exactement**.
`Distribution.py augmented_directory` montre 8 barres strictement égales et
un camembert à 12,5 % partout. C'est le critère de sortie Phase 2 du
roadmap, prouvé sur le vrai dataset.

**Phase 3 validée** : mode batch sur 24 images réelles (3 par classe, les 8
classes) → 120 fichiers, aucun crash, 2,5 s. Masques contrôlés visuellement
sur Apple **et** Grape, y compris `Grape_Esca` dont les feuilles sont
trouées : fond supprimé proprement, contours et taches de maladie préservés.
Le pipeline LAB-a/Otsu de D-013 tient sur le vrai dataset.

**Phase 4 — le modèle ne passe pas le critère du sujet** :

| mesure | valeur |
|---|---|
| accuracy validation (1444 images) | **85,73 %** |
| accuracy train (échantillon 800) | 87,88 % |
| exigence du sujet | > 90 % |

**Diagnostic : sous-apprentissage, pas sur-apprentissage.** L'écart
train/validation n'est que de ~2 points — le modèle n'a pas encore appris
ses propres données d'entraînement. Confirmé par les confusions observées
dans la matrice : `Grape_spot` → `Apple_rust` (19), `Grape_Black_rot` →
`Apple_healthy` (15). Des confusions **entre plantes différentes**, dont la
forme de feuille n'a rien de commun — signature d'un réseau qui n'a pas
convergé, pas d'une maladie intrinsèquement ambiguë.

**Conséquence sur D-009 / l'option B** : la comparaison A/B (RGB brut vs
image masquée) prévue « si l'accuracy plafonne sous 90 % » **ne doit pas
être lancée ici**. Le masquage attaque le bruit de fond, donc le
sur-apprentissage ; il ne corrige pas un modèle qui sous-apprend. L'option A
reste retenue.

**Cause retenue** : entraînement arrêté trop tôt. Les images augmentées du
zip livré datent de 11:50 et le zip de 12:18, soit ~20 min de training à
~4,5 min/époque → environ 4 époques. Insuffisant pour un CNN from scratch
sur 10 496 images.

**Correction apportée à `Train.py`** : `EarlyStopping` et `ModelCheckpoint`
surveillaient `val_loss` (le défaut Keras) alors que le critère du sujet est
l'accuracy. Avec BatchNorm, la `val_loss` remonte quand le réseau devient
sur-confiant, pendant que la `val_accuracy` progresse encore : surveiller la
loss coupe l'entraînement alors que le modèle s'améliore toujours. Passés à
`monitor="val_accuracy", mode="max"`, patience 5 → 8.

Second correctif : `run()` affichait `val_accuracy[-1]` (dernière époque)
alors que `restore_best_weights=True` livre les poids de la **meilleure**
époque — le chiffre annoncé ne décrivait pas le modèle sauvegardé. Affiche
désormais la meilleure époque et son rang.

**Incident** : `train_workdir/` a été supprimé par erreur pendant cette
session (un `rm -rf` avant relance d'entraînement), alors qu'il contenait le
set de validation du modèle livré — absent du zip par conception. Sans
conséquence : `split_dataset` est déterministe (`SPLIT_SEED = 42`), donc
régénérer le split sur le même `data/images` reproduit exactement les mêmes
1444 images. Vérifié : le train régénéré compte 10 496 images, exactement le
nombre d'images augmentées présentes dans le zip livré. **C'est précisément
ce que le déterminisme du split achète** — argument à resservir en
soutenance.

**Non tranché** : `evaluate()` (`Predict.py`) ne passe jamais `save_path` à
`plot_confusion_matrix`, qui le supporte pourtant. Sans `$DISPLAY`, la
matrice n'est donc pas récupérable en fichier. Sans effet en soutenance sur
une machine avec écran, mais un `--save` serait utile pour archiver la
preuve du > 90 %.

---

## D-016 — Phase 4 franchie (93,98 %) et Phase 5 : zip figé, `signature.txt` générée
**Date** : 2026-09-23 · **Statut** : acté

Suite directe de D-015 : le correctif `monitor="val_accuracy"` est validé.

**Résultat du ré-entraînement** : meilleure époque **9 sur 17**
(`EarlyStopping` a coupé à 17 après 8 époques sans progrès), val_accuracy
0,9370 côté Keras, **0,9398 mesurée indépendamment** par
`Predict.py --evaluate` sur les 1444 images de validation.

| | v1 (12:18) | v2 (livré) |
|---|---|---|
| accuracy validation | 85,73 % | **93,98 %** |
| meilleure époque | ~4 (estimé) | 9 / 17 |

**Le correctif a bien traité la cause.** Les confusions entre plantes
différentes ont disparu : `Grape_spot` → `Apple_rust` passe de 19 à **0**,
`Grape_Black_rot` → `Apple_healthy` de 15 à 2. Il ne reste que des
confusions **intra-plante** botaniquement plausibles, la pire classe étant
`Apple_scab` à 81,7 % de rappel (confondue avec `Apple_Black_rot` 12 fois et
`Apple_healthy` 10 fois — deux affections du même pommier).

**La `val_accuracy` est très bruitée d'une époque à l'autre** (0,51 → 0,88 →
0,59 → 0,75 → 0,94…). C'est exactement ce qui rendait la surveillance de la
`val_loss` dangereuse, et ça justifie la patience portée à 8 : avec patience
5 sur une courbe aussi instable, l'arrêt tombe sur un creux. À savoir
expliquer en soutenance si la question vient.

**Absence de fuite train/validation prouvée empiriquement**, pas seulement
par lecture du code : extraction des 10 496 chemins `classe/fichier` du zip
et des 1444 du set de validation → **intersection vide**. Les entrées de
validation ne portent d'ailleurs aucun suffixe `_Flip_` / `_Rotate_`, donc
elles n'ont jamais été augmentées. Attention au piège de lecture : les noms
de fichiers se répètent d'une classe à l'autre (`image (103).JPG` existe
dans presque toutes), donc la comparaison **doit** porter sur
`classe/fichier` et non sur le seul nom de fichier.

**Autosuffisance du zip vérifiée** : zip copié hors du repo + image hors du
repo → `Predict.py` prédit correctement `Grape_Esca` à 100 %.

**Phase 5 — zip figé** : `learnings_v2.zip` renommé en `learnings.zip`
(l'ancien modèle à 85,73 %, qui échouait au critère du sujet, est écrasé —
bascule autorisée par Charles sous condition des 90 %, condition remplie).

```
sha1 : e1a6e28e5dbe5d32659ad461a6c217840d42bcef
taille : 277 006 992 octets
```

> ⛔ **Ne plus jamais régénérer ce zip.** Relancer `Train.py` produit un
> fichier au hash différent (horodatages de compression + poids ré-entraînés)
> et invalide `signature.txt` → note 0. Si un ré-entraînement devient
> nécessaire, il faut **regénérer `signature.txt` dans la foulée** et
> recommiter.

Vérifié après coup que `Predict.py --evaluate` (qui décompresse le zip dans
un répertoire temporaire puis le supprime) **ne modifie pas** l'archive :
`sha1sum -c signature.txt` repasse OK après une évaluation complète.
