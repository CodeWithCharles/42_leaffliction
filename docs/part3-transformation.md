# Partie 3 — `Transformation.py`

Extraction de caracteristiques d'une feuille via [PlantCV](https://plantcv.org/)
v4.11.3 (sujet IV.3, p.7-8). Historique de la decision et pieges connus :
`.ai/roadmap.md` (Phase 3) et `.ai/decisions.md`.

## Usage

```bash
# Une image -> affiche les transformations (fenetre, ou fichier via matplotlib
# si aucun $DISPLAY)
python "src/Transformation.py ./data/images/Apple_healthy/image (1).JPG"

# Un dossier -> sauvegarde les transformations, arborescence des classes
# reproduite sous -dst
python src/Transformation.py -src ./data/images/Apple_healthy -dst dst_directory

# Ne generer qu'une sous-partie des transformations
python src/Transformation.py --mask --histogram ./data/images/Apple_healthy/image1.JPG

python src/Transformation.py -h
```

Regle : `image` **XOR** (`-src` + `-dst`) — toute autre combinaison est
rejetee proprement par `argparse` (`parser.error`, code de sortie 2).

Flags de selection : `--blur`, `--mask`, `--roi`, `--analyze`,
`--pseudolandmarks`, `--histogram`. Aucun flag = toutes les transformations.
En mode batch (`-src`/`-dst`), l'histogramme n'est **pas** sauvegarde : ce
n'est pas une image mais des donnees a tracer, il n'y a pas de destination
naturelle pour lui en tant que fichier `<nom>_<Type>.JPG`.

## Pipeline de masque (`utils/transform.py::build_mask`)

1. `pcv.rgb2gray_lab(img, channel="a")` — canal `a` de l'espace LAB
   (vert ↔ magenta). C'est le canal le plus discriminant pour separer une
   feuille verte d'un fond gris/blanc uniforme : le fond a une valeur `a`
   proche du neutre (~128), la feuille une valeur nettement plus basse.
2. `pcv.threshold.otsu(gray, object_type="dark")` — seuillage automatique
   (la feuille est l'objet "sombre" dans ce canal).
3. `pcv.fill(binary, size=200)` — supprime le bruit residuel (petits ilots
   de faux positifs).
4. `pcv.closing(filled, kernel=5x5)` — comble les petits trous internes du
   masque (nervures plus claires, reflets).

C'est l'approche standard documentee dans les tutoriels PlantCV pour ce type
de fond ; elle a ete validee sur une image synthetique (ellipse verte sur
fond gris) durant cette session, cf. limites ci-dessous.

## Les 7 transformations

| # | Nom (`TRANSFORMATIONS` / flag) | Fonction PlantCV | Ce qu'elle montre |
|---|---|---|---|
| 1 | Original | — | l'image telle que lue |
| 2 | `GaussianBlur` / `--blur` | `pcv.gaussian_blur` | flou applique au masque, met en evidence les contours |
| 3 | `Mask` / `--mask` | `pcv.apply_mask` | fond efface (blanc), feuille conservee |
| 4 | `RoiObjects` / `--roi` | `pcv.roi.rectangle` + `pcv.roi.filter` | objets retenus dans la ROI (masque en vert, bordure en bleu) |
| 5 | `AnalyzeObject` / `--analyze` | `pcv.analyze.size` | contour et axe principal de l'objet |
| 6 | `Pseudolandmarks` / `--pseudolandmarks` | `pcv.homology.x_axis_pseudolandmarks` + `y_axis_pseudolandmarks` | points de repere le long des deux axes |
| 7 | histogramme couleur / `--histogram` | `pcv.analyze.color(colorspaces="all")` | proportion de pixels (%) par intensite, 9 canaux (RGB, LAB, HSV) |

Le masque (`build_mask`) est calcule une seule fois par image et partage
entre toutes les transformations qui en ont besoin — c'est ce qui garantit
la coherence entre elles (meme feuille segmentee partout).

### Histogramme couleur

`pcv.analyze.color` enregistre ses resultats dans `pcv.outputs.observations`
plutot que de renvoyer directement les donnees ; `t_color_histogram` les en
extrait (une liste de proportions par canal : `blue, blue-yellow, green,
green-magenta, hue, lightness, red, saturation, value`). Simplification
assumee : chaque canal est trace contre son propre indice de position
(`range(len(valeurs))`), pas contre son unite physique reelle (`hue` va par
exemple de 0 a 179 indices pour une plage de 0 a 359 degres). Ce choix
reproduit visuellement la Figure IV.7 du sujet sans complexifier l'axe des
abscisses avec 3 unites differentes (0-255, 0-100%, 0-359°).

## Limites connues / a valider

- Le pipeline de masque a ete verifie fonctionnellement (pas de crash, sortie
  coherente) sur une image synthetique — **pas encore sur le vrai dataset**,
  absent de cette machine au moment de l'implementation. A faire avant de
  clore la phase : lancer `Transformation.py` sur 3-4 classes d'Apple et de
  Grape et verifier visuellement que le masque colle bien au contour de la
  feuille (cf. `.ai/next-steps.md`).
- Le mode batch n'a ete teste que sur un tres petit dossier (2 images) ; la
  verification "sans crash ni fuite memoire sur ~50 images" du roadmap reste
  a faire sur le vrai dataset.
