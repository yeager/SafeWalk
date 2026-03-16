# SafeWalk - Trygg promenad-app

En enkel GTK4/Adwaita-app för att känna sig tryggare under promenader. Dela din position med nära och kära och bekräfta när du kommit fram.

## Funktioner

- **Sparade rutter** – Välj bland fördefinierade rutter (hem till jobbet, kvällspromenad, etc.)
- **GPS-simulering** – Visar din framfart längs rutten steg för steg
- **Dela position** – Kopiera din aktuella position för att skicka till kontakter
- **"Jag är framme"-knapp** – Bekräfta att du kommit fram tryggt
- **Trygga kontakter** – Hantera lista över personer som får din position

## Installation

### Krav

- Python 3.8+
- GTK4
- libadwaita
- PyGObject

### macOS

```bash
brew install gtk4 libadwaita pygobject3
```

### Ubuntu/Fedora

```bash
# Ubuntu
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita
```

### Kör appen

```bash
python -m safewalk.app
```

Eller installera:

```bash
pip install -e .
safewalk
```

## Filstruktur

```
SafeWalk/
├── safewalk/
│   ├── __init__.py      # Paketinfo
│   └── app.py           # Huvudapplikation (GTK4 UI + logik)
├── data/
│   └── routes.json      # Rutter och kontakter
├── setup.py             # Installationsfil
├── safewalk.desktop     # Skrivbordsgenväg
└── README.md
```

## Användning

1. Starta appen
2. Välj en sparad rutt och tryck **Starta**
3. Appen simulerar din position längs rutten
4. Tryck **Dela min position** för att kopiera position till clipboard
5. När du kommit fram, tryck **Jag är framme!**
6. Under **Kontakter** kan du lägga till trygga kontakter

## Licens

MIT
