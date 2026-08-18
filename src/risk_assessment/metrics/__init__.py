"""Privacy and anonymization quality metrics.

This package provides two sub-packages:

- :mod:`~risk_assessment.metrics.informationloss` — information-loss metrics
  used to evaluate the quality of an anonymized dataset compared to the
  original.  Includes categorical precision, discernibility, non-uniform
  entropy, generalized loss metric, and global certain penalty.

- :mod:`~risk_assessment.metrics.uniqueness_estimation` — statistical
  estimators for the fraction of records that are unique in the population
  based on a sample, using the Zayatz hypergeometric estimator.

These metrics are consumed internally by the anonymization algorithms
(:mod:`risk_assessment.anonymization`) and can also be used directly to
assess re-identification risk in a dataset.
"""
