"""Minimal demo safeguards. No claim that regex is comprehensive privacy protection."""
import re
PATTERNS = [
    ('EMAIL', re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')),
    ('PHONE', re.compile(r'(?<!\w)(?:\+44\s?\d[\d\s\-]{8,12}|0[127]\d[\d\s\-]{8,12})(?!\w)')),
    ('CARD', re.compile(r'(?<!\d)(?:\d[ -]?){13,19}(?!\d)')),
]

def redact(text: str) -> tuple[str, list[str]]:
    found=[]
    for kind,pattern in PATTERNS:
        text,count=pattern.subn(f'[{kind}_REDACTED]',text)
        if count: found.append(kind)
    return text,found

# A shallow keyword check is a warning, not a security boundary.
SUSPICIOUS = re.compile(r'ignore (?:all |your |the )?(?:previous |system )?instructions|reveal (?:your |the )?(?:system prompt|secret|api key)|developer message|override (?:your |the )?rules', re.I)
def injection_warning(text: str) -> bool:
    return bool(SUSPICIOUS.search(text))
