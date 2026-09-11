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
| `release/*` ou `hotfix/*` vers `main` | **Squash and merge** | `main` impose un historique **lineaire** (section 3) : GitHub y refuse les merge commits. La tracabilite d'une livraison est portee par le tag `vX.Y.Z`, pas par un commit de merge |
| `main` vers `develop` (apres une release/hotfix) | **Rebase** (`git rebase origin/main`) | Reinjecte les correctifs sans creer de merge commit |

> Ce choix decoule de l'option « Require linear history » activee sur `main` et
> `develop` : merge commits et historique lineaire sont incompatibles, il fallait
> trancher. On garde donc le squash partout.

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

### Sur les branches `main` et `develop`

- Require a pull request before merging
- Require approvals : **1**
- Dismiss stale pull request approvals when new commits are pushed
- Require review from **Code Owners** (active `.github/CODEOWNERS`)
- Require conversation resolution before merging
- Require branches to be up to date before merging
- Require status checks to pass : `Verifier le perimetre de l'auteur`
- **Require linear history** (d'ou le squash systematique, section 2)
- **Do not allow bypassing the above settings** — sans cette case, les
  administrateurs du depot (dont le proprietaire) continuent de pousser
  directement sur `main` : c'est le piege classique
- Allow force pushes / Allow deletions : **decoches**

Une regle de protection classique ne porte qu'**un seul motif de branche** : il
faut donc une regle pour `main` et une pour `develop` (ou un ruleset unique
ciblant les deux). Le champ « Branch name pattern » est bien un motif de nom de
branche, pas un nom de regle.

### Sur les tags de release

La protection des tags ne se fait pas dans la protection de branche, mais via
un **ruleset de tags** (Settings > Rules > Rulesets > New tag ruleset) :

- motif cible : `v*`
- Restrict deletions : un tag `v1.0.0` ne peut plus etre supprime
- Block force pushes : il ne peut plus etre deplace sur un autre commit

### Verification (a faire, pas seulement a cocher)

```bash
# 1. Push direct sur main -> doit echouer avec "GH006: Protected branch update failed"
git checkout main && git pull
echo test >> test-protection.txt
git add test-protection.txt && git commit -m "test: push direct interdit"
git push origin main
git reset --hard origin/main   # nettoyage

# 2. Suppression d'un tag protege -> doit etre refusee
git tag -a v1.0.0 -m "Version 1.0.0" && git push origin v1.0.0
git push origin :refs/tags/v1.0.0
```

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
├── hooks/
│   └── pre-commit                 # Refuse un commit contenant un secret
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

## 4 bis. Securite locale : hook pre-commit et signature

Les regles de la section 3 sont appliquees **par GitHub**, donc au plus tot au
moment du push. Les deux mecanismes ci-dessous agissent en amont, **sur le poste
de chacun**.

### Le hook `pre-commit`

`hooks/pre-commit` est execute par Git avant la creation de chaque commit. Il
inspecte **les lignes ajoutees** dans l'index et refuse le commit s'il detecte :

| Detection | Exemples |
|---|---|
| Cle d'acces AWS | `AKIA` + 16 caracteres |
| Token GitHub | `ghp_...`, `gho_...` |
| Cle d'API Google, token Slack | `AIza...`, `xoxb-...` |
| Cle privee | `-----BEGIN ... PRIVATE KEY-----` |
| Mot de passe en dur | `password = "..."`, `api_key: "..."` |
| URL avec identifiants | `postgres://user:motdepasse@host` | <!-- pragma: allowlist secret -->
| Fichier sensible | `.env`, `*.pem`, `*.key`, `id_rsa`, `credentials.json` |

**Installation — a faire une fois par personne apres le clone :**

```bash
git config core.hooksPath hooks
chmod +x hooks/pre-commit   # inutile sous Windows
```

`.git/hooks/` n'est **ni versionne ni clone** : c'est pour cela que le script
vit dans `hooks/` (suivi par Git) et que `core.hooksPath` l'y redirige. Sans
cette commande, le hook n'existe pas chez toi.

**Test (le commit doit etre refuse) :**

```bash
echo 'AWS_KEY = "AKIA................"' > src/faux_secret.py
git add src/faux_secret.py
git commit -m "test: faux secret"   # -> COMMIT REFUSE, code de sortie 1
git reset && rm src/faux_secret.py
```

Faux positif assume : ajouter le marqueur `pragma: allowlist secret` en
commentaire sur la ligne concernee.

**Limites, a connaitre :** `git commit --no-verify` contourne le hook, et un
hook reste local. C'est une premiere barriere, pas une garantie ; le pendant
cote serveur est le *secret scanning / push protection* de GitHub, actif par
defaut sur les depots publics. Et si un secret reel a fuite, le supprimer ne
suffit jamais : il faut le **revoquer**.

### Signature des commits

Un auteur de commit n'est qu'un champ texte : n'importe qui peut committer sous
le nom d'un autre. Signer un commit y attache une preuve cryptographique, que
GitHub materialise par le badge **Verified**.

Le badge n'apparait que si **les trois** conditions sont reunies : la cle
existe, Git sait qu'il doit s'en servir, et la moitie publique est enregistree
sur le compte GitHub. Un oubli sur l'une des trois donne un commit signe en
local mais jamais verifie cote serveur.

Version **SSH** (recommandee ici : on reutilise la cle qui sert deja a pousser) :

```bash
# 1. Une cle existe ? sinon : ssh-keygen -t ed25519 -C "moi@example.com"
ls ~/.ssh/id_ed25519.pub

# 2. Declarer la cle a Git comme cle de signature
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true

# 3. Enregistrer la cle publique sur GitHub :
#    Settings > SSH and GPG keys > New SSH key > Key type : **Signing Key**
#    (c'est un second ajout, meme si la cle y figure deja en Authentication Key)
cat ~/.ssh/id_ed25519.pub

# Verification
git commit --allow-empty -m "chore: test de signature"
git log --show-signature -1
```

Version **GPG** : `gpg --list-secret-keys --keyid-format=long` pour recuperer
l'identifiant de la cle, `git config --global user.signingkey <ID>`, puis
`gpg --armor --export <ID>` et coller le resultat dans Settings > SSH and GPG
keys > New GPG key.

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
