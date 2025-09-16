"""Prompt templates for the novelgen pipeline."""

PREMISE_PROMPT = """You are outlining a novel. Using the provided constraints, craft a concise high-level premise. Return clean Markdown with sections for Logline, Tone, Themes, and Risks.
Constraints:\n{constraints}\n"""

SEED_PROMPT = """Expand the premise into 10 provocative seed ideas that could power a long novel. Each idea should be a Markdown bullet with a short label and 2 sentence description. Use the premise and constraints below.\nPremise:\n{premise}\nConstraints:\n{constraints}\n"""

CHARACTERS_PROMPT = """Produce a Markdown roster of exactly 8 characters. For each include: role, archetype, desire, internal conflict, external pressure, and a 3-beat micro-arc tied to the premise. Keep entries tight and scannable.\nSeed ideas:\n{seed}\n"""

ARCS_PROMPT = """Transform the character roster into linked 6-beat arcs for each major character. Present as Markdown with subsections per character and a numbered list of beats named Setup, Disruption, Commitment, Reversal, Climax, Resolution. Reference relationships across characters.\nRoster:\n{roster}\n"""

WORLD_PROMPT = """Summarize the story world in Markdown with sections for History, Power Structures, Culture, Technology/Magic, Factions, and Ticking Clocks. Keep each section under 6 bullet points.\nSeed ideas:\n{seed}\n"""

LOCATIONS_PROMPT = """Design 15 key locations relevant to the story world. First output a Markdown table listing id, name, type, summary, and first_seen. Then output a JSONL block where each line is an object with fields id, name, type, summary, sensory (array), plot_functions (array), hazards (array), ties (array), first_seen, coords. Only return valid JSONL in the block.
Seed ideas:\n{seed}\nWorld summary:\n{world}\n"""

CHAPTER_PLAN_PROMPT = """Create a 50 chapter outline for the novel. Return a Markdown table with columns: #, POV, location_id, setting, goal, conflict, outcome, exit_hook, words=2400. Ensure exactly 50 rows. After the table, add short Act I/II/III beat summaries in Markdown paragraphs.
Seed ideas:\n{seed}\nCharacter arcs:\n{arcs}\nWorld bible:\n{world}\nLocations JSONL:\n{locations}\n"""

SCENE_CARD_PROMPT = """Write a scene card summarizing the chapter entry below. Provide Markdown with sections: Summary, POV, Setting, Stakes, Beats (bullet list), Foreshadowing, Questions.\nChapter row:\n{row}\n"""

SCENE_DRAFT_PROMPT = """Draft a 700-900 word scene based on the scene card and chapter details. Keep prose energetic and coherent. Output Markdown with a title and scene body paragraphs only.\nChapter row:\n{row}\nScene card:\n{card}\n"""

BIBLE_UPDATE_PROMPT = """Extract key canon updates from the scene draft. Return Markdown bullets grouped under Characters, Locations, Lore, Callbacks. Mention only durable facts suitable for a story bible.\nScene text:\n{scene}\n"""
