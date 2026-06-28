# Content Engine

A repeatable pipeline for turning one topic into a full content cycle across
every channel Plaza Park Interiors (and any future Morris Mayer ventures,
including AI-influence content) actually posts to. One cornerstone blog post
in, a full week-plus of derivative content out.

## How it works

```
brand/                      ← who's talking and how (reused on every run)
  plaza-park-interiors.md     researched brand facts, services, differentiators
  voice-guide.md               SelfScribe 3.0 / BrandScribe voice notes

runs/<date>-<topic-slug>/   ← one folder per content cycle
  00-brief.md                  topic, audience, CTA, assumptions for this run
  01-blog-post.md              2,000-3,000 word cornerstone post
  02-facebook-thread-posts.md  5 thread-style (numbered/serial) FB posts
  03-facebook-posts.md         5 standard single-caption FB posts
  04-instagram-posts.md        3 IG captions
  05-linkedin-posts.md         3 trade-audience LinkedIn posts
  06-video-scripts.md          3 x 30-second talking-head video scripts
  07-gemini-omni-prompts.md    5 multimodal generation prompts
  08-grok-imagine-video-prompts.md  6 x 10-second video prompts
  09-grok-image-prompts.md     5 still-image generation prompts
  10-email-constant-contact.md draft email for the Constant Contact list
  INDEX.md                     quick links + at-a-glance summary of the run
```

Everything downstream is pulled from the blog post — same facts, same voice,
same CTA — so the whole week of content reinforces one idea instead of
scattering ten unrelated ones.

## Running it again for a new topic

1. Copy `runs/_template/` (or the most recent run folder) to
   `runs/<date>-<new-topic-slug>/`.
2. Fill in `00-brief.md`: topic, audience, the one CTA for this cycle, any
   facts/offers that need to be true.
3. Update `brand/voice-guide.md` first if SelfScribe 3.0 / BrandScribe output
   has changed — every run after that inherits it automatically.
4. Write the blog post first, then derive every other file from it in order.
5. Drop the run's `INDEX.md` into whatever you use to actually schedule/post
   (Buffer, Later, Constant Contact, etc.) — it's the copy-paste jumping-off
   point.

## Known gaps (fix these to make future runs faster and more accurate)

- **Voice source**: `brand/voice-guide.md` is now built from Morris's real
  "Brandscribe Agentic Workflow Info" doc plus real published samples from his
  existing Daily Grind Content Engine / Daily Authority Content pipeline (both
  found in Google Drive). What's still missing: a completed personal SelfScribe
  3.0 "style snippet" for Morris himself — Drive only had the generic
  SelfScribe interview/prompt tool and an unopened `SELFscribe 3.skill` package,
  not a finished output. If/when that personal output exists, fold it in.
- **Brand facts**: `brand/plaza-park-interiors.md` is now verified against
  internal docs (official company dossier, workers'-comp legal-entity filing,
  live site copy) — legal name, address, phone, founding date, and the
  Metro-North concierge detail are all confirmed. Still open: current
  promotions/lead times/capacity for any specific run's CTA — confirm per run.
- **AI-influence content**: this run covers the interior-design/trade side
  only. Morris's "AI influence" persona (e.g. live AI build/launch events at
  The White Room at 707) needs its own `brand/<persona>.md` and a parallel
  `runs/` entry rather than blending it into the interiors voice.
- **Existing pipeline overlap**: Morris already runs an automated "Daily Grind
  Content Engine" / "Daily Authority Content" system producing similar
  cornerstone-post-plus-derivatives output on a regular cadence. This
  `content-engine/` is a parallel, version-controlled, repo-based version of
  that same idea — worth comparing outputs over a few runs to see whether they
  should be merged into one system rather than run in parallel.
