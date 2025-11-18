"""
Enumerations for Safety Graph Twin.

Contains all enum types used throughout the application for validation
and type safety.
"""

from enum import Enum


class ASILLevel(str, Enum):
    """
    ASIL (Automotive Safety Integrity Level) ratings per ISO 26262.

    QM: Quality Management (no ASIL requirement)
    A: Lowest ASIL level
    B: Medium-low ASIL level
    C: Medium-high ASIL level
    D: Highest ASIL level (most stringent)
    """

    QM = "QM"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class TestStatus(str, Enum):
    """
    Test case execution status.
    """

    PASSED = "passed"
    FAILED = "failed"
    NOT_RUN = "not_run"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"


class DefectStatus(str, Enum):
    """
    Defect instance status (Phase 3).
    """

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    WONT_FIX = "Won't Fix"
    DUPLICATE = "Duplicate"


class DefectSeverity(str, Enum):
    """
    Defect severity levels (Phase 3).
    """

    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    TRIVIAL = "Trivial"


class DefectSource(str, Enum):
    """
    Source of defect report (Phase 3).
    """

    WARRANTY = "warranty"
    FIELD = "field"
    CONNECTED_VEHICLE = "CV"
    TEST = "test"
    INTERNAL = "internal"


class ComponentType(str, Enum):
    """
    Component types in system architecture.
    """

    HARDWARE = "hardware"
    SOFTWARE = "software"
    SYSTEM = "system"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"


class TestType(str, Enum):
    """
    Types of test cases.
    """

    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    HIL = "HIL"  # Hardware-in-the-Loop
    SIL = "SIL"  # Software-in-the-Loop
    MIL = "MIL"  # Model-in-the-Loop
    REGRESSION = "regression"
    ACCEPTANCE = "acceptance"


class CoverageLevel(str, Enum):
    """
    Test coverage levels.
    """

    STATEMENT = "statement"
    BRANCH = "branch"
    CONDITION = "condition"
    MC_DC = "MC/DC"  # Modified Condition/Decision Coverage
    PATH = "path"


class FTEventType(str, Enum):
    """
    Fault Tree event types.
    """

    TOP = "top"
    INTERMEDIATE = "intermediate"
    BASIC = "basic"


class FTGateType(str, Enum):
    """
    Fault Tree gate types.
    """

    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    NOT = "NOT"
    PRIORITY_AND = "PRIORITY_AND"
    VOTING = "VOTING"


class FailureModeCategory(str, Enum):
    """
    Categories of failure modes.
    """

    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    SOFTWARE = "software"
    THERMAL = "thermal"
    ENVIRONMENTAL = "environmental"
    HUMAN_ERROR = "human_error"
    SYSTEMATIC = "systematic"
    RANDOM = "random"


class CoverageStatus(str, Enum):
    """
    Hazard coverage status.
    """

    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
    UNKNOWN = "unknown"


class Standard(str, Enum):
    """
    Safety and quality standards.
    """

    ISO_26262 = "ISO 26262:2018"
    ISO_21448 = "ISO/PAS 21448:2019"  # SOTIF
    ISO_21434 = "ISO/SAE 21434:2021"  # Cybersecurity
    ISO_9001 = "ISO 9001:2015"
    ASPICE = "Automotive SPICE"


class ControllerType(str, Enum):
    """
    STPA controller types (Phase 5).
    """

    SOFTWARE = "software"
    HARDWARE = "hardware"
    HUMAN = "human"
    HYBRID = "hybrid"
