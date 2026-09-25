# Rollback manuel - atelier 4

Ce rollback concerne un probleme decouvert apres un deploiement deja valide.
Il doit repasser par le pipeline normal, sans modifier directement nginx ou le
fichier `active_color`.

```bash
git log --oneline --decorate -10
git checkout -b fix/rollback-version
git revert <sha-du-commit-a-annuler>
git diff HEAD^ HEAD
git push -u origin fix/rollback-version
```

Ouvrir ensuite une Pull Request vers `main`, attendre la CI et fusionner la PR
selon les regles du depot. Le nouveau push sur `main` reconstruit l'image et
relance le deploiement.