// The filter bar on prophecies-of-christ.md (under Explore). hooks/prophecies.py writes the bar (every facet
// and chip label) and tags each card with data-category, data-control, data-recognition and the
// rest, so this script only reads what the page already says. Values chosen within one facet are
// alternatives (passion or ministry); facets combine (passion, and done by His opponents). Each
// chip counts the cards it would show beside the other facets' choices, so a reader can see where a
// pivot leads before taking it. The choice lives in the address (?category=passion&control=opponents),
// so a filtered view can be shared. Without this script the bar stays hidden and every card shows.
//
// The explorer above the bar (<!-- prophecies-of-christ: explorer -->) is three pictures of the same
// cards, and each book, subject, writer or cell in them is a choice. A choice the bar has a chip for
// presses that chip; one it has none for (a book, a division, a New Testament writer) is kept in
// `extra` and shown in the bar as a button that removes it. Each mark's `data-units` names the
// entries it stands for ("<id>", or "<id>@<nt book>" for one New Testament use), so the pictures dim
// and recount from the cards left showing.
//
// Each card's facts are choices too (hooks/prophecies.py _pivot): "His opponents", "Partly fulfilled",
// "follows the Septuagint" carry the same facet:value pairs as the explorer's marks. Clicking one
// pivots the page to the cards that share it, and the card clicked holds its place on the screen
// while the others close up around it. Down among the cards the bar is out of sight, so a pill at
// the foot of the window says how many are showing and clears the choice.

const bar = document.querySelector('.pc-filter');
const cards = [...document.querySelectorAll('.pc-group[data-category] .pc-entry')];
const explorer = document.querySelector('.px');
const extra = {};
const pivots = [...document.querySelectorAll('.pc-group[data-category] .pc-pivot')];
let pill = null;
let barInView = true;

function chosen() {
  const picks = {};
  for (const chip of bar.querySelectorAll('.pc-chip[aria-pressed="true"]')) {
    (picks[chip.dataset.facet] ??= new Set()).add(chip.dataset.value);
  }
  for (const [facet, values] of Object.entries(extra)) {
    for (const value of values) (picks[facet] ??= new Set()).add(value);
  }
  return picks;
}

const chipFor = (facet, value) => bar.querySelector(`.pc-chip[data-facet="${facet}"][data-value="${value}"]`);

function isPicked(facet, value) {
  const chip = chipFor(facet, value);
  return chip ? chip.getAttribute('aria-pressed') === 'true' : Boolean(extra[facet]?.has(value));
}

function setPick(facet, value, on) {
  const chip = chipFor(facet, value);
  if (chip) {
    chip.setAttribute('aria-pressed', String(on));
    return;
  }
  const values = (extra[facet] ??= new Set());
  if (on) values.add(value);
  else values.delete(value);
  if (!values.size) delete extra[facet];
}

const pairsOf = (mark) => mark.dataset.pick.split(' ').map((pair) => pair.split(':'));

// A grid cell is two choices at once; clicking it again lifts both.
function togglePick(mark) {
  const pairs = pairsOf(mark);
  const on = !pairs.every(([facet, value]) => isPicked(facet, value));
  for (const [facet, value] of pairs) setPick(facet, value, on);
  update();
}

function paintExplorer(picks) {
  const shownIds = new Set(cards.filter((c) => !c.hidden).map((c) => c.id.replace(/^prophecy-/, '')));
  const any = Object.keys(picks).length > 0;
  const hot = (el) => {
    const units = el.dataset.units.split(' ');
    const n = units.filter((u) => {
      const [id, nt] = u.split('@');
      return shownIds.has(id) && (!nt || !picks.nt || picks.nt.has(nt));
    }).length;
    return [n, units.length];
  };
  for (const band of explorer.querySelectorAll('.px-band')) {
    const [h, n] = hot(band);
    band.style.opacity = any ? String(h ? 0.2 + (0.55 * h) / n : 0.06) : '';
  }
  for (const mark of explorer.querySelectorAll('.px-pick')) {
    const [h, n] = hot(mark);
    mark.classList.toggle('px-dim', any && h === 0);
    mark.setAttribute('aria-pressed', String(pairsOf(mark).every(([facet, value]) => isPicked(facet, value))));
    const count = mark.querySelector('.px-n');
    if (count) count.textContent = any && h !== n ? `${h} of ${n}` : String(n);
    const fill = mark.querySelector('.px-fill');
    if (fill) fill.setAttribute('r', String(h ? 4 + 24 * Math.sqrt(h / Number(fill.dataset.most)) : 0));
  }
  for (const total of explorer.querySelectorAll('.px-total')) {
    const [h, n] = hot(total);
    total.textContent = String(h);
    total.nextElementSibling.textContent = h === n ? 'prophecies' : `of ${n}`;
  }
}

function showExtra() {
  let box = bar.querySelector('.pc-picked');
  if (!box) {
    box = document.createElement('p');
    box.className = 'pc-picked';
    bar.querySelector('.pc-shown').after(box);
  }
  box.replaceChildren();
  for (const [facet, values] of Object.entries(extra)) {
    for (const value of values) {
      const mark = explorer?.querySelector(`.px-pick[data-pick~="${facet}:${value}"]`);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'pc-unpick';
      button.setAttribute('aria-pressed', 'true');
      button.textContent = `${(mark?.dataset.label ?? value).replace(/[:;].*$/, '')} ✕`;
      button.addEventListener('click', () => {
        setPick(facet, value, false);
        update();
      });
      box.append(button);
    }
  }
  box.hidden = !box.childElementCount;
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
  showExtra();
  if (explorer) paintExplorer(picks);
  for (const el of pivots) {
    el.setAttribute('aria-pressed', String(pairsOf(el).every(([facet, value]) => isPicked(facet, value))));
  }
  if (pill) {
    pill.querySelector('.pc-pill-shown').textContent = `Showing ${shown} of ${cards.length}`;
    pill.hidden = !any || barInView;
  }

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
  for (const [facet, value] of params) {
    for (const v of value.split(',')) if (v && !chipFor(facet, v)) setPick(facet, v, true);
  }
  bar.querySelector('.pc-clear').addEventListener('click', () => {
    for (const chip of bar.querySelectorAll('.pc-chip')) chip.setAttribute('aria-pressed', 'false');
    for (const facet of Object.keys(extra)) delete extra[facet];
    update();
  });
  const pivot = (el) => {
    const card = el.closest('.pc-entry');
    const before = card.getBoundingClientRect().top;
    togglePick(el);
    window.scrollBy(0, card.getBoundingClientRect().top - before);
  };
  for (const el of pivots) {
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');
    el.title = 'Show the prophecies that share this (click again to undo)';
    el.addEventListener('click', () => pivot(el));
    el.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        pivot(el);
      }
    });
  }
  pill = document.createElement('div');
  pill.className = 'pc-pill';
  pill.hidden = true;
  pill.innerHTML = '<button type="button" class="pc-pill-shown"></button>'
    + '<button type="button" class="pc-pill-clear">Clear ✕</button>';
  pill.querySelector('.pc-pill-shown').addEventListener('click', () => bar.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  pill.querySelector('.pc-pill-clear').addEventListener('click', () => bar.querySelector('.pc-clear').click());
  document.body.append(pill);
  new window.IntersectionObserver(([entry]) => {
    barInView = entry.isIntersecting;
    pill.hidden = barInView || !Object.keys(chosen()).length;
  }).observe(bar);
  if (explorer) {
    for (const mark of explorer.querySelectorAll('.px-pick')) {
      mark.addEventListener('click', () => togglePick(mark));
      mark.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          togglePick(mark);
        }
      });
    }
    // Without this script all three pictures stand one under another; with it, one at a time.
    const tabs = explorer.querySelector('.px-tabs');
    const show = (view) => {
      for (const tab of tabs.querySelectorAll('.px-tab')) tab.setAttribute('aria-selected', String(tab.dataset.view === view));
      for (const figure of explorer.querySelectorAll('.px-view')) figure.hidden = figure.dataset.view !== view;
    };
    for (const tab of tabs.querySelectorAll('.px-tab')) tab.addEventListener('click', () => show(tab.dataset.view));
    tabs.hidden = false;
    show('flow');
  }
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
