---
name: unslop
description: Cut AI tells from writing. Must apply to text intended to outlive the current session.
---

# Unslop

Edit text to remove AI patterns.

## Process

1. Scan for the patterns below.
2. Rewrite. Preserve meaning, required syntax, and intended tone. Never invent facts, numbers, quotes, or anecdotes. When a detail is missing, keep the claim the source supports or ask for the detail.
3. When asked to review rather than edit, quote each tell with its rule number and a fix. Don't rewrite, score, or guess who wrote the text.

## Patterns to detect and fix

### Content

1. Puffery. "load bearing", "belt and suspenders", "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted". Cut puffery, state what happened.
2. Name-dropping. Listing media outlets without context. Pick one, say what was said.
3. Superficial -ing phrases. "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete, or state the concrete consequence.
4. Promotional language. "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit". Use neutral descriptions.
5. Vague attributions. "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.
6. Formulaic challenges. "Despite challenges... continues to thrive." Replace with specific facts.

### Language

7. AI vocabulary. Additionally, crucial, delve, enduring, enhance, fostering, garner, genuinely (as intensifier), heavy lifting (figurative), Interestingly (opener), interplay, intricate, landscape (abstract), Notably (opener), pivotal, quietly (as praise), showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words.
8. Fancy ways to say "is". "serves as", "stands as", "boasts", "features". Just say "is" or "has".
9. Staged reveals. "Not just X, but Y", "It's not X. It's Y.", "No X. Just Y.", a question the writer answers ("Why? The cache was cold."), count teasers ("There are two reasons this matters"), and teasers that promise a point instead of making it ("Here's the surprising part"). State the point directly.
10. Rule of three. Forcing ideas into groups of three. Use the natural number.
11. Synonym cycling. Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
12. False ranges. "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

13. Em dashes. Never use them. Separate thoughts with a period or comma, or a colon before a list or example. Parenthetical asides, en dashes, and spaced hyphens trade one tell for another.
14. Colon overuse. Colons belong before a list or example, not as a mid-sentence hinge ("The catch: it's slow").
15. Markdown overuse. Don't bold every proper noun or acronym. Use no markdown in plain-text output such as commit messages.
16. Inline-header lists. A bold label at the start of a line or bullet ("**Performance:** Performance improved", "**Schema.** Tables live in one file.") is a tell. Fold the label into a plain sentence or drop it.
17. Headings. Use sentence case. Name what the section says, not "Closing thoughts" or "Key takeaways". Conventional and template headings like "Installation" stay.
18. Decorative emojis. Remove from headings and bullets.
19. Curly quotes. Replace with straight quotes.

### Communication artifacts

20. Chatbot phrases. "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
21. Cutoff disclaimers. "While specific details are limited..." Find sources or remove.
22. Sycophantic tone. "Great question! You're absolutely right!" Respond directly.

### Filler

23. Filler phrases. "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that", "worth noting", "To be clear," and "Honestly," get deleted.
24. Excessive hedging. "could potentially possibly be argued that it might" becomes "may".
25. Windups and generic closers. Cut an opening paragraph that only sets context. Cut "The future looks bright", endings that restate the opening, and one-line closers. Stop at the final fact.

### Jargon

26. Abstract metaphor nouns. Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word. Terms of art stay ("attack surface", "attack vector").

### Plain speech

27. Say what it does, not how it feels. "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. Replace "This is intentional" or "Here's why that matters" with the reason.
28. Shorten or split dense sentences. If the reader has to backtrack to parse a sentence, break it in two or drop clauses. Vary sentence length. Merge short sentences split for effect ("X works. Y doesn't.") into one.
29. Active voice. Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or doesn't matter.
30. Cut adverbs, or use a stronger verb. "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. Prefer the plain word. "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer.
32. Mannered prose. Metaphor or flourish where a literal phrase exists: aphorisms ("wire it or delete it"), personified code ("the plan holds it"), figurative verbs ("rides along", "stands on"), stock framing phrases. "A dial worth turning" becomes "a parameter worth varying". Say what you mean. Rule 26 covers the metaphor nouns.
33. Over-compression. Dropped articles, verbless fragments, symbol-speak, and abbreviations that make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs, and spell out arrows and abbreviations.
