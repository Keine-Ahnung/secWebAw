# Implementierte Features

## Registrierung
- [X] User kann ein Account registrieren
- [X] Backend prüft nach, ob User schon existiert
- [ ] Backend prüft auf SQLi
- [X] Backend prüft auf Passwortbestätigung
- [ ] Backend sanitized (normalisiert) Eingabe bzw. escaped
- [ ] Nur Email-Adressen zulassen

## Account bestätigen
- [X] Mail an User senden
- [X] System sendet zufällige Buchstabenfolge als Mail, muss bei Bestätigung unverändert zurückgeliefert werden
- [X] Bestätigungsstatus in DB ändern nach erfolgreicher Bestätigung
- [X] Rückmeldung an User wenn gleicher Bestätigungslink erneut angeklickt wird
- [ ] Token sanitizen bevor es zur DB geschickt wird

## Login
- [X] Auf SQLi prüfen
- [ ] Rollen für User abrufen und in die Session eintrage (für Admin Dashboard)


## Nachricht posten
- [ ] Auf XSS prüfen

## Passwort vergessen
- [ ] Auf SQLi prüfen

## Session
- [ ] Pollingservice der Sessionstartzeiten ständig überprüft und Benutzer ausloggt, die zu lange inaktiv waren