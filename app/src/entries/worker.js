/* global Request */
// The site's Worker. Static assets serve every page as before; only /mcp runs code (wrangler.jsonc's
// run_worker_first), where the public connector reads the same assets through the ASSETS binding.

import { createData } from '../connector/data.js';
import { handleHttp } from '../connector/server.js';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/mcp' || url.pathname === '/mcp/') {
      const data = createData(async (path) => {
        const response = await env.ASSETS.fetch(new Request(new URL(`/${path}`, url.origin)));
        return response.ok ? response.text() : null;
      });
      return handleHttp(request, data);
    }
    return env.ASSETS.fetch(request);
  },
};
