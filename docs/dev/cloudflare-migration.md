# Cloudflare Workers migration plan

Moving the site from GitHub Pages to Cloudflare Workers static assets, keeping `the-way.lewy.au`.

**Status: Phase 1 in progress (2026-09-05).** `lewy.au` added to Cloudflare (Free plan). Assigned
nameservers: `simone.ns.cloudflare.com`, `zac.ns.cloudflare.com` (original VentraIP nameservers were
`ns1/2/3.nameserver.net.au` — see the rollback section).

**Motivation:** site analytics. GitHub Pages gives none. Cloudflare Web Analytics is server-side
once the zone is proxied — no JS beacon, no cookie banner, not defeated by ad blockers.

**Two constraints drive every decision below:** it must stay free, and the DNS move must not break
anything. Both are addressed first; the ordered steps follow.

---

## 1. Cost

**Total ongoing cost: $0.** Nothing in this migration moves off a free tier, and the registrar bill
at VentraIP is unchanged.

| Item | Plan | Cost |
|---|---|---|
| Domain registration (`lewy.au`) | VentraIP, unchanged — registrar does **not** move | as today |
| DNS hosting | Cloudflare Free — unlimited records | $0 |
| TLS certificate | Cloudflare Universal SSL, auto-issued and auto-renewed | $0 |
| Static asset requests | Free **and unlimited**, explicitly, on every plan | $0 |
| Worker script invocations | Workers Free — 100,000/day | $0 (see below) |
| Web Analytics | Cloudflare Free | $0 |
| CI | GitHub Actions, public repo | $0 |

### Why the 100,000/day cap never applies here

That cap counts **Worker script invocations**, not asset requests. This site deploys as an
*assets-only* Worker — `wrangler.jsonc` has no `main` key, so there is no script to invoke. Every
request is served directly from Cloudflare's asset store, which is free and unlimited. The daily
cap is not something this site can reach; it is not a traffic ceiling.

### Headroom against the free-plan limits

| Limit (free plan) | Ceiling | This site | Headroom |
|---|---|---|---|
| Files per Worker version | 20,000 | ~1,200–1,500 built files | ~93% spare |
| Individual file size | 25 MiB | 3.0 MB (`assets/js/references.js`) | ~88% spare |

Source files are 579 across `docs/content/`; the build expands that to roughly 900 HTML pages
(556 content pages plus the ~346 `mkdocs-redirects` stubs) plus assets and the Material theme.
Even tripling the corpus stays inside the free tier.

### The three tripwires that would start a bill

Cost here is a **consequence of adding server-side behaviour**, not of traffic growth. Watch for:

1. **Adding a `main` script** to `wrangler.jsonc` — every request then becomes a billable
   invocation, and the 100,000/day cap becomes real. Requires Workers Paid ($5/mo) beyond that.
2. **Setting `run_worker_first`** — same effect, and worse on the free plan: requests matching the
   pattern that exceed the free allowance return `429 Too Many Requests` rather than falling back
   to serving the static asset. Do not set this without moving to the paid plan first.
3. **Exceeding 20,000 files** — distant, but the generated cross-reference pages are the thing that
   would get there. Workers Paid raises this to 100,000.

None of these are needed for a static site. If the plan stays assets-only, the plan stays free.

---

## 2. DNS — the actual risk

### The hard constraint

Cloudflare's own migration guide states it plainly: **"Workers does not support any domain whose
nameservers are not managed by Cloudflare."** Pages allowed a CNAME from external nameservers;
Workers does not. Cloudflare only sells subdomain-only zones (i.e. `the-way.lewy.au` as its own
zone) on Business and Enterprise plans, which would breach the cost constraint.

So the **entire `lewy.au` zone must move to Cloudflare nameservers**. VentraIP remains the
registrar; only DNS hosting moves. This is the single irreversible-feeling step, and it is where
the risk sits.

### What is actually in the zone

Checked over public DNS on 2026-09-05:

| Name | Type | Value | What it is |
|---|---|---|---|
| `lewy.au` | A | `103.42.108.46` | VentraIP/Synergy parking page |
| `www.lewy.au` | A | `103.42.108.46` | same parking page |
| `the-way.lewy.au` | A ×4 | `185.199.108–111.153` | GitHub Pages — the site |
| `lewy.au` | NS | `ns1/2/3.nameserver.net.au` | VentraIP nameservers |

And, confirmed absent at the apex:

- **No MX records.** There is no email on this domain to break.
- **No SPF, no DKIM, no DMARC, no CAA.** Nothing subtle to carry across.

The reverse lookup on `103.42.108.46` is `redirection.synergywholesale.com`, and the page it serves
is a VentraIP parking template — so the apex and `www` carry no real service either.

**This is close to the best case.** The zone is three records deep, one of which is the site being
migrated and two of which are a parking page. The usual reasons a nameserver move goes wrong —
dropped MX, lost SPF/DKIM causing silent mail rejection — do not apply, because there is no mail.

### The one caveat on that finding

The sweep above was a **guessed-name probe**, not a zone transfer. It resolved the apex, `www`,
`the-way`, and ~20 common names (`mail`, `api`, `nas`, `vpn`, `staging`, …). A subdomain with an
unguessable name would not have shown up. **Step 1 is therefore still mandatory and not optional:
export the authoritative zone from VIPControl and diff it against Cloudflare's import.** Do not
skip it on the strength of this table.

### What to expect on the parking page

VentraIP's domain-redirection feature is tied to their DNS. Once nameservers move, that feature
stops being available in VIPControl even though the A record still resolves to their IP. If the
apex/`www` parking is worth keeping, replace it with a **Cloudflare Redirect Rule** — free, and
better, since it can send `lewy.au` and `www.lewy.au` straight to the site instead of a parking
page. Decide this at step 10; nothing depends on it.

### Why the plan is sequenced the way it is

The nameserver change is made **while Cloudflare is serving a byte-identical record set** —
including the existing GitHub Pages A records, left DNS-only. Visitors see no change at the moment
of the NS flip, so if anything is wrong it shows up as a DNS resolution problem to diagnose calmly,
not as a site outage. The site itself moves later, in one small record change that is trivially
reversible. **The scary step and the site-moving step are deliberately not the same step.**

---

## 3. Ordered steps

### Phase 1 — Prepare (no visible change)

1. **Export the `lewy.au` zone from VIPControl.** This isn't a technical zone transfer (AXFR) —
   VIPControl has no one-click export. Log in → **My Services → Domains → lewy.au → DNS**, and
   write down (or screenshot) every record shown: A, CNAME, MX, TXT, SRV, CAA. Save it alongside
   this file or in a note. This is the rollback reference and the diff source — Cloudflare's
   auto-scan in the next step guesses common subdomain names, it doesn't read VentraIP's zone
   directly, so it can miss something this manual pass would catch.
2. **Create the Cloudflare account** (Free plan) and add **`lewy.au`** as the site — the apex/root
   domain, not `the-way.lewy.au`. A Cloudflare zone is always the whole registrable domain; it
   can't be created for just a subdomain on the Free plan (that's the Business/Enterprise
   subdomain-zone feature mentioned above). Adding `lewy.au` gives Cloudflare authority over every
   name under it — `the-way`, `www`, anything else — as records inside that one zone.
   Cloudflare auto-scans and imports what it can find. **Diff the import against the step 1
   export, line by line**, and hand-add anything the scan missed.
3. **Set every record to DNS-only (grey cloud), not proxied (orange cloud).** Cloudflare's import
   sometimes auto-proxies records it recognizes as web traffic — check the cloud icon next to
   *each* record (there's usually a page-level "proxy all" toggle too; turn it off). This includes
   the four GitHub Pages A records for `the-way`. Grey-cloud means Cloudflare only answers DNS
   queries for now; traffic still goes exactly where it already goes. This is what makes the
   nameserver flip in step 8 a pure no-op — proxying `the-way` gets turned on deliberately, later,
   in step 10, once the Worker exists and has the custom domain attached. Set SSL/TLS mode to
   **Full (strict)** while here. Do not change nameservers yet.

### Phase 2 — Build the Worker (still no visible change)

4. **Add `wrangler.jsonc` at the repo root** — assets-only, no `main`:

   ```jsonc
   {
     "name": "the-way",
     "compatibility_date": "2026-09-05",
     "assets": {
       "directory": "./site",
       "not_found_handling": "404-page",
       "html_handling": "auto-trailing-slash"
     }
   }
   ```

   `auto-trailing-slash` is the default and is correct for mkdocs directory URLs: `/about/copyright/`
   serves `about/copyright/index.html` with a 200. `404-page` serves the `site/404.html` that
   mkdocs-material generates. **Do not use `single-page-application`** — it returns 200 for every
   bad URL, which poisons search indexing.

   `site/` is already gitignored, so the build output needs no `.gitignore` change.

5. **Deploy manually to `workers.dev` and test.** From the repo root:

   ```bash
   cd app && npm ci && npm run build:tools && cd ..
   uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin \
       --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects \
       mkdocs build --site-dir site
   npx wrangler deploy
   ```

   On the preview URL, check specifically:

   - **`/timeline/` and `/genealogy/`** — their bundles load from site-absolute paths, which is the
     exact failure mode that silently 404'd every tool asset in August 2026.
   - **A `mkdocs-redirects` target**, e.g. `/bible/commentaries/01-genesis/chapter-001/`. These are
     meta-refresh HTML pages so they should work untouched, but confirm one.
   - **Search, `/tags/`, and a deep commentary page.**
   - **A deliberately bad URL** → must return the 404 page with a 404 status, not a 200.

### Phase 3 — CI/CD

6. **Keep GitHub Actions. Swap only the deploy step.** Do *not* use Cloudflare Workers Builds: this
   build needs `fetch-depth: 0` (both `utils/generate_recent_updates.py` and the git-revision-date
   plugin read full history), needs `uv` *and* Node 24, and sits in a repo with 18 submodules that
   CI deliberately does not clone. Workers Builds is a fight for no gain, and GitHub Actions is
   equally free on a public repo.

   In Cloudflare, create an API token from the **"Edit Cloudflare Workers"** template. Add
   `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as GitHub repo secrets.

   In `.github/workflows/deploy.yml`: delete the separate `deploy` job, the `environment:` and
   `permissions:` blocks, and the `upload-pages-artifact` step; change `concurrency.group` from
   `pages` to `deploy`; add `wrangler.jsonc` to the `paths:` filter; and append to the `build` job:

   ```yaml
         - name: Deploy to Cloudflare Workers
           uses: cloudflare/wrangler-action@v3
           with:
             apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
             accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
   ```

   The existing path-filter caveat is unchanged: a commit touching only `references/` or `utils/`
   still deploys nothing.

7. **Push and confirm** the Action deploys cleanly to `workers.dev`. Two live copies now exist:
   GitHub Pages on the real domain, Workers on `workers.dev`.

### Phase 4 — Cutover

8. **Change nameservers at VentraIP** to the two Cloudflare nameservers assigned to the zone.
   Because Cloudflare is already serving an identical record set, **visitors see nothing change**.
   `.au` registry propagation is typically an hour or two; Cloudflare emails when the zone is active.
9. **Soak for a day.** Confirm `the-way.lewy.au` still resolves and serves, and that anything found
   in the step 1 export still works.
10. **Point the domain at the Worker.** In the Worker's Settings → Domains & Routes, add Custom
    Domain `the-way.lewy.au`. Cloudflare replaces the A records with its own proxied record and
    issues the certificate automatically; delete any leftover GitHub A records. Verify:

    ```bash
    curl -sI https://the-way.lewy.au | head
    ```

    The `server:` header should now be Cloudflare, not `GitHub.com`. This is also the point to add
    the apex/`www` Redirect Rule if the parking page is being replaced.

### Phase 5 — Clean up (after a week's soak)

11. **Enable Web Analytics** — automatic once traffic is proxied. This is the payoff.
12. **Remove the custom domain from GitHub Pages settings** and disable the Pages source. This ends
    easy rollback, hence the wait.
13. **Update the docs:** `AGENTS.md` (Commands and Architecture both describe a GitHub Pages
    deploy), `README.md`, and `docs/dev/README.md`. Note that `docs/dev/CONTRIBUTING.md` also still
    describes the pre-2026-08 Astro split and is already stale independently of this migration.
    Bump `VERSION`, note it in `CHANGELOG.md`.

---

## 4. Rollback

**Before step 12**, rollback is: re-add the four A records `185.199.108–111.153` as DNS-only, and
remove the Custom Domain from the Worker. This works only while GitHub Pages still has the custom
domain configured — which is the entire reason step 12 waits a week.

**Rolling back the nameserver move itself** (step 8) means setting the NS records at VentraIP back
to `ns1/2/3.nameserver.net.au` and restoring the zone from the step 1 export. Registry propagation
means this is a matter of hours, not minutes, which is why steps 1–3 are worth doing carefully.

## 5. No content changes required

`site_url` stays `https://the-way.lewy.au/`. Every site-absolute URL, the copyright footer link in
`mkdocs.yml`, and both tool bundle paths keep working untouched. This migration does not touch
`docs/content/`.
