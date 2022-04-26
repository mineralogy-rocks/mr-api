from django.utils.safestring import mark_safe


def formula_to_html(formula):
    if formula:
        replacements = [
            dict(to_replace=r'(_)(.*?_)', replacement=r'\1<sub>\2</sub>'),
            dict(to_replace=r'(\^)(.*?\^)', replacement=r'\1<sup>\2</sup>'),
            dict(to_replace=r'_', replacement=''),
            dict(to_replace=r'\^', replacement='')
        ]
        parsed = formula
        [parsed := re.sub(replacement['to_replace'], replacement['replacement'], parsed) for replacement in replacements]
        return mark_safe(parsed)
    return None