// Night Sky: a starfield with a faint Milky Way, a crescent moon in the top right corner and an occasional meteor.
// Pure string building: no DOM, nothing brought in from outside this file.
// The resting picture (what a reduced-motion user sees) is set in plain attributes: every star at its own brightness,
// the meteor hidden. The keyframes only move away from that and back.

const WIDTH = 1600
const HEIGHT = 1000

/** Stars from a fixed seed, so the sky is the same every session. */
function stars(): string {
  let s = 42
  const rand = () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296
  let out = ''
  for (let i = 0; i < 220; i++) {
    const x = (rand() * WIDTH).toFixed(1)
    const y = (rand() * HEIGHT).toFixed(1)
    const r = (rand() < 0.9 ? 0.5 + rand() * 0.9 : 1.4 + rand() * 0.8).toFixed(2)
    const tw =
      rand() < 0.35
        ? ` class="tw" style="animation-delay:${(rand() * 6).toFixed(2)}s;animation-duration:${(3 + rand() * 4).toFixed(2)}s"`
        : ''
    const o = (0.45 + rand() * 0.55).toFixed(2)
    out += `<circle cx="${x}" cy="${y}" r="${r}" fill="#ffffff" opacity="${o}"${tw}/>`
  }
  return out
}

export function nightSkySvg(): string {
  const style = `
.tw{animation-name:tw;animation-iteration-count:infinite;animation-timing-function:ease-in-out}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
.meteor{opacity:0;animation:meteor 14s linear infinite}
@keyframes meteor{0%,88%{transform:translate(0,0);opacity:0}89%{opacity:.9}94%{transform:translate(-260px,160px);opacity:0}100%{opacity:0}}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}`

  const defs = `
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05070f"/><stop offset=".6" stop-color="#0b1020"/><stop offset="1" stop-color="#18203f"/></linearGradient>
<filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
<radialGradient id="glow"><stop offset="0" stop-color="#fff6d8" stop-opacity=".35"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/></radialGradient>
<mask id="crescent"><circle cx="60" cy="60" r="34" fill="#fff"/><circle cx="76" cy="50" r="30" fill="#000"/></mask>`

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${WIDTH} ${HEIGHT}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"><style>${style}</style><defs>${defs}</defs>
<rect width="${WIDTH}" height="${HEIGHT}" fill="url(#sky)"/>
<g filter="url(#soft)" opacity=".5" transform="rotate(-28 800 500)"><ellipse cx="800" cy="500" rx="900" ry="70" fill="#4a5a9a"/><ellipse cx="760" cy="510" rx="600" ry="35" fill="#8a8fc0"/></g>
${stars()}
<line class="meteor" x1="1180" y1="140" x2="1230" y2="110" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round"/>
<svg x="0" y="0" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}" preserveAspectRatio="xMaxYMin meet"><g transform="translate(1440 40)"><circle cx="60" cy="60" r="80" fill="url(#glow)"/><rect width="120" height="120" fill="#f6edd0" mask="url(#crescent)"/></g></svg>
</svg>`
}
