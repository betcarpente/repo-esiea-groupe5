# repo-esiea-groupe5

Projet du cours DevOps (groupe 5)

---

## 1. Strategie de branches retenue : Git Flow

### Les branches

| Branche | Role | Duree de vie |
|---|---|---|
| `main` | Code stable, correspond aux versions rendues / livrees. Protegee. | Permanente |
| `develop` | Branche d'integration : tout le travail termine y est fusionne. Protegee. | Permanente |
| `feature/*` | Developpement d'une nouvelle fonctionnalite. Part de `develop`. | Ephemere |
| `fix/*` | Correction d'un bug non urgent. Part de `develop`. | Ephemere |
| `hotfix/*` | Correction urgente sur du code deja en `main`. Part de `main`. | Ephemere |
| `release/*` | Preparation d'une livraison (gel, version). Part de `develop`. | Ephemere |

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

## 3 bis. Qui peut modifier quoi

Deux mecanismes complementaires, car ils ne font pas la meme chose :

| Mecanisme | Ce qu'il fait | Ce qu'il ne fait pas |
|---|---|---|
| `.github/CODEOWNERS` | Assigne automatiquement les relecteurs et, avec « Require review from Code Owners », bloque le **merge** sans l'approbation du proprietaire du chemin | Il n'interdit a personne d'**ecrire** dans un fichier sur sa branche |
| `.github/workflows/path-policy.yml` | Fait **echouer la PR** si son auteur touche un fichier hors de son perimetre | Rien s'il n'est pas declare en « required status check » |

Perimetres retenus :

- `docs/`, `README.md`, `.github/`, `.gitignore` : **betcarpente** uniquement
- `*.py` et `*.txt` : perimetre de **Madaaaaaaaaaaaaaa** (elle ne peut pas
  modifier autre chose)
- le reste du depot : proprietaire par defaut **betcarpente**

Les proprietaires doivent etre des collaborateurs du depot avec le droit
**Write** : le depot n'appartenant pas a une organisation, on ne peut designer
que des utilisateurs (`@pseudo`), pas des equipes (`@org/equipe`).

Limite a connaitre : un **administrateur** du depot peut contourner ces regles
s'il ne coche pas « Do not allow bypassing the above settings », et un push
direct sur une branche non protegee n'est pas verifie.

## 4. Structure du depot

```
.
├── .github/
│   ├── CODEOWNERS                 # Qui est responsable de quels chemins
│   ├── pull_request_template.md   # Template de PR, rempli a chaque PR
│   └── workflows/
│       └── path-policy.yml       # Bloque une PR hors perimetre
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
| betcarpente | Owner |
| Antonin | Maintainer |
| Enzo | Maintainer |
| Salomé | Maintainer |
