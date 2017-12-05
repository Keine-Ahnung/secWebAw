# Implementierte Features

## Zugriff auf die Datenbank
- [ ] Benutzen von Stored Procedures
- [ ] autogenerate tech. user

## Registrierung
- [X] User kann ein Account registrieren
- [X] Backend prüft nach, ob User schon existiert
- [ ] Backend prüft auf SQLi
- [X] Backend prüft auf Passwortbestätigung
- [X] Backend sanitized (normalisiert) Eingabe bzw. escaped
- [ ] Nur Email-Adressen zulassen

## Account bestätigen
- [X] Mail an User senden
- [X] System sendet zufällige Buchstabenfolge als Mail, muss bei Bestätigung unverändert zurückgeliefert werden
- [X] Bestätigungsstatus in DB ändern nach erfolgreicher Bestätigung
- [X] Rückmeldung an User wenn gleicher Bestätigungslink erneut angeklickt wird
- [ ] Token sanitizen bevor es zur DB geschickt wird

## Login
- [X] Auf SQLi prüfen
- [ ] prüfen ob user schon verifiziert ist
- [ ] Rollen für User abrufen und in die Session eintragen (für Admin Dashboard)


## Nachricht posten
- [X] Auf XSS prüfen (sollte durch Verwendung von `, (val)` escaped werden)
- [X] Nachricht in DB posten mit Postdaten
- [X] Es können keine leeren Posts abgesendet werden (wird client- und serverseitig überprüft)


## Passwort vergessen
- [ ] Auf SQLi prüfen

## Session
- [ ] Pollingservice der Sessionstartzeiten ständig überprüft und Benutzer ausloggt, die zu lange inaktiv waren

## Postliste
- [X] Zufällige Auswahl von Farben für den Hintergrund von Posts
- [X] Email über dem Post anzeigen
- [X] Up- und Downvotebuttons durch Links (mit Icons) ersetzen
- [ ] Zeilenumbruch für lange Nachrichten einfügen
- [ ] Es dürfen nur Benutzer posten, deren Account verifiziert ist
- [ ] Was passiert, wenn Hashtags nicht im erwarteten Format angegeben wurden?
- [ ] Pro Post darf nur ein User voten
- [ ] Wenn Benutzer gelöscht wurde, zeige OP als unbekannt an

## Voting
- [ ] Ungültige Formen von Parametern: IDs als Text, IDs negativ oder zu groß, ...

## Security
- [x] Implemented a method to strip down html from messagebox
- [x] Implemented method to strip down html and # from hashtags. Method is based on the change request.
- [x] Check password strength (Length, Charset)
- [x] Check if mail is correct

## Changerequests
- [x] Change method to store the hashtags from the actual to something like: Storing data in database splitted by,
      Read list from db and add # before rendering
