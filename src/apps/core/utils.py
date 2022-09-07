# -*- coding: UTF-8 -*-
import re

from django.utils.safestring import mark_safe


def formula_to_html(formula):
    if formula:
        replacements = [
            dict(to_replace=r"(_)(.*?_)", replacement=r"\1<sub>\2</sub>"),
            dict(to_replace=r"(\^)(.*?\^)", replacement=r"\1<sup>\2</sup>"),
            dict(to_replace=r"_", replacement=""),
            dict(to_replace=r"\^", replacement=""),
        ]
        parsed = formula
        [
            parsed := re.sub(
                replacement["to_replace"], replacement["replacement"], parsed
            )
            for replacement in replacements
        ]
        return mark_safe(parsed)
    return None


def get_relation_note(relation_type):
    note = ""
    if relation_type == 1:
        note = "Synonym"
    elif relation_type == 2:
        note = "Mixture"
    elif relation_type == 3:
        note = "Mixture (?)"
    elif relation_type == 4:
        note = "Minerals structurally related to group"
    elif relation_type == 5:
        note = "Associated Minerals at the locality"
    elif relation_type == 6:
        note = "Epitaxial Relationships"
    elif relation_type == 7:
        note = "Polymorph of"
    elif relation_type == 8:
        note = "Isostructural with"
    elif relation_type == 9:
        note = "Minerals chemically related to group"
    elif relation_type == 10:
        note = "Common Associates"
    elif relation_type == 11:
        note = "Mineralogy of  Essential minerals - these are minerals that are required within the classification of this rock"
    elif relation_type == 12:
        note = "Ores of  Common ore minerals of"
    elif relation_type == 13:
        note = "Mineralogy of  Accessory minerals - these are minor components, often far less than 1 percent of the total mineral material"
    return note
