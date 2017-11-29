# Securitychecks
- [ ] Wo sollen Eingaben geprüft und sanitized werden? Direkt im Backend oder im DB Handler?


# Schwachstellen

Welche Schwachstellen sollen überprüft und sanitized werden?

1. SQL Injection (SQLi)
1. Cross Site Scripting (XSS)

# Mitigation
## SQLi

Verwendung einer Escaped Substitution, wenn Daten über einen SQL-Cursor an die Datenbank übergeben werden.

```python
cursor.execute("select email, verified from " + self.DB_TABLE_TRALALA_USERS + " where verification_token=\"%s\"", (token,))
```

Mithilfe von `%s` und der Übergabe eines Tupels mit `,(var)` wird der String escaped an den Cursor übergeben. Die Verwendung von `%s` mittels `% (var)` würde einer direkt Stringsubstitution gleichkommen.

*Test durchführen, ob das auch wirklich so ist* [StackOverflow](https://stackoverflow.com/questions/7929364/python-best-practice-and-securest-to-connect-to-mysql-and-execute-queries)

1. X