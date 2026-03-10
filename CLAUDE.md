# HomeLaunchPad

En PyQt6-baserad launcher-applikation för att starta Blender (och andra applikationer) med korrekta miljövariabler för ett VFX/animation pipeline.

## Syfte

HomeLaunchPad är en hemmaversion av ett professionellt LaunchPad-verktyg. Appen låter användaren:

1. Välja **Projekt** > **Sekvens** > **Shot** från en mappstruktur
2. Starta Blender med rätt miljövariabler satta (JOBS, JOBPROJ, JOBSEQ, JOBSHOT, etc.)
3. Öppna terminal eller filhanterare i shot-mappen

Detta är nödvändigt för att Blender-addons ska hitta rätt filer och för att pipeline-verktyg ska fungera korrekt.

## Arkitektur

```
homelaunchpad/
├── main.py              # Entry point, startar PyQt6-appen
├── core/
│   ├── __init__.py      # Exporterar HomeLaunchPad
│   ├── launchpad.py     # Kärnlogik: läser projekt/sekvenser/shots, bygger miljö
│   └── launcher.py      # Startar Blender, terminal, filhanterare
├── gui/
│   ├── __init__.py
│   ├── main_window.py   # Huvudfönster med listor och knappar
│   └── styles.py        # Dark theme stylesheet
└── icons/               # PNG-ikoner för UI
```

## Konfiguration

Konfigurationsfilen ligger på `~/.homelaunchpad/config.json`:

```json
{
  "sources": {
    "milford": {
      "name": "Milford",
      "jobs_path": "/var/mnt/jack/JOBS",
      "system_path": "/var/mnt/jack/SYSTEM"
    },
    "private": {
      "name": "Privat",
      "jobs_path": "/home/mlind/Insync/mattiaslind93@gmail.com/Google Drive/Pipeline",
      "system_path": "/var/mnt/jack/SYSTEM"
    }
  },
  "current_source": "milford",
  "user_name": "mlind",
  "blender_executable": "/home/mlind/Dokument/Blender/blender_config/blender-5.0.1-linux-x64/blender",
  "last_project": null,
  "last_sequence": null,
  "last_shot": null
}
```

| Nyckel | Beskrivning |
|--------|-------------|
| `sources` | Dictionary med projekt-källor (se nedan) |
| `current_source` | ID för aktiv källa ("milford" eller "private") |
| `user_name` | Användarnamn för miljövariabeln USER_NAME |
| `blender_executable` | Full sökväg till Blender-binären |
| `last_*` | Sparar senaste val för nästa körning |

### Projekt-källor (sources)

Varje källa har:
- `name`: Visningsnamn i UI:t
- `jobs_path`: Sökväg till JOBS-mappen där projekt ligger
- `system_path`: Sökväg till SYSTEM-mappen med pipeline-verktyg

Du kan lägga till fler källor genom att editera config.json.

**Tillgänglighetskontroll:** Appen kontrollerar var 10:e sekund om varje källas `jobs_path` är tillgänglig. Källor som inte är tillgängliga (t.ex. Milford när VPN är frånkopplad) visas som gråade/disabled i dropdown-menyn.

## Miljövariabler

När en applikation startas sätts följande miljövariabler:

| Variabel | Exempel | Beskrivning |
|----------|---------|-------------|
| `JOBS` | `/var/mnt/jack/JOBS` | Rot för alla projekt |
| `SYSTEM` | `/var/mnt/jack/SYSTEM` | Systemverktyg och pipeline |
| `USER_NAME` | `mlind` | Aktuell användare |
| `MF_ROOT` | `$SYSTEM/TOOLS/mfpipeline/pipeline_v7.0.0` | Pipeline-rot |
| `JOBPROJ` | `MyProject` | Projektnamn |
| `JOBSEQ` | `seq010` | Sekvensnamn |
| `JOBSHOT` | `shot_0010` | Shotnamn |
| `JOBPATH` | `MyProject/seq010/shot_0010` | Relativ sökväg |
| `SHOTPATH` | `/var/mnt/jack/JOBS/MyProject/seq010/shot_0010` | Absolut sökväg |

## Körning

```bash
cd ~/projects/homelaunchpad
python main.py
```

Eller via desktop-filen: `~/.local/share/applications/homelaunchpad.desktop`

## Beroenden

- Python 3.10+
- PyQt6

Installation:
```bash
pip install PyQt6
```

## Exkluderade mappar

Följande mappar visas inte i listorna (definierade i `core/launchpad.py`):

- `_projData`, `_shotData`
- `dailies`, `delivery`, `editorial`
- `incoming`, `personal`, `tools`

## Känt problem: Sökvägar

Blender-addons kan förvänta sig sökvägar som `/jack/JOBS/...` medan systemet monterar på `/var/mnt/jack/JOBS/...`.

**Lösning:** Skapa en symlink:
```bash
sudo ln -s /var/mnt/jack /jack
```

Alternativt: Uppdatera `config.json` så att `jobs_path` och `system_path` använder `/jack/` istället för `/var/mnt/jack/`.

## Felsökning

**Blender startar inte:**
- Kontrollera att `blender_executable` i config.json pekar på rätt fil
- Verifiera att filen är körbar: `chmod +x /path/to/blender`

**Inga projekt visas:**
- Kontrollera att `jobs_path` är korrekt och att mappen är monterad
- Kör `ls /var/mnt/jack/JOBS` för att verifiera

**Terminal öppnas inte:**
- Appen försöker hitta: gnome-terminal, konsole, xfce4-terminal, xterm, kitty, alacritty
- Installera en av dessa om ingen finns
