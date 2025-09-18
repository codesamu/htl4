# REST-Client (Python) für Users-API

Basis-URL: `http://10.10.11.11:5003/api/users`

## Installation

```bash
python3 -m pip install -r requirements.txt
```

## Verwendung

Allgemeines Schema:
```bash
python3 client.py [COMMAND] [OPTIONS]
```

Verfügbare Commands:
- `list`: Alle Benutzer auflisten
- `get`: Einen Benutzer per ID holen
- `create`: Einen neuen Benutzer anlegen
- `search`: Client-seitige Suche in Name/Email (Substring)

Optional kann die Basis-URL überschrieben werden:
```bash
python3 client.py --base-url http://10.10.11.11:5003/api/users list
```

## Beispiele

- Alle Benutzer:
```bash
python3 client.py list
```

- Benutzer anlegen:
```bash
python3 client.py create --name "Samuel Fronthaler" --email "sfronthaler@tsn.at"
```

- Benutzer per ID holen (z.B. 12):
```bash
python3 client.py get --id 12
```

- Benutzer suchen (Substring in Name oder Email, client-seitig):
```bash
python3 client.py search --q "htlinn"
```

## Hinweise

- `get` liefert bei nicht vorhandener ID `{"error": "Not Found", "id": <ID>}`.
- `search` lädt erst alle Benutzer (`list`) und filtert lokal; Server-Filter wird nicht vorausgesetzt.
- Netzwerk-/API-Fehler werden als Fehlermeldung auf `stderr` ausgegeben und der Prozess endet mit Code `1`. 
