"""City-name standardisation helpers."""
import re
import unicodedata


def normalize_name(value) -> str:
    """Lower-case, strip punctuation and collapse whitespace ('Navi-Mumbai.' -> 'navi mumbai')."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
