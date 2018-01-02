# Securitychecks
- [ ] Wo sollen Eingaben geprüft und sanitized werden? Direkt im Backend oder im DB Handler?

# Inputchecks
- Registrierung
	* E-Mail
	* Passwort
	* Passwortbestätigung
- Login
	* E-Mail
	* Passwort

# Schwachstellen

Welche Schwachstellen sollen überprüft und sanitized werden?

1. SQL Injection (SQLi)
1. Cross Site Scripting (XSS)
1. User Enumeration über das Verification Token
1. Session Tampering
1. Clientseitige Überprüfung
1. Trennung der Email durch Semikolon (mehrere Emails). Die Bestätigungsemail wird dennoch an die erste Email-Adresse gesendet.
1. Serverseitige Überprüfung
1. Serverzeit
1. Cross Site Request Forgery (CSRF)
1. Attacke auf den Passwort Reset


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

## Trennung der Email durch Semikolon (mehrere Emails). Die Bestätigungsemail wird dennoch an die erste Email-Adresse gesendet.

Überprüfung im Backend auf Email Format mit Regex.

## Serverseitige Überprüfung

### Eingabestärke

Mit W3-Code das Passwort auf dessen Stärke während der Eingabe überprüfen. Implementierung W3Schools Password Validation im Frontend als auch im Backend (siehe Regex die von diesem Code bereitgestellt wird).

### Registrierungsmail

Überprüfung, ob E-Mail bei der Registrierung schon bekannt ist.

#### Posts

- XSS in Nachricht und Hashtags
- Hashtags nur mit Komma eingeben
- HTML Entity Injection (HTML darf nicht gerendert werden)

Lösungen:
- HTTP-Only und Secury Flag
- Nachrichtenlänge im Frontend auf 280 Zeichen beschränken in HTML Tag
- Prüfung der Hashtagliste im Frontend (durch Kommatrennung)


## Serverzeit

**TODO** Serverzeit nicht synchron (-1 h).

## Cross Site Request Forgery (CSRF)

**TODO** Muss überarbeitet werden.

## Attacke auf den Passwort Reset

Reset Token und UID werden über den Reset Link mitgegeben. Suche mithilfe der über die URL spezifizierten UID in der Datenbank nach einem Reset Token. Wurde eins gefunden, vergleiches diese Token mit dem über die URL mitgelieferten Token. Sind diese Token identisch, erlaube dem Benutzer sein Passwort zu ändern. Ändere nur das Passworts des Benutzers mit der UID, welche in der Datenbank mit dem Token gespeichert wurde und nicht die UID, die der Benutzer über die URL mitgegeben hat.


Spam durch Passwort Reset Funktion: Erlaube maximal 5 gleichzeitige Password Change Requests (um Spam durch diese Funktion zu verhindern), resette Sperre nach erfolgreicher Änderung 