# Sicherheitsrisiken und Lösungen

## index.html

Kommentarblock löschen (wird aber redundant, sobald HTML in der Postbox nicht gerendert wird)

## Registrierung

Trennung der Email durch Semikolon (mehrere Emails). Die Bestätigungsemail wird dennoch an die erste Email-Adresse gesendet.

**Lösung:** Überprüfung im Backend auf Email Format mit Regex.

## Passwortüberprüfung

Mit W3-Code das Passwort auf dessen Stärke während der Eingabe überprüfen. 


**Lösung:** Implementierung W3Schools Password Validation im Frontend als auch im Backend (siehe Regex die von diesem Code bereitgestellt wird)

## E-Mail

**Lösung:** Überprüfe bei der Registrierung, ob die Email schon verwendet wurde.

## SQLi 

**Lösung:** Escaped Stringsubstitution konsequent in allen SQL-Abfragen durchziehen

## Zeit

Serverzeit nicht synchron (-1 h)

# Sitzung

Timeout für Sitzungen implementieren.

## Post

- XSS in Nachricht und Hashtags
- Hashtags nur mit Komma eingeben
- HTML Entity Injection (HTML darf nicht gerendert werden)

**Lösungen:**
- HTTP-Only und Secury Flag
- Nachrichtenlänge im Frontend auf 280 Zeichen beschränken in HTML Tag
- Prüfung der Hashtagliste im Frontend (durch Kommatrennung)

## CSRF

CSRF-System überarbeiten.