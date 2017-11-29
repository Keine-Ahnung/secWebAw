# Implementierte Features

## Registrierung
- [X] User kann ein Account registrieren
- [X] Backend prüft nach, ob User schon existiert
- [ ] Backend prüft auf SQLi
- [X] Backend prüft auf Passwortbestätigung
- [ ] Backend sanitized (normalisiert) Eingabe bzw. escaped

## Account bestätigen
- [X] Mail an User senden
- [X] System sendet zufällige Buchstabenfolge als Mail, muss bei Bestätigung unverändert zurückgeliefert werden
- [X] Bestätigungsstatus in DB ändern nach erfolgreicher Bestätigung
- [X] Rückmeldung an User wenn gleicher Bestätigungslink erneut angeklickt wird
- [ ] Token sanitizen bevor es zur DB geschickt wird

## Login
- [ ] Auf SQLi prüfen


## Nachricht posten
- [ ] Auf XSS prüfen

## Passwort vergessen
- [ ] Auf SQLi prüfen
