
Additional extraction contract: skill-extraction/2.
Return skill_mentions as well as the original claims. Read the entire description,
not just tools in existing claims. Each surface is a short EXACT substring naming
one specific skill, knowledge concept, technology or other requirement. Each quote
is an exact supporting clause. Preserve wording, punctuation and whitespace.
section_context is an exact nearby heading/clause establishing required/preferred
status, or the empty string. Never infer required status solely from your judgment.

Kinds: practice (doing engineering work), knowledge (concept or method), technology
(named language/library/platform/tool), other-requirement (experience, qualification,
work condition). RAG, embeddings, hybrid search and tool calling are knowledge;
model evaluation and fine-tuning are practices. A named library is technology.
Do not count compensation, benefits or immigration terms as technical skills.
Do not extract negated requirements, company aspirations, perks or generic company
descriptions as demanded skills. No inferred fashionable prerequisites. Distinct
mentions may share an evidence quote; repeated mentions need not be repeated.
Preserve novel source phrases. You do not create canonical IDs or alias merges.
An exact quote validator cannot prove semantic accuracy; preserve unknowns.
