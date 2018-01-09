# Inputchecks

- Registrierung
	* E-Mail
	* Passwort
	* Passwortbestätigung
	* Confirmtoken
- Login
	* E-Mail
	* Passwort
- Passwort vergessen
	* E-Mail
	* Resettoken
	* Neues Passwort
	* Neues Passwort bestätigen
- Neuer Post
	* Nachricht
	* Hashtags
- Vote
	* URL
	* Verifikationstoken
- Dashboard
	* Passwortbestätigung
- E-Mail ändern
	* Neue E-Mail
	* Neue E-Mail wiederholen
	* Passwort
- Passwort ändern
	* Altes Passwort
	* Neues Passwort
	* Neues Passwort wiederholen

### Registrierung

**E-Mail** (`post_user()`)

Check auf Länge (> 0) und korrektes Format mit `security_helper.check_mail()`

**Password** (`post_user()`)

Check auf Länge (> 0) und Passwortstärke/-richtlinien mit `security_helper.check_password_strength()`'

**Passwortbestätigung** (`post_user()`)

Check auf Länge (> 0) und Passwortstärke/-richtlinien mit `security_helper.check_password_strength()`

**Confirmtoken** (`confirm()`)

Check auf Länge (> 0) und korrektes Format mit `function_helper.check_params()` . Dies prüft, ob `str.isalphanum()`. Sind Sonderzeichen im Token enthalten, wird ein Fehler ausgegeben. SQLi oder ähnliches wird vom DB-Handler in `get_user_for_token()` durch Escaped Statements überprüft.

### Login

**E-Mail** (`login()`)

Check auf Länge (> 0). SQLi-Handling durch Escaped Statement in `check_for_existence()`.

**Passwort** (`login()`)

Check auf Länge (> 0). Überprüfung auf SQLi nicht nötig, da dieser Input nie in Kontakt mit der Datenbank gerät.

### Passwort vergessen

**E-Mail** (`handle_password_request()`)

E-Mail wird Länge (> 0) und richtiges E-Mail-Format geprüft. Anschließend wird in `check_for_existence()` die Möglichkeit auf eine SQLi durch ein Escaped Statement verhindert.

**Resettoken** (`handle_password_request()`)

Übergebenes Resettoken wird zu erst mithilfe von `check_params()` überprüft, ob es exklusiv alphanumerisch ist, gängige Sonderzeichen bei einer SQLi wie `'` oder `);` werden dadurch nicht erlaubt. Weiterhin wird das nach dem Token in der Datenbank gesucht mit `get_reset_token()`. Dafür wird ein Escaped Statement verwendet, welches alle Sonderzeichen escaped.

**Neues Passwort** (`set_new_password()`)

Passwort wird auf Länge (> 0) geprüft als auch auf dessen Übereinstimmung mit unseren Passwortrichtlinien. Mögliche SQLi werden durch Escaped Statements verhindert.

**Neues Passwort bestätigen*** (`set_new_password()`)

Passwortbestätigung wird auf Länge (> 0) geprüft als auch auf dessen Übereinstimmung mit unseren Passwortrichtlinien. Mögliche SQLi werden durch Escaped Statements verhindert.

### Neuer Post

**Nachricht** (`post_message()`)

Die eingegebene Nachricht wird auf Länge (> 0) getestet. Bei dem Persistieren der Nachricht in die Datenbank wird diese mithilfe des `bleach`-Packages gesäubert: das bedeutet, dass nur HTML-Tags wie `<br>`, `<b>`, `<i>` und `<strong>` zulässig sind. Dies soll eine bis zu einem gewissen Grad individualisierbare Nachricht ermöglichen. Alle anderen nicht zulässigen Zeichen werden in HTML-Entities umgewandelt. Diese werden vom Browser nicht interpretiert, was XSS-Attacken verhindert. Beim Schreiben in die Datenbank werden wieder Escaped Statements verwendet, was SQLi unterbindet.

**Hashtags** (`post_message()`)

Die eingegebenen Hashtags werden auf Länge (> 0) getestet. Bei dem Persistieren der Hashtags in die Datenbank werden diese mithilfe des `bleach`-Packages gesäubert: das bedeutet, dass für die Hashtags keinerlei HTML-Tags zulässig sind. Alle Tags werden in HTML-Entities umgewandelt. Diese werden vom Browser nicht interpretiert, was XSS-Attacken verhindert. Beim Schreiben in die Datenbank werden wieder Escaped Statements verwendet, was SQLi unterbindet.

### Vote

**URL** (`vote()`)

Sollte in der URL die Art des Votes verändert werden, also ob Up- oder Downvote, wird dies erkannt und mit einer entsprechenden Fehlerseite behandelt. Der `post_id`-Parameter nimmt ebenfalls nur Zahlen entgegen. Wird diesem Parameter eine unbekannte Post-ID übergeben, wird dies mit einer entsprechenden Fehlerseite behandelt. Die Angabe anderer gültiger Post-IDs ist möglich, da darin keine Angriffsmöglichkeit erkannt wird.

**Verifikationstoken** (`vote()`)

Eine Angriffsmöglichkeit auf das Verifikationstoken selbst ist uns nicht bekannt, da lediglich das gespeicherte als auch das zurückgelieferte Token auf Gleichheit überprüft werden.

### Dashboard

**Passwortbestätigung** (`delete_user()`)

Das eingegebene Passwort kommt nicht in Berührung mit der Datenbank. Um das eingegebene Passwort zu verifizieren, wird der in der Session eingetragene Benutzer verwendet. Das eingegebene Passwort dient lediglich als Vergleichswert.

### E-Mail ändern

**Neue E-Mail** (`change_email_handler()`)

Die neue E-Mail wird auf Länge (> 0) und auf korrektes E-Mail Format überprüft. Die neue E-Mail-Addresse wird anschließend temporär in einer Datenbanktabelle zwischengespeichert. Die Persistierung erfolgt über ein Escaped Statement und verhindert somit SQLi.

**Neue E-Mail wiederholen** (`change_email_handler()`)

Die Bestätigung der E-Mail wird auf Länge (> 0) und korrektes E-Mail Format überprüft. Jedoch kommt diese Eingabe nie in Berührung mit der Datenbank und dient lediglich als Referenzwert, weshalb dieser kein Sicherheitsrisiko zugeschrieben wird.

**Passwort** (`change_email_handler()`)

Das Passwort wird lediglich als Referenzwert verwendet. Mithilfe der in der Session gespeicherten E-Mail des angemeldeten Benutzers wird der Hash des Passworts aus der Datenbank ermittelt und im Anschluss gegen das eingegebene Passwort überprüft. Dieser Eingabe wird kein Sicherheitsrisiko zugeschrieben, da dieses nicht in Berührung mit der Datenbank kommt.

### Passwort ändern

**Altes Passwort** (`change_password_handler()`)

Das alte Passwort (also das aktuelle Passwort) wird auf dessen Länge und dessen Übereinstimmung mit den Passwortrichtlinien überprüft. Überprüfung auf Stärke eigentlich unnötig, da das schon bei der Registrierung geprüft wurde, wird jedoch aus "Bequemlichkeit" verwendet, da die überprüfende Funktion ebenfalls auf korrektes Format überprüft (was die eigentliche Intention der Überprüng ist).

**Neues Passwort** (`change_password_handler()`)

Das neue Passwort wird auf Länge und Format überprüft. Anschließend wird es temporär in eine Datenbanktabelle geschrieben, während die Bestätigung der Änderung, die per Mail durchgeführt werden muss, aussteht. Die Persistierung in die Datenbank geschieht über ein Escaped Statement, was SQLi unterbindet.

**Neues Passwort wiederholen** (`change_password_handler()`)

Dient lediglich als Referenzwert, um die Änderung registrieren zu können. Kommt nicht mit der Datenbank in Verbindung und stellt deshalb kein Sicherheitsrisiko dar.

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
1. Fehlermeldungen
1. Deaktivieren des Debug-Modus

# Mitigation
## SQL Injection

Verwendung einer Escaped Substitution, wenn Daten über einen SQL-Cursor an die Datenbank übergeben werden.

```python
cursor.execute("select email, verified from " + self.DB_TABLE_TRALALA_USERS + " where verification_token=\"%s\"", (token,))
```

Mithilfe von `%s` und der Übergabe eines Tupels mit `, (var)` (mit einem Komma) wird der String escaped an den Cursor übergeben. Die Verwendung von `%s` mittels `% (var)` würde einer direkt Stringsubstitution gleichkommen.

Zusätzlich wurden nachträglich Stored Procedures verwendet. Dies sind festgelegte Abfragepläne innerhalb der Datenbank. Mehr Informationen dazu unter [MSDN](https://blogs.msdn.microsoft.com/brian_swan/2011/02/16/do-stored-procedures-protect-against-sql-injection/).

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
- HTTP-Only und Secure Flag
- Nachrichtenlänge im Frontend auf 280 Zeichen beschränken in HTML Tag
- Prüfung der Hashtagliste im Frontend (durch Kommatrennung)

## Serverzeit

Zeitstempel in den Logs stimmt nun.

## Cross Site Request Forgery (CSRF)

**TODO** Muss überarbeitet werden.

## Attacke auf den Passwort Reset

Reset Token und UID werden über den Reset Link mitgegeben. Suche mithilfe der über die URL spezifizierten UID in der Datenbank nach einem Reset Token. Wurde eins gefunden, vergleiches diese Token mit dem über die URL mitgelieferten Token. Sind diese Token identisch, erlaube dem Benutzer sein Passwort zu ändern. Ändere nur das Passworts des Benutzers mit der UID, welche in der Datenbank mit dem Token gespeichert wurde und nicht die UID, die der Benutzer über die URL mitgegeben hat.

Spam durch Passwort Reset Funktion: Erlaube maximal 5 gleichzeitige Password Change Requests (um Spam durch diese Funktion zu verhindern), resette Sperre nach erfolgreicher Änderung

## Fehlermeldungen

Möchte ein Benutzer ungültige Seiten wie z.B. `<seite>/ungueltigerPfad` aufrufen (was einen HTTP 400 Error generieren würde) wird der Benutzer stattdessen auf die Indexseite weitergeleitet, was es verhindert, möglicherweise Fehlermeldungen auszugeben (bspw. im Fall, dass der Debug-Modus in `app.run(debug=True)` versehentlich aktiviert gelassen wurde)

## Deaktivieren des Debug-Modus

Bei auftretenden Fehlermeldungen z.B. beim Anfordern einer unbekannten Ressource werden Fehlermeldungen direkt im Browser auf einer Flask-spezifischen Debugseite angezeigt. Ein gravierendes Sicherheitsrisiko besteht darin, dass diese Fehlerseiten absolute Dateipfade preisgeben, wie z.B. im folgenden Beispiel.

Aufgerufen wurde die URL `http://localhost:5000/auth/vote?method=upvawote&post_id=6`. In dem Pfad wurde anstatt "upvote" "upvawote" eingegeben, was zu einem Fehler führt. Ist der Debug-Modus durch `app.run(debug=True)` aktiviert, wird folgender Output generiert (verkürzte Darstellung):

```
File "E:\IT Security\ITSBSc7\Sichere Webanwendungen\Praktikum\repo\secWebAw\webapp\tralala\main.py", line 483, in vote
method_label=method_labels[method])
KeyError: 'upvawote'
```
Dieser Modus kann durch `app.run(debug=True)` deaktiviert werden. Somit wird nur noch eine generische Fehlerseite für den HTTP-Errorcode 500 angezeigt.

# Konformität mit Webapp Skript

### Testen

* X TLS
* X Crawling/Spidering
* ✓ Alle möglichen Inputs ermitteln
* X Alle Rollen und deren Rechte ermitteln
* X automatisiert auf Schwachstellen prüfen
* ✓ Default Credentials (haben wir nicht)
* X Default Content (Debug-Error Seiten)
* ✓ Hidden Content (haben wir nicht)
* X gefährliche HTTP-Methoden (` @app.route("/pfad", ["GET", "POST"])`)
* X Verwendung der Webapp als Proxy
* X Verwendung der Webapp als Spammer
* X Hosting Misconfiguration
* X Software Bugs
* X Updateprozess implementieren, um gefundene Schwachstellen schnell zu patchen (brauchen wir sowas wirklich? App wird nach Abgabe nicht mehr gewartet)
* X Server Hardening (bezieht auch Rechte des technischen DB-Users mit ein)

### Clientseitige Schwachstellen

* X Feldlängen
* X Hidden Fields
* X Client Side Input Validation
* ✓ Java Applets die dekompiliert und analysiert werden (haben wir nicht)
* ✓ Active X Objekte die dekompiliert und analysiert werden (haben wir nicht)
* ✓ Flash Objekte die dekompiliert und analysiert werden (haben wir nicht)

### Clientseitige Schwachstellen (Gegenmaßnahmen)

* X Alle Inputs Server Side checken
* X Client Side Checks möglich (und erwünscht), sind aber nur für die Convenience da

### Authentication Schwachstellen

* ✓ Passwortstärke und -richtlinien
* X User Enumeration
* X Passwort Guessing
* X Sichere Account Recovery
* ✓ Remember Me (haben wir nicht)
* ✓ Automatisch generierte Passworter (haben wir nicht)
* X Übertragung von Credentials (nur über TLS)
* X Verteilung von Credentials (bspw. keine Klartextpasswörter an die Mail schicken, aber Link generieren, über den das Klartextpasswort eingesehen werden kann)

### Authentication Schwachstellen (Gegenmaßnahmen)

* ✓ Passwortqualität erzwingen
* X Bruteforce-Schutz (Tracking wie oft ein User sich schon von IP X anmelden wollte)
* ✓ Sichere Passwortspeicherung (mit Salt gehasht und als Hash abgespeichert)
* ✓ angemessene Login Forms. Soll keine Rückschlüsse über existierende Benutzer zulassen. Nach Absenden kann Auskunft über bereits existierenden Benutzer gegeben werden, aber nicht direkt im Login Form (da hilfreich für automatische User Enumeration)
* X Übertragung über TLS
* ✓ angemessene Account Recovery (läuft bei uns über die E-Mail. Sicher genug?)

### Session Management Schwachstellen

* X Wie sieht die Verwendung des Tokens innerhalb der App aus (?)
* ✓ Tokens können nicht vorhergesagt werden (zumindest nicht ohne extremen Aufwand)
* X Übertragung per HTTP (HttpSecure-Flag)
* ✓ Tokens werden als Cookie gespeichert und nicht in der URL
* X Session Termination (?)
* X Session Fixation
* X Cookie Scope (?)

### Session Management Schwachstellen (Gegenmaßnahmen)

* ✓ kryptografisch sicheres Session Management (Verschlüsselung mit Master Key)
* ✓ sichere Tokengenerierung
* X Session Timeouts (unterschiedliche Zeiten für unterschiedlich kritische Transaktionen)
* X Nonces für Requests (Anti-CSRF)
* ✓ Re-Authentication bei kritischen Transaktionen/Funktionen
* X Regenerierung des Session Tokens bei kritischen Anwendungen (nötig bei unserer Webapp? Wir haben keine hochkritischen Anwendungen)
* X Generelle Regenerierung des Session Tokens (brauchen wir das?)
* X Tokens nicht wiederverwenden (muss noch nachgeprüft werden)
* ✓ Transportverschlüsselung (gesamtes Session Cookie ist durch Master Key verschlüsselt)

### Access Controls Schwachstellen

* ✓ Sicherer Zugriffsschutz (User A kann keine Daten von User B abrufen)
* ✓ Privilege Escalation nur bei direktem Zugriff auf die Datenbank möglich
* ✓ Horizontale Privilege Escalation nicht möglich
* ✓ Vertikale Privilege Escalation nicht möglich
* ✓ Durch Direktlink auf Seiten zugreifen und Access Control umgehen (Seite mit Access Control check auch immer nach Rollen ID)
* ✓ SQLi (nicht möglich durch Stored Procedures)

### Access Controls Schwachstellen (Gegenmaßnahmen)

* X Zugriffsmodell (benötigt Review)
* X Zugriffsframework (nötig bei uns?)
* X Manual Review und Test

### Injection Attacks

* ✓ SQL injection
* X XSS (neue Überprüfung nach eigener Implementierung für Input Sanitizer)
* ✓ LDAP Injection (haben wir nicht)
* ✓ SMTP Injection (haben wir nicht)
* ✓ SOAP Injection (haben wir nicht)
* ✓ XPath Injection (haben wir nicht)
* ✓ OS Command Injection (Webapp hat keinen direkten Zugriff auf das OS, höchstens über SQLi möglich)
* [FuzzDB](github.com/fuzzdb-project/fuzzdb)
* [SecLists](github.com/danielmiessler/SecLists)






































