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
