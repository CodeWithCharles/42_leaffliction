# AGENTS.md

Guidance for coding agents working in this repository (école 42, projet
"Leaffliction" — classification de maladies de feuilles par vision par
ordinateur).

## Commands

Activate the venv first (or prefix commands with `.venv/bin/`):

```bash
source .venv/bin/activate
```

- Lint (must pass, 79-col default, `.venv` excluded via `.flake8`):
  ```bash
  flake8 .
  ```
- Run a program (always from the repo root — imports rely on `src/` being
  `sys.path[0]`):
  ```bash
  python src/Distribution.py ./data/images
  python src/Distribution.py ./data/images/Apple        # also works, 1 level in
  python src/Augmentation.py "./data/images/Apple_rust/image (1).JPG"
  python src/Augmentation.py --balance ./data/images --dst augmented_directory
  python src/Transformation.py ./data/images/Apple_healthy/image1.JPG
  python src/Transformation.py -src ./data/images/Apple_healthy -dst dst_directory --mask
  ```
- No automated test suite exists yet. Validation is manual/visual (see
  "Validation checkpoints" below) plus `flake8 .`.
- There is no `data/` in the repo — the dataset is external (42's zip),
  unpacked outside the repo or under `data/images/` (gitignored). Do not
  attempt to fetch or fabricate it.

## Architecture

Thin CLI scripts at `src/*.py`, shared logic in `src/utils/`. This split is
enforced, not stylistic:

```
src/
├── Distribution.py    # argparse -> utils.dataset -> utils.plotting
├── Augmentation.py     # argparse -> utils.augment -> utils.io_utils/plotting
├── Transformation.py   # PlantCV feature extraction (in progress)
├── Train.py             # CNN training (not started)
├── Predict.py            # inference (not started)
└── utils/
    ├── dataset.py     # list_images / count_images_per_class — the single
    │                  # source of truth for "what is a class"
    ├── io_utils.py    # read_image/write_image — the ONLY layer that knows
    │                  # about OpenCV's BGR; everything else is RGB
    ├── plotting.py    # matplotlib helpers (Agg backend fallback when no
    │                  # $DISPLAY), shared color palette across plots
    └── augment.py     # the 6 augmentation functions + AUGMENTATIONS dict
```

Why scripts live under `src/` (not the repo root) and import as
`from utils.xxx import ...` (not `from src.utils...`): Python puts the
*script's own directory* on `sys.path[0]`, not the invocation cwd. So
`python src/Distribution.py` puts `src/` on the path, making `utils` (a
sub-package of `src/`) importable directly with no `sys.path` hacking. This
means every program **must be invoked as `python src/<Name>.py ...`** — never
via `python -m` or from inside `src/`.

Each CLI script follows the same shape: `parse_args()` → `run(args)` →
`main()` that catches `(OSError, ValueError)` (and `NotImplementedError` for
unfinished phases), prints a clean message to stderr, and returns a non-zero
exit code — no bare tracebacks on user-facing errors.

### Core invariants

- **Class = parent directory name.** `list_images`/`count_images_per_class`
  in `dataset.py` walk the tree recursively; an image's class is its
  *direct* parent folder's name. This makes every program tolerant of both a
  flat `data/images/Apple_healthy/` and a nested `Apple/Apple_healthy/`
  layout — required because the real dataset is flat while the subject's
  examples assume nesting.
- **RGB everywhere except at the OpenCV boundary.** `io_utils.read_image`
  converts BGR→RGB on load, `write_image` converts back on save. Any new
  code touching `cv2.*` directly needs the same care.
- **Augmentations preserve image dimensions.** All 6 functions in
  `augment.py` (`Flip, Rotate, Skew, Shear, Crop, Distortion` — this exact
  naming, chosen to match the subject's shown `ls` output rather than its
  prose) take and return a same-shaped `np.ndarray`, keyed in the
  `AUGMENTATIONS` dict — this uniform signature is what lets the balancing
  mode iterate them generically.
- **Balancing must be deterministic.** When generating images to equalize
  class counts, enumerate all `(image, augmentation)` pairs, shuffle with
  `random.seed(42)`, and take the first N — never sample-with-replacement.
  With the real dataset's smallest class (275 originals) needing 1365 new
  images out of only 1650 possible pairs (83% of the space), a naive random
  draw risks pathological collision rates. Determinism is also required
  because the delivered zip's `signature.txt` is a hash of its exact
  contents.
- **Split before augment, always.** Not yet implemented (Phase 4), but
  binding for `Train.py`: train/validation split must happen on *original*
  images before augmentation. Augmenting first and splitting after leaks
  near-duplicate images across the split and invalidates the accuracy
  measurement.
- **PlantCV is pinned to v4** (`plantcv==4.11.3`, see `requirements.txt`).
  Its API changed materially from v3 (e.g. `pcv.analyze.size(...)` /
  `pcv.analyze.color(...)`, no more `pcv.find_objects()` or manual
  `objects`/`hierarchy`). Don't reuse v3-style examples found online.
  Similarly this repo is on **numpy 2.x** (`np.float`/`np.int`/`np.bool`
  aliases removed — use the native types) and **matplotlib 3.11**
  (`matplotlib.cm.get_cmap()` removed — use `matplotlib.colormaps[name]`).

### Deliverable constraints (why some things look unusual)

- Git must never contain the dataset, a trained model, or any generated zip
  (`data/`, `images/`, `augmented_directory/`, `transformed_directory/`,
  `dst_*/`, `*.zip`, `*.h5`, `*.keras` are all gitignored) — committing the
  dataset is an automatic zero per the subject.
- `.ai/` (this project's own decision log/roadmap/state, in French) *is*
  versioned on purpose — it's session context meant to survive a machine
  switch, not sensitive material. `.ai/*.pdf` is the one exception
  (the subject PDF itself, not a deliverable).
- The final submission is a single zip (dataset + trained model) whose
  `sha1sum` must exactly match a committed `signature.txt` — never re-zip
  after generating that signature.

## Validation checkpoints

Each phase is expected to satisfy `flake8 .` plus a manual check before
being considered done — see `.ai/decisions.md` and `.ai/next-steps.md` for
the authoritative, current per-phase checklist and status. Notably:
`Distribution.py` re-run on `augmented_directory/` after balancing must show
exactly equal class counts — the standard proof that balancing worked.
