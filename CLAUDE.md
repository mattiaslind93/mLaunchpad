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
│   ├── launcher.py      # Startar Blender, terminal, filhanterare
│   └── platform_utils.py # OS-detektering: Blender-upptäckt + default-källor (Linux/macOS)
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

> **Plattform:** Exemplet ovan visar Linux-sökvägar. Vid första körningen skapas
> default-konfigurationen plattformsanpassad (se `core/platform_utils.py`). På macOS
> blir det t.ex. `blender_executable: /Applications/Blender.app/Contents/MacOS/Blender`,
> `private.jobs_path: ~/Insync/mattiaslind93@gmail.com/Google Drive/Pipeline` och
> `milford.jobs_path: /Volumes/jack/JOBS`. Befintliga config-filer skrivs aldrig om
> automatiskt – redigera `config.json` själv om sökvägarna behöver justeras.

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
| `JOBROOT` | `/var/mnt/jack/JOBS` | Samma som `JOBS` (alias som Blender-addon förväntar sig) |
| `SYSTEM` | `/var/mnt/jack/SYSTEM` | Systemverktyg och pipeline |
| `USER_NAME` | `mlind` | Aktuell användare |
| `MF_ROOT` | `$SYSTEM/TOOLS/mfpipeline/pipeline_v7.0.0` | Pipeline-rot |
| `JOBPROJ` | `MyProject` | Projektnamn |
| `JOBSEQ` | `seq010` | Sekvensnamn |
| `JOBSHOT` | `shot_0010` | Shotnamn |
| `JOBPATH` | `MyProject/seq010/shot_0010` | Relativ sökväg |
| `SHOTPATH` | `/var/mnt/jack/JOBS/MyProject/seq010/shot_0010` | Absolut sökväg |

## Körning

**Linux:**
```bash
cd ~/projects/homelaunchpad
python main.py
```
Eller via desktop-filen: `~/.local/share/applications/homelaunchpad.desktop`

**macOS:**
Rekommenderat: bygg en riktig `.app` (visas i Launchpad/Dock med Milford-ikonen):
```bash
./build_macos_app.sh          # installerar /Applications/HomeLaunchPad.app
```
`.app`-paketet är en tunn wrapper som kör repots `.venv` på `main.py`, så det
startar alltid senaste koden. Ikonen genereras från `icons/homelaunchpad_icon.png`.

Alternativ: dubbelklicka `homelaunchpad.command` i Finder, eller kör manuellt:
```bash
cd ~/Documents/GItHub/mLaunchpad
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

> **OBS (macOS):** PyQt6-bindningarna och Qt6-biblioteken måste ha *samma* version,
> annars vägrar Qt ladda sina plattforms-plugins och appen kraschar direkt vid start
> (symptom: `Could not find the Qt platform plugin "cocoa"`). Därför är båda pinnade
> i `requirements.txt`.

## Beroenden

- Python 3.9+ (3.10+ rekommenderas)
- PyQt6

Installation:
```bash
pip install PyQt6
```

## Plattformsstöd (Linux & macOS)

Appen körs på både Linux och macOS. All OS-specifik logik är samlad i
`core/platform_utils.py` (`IS_MAC`/`IS_LINUX` via `sys.platform`). Skillnaderna:

| Område | Linux | macOS |
|--------|-------|-------|
| Blender-upptäckt | `~/Dokument/Blender/blender_config/blender-X.Y.Z-linux-x64/blender` | `Blender*.app` i `/Applications` och `~/Applications` (version läses från Info.plist) |
| Blender-binär | `.../blender` | `Blender.app/Contents/MacOS/Blender` (inre binären, så env kan sättas) |
| Terminal | gnome-terminal, konsole, xfce4-terminal, xterm, kitty, alacritty | Terminal.app via AppleScript (`osascript`) som re-exporterar JOB-variablerna |
| Filhanterare | nautilus, dolphin, thunar, nemo, pcmanfm, xdg-open | Finder via `open` |
| JOBS-montering | `/var/mnt/jack/...` | `/Volumes/jack/...` (SMB-share) |
| Privat-källa | `/home/mlind/Insync/...` | `~/Insync/.../Google Drive/Pipeline` |

> På macOS kan `open`/`open -a` inte skicka med en egen miljö, så terminalen
> startas via AppleScript där JOB-variablerna (`JOBPROJ`, `SHOTPATH`, …)
> re-exporteras explicit i den nya shell-sessionen.

## Exkluderade mappar

Följande mappar visas inte i listorna (definierade i `core/launchpad.py`):

- `_projData`, `_shotData`
- `dailies`, `delivery`, `editorial`
- `incoming`, `personal`, `tools`

## Känt problem: Sökvägar

Blender-addons kan förvänta sig sökvägar som `/jack/JOBS/...` medan systemet monterar på `/var/mnt/jack/JOBS/...` (Linux) eller `/Volumes/jack/JOBS/...` (macOS).

**Lösning (Linux):** Skapa en symlink:
```bash
sudo ln -s /var/mnt/jack /jack
```

**Lösning (macOS):** Skapa en symlink mot monteringen under `/Volumes`:
```bash
sudo ln -s /Volumes/jack /jack
```

Alternativt: Uppdatera `config.json` så att `jobs_path` och `system_path` använder `/jack/`.

## Felsökning

**Blender startar inte:**
- Kontrollera att `blender_executable` i config.json pekar på rätt fil
- Verifiera att filen är körbar: `chmod +x /path/to/blender`

**Inga projekt visas:**
- Kontrollera att `jobs_path` är korrekt och att mappen är monterad
- Linux: kör `ls /var/mnt/jack/JOBS`, macOS: kör `ls /Volumes/jack/JOBS` för att verifiera
- macOS: en otillgänglig källa (t.ex. Milford utan VPN/monterad share) gråas ut i dropdownen

**Terminal öppnas inte:**
- Linux: appen försöker hitta gnome-terminal, konsole, xfce4-terminal, xterm, kitty, alacritty – installera en om ingen finns
- macOS: använder Terminal.app via `osascript`; om inget händer, kontrollera att appen har behörighet att styra Terminal (System­inställningar → Sekretess & säkerhet → Automation)
