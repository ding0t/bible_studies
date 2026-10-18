// Spaced review for the Hebrew and Greek word cards (docs/content/hebrew/names-of-god-cards.md).
//
// A Leitner schedule: a card read correctly moves up a box and comes back after that box's
// interval; a miss sends it to box 0 and back into today's session. New cards are introduced in
// deck order, a few a day, because the deck is ordered to teach the alphabet a few letters at a
// time -- shuffling it would hand a learner letters they have not met.

export const INTERVAL_DAYS = [0, 1, 3, 7, 14, 30];
export const NEW_PER_DAY = 3;
const DAY = 24 * 60 * 60 * 1000;

/** progress: { [cardId]: { box, due } } (due in ms). Returns the ids to show now, in order. */
export function sessionQueue(cardIds, progress, now, newToday = 0) {
  const due = cardIds.filter((id) => progress[id] && progress[id].due <= now);
  const fresh = cardIds.filter((id) => !progress[id]).slice(0, Math.max(0, NEW_PER_DAY - newToday));
  return [...due, ...fresh];
}

export function review(entry, correct, now) {
  if (!correct) return { box: 0, due: now };
  // A first correct reading starts at box 1 (tomorrow): box 0 is for cards just missed.
  const box = Math.min((entry?.box ?? 0) + 1, INTERVAL_DAYS.length - 1);
  return { box, due: now + INTERVAL_DAYS[box] * DAY };
}

/** The text to speak: the divine name is read Adonai, never sounded out, and where it is pointed
 * for Elohim (after Adonai, as in Isaiah 61:1) it is read Elohim. */
export function spokenText(hebrew) {
  return hebrew.replace(/יְהוִה/g, 'אֱלֹהִים').replace(/יְהוָה|יהוה/g, 'אֲדֹנָי');
}
