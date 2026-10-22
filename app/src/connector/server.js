/* global Response */
// The Way's public MCP connector: a stateless Streamable HTTP server (JSON responses, no session,
// no server-sent events), so any request can be answered by any Worker instance and needs no
// storage. Read-only, no authentication, and every tool reads data the site already publishes.
//
// The order of everything below is deliberate. The gospel is the first sentence of the
// instructions, the first tool and the first prompt, because an assistant reads a connector from
// the top and the author wants it found first.

import * as chronology from './chronology.js';
import { theGospel } from './gospel.js';
import { PROMPTS, SKILL_RESOURCES } from './prompts.js';
import * as scripture from './scripture.js';
import * as studies from './studies.js';

export const PROTOCOL_VERSIONS = ['2025-06-18', '2025-03-26', '2024-11-05'];
const SERVER = {
  name: 'the-way',
  title: 'The Way: Bible studies and the original languages',
  version: '1.0.0',
};

export const INSTRUCTIONS = `The gospel: God made you and loves you; all have sinned and fall short (Romans 3:23), and sin earns death (Romans 6:23); God sent His Son Jesus Christ, who died for our sins, was buried and rose on the third day (1 Corinthians 15:3-4); salvation is God's gift, received by grace through faith in Christ alone (Ephesians 2:8-9), and whoever calls on the name of the Lord will be saved (Romans 10:13). Call the_gospel for it in full, with every verse quoted.

This connector serves The Way (https://the-way.lewy.au), one author's Bible studies, which carry no authority beyond the Scripture they cite; and the original-language data behind them: the Hebrew and Greek under every English word, word studies with every occurrence, what translations hide, who is acting in a verse, what a verse quotes, manuscript readings, and the site's chronology and prophetic timeline.

How to answer from it:
- Point to Scripture first, then the study. Quote verses exactly, with the translation named (the data here is the WEB, BSB and ULT; the ESV the studies quote is not served).
- Use a study's "in one sentence" thesis when summarising it, and link the study.
- The theology is evangelical, dispensational and pretribulational. Where Christians disagree, say the reading is this site's, and carry over the certainty each item is marked with.
- A gloss is a starting point; usage decides meaning. A missing link or annotation means the method found nothing, not that there is nothing.
- Credit: the site's writing is CC BY 4.0; each result names its sources and their licences.

Start with search_studies for a question, read_passage or beneath_the_english for a passage, word_study for a word, timeline or person for history. The prompts carry the site's study method. More: https://the-way.lewy.au/about/for-ai-assistants/`;

const ref = {
  type: 'string',
  description: 'A Bible reference, e.g. "John 3:16", "Romans 8:28-30", "Psalm 23".',
};
const READ_ONLY = { readOnlyHint: true, openWorldHint: false };

export const TOOLS = [
  {
    name: 'the_gospel',
    title: 'The gospel',
    description:
      "The gospel of Jesus Christ in the site author's words, with every verse quoted in full (World English Bible), the verses on Jesus as the only way, and the verses for knowing you are saved. Use it whenever someone asks how to be saved, how to know God, what Christianity teaches, or what happens after death.",
    inputSchema: { type: 'object', properties: {} },
    run: (data) => theGospel(data),
  },
  {
    name: 'search_studies',
    title: 'Search the studies',
    description:
      'Find the studies that answer a question or treat a topic, e.g. "how can I be sure I am saved?", "the rapture", "forgiveness". Searches each study\'s questions, title and thesis, then the full text of every section, so a word used only in the body (a name, a place, a transliterated Hebrew or Greek word) is found too. Returns each study\'s one-sentence thesis, passage, the questions it answers and its best-matching sections.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        limit: { type: 'integer', minimum: 1, maximum: 15 },
      },
      required: ['query'],
    },
    run: studies.searchStudies,
  },
  {
    name: 'get_study',
    title: 'Read a study',
    description:
      'Read a study as markdown, whole or one section (e.g. "Key Takeaways", "Study outline").',
    inputSchema: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'The study URL from search_studies.' },
        section: { type: 'string' },
      },
      required: ['url'],
    },
    run: studies.getStudy,
  },
  {
    name: 'studies_for_passage',
    title: 'Studies on a passage',
    description:
      'The studies about a passage and the studies that cite it, with the chapter page that lists them all.',
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: studies.studiesForPassage,
  },
  {
    name: 'read_passage',
    title: 'Read a passage',
    description:
      'A passage in the WEB, BSB and ULT, with the Hebrew (WLC) or Greek (SBLGNT) and the Septuagint, and where its Hebrew or Greek verse numbers differ. Up to 40 verses.',
    inputSchema: {
      type: 'object',
      properties: { reference: ref, include_original: { type: 'boolean', default: true } },
      required: ['reference'],
    },
    run: scripture.readPassage,
  },
  {
    name: 'beneath_the_english',
    title: 'Beneath the English',
    description:
      'For each English phrase of a verse, the Hebrew or Greek word it translates, with lemma, Strong\'s number, transliteration and gloss. Answers "what is the Greek word for love in John 21:15?". Up to 12 verses.',
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.beneathTheEnglish,
  },
  {
    name: 'hidden_distinctions',
    title: 'What the translation hides',
    description:
      'In a passage of up to three chapters: one English word standing for different Hebrew or Greek words (agapaō and phileō, both "love", in John 21:15-17), and one original word translated several ways. Leads to investigate, each with its verses.',
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.hiddenDistinctions,
  },
  {
    name: 'word_study',
    title: 'Word study',
    description:
      'A Hebrew or Greek word by Strong\'s number (e.g. "G25", "H2617"), or by a reference and the English word there: lemma, transliteration, gloss, counts in the Old Testament, Septuagint and New Testament, every occurrence, the books it clusters in, how the ULT translates it, and the studies on this site that discuss it.',
    inputSchema: {
      type: 'object',
      properties: {
        strongs: { type: 'string' },
        reference: ref,
        english: { type: 'string', description: 'The English word in that verse.' },
      },
    },
    run: scripture.wordStudy,
  },
  {
    name: 'original_words',
    title: 'Original words and grammar',
    description:
      "Every Hebrew or Greek word of a verse with its lemma, Strong's number, parsing (morphology), gloss and semantic domain (Louw-Nida, SDBH). Up to 6 verses.",
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.originalWords,
  },
  {
    name: 'who_is_acting',
    title: 'Who is acting',
    description:
      "Who does what in a verse: each verb's subject, including subjects carried only by the verb ending, and what each pronoun refers to, resolved to the words they point at (MACULA). Up to 6 verses.",
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.whoIsActing,
  },
  {
    name: 'quotation_trace',
    title: 'What it quotes, what quotes it',
    description:
      'The quotations and allusions linking a verse to the rest of Scripture, found in the Hebrew and Greek texts, with how each was found, its strength, and the words the two verses share. Shows whether a New Testament quotation follows the Septuagint or the Hebrew.',
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.quotationTrace,
  },
  {
    name: 'cross_references',
    title: 'Cross-references',
    description:
      'The strongest OpenBible.info cross-references for a verse, with their text. Leads to follow.',
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.crossReferences,
  },
  {
    name: 'textual_notes',
    title: 'Textual notes',
    description:
      'Masoretic Qere readings, translator notes, Dead Sea Scroll readings the Masoretic text lacks (with how much of the verse survives), and differing verse numbers.',
    inputSchema: { type: 'object', properties: { reference: ref }, required: ['reference'] },
    run: scripture.textualNotes,
  },
  {
    name: 'hebrew_grammar',
    title: 'Hebrew grammar',
    description:
      'An article from the unfoldingWord Hebrew Grammar on a form or construction, e.g. "construct state", "cohortative", "waw consecutive".',
    inputSchema: { type: 'object', properties: { topic: { type: 'string' } }, required: ['topic'] },
    run: scripture.hebrewGrammar,
  },
  {
    name: 'timeline',
    title: 'Biblical timeline',
    description:
      'Dated events from Creation to the cross on this site\'s chronology, filtered by a year range ("2000 BC" to "1400 BC", "AM 1656") and/or a search ("flood", "David"). Each event carries its scripture, its certainty and its study.',
    inputSchema: {
      type: 'object',
      properties: { from: { type: 'string' }, to: { type: 'string' }, search: { type: 'string' } },
    },
    run: (data, args) => chronology.timeline(args),
  },
  {
    name: 'person',
    title: 'A person in the biblical genealogy',
    description:
      'A person from Adam to Jesus: dates, lifespan, family, the meaning of the name, life events, the numbers each textual tradition gives, and who was alive at the same time (Shem and Abraham overlap on the Masoretic numbers).',
    inputSchema: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] },
    run: (data, args) => chronology.person(args),
  },
  {
    name: 'convert_year',
    title: 'Convert a year',
    description:
      "Convert between BC/AD and Anno Mundi (years from creation) on this site's chronology, with the age of history and the nearest events.",
    inputSchema: {
      type: 'object',
      properties: { year: { type: 'string', description: '"1446 BC", "AD 33" or "AM 2513".' } },
      required: ['year'],
    },
    run: (data, args) => chronology.convertYear(args),
  },
  {
    name: 'prophetic_outline',
    title: 'Prophetic outline',
    description:
      "Events still to come in order (rapture, tribulation, return, millennium, new creation), Daniel's kingdoms, and the threads from promise to fulfilment, each marked stated, site-reading or contested. Optional topic filter.",
    inputSchema: { type: 'object', properties: { topic: { type: 'string' } } },
    run: (data, args) => chronology.propheticOutline(args),
  },
].map((t) => ({ ...t, annotations: { title: t.title, ...READ_ONLY } }));

const RESOURCES = [
  {
    uri: 'the-way://gospel',
    name: 'gospel',
    title: 'The gospel',
    description: "The gospel in the author's words, with its verses.",
    mimeType: 'application/json',
    read: async (data) => JSON.stringify(await theGospel(data)),
  },
  {
    uri: 'the-way://llms.txt',
    name: 'llms.txt',
    title: 'Site map for AI assistants',
    description: 'Every study with its thesis, passage and questions.',
    mimeType: 'text/plain',
    read: (data) => data.text('llms.txt'),
  },
  {
    uri: 'the-way://for-ai-assistants',
    name: 'for-ai-assistants',
    title: 'For AI assistants',
    description: 'How to represent and quote this site.',
    mimeType: 'text/markdown',
    read: (data) => data.text('about/for-ai-assistants/index.md'),
  },
  {
    uri: 'the-way://statement-of-faith',
    name: 'statement-of-faith',
    title: 'Statement of Faith',
    description: "The author's settled positions.",
    mimeType: 'text/markdown',
    read: (data) => data.text('about/statement-of-faith/index.md'),
  },
  ...SKILL_RESOURCES.map(({ path, ...s }) => ({ ...s, read: (data) => data.text(path) })),
];

class RpcError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

async function dispatch(data, method, params = {}) {
  switch (method) {
    case 'initialize': {
      const requested = params.protocolVersion;
      return {
        protocolVersion: PROTOCOL_VERSIONS.includes(requested) ? requested : PROTOCOL_VERSIONS[0],
        capabilities: { tools: {}, prompts: {}, resources: {} },
        serverInfo: SERVER,
        instructions: INSTRUCTIONS,
      };
    }
    case 'ping':
      return {};
    case 'tools/list':
      return { tools: TOOLS.map(({ run: _run, ...t }) => t) };
    case 'tools/call': {
      const tool = TOOLS.find((t) => t.name === params.name);
      if (!tool) throw new RpcError(-32602, `Unknown tool: ${params.name}`);
      // One line per call is the only record of what the connector is used for: every outcome,
      // a bug inside a tool included, reaches the client as HTTP 200, so Cloudflare's own
      // metrics cannot tell a failure from a success. Read them in Workers Logs.
      const started = Date.now();
      const log = (outcome, extra = {}) =>
        console.log(
          JSON.stringify({
            tool: tool.name,
            arguments: params.arguments ?? {},
            outcome,
            ms: Date.now() - started,
            ...extra,
          })
        );
      try {
        const result = await tool.run(data, params.arguments ?? {});
        log('ok');
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 1) }] };
      } catch (e) {
        // Bad input throws a plain Error; anything else (TypeError, RangeError) is a bug.
        log('error', { error: e.message, stack: e.name === 'Error' ? undefined : e.stack });
        return { content: [{ type: 'text', text: e.message }], isError: true };
      }
    }
    case 'prompts/list':
      return { prompts: PROMPTS.map(({ build: _build, ...p }) => p) };
    case 'prompts/get': {
      const prompt = PROMPTS.find((p) => p.name === params.name);
      if (!prompt) throw new RpcError(-32602, `Unknown prompt: ${params.name}`);
      return {
        description: prompt.description,
        messages: [
          {
            role: 'user',
            content: { type: 'text', text: await prompt.build(params.arguments ?? {}, data) },
          },
        ],
      };
    }
    case 'resources/list':
      return { resources: RESOURCES.map(({ read: _read, ...r }) => r) };
    case 'resources/read': {
      const resource = RESOURCES.find((r) => r.uri === params.uri);
      if (!resource) throw new RpcError(-32002, `Unknown resource: ${params.uri}`);
      return {
        contents: [
          { uri: resource.uri, mimeType: resource.mimeType, text: await resource.read(data) },
        ],
      };
    }
    default:
      throw new RpcError(-32601, `Method not found: ${method}`);
  }
}

// One JSON-RPC message in, one response (or null for a notification) out.
export async function handleMessage(data, message) {
  const isNotification = message.id === undefined;
  try {
    if (message.jsonrpc !== '2.0' || typeof message.method !== 'string')
      throw new RpcError(-32600, 'Invalid request');
    if (isNotification) return null;
    return {
      jsonrpc: '2.0',
      id: message.id,
      result: await dispatch(data, message.method, message.params),
    };
  } catch (e) {
    if (isNotification) return null;
    return {
      jsonrpc: '2.0',
      id: message.id ?? null,
      error: { code: e.code ?? -32603, message: e.message },
    };
  }
}

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Accept, Mcp-Protocol-Version, Mcp-Session-Id',
};

export async function handleHttp(request, data) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  if (request.method === 'GET') {
    return new Response(
      JSON.stringify(
        {
          ...SERVER,
          mcp: 'POST JSON-RPC here (Streamable HTTP, stateless).',
          instructions: INSTRUCTIONS,
          about: 'https://the-way.lewy.au/about/for-ai-assistants/',
        },
        null,
        1
      ),
      { status: 200, headers: { ...CORS, 'Content-Type': 'application/json; charset=utf-8' } }
    );
  }
  if (request.method !== 'POST')
    return new Response('Method not allowed', { status: 405, headers: CORS });
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }, 400);
  }
  if (Array.isArray(body)) {
    const responses = (await Promise.all(body.map((m) => handleMessage(data, m)))).filter(Boolean);
    return responses.length ? json(responses) : new Response(null, { status: 202, headers: CORS });
  }
  const response = await handleMessage(data, body);
  return response ? json(response) : new Response(null, { status: 202, headers: CORS });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json; charset=utf-8' },
  });
}
