---
name: unslop
description: Cut AI tells from writing. Must apply to text intended to outlive the current session.
---

# Unslop

Edit text to remove AI patterns.

## Process

1. Scan for the patterns below.
2. When asked to review rather than edit, quote each tell with its pattern number and a fix, then stop. Don't rewrite, score, or guess who wrote the text.
3. Otherwise, rewrite. Preserve meaning, required syntax, and intended tone. Never invent facts, numbers, quotes, or anecdotes. When a detail is missing, keep the claim the source supports or ask for the detail. Finish when every tell is fixed or its missing detail is requested.

## Patterns

Pattern numbers are stable ids. A removed pattern leaves a gap.

3. No trailing "-ing" phrase that adds no fact. State the concrete consequence or delete it.
5. No vague attributions. Name the source or delete the claim.
7. No AI vocabulary: additionally, belt and suspenders, crucial, delve, enduring, enhance, fostering, garner, genuinely (as intensifier), heavy lifting (figurative), Interestingly (opener), interplay, intricate, landscape (abstract), load bearing, Notably (opener), pivotal, quietly (as praise), showcase, tapestry (abstract), testament, underscore, vibrant. Use the plain word.
8. Say "is" or "has", not "serves as", "stands as", "boasts", or "features".
9. No staged reveals: contrast frames, questions the writer answers, count teasers, or teasers that promise a point. State the point.
10. Use the natural number of items, not a forced three.
11. Use one name per thing, and repeat it.
12. Use "from X to Y" only when X and Y sit on a real scale.
13. No em dashes, en dashes, or spaced hyphens, and no parentheses in their place. Use a period or a comma, or a colon before a list or example.
14. Use a colon only before a list or example, never as a mid-sentence hinge.
15. Don't bold every proper noun or acronym. Use no markdown in plain-text output, such as commit messages.
16. Don't start a line or bullet with a bold label. Fold it into a plain sentence or drop it.
17. Use sentence-case headings that name what the section says, not a generic label. Conventional and template headings, such as "Installation", stay.
18. No decorative emojis.
19. Use straight quotes.
20. No chatbot pleasantries or offers of more help.
22. No praise or agreement openers. Respond directly.
23. Cut filler phrases and asides that announce a point instead of making it.
24. Hedge at most once, with "may".
25. Cut an opening that only sets context, a closing that restates the opening or predicts the future, and one-line closers. Stop at the final fact.
26. No abstract metaphor nouns: substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. Use the concrete word. Terms of art, such as "attack surface", stay.
27. Say what it does, not how it feels. Name the mechanism or the number. Cut a sentence you can't restate as a concrete instruction, fact, or number. Give the reason instead of saying something is intentional or matters.
28. Split a sentence the reader has to reread. Vary sentence length. Merge short sentences split for effect.
29. Use active voice. Name the actor unless it is unknown or doesn't matter.
30. Cut adverbs or use a stronger verb. Give the number instead of an intensifier.
31. Use the plainest word that fits.
32. Write literally. No metaphor, aphorism, personified code, figurative verb, or stock framing where a literal phrase exists. Data, files, and types never act. Make a person or program the subject, or describe the state.
33. Write whole sentences with their articles and verbs. Spell out arrows, symbols, and abbreviations.
