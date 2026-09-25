# Rollback manuel

```bash
git log --oneline --decorate -10
git checkout -b fix/rollback-version
git revert <sha-du-commit-a-annuler>
git diff HEAD^ HEAD
git push -u origin fix/rollback-version
```

Ouvrir ensuite une PR attendre le workflow et fusionner la PR