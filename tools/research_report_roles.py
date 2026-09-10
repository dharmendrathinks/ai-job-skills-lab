"""Title-only navigation hints, never requirement analysis or corpus admission."""
import re
import unicodedata

VERSION = 'report-title-families/1'
OTHER = 'Other / unclassified'


def role_families(title):
    """Allow overlapping families; ambiguous titles stay unclassified.

    Uses no description, query, employer or profile inference. These English
    title cues deliberately do not establish AI relevance or responsibilities.
    """
    title = unicodedata.normalize('NFKC', title).casefold()
    title = re.sub(r'[-–—_]', ' ', title)

    def has(pattern):
        return re.search(r'\b(?:' + pattern + r')\b', title) is not None

    ai = has(r'ai|artificial intelligence|llms?|large language models?|generative ai|genai')
    ml = has(r'ml|machine learning|mlops|deep learning')
    families = []

    def add(name, matches):
        if matches:
            families.append(name)

    add('Machine learning', ml)
    add('AI product engineering', ai and has(r'product') and has(r'engineer(?:ing)?|developer|architect'))
    add('Applied AI', has(r'applied (?:ai|artificial intelligence)'))
    add('LLM & generative AI', has(r'llms?|large language models?|generative ai|genai'))
    add('Agents & automation', has(r'agentic|multi ?agents?') or
        ai and has(r'agents?|automation|automations'))
    add('Retrieval & knowledge systems', has(r'rag|retrieval|knowledge graphs?'))
    add('AI evaluation & reliability', (ai or ml) and has(r'evaluation|evals?|reliability|observability|testing|quality'))
    add('AI security', (ai or ml) and has(r'security|safety|red team(?:ing)?'))
    add('AI infrastructure & MLOps', has(r'mlops|inference') or
        (ai or ml) and has(r'infrastructure|platforms?|deployment|operations'))
    add('Research & applied science', has(r'(?:research|applied) scientists?|research engineer|research engineering'))
    add('Data science', has(r'data scien(?:ce|tists?)'))
    add('Data engineering & pipelines', has(r'data engineers?|data engineering|data pipelines?|data architects?'))
    # Generic AI engineering is a fallback, not an extra label on every specialist.
    add('General AI engineering', not families and ai and has(r'engineer(?:ing)?|developer|architect'))
    return families or [OTHER]
