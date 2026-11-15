import type { ThemeBackdropGlass } from 'claude-code'

import { nightSkySvg } from './scenes/night-sky'
import { rubinPachonSvg } from './scenes/rubin-pachon'
import { rubinPachonDaySvg } from './scenes/rubin-pachon-day'
import { rubinPachonNightSvg } from './scenes/rubin-pachon-night'
import { rubinPachonSunriseSvg } from './scenes/rubin-pachon-sunrise'

/** One theme: its title and blurb, the glass over it, and its scene: a function that builds one SVG whose own CSS
 *  animates it. Laid out as a table, so more scenes can be added beside these. */
export type Theme = {
  id: string
  title: string
  blurb: string
  window: 'light' | 'dark'
  glass: ThemeBackdropGlass
  scene: () => string
}

export const THEMES: readonly Theme[] = [
  {
    id: 'rubin-pachon',
    title: 'Rubin on Cerro Pachon',
    blurb: 'An ASCII Rubin Observatory under the last of twilight: a purple Milky Way, twinkling stars and a comet every 20 seconds',
    window: 'dark',
    // Light glass: the dotted Milky Way and stars blur away under a heavy one.
    glass: { blur: 5, tint: '#0e1238', opacity: 0.3 },
    scene: rubinPachonSvg,
  },
  // The same summit at other times of day, from `tools/rubin-pachon.py --time <name>`. Plain rubin-pachon is sunset.
  {
    id: 'rubin-pachon-sunset',
    title: 'Rubin at sunset',
    blurb: 'Rubin under the last of twilight: a purple Milky Way, a peach horizon and a comet every 20 seconds',
    window: 'dark',
    glass: { blur: 5, tint: '#0e1238', opacity: 0.3 },
    scene: rubinPachonSvg,
  },
  {
    id: 'rubin-pachon-night',
    title: 'Rubin at night',
    blurb: 'Rubin in full dark: a black sky, a bright Milky Way, moonlit clouds and a comet every 20 seconds',
    window: 'dark',
    glass: { blur: 5, tint: '#0a0e2c', opacity: 0.3 },
    scene: rubinPachonNightSvg,
  },
  {
    id: 'rubin-pachon-sunrise',
    title: 'Rubin at sunrise',
    blurb: 'Rubin at dawn: the last stars fading over a gold and rose horizon',
    window: 'dark',
    glass: { blur: 6, tint: '#141e48', opacity: 0.32 },
    scene: rubinPachonSunriseSvg,
  },
  {
    id: 'rubin-pachon-day',
    title: 'Rubin by day',
    blurb: 'Rubin under a clear blue sky, white clouds drifting over the summit',
    window: 'dark',
    glass: { blur: 8, tint: '#14284e', opacity: 0.4 },
    scene: rubinPachonDaySvg,
  },
  {
    id: 'night-sky',
    title: 'Night Sky',
    blurb: 'Twinkling stars, a faint Milky Way, a crescent moon and the odd meteor',
    window: 'dark',
    glass: { blur: 14, tint: '#0b1020', opacity: 0.34 },
    scene: nightSkySvg,
  },
]

const built = new Map<string, string>()

/** A theme's SVG, built the first time it is asked for. */
export function sceneOf(theme: Theme): string {
  const ready = built.get(theme.id)
  if (ready !== undefined) return ready
  const source = theme.scene()
  built.set(theme.id, source)
  return source
}

export function themeOf(id: string | undefined): Theme | undefined {
  return THEMES.find(theme => theme.id === id)
}

/** The scene's name as the engine hands it to the Backdrop hook: under `scene` on newer engines, `id` on older ones. */
export function sceneNameOf(props: { scene?: unknown; id?: unknown }): string | undefined {
  if (typeof props.scene === 'string') return props.scene
  return typeof props.id === 'string' ? props.id : undefined
}
