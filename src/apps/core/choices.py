# -*- coding: UTF-8 -*-

CRYSTAL_SYSTEM_CHOICES = (
    (1, "hexagonal"),
    (2, "isometric"),
    (3, "monoclinic"),
    (4, "orthorhombic"),
    (5, "tetragonal"),
    (6, "triclinic"),
    (7, "trigonal"),
    (8, "amorphous"),
    (9, "icosahedral"),
)


APPROVED = 1
DISCREDITED = 2
PENDING_PUBLICATION = 3
GRANDFATHERED = 4
QUESTIONABLE = 5

IMA_STATUS_CHOICES = (
    (APPROVED, "Approved"),
    (DISCREDITED, "Discredited"),
    (PENDING_PUBLICATION, "Pending Publication"),
    (GRANDFATHERED, "Grandfathered"),
    (QUESTIONABLE, "Questionable"),
)


REJECTED = 1
PENDING_APPROVAL = 2
GROUP = 3
REDEFINED = 4
RENAMED = 5
INTERMEDIATE = 6
PUBLISHED_WITHOUT_APPROVAL = 7
UNNAMED_VALID = 8
UNNAMED_INVALID = 9
NAMED_AMPHIBOLE = 10

IMA_NOTE_CHOICES = (
    (REJECTED, "Rejected"),
    (PENDING_APPROVAL, "Pending Approval"),
    (GROUP, "Group"),
    (REDEFINED, "Redefined"),
    (RENAMED, "Renamed"),
    (INTERMEDIATE, "Intermediate"),
    (PUBLISHED_WITHOUT_APPROVAL, "Published without Approval"),
    (UNNAMED_VALID, "Unnamed Valid"),
    (UNNAMED_INVALID, "Unnamed Invalid"),
    (NAMED_AMPHIBOLE, "Named Amphibole"),
)
