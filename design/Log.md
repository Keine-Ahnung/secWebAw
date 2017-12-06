# Zu klären

- Sollen wir in User Messages nur br, b, i und strong zulassen? bleach.ALLOWED_TAGS ist etwas liberaler und lässt den Benutzern auch mehr Freiheit, ihre eigenen
Posts besser zu designen


# Implementierte Features

## Zugriff auf die Datenbank
- [ ] Benutzen von Stored Procedures

## Registrierung
- [X] User kann ein Account registrieren
- [X] Backend prüft nach, ob User schon existiert
- [X] Backend prüft auf SQLi
- [X] Backend prüft auf Passwortbestätigung
- [X] Backend sanitized (normalisiert) Eingabe bzw. escaped
- [x] Nur Email-Adressen zulassen
- [x] Backend ist nicht mehr buchstabensensitiv (es wird nur mit lowercase in den E-Mail Adressen gearbeitet)

## Account bestätigen
- [X] Mail an User senden
- [X] System sendet zufällige Buchstabenfolge als Mail, muss bei Bestätigung unverändert zurückgeliefert werden
- [X] Bestätigungsstatus in DB ändern nach erfolgreicher Bestätigung
- [X] Rückmeldung an User wenn gleicher Bestätigungslink erneut angeklickt wird
- [ ] Token sanitizen bevor es zur DB geschickt wird

## Login
- [X] Auf SQLi prüfen
- [x] Nur verifizierte Benutzer können sich einloggen
- [ ] Rollen für User abrufen und in die Session eintragen (für Admin Dashboard)


## Nachricht posten
- [X] Auf XSS prüfen (sollte durch Verwendung von `, (val)` escaped werden)
- [X] Nachricht in DB posten mit Postdaten
- [X] Es können keine leeren Posts abgesendet werden (wird client- und serverseitig überprüft)
- [ ] Nachrichten die reinkopiert werden bekommen keinen Linebreak, Nachrichten, die man schreibt jedoch schon

## Session
- [X] Timestamp bei Erstellung der User Session anlegen, nach jedem weiterem Request der selben Session überprüfen, ob inaktiv
- [X] User wird nach einer bestimmten Zeit automatisch ausgeloggt und die Session wird aus der zugehörigen Tabelle entfernt

## Postliste
- [X] Zufällige Auswahl von Farben für den Hintergrund von Posts
- [X] Email über dem Post anzeigen
- [X] Up- und Downvotebuttons durch Links (mit Icons) ersetzen
- [ ] Zeilenumbruch für lange Nachrichten einfügen
- [X] Es dürfen nur Benutzer posten, deren Account verifiziert ist
- [ ] Was passiert, wenn Hashtags nicht im erwarteten Format angegeben wurden?
- [X] Pro Post darf nur ein User voten
- [ ] Wenn Benutzer gelöscht wurde, zeige OP als unbekannt an

## Voting
- [ ] Ungültige Formen von Parametern: IDs als Text, IDs negativ oder zu groß, ...

## Security
- [x] Implemented a method to strip down html from messagebox
- [x] Implemented method to strip down html and # from hashtags. Method is based on the change request.
- [x] Check password strength (Length, Charset)
- [x] Check if mail is correct
- [x] Use escaped string substitution for parametrized SQL queries
- [x] Corrected logic flaws in the validation of the password strength
- [x] Set HttpOnly und Secure Flags

## Skripte
- [X] Generierung des technischen Benutzers durch das Skript
- [X] Rechtevergabe durch SQL-Skript
- [X] Passwörter für Mockdaten durch Webapp generieren lassen, sodass sie im PKCS-Format geschrieben werden können

## Changerequests
- [x] Change method to store the hashtags from the actual to something like: Storing data in database splitted by,
      Read list from db and add # before rendering

