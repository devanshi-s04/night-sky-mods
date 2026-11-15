# night-sky

Animated backdrops for Claude Code's desktop app. A theme mod that paints a scene behind the conversation and tints the app navy to match.

The main scene is an ASCII **Vera C. Rubin Observatory** on Cerro Pachón, with Gemini South and SOAR on the ridges beside it. Stars twinkle, clouds drift across the domes, Rubin's dome turns now and then, its camera glows neon cyan in Rubin teal, and a comet crosses every 20 seconds.

| Scene | What you see |
|---|---|
| `rubin-pachon` | the default: Rubin at sunset |
| `rubin-pachon-sunset` | the last of twilight: a purple Milky Way over a peach horizon |
| `rubin-pachon-night` | full dark: a black sky and a bright Milky Way |
| `rubin-pachon-sunrise` | dawn: the last stars fading over a gold and rose horizon |
| `rubin-pachon-day` | a blue sky, the sun, birds and white clouds; the buildings in white concrete |
| `night-sky` | a plain starfield with a crescent moon and the odd meteor |

## Install

At the prompt of a Claude Code terminal session:

```
/plugin install night-sky --marketplace devanshi-s04/night-sky-mods
```

Answer `y` to add the marketplace, then pick a scope (the user scope is first). The mod is active at once.

From a shell:

```bash
claude plugin install night-sky --marketplace devanshi-s04/night-sky-mods
```

In the desktop app, where `/plugin` does not run: click **+** next to the prompt box, then **Plugins**, **Add marketplace** with `devanshi-s04/night-sky-mods`, then **Add plugin**.

## Use

```
/sky rubin-pachon-night
```

`/sky <name>` switches scene for the session; `/sky` alone redraws the current one. `/plain` takes the backdrop off. A new session starts on `rubin-pachon`.

Backdrops are drawn on the desktop and mobile apps; the terminal shows none. Motion stops when your system asks for reduced motion.

## Changing the Rubin scenes

The Rubin scenes are generated, not hand-written. Edit `tools/rubin-pachon.py` (Python 3, standard library only) and run it once per time of day:

```bash
python3 tools/rubin-pachon.py --time sunset
```

`--time` takes `night`, `sunset`, `sunrise` or `day`, and writes `hooks/scenes/rubin-pachon*.ts`. Add `--svg out.svg` to also save the SVG for a browser preview. Keep each scene under 131,072 characters, the app's limit for a backdrop. Avoid aspect-ratio media queries in the scene's CSS: they stop all animation in the app.

## Credits

`hooks/make-colors.js` and `hooks/make-colors.d.ts` are Anthropic's colour helper for Claude Code mods, copied unchanged as their header asks. The Rubin building is traced from a NOIRLab night photo of the observatory. Rubin's brand teals (`#058B8C`, `#0C4A4C`) colour the camera glow. This is a fan project, not affiliated with Rubin Observatory, NSF, DOE or NOIRLab.
