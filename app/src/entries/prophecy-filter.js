// The filter bar on prophecies-of-christ.md (under Explore). hooks/prophecies.py writes the bar (every facet
// and chip label) and tags each card with data-category, data-control, data-recognition and the
// rest, so this script only reads what the page already says. Values chosen within one facet are
// alternatives (passion or ministry); facets combine (passion, and done by His opponents). Each
// chip counts the cards it would show beside the other facets' choices, so a reader can see where a
// pivot leads before taking it. The choice lives in the address (?category=passion&control=opponents),
// so a filtered view can be shared. Without this script the bar stays hidden and every card shows.

const bar = document.querySelector('.pc-filter');
const cards = [...document.querySelectorAll('.pc-group[data-category] .pc-entry')];

function chosen() {
  const picks = {};
  for (const chip of bar.querySelectorAll('.pc-chip[aria-pressed="true"]')) {
    (picks[chip.dataset.facet] ??= new Set()).add(chip.dataset.value);
  }
  return picks;
}

function matches(card, picks, except) {
  return Object.entries(picks).every(([facet, values]) => {
    if (facet === except) return true;
    const have = (card.dataset[facet] ?? '').split(' ');
    return have.some((v) => values.has(v));
  });
}

function update() {
  const picks = chosen();
  let shown = 0;
  for (const card of cards) {
    const on = matches(card, picks);
    card.hidden = !on;
    if (on) shown += 1;
  }
  // A subject with nothing left loses its heading too, so the page closes up around what remains.
  for (const group of document.querySelectorAll('.pc-group[data-category]')) {
    const empty = !group.querySelector('.pc-entry:not([hidden])');
    group.hidden = empty;
    const heading = group.previousElementSibling;
    if (heading?.matches('h3')) heading.hidden = empty;
  }
  for (const chip of bar.querySelectorAll('.pc-chip')) {
    const n = cards.filter((c) => matches(c, picks, chip.dataset.facet) && (c.dataset[chip.dataset.facet] ?? '').split(' ').includes(chip.dataset.value)).length;
    chip.querySelector('.pc-n').textContent = String(n);
    chip.disabled = n === 0 && chip.getAttribute('aria-pressed') !== 'true';
  }
  const any = Object.keys(picks).length > 0;
  bar.querySelector('.pc-shown').textContent = any
    ? `Showing ${shown} of the ${cards.length} prophecies below.`
    : `All ${cards.length} prophecies below. Choose any values to narrow them; choices within a group are alternatives.`;
  bar.querySelector('.pc-clear').hidden = !any;

  const params = new window.URLSearchParams();
  for (const [facet, values] of Object.entries(picks)) params.set(facet, [...values].join(','));
  const query = params.toString();
  window.history.replaceState(null, '', `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`);
}

if (bar && cards.length) {
  const params = new window.URLSearchParams(window.location.search);
  for (const chip of bar.querySelectorAll('.pc-chip')) {
    const wanted = (params.get(chip.dataset.facet) ?? '').split(',');
    if (wanted.includes(chip.dataset.value)) chip.setAttribute('aria-pressed', 'true');
    chip.addEventListener('click', () => {
      chip.setAttribute('aria-pressed', String(chip.getAttribute('aria-pressed') !== 'true'));
      update();
    });
  }
  bar.querySelector('.pc-clear').addEventListener('click', () => {
    for (const chip of bar.querySelectorAll('.pc-chip')) chip.setAttribute('aria-pressed', 'false');
    update();
  });
  bar.hidden = false;
  update();
}

// The chance floor (hooks/prophecies.py, <!-- prophecies-of-christ: floor -->): the reader sets one
// chance in k for each moment, and the page multiplies them. The hook counts the moments; this only
// does the arithmetic, exactly, since k to the fourteenth overflows a float's exact range.
const floor = document.querySelector('.pc-floor');
if (floor) {
  const n = Number(floor.dataset.n);
  const slider = floor.querySelector('.pc-k');
  const show = () => {
    const k = Number(slider.value);
    const odds = BigInt(k) ** BigInt(n);
    floor.querySelector('.pc-k-out').textContent = String(k);
    floor.querySelector('.pc-floor-result').textContent =
      `With ${n} independent moments at one chance in ${k} each, the chance that all came to pass is ` +
      `one in ${k}^${n}, that is one in ${odds.toLocaleString('en')}.`;
  };
  slider.addEventListener('input', show);
  show();
}
