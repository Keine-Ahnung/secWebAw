# Securitychecks
- [ ] Wo sollen Eingaben geprüft und sanitized werden? Direkt im Backend oder im DB Handler?


# Schwachstellen

Welche Schwachstellen sollen überprüft und sanitized werden?

1. SQL Injection (SQLi)
1. Cross Site Scripting (XSS)
1. User Enumeration über das Verification Token
1. Session Tampering

# Mitigation
## SQL Injection

Verwendung einer Escaped Substitution, wenn Daten über einen SQL-Cursor an die Datenbank übergeben werden.

```python
cursor.execute("select email, verified from " + self.DB_TABLE_TRALALA_USERS + " where verification_token=\"%s\"", (token,))
```

Mithilfe von `%s` und der Übergabe eines Tupels mit `, (var)` (mit einem Komma) wird der String escaped an den Cursor übergeben. Die Verwendung von `%s` mittels `% (var)` würde einer direkt Stringsubstitution gleichkommen.

**Test durchführen, ob das auch wirklich so ist** [StackOverflow](https://stackoverflow.com/questions/7929364/python-best-practice-and-securest-to-connect-to-mysql-and-execute-queries)

## User Enumeration über das Verification Token

Sobald das Token entweder manipuliert wurde wird dem Benutzer eine Seite präsentiert, die ihn darüber informiert, dass der Benutzer mit diesem Token nicht bestätigt wurde (*Der Benutzer konnte nicht bestätigt werden!*). Dadurch wird kein Rückschluss darauf zugelassen, ob ein User mit diesem Token überhaupt existiert. Wird ein User erneut über eine Bestätigungs-URL bestätigt, wird eine andere Nachricht präsentiert (*Der Benutzer wurde bereits bestätigt!*).

## Session Tampering

Backend reagiert nur auf valide Session Tokens, andere werden mit generischen Nachrichten abgefangen.

## Clientseitige Überprüfung

Alles, was clientseitig durch JavaScript überprüft wird, muss ebenfalls serverseitig überprüft werden, da die Überprüfungen durch einen erfahrenen Anwender/Hacker aus der Seite entfernt werden können. Dies betrifft:

* Überprüfung der Passwortstärke
* Sind alle Eingabefelder ausgefüllt?
* Sind alle Eingabefelder im richtigen Format?
* ...