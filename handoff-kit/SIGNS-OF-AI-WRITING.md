**For the agent. Never tell the user to read this. Apply it to every piece of copy and every script.**

# Signs of AI writing: local checklist

Source: Wikipedia, "Signs of AI writing" (https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). This is a short paraphrased checklist of that page, kept here so it works offline. Snapshot: November 2026. When you have web access, open the page once per new channel and add any new pattern to this list and to `templates/tools/copy_check.py` (the kit source), so the check grows with the page.

`copy_check.py` tests every mechanical item below that a pattern can catch. The ones marked (read) need a human-style read-aloud.

## Language and tone
- **AI vocabulary.** Words like delve, tapestry, testament, pivotal, crucial, intricate, vibrant, showcase, underscore, foster, garner, enhance, align, boast, enduring, interplay, valuable, landscape, realm, meticulous, seamless, additionally, moreover, furthermore, notably.
- **Inflated significance.** "marks a pivotal moment", "plays a vital role", "stands as a testament", "serves as a reminder".
- **Promotional language.** nestled, in the heart of, breathtaking, stunning, must-see, renowned, rich heritage, boasts a.
- **Superficial analysis.** A clause ending in ", highlighting ...", ", underscoring ...", ", reflecting ...", ", contributing to ...".
- **Vague attribution.** "experts say", "critics argue", "industry reports suggest", "many people believe", with no named source.
- **Negative parallelism.** "not X, it's Y", "it's not about X", "not only X but also Y", "no X, no Y, just Z".
- **Rule of three.** Lists of three adjectives or phrases used for rhythm rather than information.
- **False ranges.** "from X to Y, from A to B" where the ends are not on one scale.
- **Summary closers.** "In summary", "In conclusion", "Overall,", "To sum up".
- **Challenges and prospects formula.** "Despite its success, X faces challenges ...".
- **Elegant variation (read).** Swapping synonyms for the same thing every sentence to avoid repetition.
- **Copula avoidance (read).** "serves as", "functions as", "stands as" where "is" would do.

## Style and formatting
- **Em dashes and en dashes.** Zero, anywhere. Use a comma, period or colon.
- **Curly quotes and the ellipsis character.** Straight quotes and three typed dots only.
- **Title Case Everywhere (read).** Only where the measured competitor style does it.
- **Bold and emoji overuse.** Bolded phrases scattered through a paragraph, emoji bullets.
- **Colons stacked in one line.**
- **Uniform rhythm (read).** Every sentence the same length and shape. Real people vary.

## Chatbot leftovers
- "I hope this helps", "Certainly!", "Great question", "I'd be happy to", "Let me know if", "As of my last update".
- Stock hooks: "Ever wondered", "Buckle up", "You won't believe", "Here's the thing", "Let's dive in", "In today's fast-paced world", "Without further ado".

## Beyond the checklist
Avoiding these tells is not enough. Copy must also:
1. Match the measured style of the most-viewed comparable competitor copy: `python tools/copy_check.py style --ours ours.txt --theirs research/parity/competitor_titles.txt` (or `competitor_descriptions.txt`). Length, words per sentence, capitals, numbers, questions and how lines open all sit inside their band.
2. Improve on it, and win a strict blind pairwise test against it (`BLIND-TEST.md` section 8). Copy that has not won is not final.
