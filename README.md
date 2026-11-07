# Calendario Samma Under 14

Il file `samma-under14.ics` contiene le partite della squadra `rom-93788-samma-under-14`.

## Configurazione
1. Crea un repository GitHub **pubblico** e carica `genera_calendario.py`, `samma-under14.ics` e `.github/workflows/aggiorna.yml`.
2. Apri **Settings → Secrets and variables → Actions → Variables** e crea `JSON_URL`, con il valore `https://DOMINIO-REALE/api/v1/bootstrap` (sostituisci il dominio).
3. Apri **Settings → Pages**, scegli **Deploy from a branch**, branch **main**, cartella **/(root)** e salva.
4. Apri **Actions → Aggiorna calendario Samma Under 14 → Run workflow** per testare la prima esecuzione.
5. Il link dell'abbonamento sarà `https://NOMEUTENTE.github.io/NOMEREPOSITORY/samma-under14.ics`.

La pianificazione è ogni 6 ore (GitHub Actions può ritardare le esecuzioni). Il calendario client determina autonomamente ogni quanto rilegge l'ICS.

**Nota:** per l'aggiornamento automatico l'endpoint JSON deve essere pubblicamente raggiungibile e autorizzato all'accesso; un endpoint che richiede autenticazione o blocca le richieste automatiche richiede una configurazione diversa.
