# Sicherheitsrisiken und L�sungen

## index.html

Kommentarblock l�schen (wird aber redundant, sobald HTML in der Postbox nicht gerendert wird)

## Registrierung

Trennung der Email durch Semikolon (mehrere Emails). Die Best�tigungsemail wird dennoch an die erste Email-Adresse gesendet.

**L�sung:** �berpr�fung im Backend auf Email Format mit Regex.

## Passwort�berpr�fung

Mit W3-Code das Passwort auf dessen St�rke w�hrend der Eingabe �berpr�fen. 


**L�sung:** Implementierung W3Schools Password Validation im Frontend als auch im Backend (siehe Regex die von diesem Code bereitgestellt wird)

## E-Mail

**L�sung:** �berpr�fe bei der Registrierung, ob die Email schon verwendet wurde.

## SQLi 

**L�sung:** Escaped Stringsubstitution konsequent in allen SQL-Abfragen durchziehen

## Zeit

Serverzeit nicht synchron (-1 h)

# Sitzung

Timeout f�r Sitzungen implementieren.

## Post

- XSS in Nachricht und Hashtags
- Hashtags nur mit Komma eingeben
- HTML Entity Injection (HTML darf nicht gerendert werden)

**L�sungen:**
- HTTP-Only und Secury Flag
- Nachrichtenl�nge im Frontend auf 280 Zeichen beschr�nken in HTML Tag
- Pr�fung der Hashtagliste im Frontend (durch Kommatrennung)

## CSRF

CSRF-System �berarbeiten.