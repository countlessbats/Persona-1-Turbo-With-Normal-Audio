# Persona 1 Turbo With Normal Audio

Hold a button to speed up **Shin Megami Tensei: Persona** (PSP, US) in PPSSPP, while the music
keeps playing at normal speed and pitch.

PPSSPP's own fast-forward speeds up the whole emulator, so the music speeds up or cuts out with it.
This cheat speeds up the game itself instead: it runs several game frames for each frame shown
on screen, and the music, which plays on its own clock, is left alone.

## Speeds

Eight cheats, one per speed. Turn on the one you want.

| Cheat | Speed while held |
|---|---|
| Turbo 1.5x | 1.5× |
| Turbo 2x | 2× |
| Turbo 2.5x (on by default) | 2.5× |
| Turbo 3x | 3× |
| Turbo 3.5x | 3.5× |
| Turbo 4x | 4× |
| Turbo 4.5x | 4.5× |
| Turbo 5x | 5× |

Turn on **only one** speed at a time.

## Install

1. Download `ULUS10432.ini` from the [latest release](../../releases/latest).
2. In PPSSPP, turn on **Settings → System → Enable cheats**.
3. Copy `ULUS10432.ini` into the `PSP/Cheats` folder of PPSSPP's memory stick folder
   (on Windows usually `Documents/PPSSPP/PSP/Cheats`; create the `Cheats` folder if it is missing).
   - Already have a `ULUS10432.ini` there? Paste everything from the first `_C` line of the
     downloaded file onto the end of yours instead.
   - Alternatively, start the game, open the pause menu → **Cheats** → **Edit cheat file**, and paste
     it there.
4. Open **Settings → Controls → Control mapping** and map a key or controller button (R2 works well)
   to **Note**. That button is the turbo button.
5. Start the game and hold the button. To change speed, open the pause menu → **Cheats**, untick the
   current speed and tick the one you want.

## Compatibility

- **Game:** Shin Megami Tensei: Persona, US release (ULUS10432). Works with or without the
  Persona Music Restoration mod. The cheat checks for the expected game code first and stays
  inactive if it does not find it.
- **Emulator:** PPSSPP (tested on 1.17.1). It does not work on real PSP hardware, where games
  cannot see the Note button.
- At the highest speeds, busy scenes may not reach the full multiplier if the emulated PSP
  runs out of processing time.

## Building the cheat file

`build_cheat.py` assembles the hooks and writes `ULUS10432.ini`.
It needs Python 3 and `keystone-engine` (`pip install keystone-engine`).

```
python build_cheat.py ULUS10432.ini
```

## License

MIT
