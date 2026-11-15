import type { Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import { THEMES, sceneNameOf, sceneOf, themeOf } from './themes'
import type { Theme } from './themes'

// A dark, navy-tinted look for the app, under one of the scenes in hooks/scenes/ (listed in themes.ts).
const { theme: colors, problems } = makeColors({
  label: 'Night sky',
  only: 'dark',
  roles: { accent: '#7aa2f7', danger: '#e06c75', success: '#8cc265', warning: '#e0a458', pro: '#b48ead' },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#0b1020',
        'surface-1': '#111833',
        'surface-2': '#161e3d',
        'surface-3': '#1b2446',
        'text-primary': '#e8ecf8',
        'text-secondary': '#c3cbe3',
        'text-muted': '#9aa5c6',
      },
    },
  },
})

// The scene a new session starts with; `/sky <name>` switches for this session.
const DEFAULT = 'rubin-pachon'

function lookOf(theme: Theme): ThemeSetArgs {
  return { colors, backdrop: { scene: theme.id, glass: theme.glass }, overrideColorScheme: theme.window }
}

const NAMES = THEMES.map(theme => theme.id).join(', ')

export const register: Register = on => {
  // The scene this session shows; a reload or a new session starts over at DEFAULT.
  let current = themeOf(DEFAULT)!

  // Neither a reload of this mod nor --resume keeps the look, so set it here
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))
    if (unpainted !== undefined) $.ui.toast(unpainted)
    const set = await $.theme.set(lookOf(current))
    if (!set.isDrawn) $.ui.status(`night-sky: ${set.reason}`)
    await $.command.register({ name: 'sky', description: `Set the backdrop (${NAMES}), and say whether the app draws it` })
    await $.command.register({ name: 'plain', description: 'Take the night sky off' })
    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    // This hook runs for every mod's backdrop; draw only ours, and only where backdrops are drawn
    if (e.props.plugin !== $.plugin.name) return next(e)
    if (e.surface !== 'desktop' && e.surface !== 'mobile') return next(e)
    const theme = themeOf(sceneNameOf(e.props))
    if (theme === undefined) return next(e)
    const { Svg } = $.ui.resolve(e)
    return <Svg isInteractive alt={`${theme.title}: ${theme.blurb}`} source={sceneOf(theme)} />
  })

  on('command.run', { command: 'sky' }, async ($, e) => {
    const asked = e.args.trim().toLowerCase()
    if (asked !== '') {
      const theme = THEMES.find(t => t.id === asked || t.title.toLowerCase() === asked)
      if (theme === undefined) return { text: `no scene called "${asked}": try ${NAMES}` }
      current = theme
    }
    const set = await $.theme.set(lookOf(current))
    return {
      text: set.isDrawn
        ? `${current.title} set: the app says it draws it`
        : `${current.title} set, but not drawn: ${set.reason}`,
    }
  })

  on('command.run', { command: 'plain' }, async $ => {
    const cleared = await $.theme.clear()
    return { text: cleared.isDrawn ? 'the night sky is still set' : cleared.reason }
  })
}
