AGGIORNAMENTO REPOSITORY SAMMA UNDER 14

Sostituisci questi due file nel repository GitHub:
- genera_calendario.py (cartella principale)
- .github/workflows/aggiorna.yml (mantieni il percorso)

Non cancellare samma-under14.ics: sarà aggiornato dal workflow.
Non modificare GitHub Pages: rimane branch main / (root).
La variabile JSON_URL non è più utilizzata e può essere eliminata dopo aver verificato la nuova esecuzione.

Avvia Actions -> Aggiorna calendario Samma Under 14 da FIPAV -> Run workflow.
Il workflow scarica la pagina FIPAV, legge le 14 gare della Samma Under 14, include palestre e link Google Maps, poi aggiorna il file ICS.
Se il sito FIPAV cambia formato o non restituisce le gare, il workflow fallisce senza sovrascrivere il file ICS.

Nota: verificato su HTML fornito il 7 novembre 2026; accessibilità del sito da GitHub Actions da confermare alla prima esecuzione.
