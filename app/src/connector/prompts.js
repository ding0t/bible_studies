// The site's study method, offered as MCP prompts and resources: the skills its own studies are
// written and checked with (.claude/skills/), which hooks/llms.py publishes at /skills/ on every
// build, so a reader's assistant can study a passage the same way, with this connector's tools
// standing in for the local research tools the skills name. Plus three short prompts of its own.

const ADAPTER = `You are running one of The Way's study skills through its public connector (https://the-way.lewy.au/mcp).
The skill below was written for the author's own workspace. Where it names a local script, a state
file, a commit or a database, use these connector tools instead, and skip what only applies to
editing the site's files:

- passage_brief, bible_verse, study_verse -> read_passage (WEB, BSB, ULT, the Hebrew or Greek, the Septuagint)
- bible_interlinear -> beneath_the_english; bible_syntax -> who_is_acting; original words with morphology -> original_words
- bible_word, bible_concordance, twot_* -> word_study (counts, every occurrence, renderings, the studies that discuss it)
- bible_trace, bible_links -> quotation_trace; bible_crossref -> cross_references
- bible_variants, footnotes -> textual_notes; bible_grammar -> hebrew_grammar
- cross_study_claims, review_gaps -> studies_for_passage and search_studies; reading a study -> get_study
- study-notes.db (commercial study Bibles) and TWOT are not available here; say so where the skill asks for them.

The ESV is not served here; quote the WEB or BSB and name the translation. Keep the skill's order:
what the text meant in its own setting before what it means now.

`;

const SKILLS = {
  'develop-bible-study': {
    title: 'Study a passage the way this site does',
    description:
      "The site's full method for studying a passage or topic: exegesis (history, literary context, the words in Hebrew and Greek, genre) before any application, then the bridge to today, cross-referencing and checking.",
    path: 'skills/develop-bible-study/SKILL.md',
  },
  'review-bible-study': {
    title: 'Check a Bible study or claim',
    description:
      'Treat every claim in a study, sermon or answer as unverified: re-check the quotations, the references, the word studies and the claims the writer built, against the sources.',
    path: 'skills/review-bible-study/SKILL.md',
  },
  'word-study-method': {
    title: 'Do a word study properly',
    description:
      "How to study a Hebrew or Greek word: its usage across time, its usage in the author's own day, then a conclusion, avoiding the root fallacy.",
    path: 'skills/develop-bible-study/word-study-method.md',
  },
};

export const PROMPTS = [
  {
    name: 'share_the_gospel',
    title: 'Share the gospel',
    description:
      "Explain the gospel of Jesus Christ from Scripture, in the site author's words, with every verse quoted, and invite a response.",
    arguments: [
      {
        name: 'situation',
        description: 'Optional: who you are talking to or what they asked.',
        required: false,
      },
    ],
    build: ({ situation }) =>
      `Call the_gospel tool first. Explain the gospel of Jesus Christ using it: plainly, warmly, in Scripture's own words, quoting the verses it returns with the translation named (World English Bible). Do not water it down or add to it. Invite a response, and point to Assurance of Salvation for someone who wants to know they are saved.${situation ? `\n\nThe situation: ${situation}` : ''}`,
  },
  {
    name: 'answer_from_scripture',
    title: 'Answer a question from Scripture',
    description:
      'Answer a Bible question the way this site asks assistants to: Scripture first, the study that treats it, its one-sentence thesis, and whose reading it is.',
    arguments: [
      { name: 'question', description: 'The question, in your own words.', required: true },
    ],
    build: ({ question }) =>
      `Question: ${question}\n\nAnswer it from Scripture using The Way's connector. Call search_studies with the question; read the best match with get_study. Quote the verses the study rests on with read_passage (name the translation), quote the study's one-sentence thesis, and link it. Where Christians disagree, say the study's reading is this site's reading, and give the other. If the question touches salvation, call the_gospel. Never present the site as an authority: point the reader to the verses to test it (Acts 17:11).`,
  },
  {
    name: 'look_beneath_the_english',
    title: 'Look beneath the English of a passage',
    description:
      'Read a passage in the original languages: the words under the English, what the translation hides, who is acting, what it quotes, and what the manuscripts say.',
    arguments: [
      { name: 'passage', description: 'A passage, e.g. "John 21:15-17".', required: true },
    ],
    build: ({ passage }) =>
      `Study ${passage} beneath the English with The Way's connector. In order: read_passage (the text in English and in the original); beneath_the_english (the original word under each English phrase); hidden_distinctions (what the English hides); word_study on the one or two words doing the most work; who_is_acting where it matters who does what; quotation_trace (what it quotes and what quotes it); textual_notes. Then say plainly what the original shows that a reader of English would miss, and mark how certain each point is. Finish with studies_for_passage, and with what the passage shows about God.`,
  },
  ...Object.entries(SKILLS).map(([name, s]) => ({
    name: name.replace(/-/g, '_'),
    title: s.title,
    description: s.description,
    arguments: [
      {
        name: 'passage_or_topic',
        description: 'The passage, topic, study or claim to work on.',
        required: true,
      },
    ],
    build: async ({ passage_or_topic }, data) =>
      `${ADAPTER}Work on: ${passage_or_topic}\n\n---\n\n${await data.text(s.path)}`,
  })),
];

export const SKILL_RESOURCES = Object.entries(SKILLS).map(([name, s]) => ({
  uri: `the-way://skills/${name}`,
  name,
  title: s.title,
  description: s.description,
  mimeType: 'text/markdown',
  path: s.path,
}));
