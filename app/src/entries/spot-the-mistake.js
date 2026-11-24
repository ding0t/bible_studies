// The exercise on resources/spot-the-mistake.md. Each .spot-answer holds sentences
// (.spot-s), one marked data-wrong, followed by a collapsed details.spot-reveal that explains it.
// Without this script the page still works: the reader opens the reveal. With it, tapping a
// sentence marks it, and finding the wrong one opens the reveal. A tap on a reference or a Strong's
// word is left to the pop-up, since reading the verse is the habit the page teaches.

const FIRST_TRY = 'spotFirstTry';

function revealFor(answer) {
  for (let node = answer.nextElementSibling; node; node = node.nextElementSibling) {
    if (node.matches('details.spot-reveal')) return node;
    if (node.matches('.spot-answer, h2')) return null;
  }
  return null;
}

function updateScore(answers, score) {
  const done = answers.filter((a) => a.dataset.spotDone);
  if (!score || done.length === 0) return;
  const first = done.filter((a) => a.dataset.spotDone === FIRST_TRY).length;
  score.hidden = false;
  score.textContent =
    done.length === answers.length
      ? `All ${answers.length} found, ${first} on the first try.`
      : `${done.length} of ${answers.length} found, ${first} on the first try.`;
}

function setUp(answer, answers, score) {
  const sentences = [...answer.querySelectorAll('.spot-s')];
  const feedback = document.createElement('p');
  feedback.className = 'spot-feedback';
  feedback.setAttribute('aria-live', 'polite');
  answer.append(feedback);
  answer.classList.add('spot-live');
  let misses = 0;

  function choose(sentence) {
    if (answer.dataset.spotDone || sentence.classList.contains('spot-miss')) return;
    if (sentence.hasAttribute('data-wrong')) {
      sentence.classList.add('spot-right');
      answer.dataset.spotDone = misses === 0 ? FIRST_TRY : 'later';
      feedback.textContent = 'Found it. The explanation is open below.';
      const reveal = revealFor(answer);
      if (reveal) reveal.open = true;
      for (const s of sentences) s.removeAttribute('tabindex');
      updateScore(answers, score);
    } else {
      misses += 1;
      sentence.classList.add('spot-miss');
      sentence.setAttribute('aria-disabled', 'true');
      feedback.textContent = 'That one checks out. Try another.';
    }
  }

  for (const sentence of sentences) {
    sentence.setAttribute('role', 'button');
    sentence.setAttribute('tabindex', '0');
    sentence.addEventListener('click', (event) => {
      if (event.target instanceof Element && event.target.closest('.pop-ref, .pop-word, a')) return;
      choose(sentence);
    });
    sentence.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        choose(sentence);
      }
    });
  }
}

const answers = [...document.querySelectorAll('.spot-answer')];
const score = document.querySelector('.spot-score');
for (const answer of answers) setUp(answer, answers, score);
