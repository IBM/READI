"""READI analyzer package.

Exposes :class:`~risk_assessment.readi.analyzer.READIAnalyzer` as the primary
entry point for detecting PII and PHI in unstructured text::

    from risk_assessment.readi import READIAnalyzer

    analyzer = READIAnalyzer()
    entities = analyzer.detect("Patient John Doe, DOB 01/01/1980")
"""

from risk_assessment.readi.analyzer import READIAnalyzer

__all__ = ["READIAnalyzer"]
