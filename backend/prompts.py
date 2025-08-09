"""Short, focused prompt definitions for the Artisty backend."""

from __future__ import annotations

def build_first_pass_user_prompt(user_message: str) -> str:
    """Short instruction: acknowledge, then 1–5 precise suggestions from inventory."""
    return (
        "You are selecting artworks strictly from the INVENTORY text above.\n"
        "Each inventory line is `Name - $Price (Country) - Description`.\n"
        "Start with a short, funny acknowledgement of the user's request.\n"
        "Then list 1 to 5 artworks that BEST match the user's request and inform that it is the main suggestion.\n"
        "Understand the core request first (country/region/continent, style, theme, color, price, specific name).\n"
        "Region→country mapping (use only countries that exist in the inventory):\n"
        "- africa → south africa, egypt, morocco\n"
        "- south america → brazil, argentina\n"
        "- north america → usa, canada\n"
        "- europe → uk, england, france, italy, spain, portugal, netherlands, germany, norway, ireland, poland, austria, hungary, denmark, switzerland, greece, iceland, finland, turkey\n"
        "- asia → japan, china, korea, thailand, india, vietnam, turkey\n"
        "- oceania → australia, new zealand\n"
        "Also accept synonyms: uk≈united kingdom≈britain≈english≈england.\n"
        "Matching rules (apply in order and be strict):\n"
        "- If a country/region/continent is mentioned, ONLY choose items whose origin exactly matches one of the mapped countries.\n"
        "- If a style/theme/color is mentioned, prefer items whose descriptions clearly include it.\n"
        "- If a specific artwork name is mentioned, include it if it exists.\n"
        "- If nothing matches exactly, say so briefly and suggest the closest alternatives from the inventory and inform that it is a closet suggestion.\n\n"
        f"User message: {user_message}"
    )


def build_second_pass_user_prompt(first_pass_answer: str) -> str:
    """Given the first-pass answer, extract ONLY the artwork names.

    Output format requirements:
    - Output ONLY the artwork names mentioned in the answer
    - Names are usually two words; list all of them
    - Return them on a single line as a space-separated sequence of words,
      where every two words form one artwork name
    - No punctuation, no quotes, no extra text
    - Example output: "golden gaze divide abstract rustle script"
    """
    return (
        "From the text below, extract the artwork NAMES only.\n"
        "Rules:\n"
        "- Names are usually two words (e.g., 'Golden Gaze').\n"
        "- Output ONLY the artwork names from main suggestion and closet suggestion only if main suggestion is not found, all in lowercase.\n"
        "- Put everything on ONE line, with a single space between words,\n"
        "  so that each consecutive PAIR of words is one artwork name.\n"
        "- No commas, no punctuation, no quotes, no numbering, no extra text.\n\n"
        f"Answer to analyze:\n{first_pass_answer}"
    )


