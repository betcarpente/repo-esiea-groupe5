# repo-esiea-groupe5

Projet du cours DevOps (ESIEA, 5e annee) — Groupe 5.

Ce README fait foi : toute personne qui rejoint le groupe doit pouvoir y trouver
la strategie de branches, la convention de nommage et la regle de merge sans
avoir a redemander.

---

## 1. Strategie de branches retenue : Git Flow

Apres discussion, le groupe a choisi **Git Flow** (et non le trunk-based
development).

**Pourquoi ce choix :**

- Le projet est rendu par lots (etapes notees), pas deploye en continu : on a
  besoin d'une branche stable qui represente le rendu, distincte de la branche
  de travail quotidien.
- Nous sommes plusieurs a travailler en parallele sur des sujets differents ;
  des branches thematiques limitent les conflits.
- Le flux impose une PR pour chaque contribution, ce qui est exactement ce que
  l'exercice demande (relecture, protection de branche, historique lisible).
- Le trunk-based supposerait des merges tres frequents sur `main` avec des
  feature flags et une CI solide : disproportionne a l'echelle du projet.

### Les branches

| Branche | Role | Duree de vie |
|---|---|---|
| `main` | Code stable, correspond aux versions rendues / livrees. Protegee. | Permanente |
| `develop` | Branche d'integration : tout le travail termine y est fusionne. Protegee. | Permanente |
| `feature/*` | Developpement d'une nouvelle fonctionnalite. Part de `develop`. | Ephemere |
| `fix/*` | Correction d'un bug non urgent. Part de `develop`. | Ephemere |
| `hotfix/*` | Correction urgente sur du code deja en `main`. Part de `main`. | Ephemere |
| `release/*` | Preparation d'une livraison (gel, version). Part de `develop`. | Ephemere |
| `docs/*` | Documentation seule (README, rapports, schemas). Part de `develop`. | Ephemere |
| `chore/*` | Maintenance : config, CI, dependances, .gitignore. Part de `develop`. | Ephemere |

```
main      --*-----------------*--------------*-->    (versions rendues)
             \               /   \          /
release       \          *--*     \     *--*         (release/1.0.0)
               \        /          \   /
develop   --*---*--*---*------------*-*--------->    (integration)
             \ /    \ /
feature       *      *                               (feature/xxx, fix/xxx)
```

### Convention de nommage des branches

Format : `<type>/<description-courte-en-kebab-case>`

- `<type>` parmi `feature` | `fix` | `hotfix` | `release` | `docs` | `chore`
- description en **minuscules**, mots separes par des **tirets**, sans accents,
  3 a 5 mots maximum
- pas d'espace, pas de majuscule, pas de caractere special
- si un ticket / une issue existe, on prefixe la description par son numero

Exemples valides :

```
feature/user-authentication
feature/12-ajout-page-login
fix/crash-au-demarrage
fix/34-mauvais-calcul-total
hotfix/token-expire
release/1.0.0
docs/readme-strategie-branches
chore/ajout-github-actions
```

Exemples a proscrire : `ma_branche`, `Test`, `nicolas`, `patch-1`,
`feature/Correction Du Bug`.

Les branches `release/*` sont nommees avec un numero de version en
[SemVer](https://semver.org/lang/fr/) : `release/MAJEUR.MINEUR.CORRECTIF`.

### Convention de messages de commit

On utilise [Conventional Commits](https://www.conventionalcommits.org/fr/) :

```
<type>(<perimetre optionnel>): <description a l'imperatif>
```

Types acceptes : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

Exemples : `feat(auth): ajoute la connexion par email`,
`fix: corrige le calcul du total panier`, `docs: complete le README`.

---

## 2. Regle de merge

**Aucun push direct sur `main` ni sur `develop`.** Tout passe par une Pull
Request.

### Le cycle d'une contribution

1. Se placer sur `develop` a jour : `git checkout develop && git pull origin develop`
2. Creer sa branche selon la convention : `git checkout -b feature/ma-fonctionnalite`
3. Commiter, puis pousser : `git push -u origin feature/ma-fonctionnalite`
4. Ouvrir une **Pull Request vers `develop`** en remplissant le template
   (`.github/pull_request_template.md`)
5. Demander une relecture a un autre membre du groupe

### Conditions pour fusionner une PR

Une PR ne peut etre fusionnee que si **toutes** ces conditions sont reunies :

- [ ] au moins **1 approbation** d'un autre membre du groupe (l'auteur ne
      s'auto-approuve jamais)
- [ ] toutes les conversations de revue sont resolues
- [ ] la branche est **a jour avec la branche cible** (rebase ou merge de
      `develop` avant de fusionner)
- [ ] les verifications automatiques (CI) sont au vert, quand elles existent
- [ ] le template de PR est rempli (description + type + checklist)

### Methode de merge

| Cible | Methode | Raison |
|---|---|---|
| `feature/*`, `fix/*`, `docs/*`, `chore/*` vers `develop` | **Squash and merge** | Un commit propre par contribution, historique de `develop` lisible |
| `release/*` ou `hotfix/*` vers `main` | **Merge commit** (pas de squash) | On conserve la tracabilite complete de la livraison |
| `main` vers `develop` (apres une release/hotfix) | **Merge commit** | Reinjecte les correctifs dans la branche d'integration |

La branche source est **supprimee apres le merge** (option GitHub
« Automatically delete head branches »).

Le titre du commit de squash reprend la convention Conventional Commits.

### Cas particulier : le hotfix

Un bug critique sur `main` se corrige sur `hotfix/*` depuis `main`, puis est
fusionne **dans `main` ET dans `develop`**, afin que la correction ne soit pas
perdue a la release suivante.

---

## 3. Protection des branches (etape 6)

Les reglages a appliquer sur `main` et `develop` decoulent directement de ce qui
precede :

- Require a pull request before merging
- Require approvals : **1**
- Dismiss stale pull request approvals when new commits are pushed
- Require conversation resolution before merging
- Require branches to be up to date before merging
- Require status checks to pass (une fois la CI en place)
- Bloquer les force push et les suppressions de branche

---

## 4. Structure du depot

```
.
├── .github/
│   └── pull_request_template.md   # Template de PR, rempli a chaque PR
├── docs/                          # Documentation, rapports, schemas
├── src/                           # Code source
├── tests/                         # Tests
├── .gitignore
└── README.md
```

### Ce que le .gitignore exclut (et pourquoi)

Volontairement pose **des le premier commit**, avant qu'un fichier indesirable
n'entre dans l'historique : une fois committe, un secret reste dans l'historique
meme s'il est supprime ensuite.

| Categorie | Exemples | Raison |
|---|---|---|
| Secrets / config locale | `.env`, `*.pem`, `*.key`, `credentials.json` | Ne **jamais** versionner un secret |
| Artefacts Python | `__pycache__/`, `*.pyc`, `*.egg-info/` | Regeneres a l'execution |
| Environnements virtuels | `.venv/`, `venv/`, `env/` | Specifiques a chaque machine, lourds |
| Dependances | `node_modules/` | Reinstallables depuis le manifeste |
| Fichiers systeme | `.DS_Store`, `Thumbs.db`, `Desktop.ini` | Bruit OS, conflits inutiles |
| Config IDE | `.idea/`, `.vscode/`, `*.swp` | Propre a chaque developpeur |
| Build / couverture / logs | `dist/`, `build/`, `htmlcov/`, `*.log` | Generes, pas des sources |
| Donnees et binaires | `*.sqlite`, `*.zip`, `data/raw/` | Alourdissent le depot |

Un fichier `.env.example` (sans valeur reelle) peut etre versionne pour
documenter les variables attendues : il est explicitement autorise par le
`.gitignore`.

---

## 5. Memo des commandes utiles

```bash
# Demarrer une fonctionnalite
git checkout develop && git pull origin develop
git checkout -b feature/ma-fonctionnalite

# Commiter et pousser
git add .
git commit -m "feat: ajoute la fonctionnalite X"
git push -u origin feature/ma-fonctionnalite

# Mettre sa branche a jour avant la PR
git fetch origin
git rebase origin/develop

# Apres le merge de la PR
git checkout develop && git pull origin develop
git branch -d feature/ma-fonctionnalite
```

---

## 6. Membres du groupe

| Nom | Role |
|---|---|
| _a completer_ | _a completer_ |
