"""Flash: Efficient, Stable and Optimal K-Anonymity algorithm.

Flash traverses the generalization lattice in a bottom-up, breadth-first
manner while continuously building and binary-searching vertical paths
("lightning-flash" paths) to find the globally optimal k-anonymous
generalization with minimal information loss.

The algorithm is described in:
    Kohlmayer, F., Prasser, F., Eckert, C., Kemper, A., & Kuhn, K. A. (2012).
    Flash: Efficient, Stable and Optimal K-Anonymity. IEEE SocialCom-PASSAT.

Key properties compared to OLA:
- Stable execution time regardless of column ordering in the input data.
- Uses a three-criterion ordering (c1/c2/c3) to induce a total order on all
  lattice nodes, guaranteeing deterministic traversal.
- Combines binary-search over paths with a min-heap of non-anonymous
  boundary nodes to continuously seed new paths.

The key components are:

- :class:`FlashOptions` — algorithm configuration.
- :class:`FlashLattice` — generalization lattice with Flash traversal logic.
- :class:`Flash` — top-level algorithm implementing
  :class:`~risk_assessment.anonymization.AnonymizationAlgorithm`.

Example::

    from risk_assessment.anonymization import KAnonymity
    from risk_assessment.anonymization.flash import Flash, FlashOptions

    options = FlashOptions(privacy_constraints=[KAnonymity(k=5)], suppression=5.0)
    flash = Flash(options)
    anonymized_df, report = flash.anonymize(df, column_information)
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pandas import DataFrame

from risk_assessment.anonymization import AnonymizationAlgorithm, AnonymizationReport, PrivacyConstraint
from risk_assessment.anonymization.optimal_lattice_anonymization import (
    AnonymityChecker,
    LatticeNode,
    _calculate_product,
    _generalized_dataset,
    _partition_dataset,
)
from risk_assessment.metrics.informationloss import ColumnInformation, ColumnType, categorical_precision
from risk_assessment.utility.hierarchy import GeneralizationHierarchy


@dataclass
class FlashOptions:
    """Configuration for the Flash anonymization algorithm.

    Attributes:
        privacy_constraints: One or more constraints every equivalence class
            must satisfy.
        suppression: Maximum percentage of rows that may be suppressed
            (0.0 = no suppression allowed). Defaults to 0.0.
        information_loss: Callable used to measure information loss between the
            original and generalized datasets.  Defaults to
            :func:`~risk_assessment.metrics.informationloss.categorical_precision`.
    """

    privacy_constraints: list[PrivacyConstraint]
    suppression: float = 0.0
    information_loss: Callable[[DataFrame, DataFrame, list[ColumnInformation]], float] = categorical_precision


# ---------------------------------------------------------------------------
# Node priority (traversal order)
# ---------------------------------------------------------------------------


def _node_priority(
    node: LatticeNode,
    max_levels: list[int],
    distinct_counts: list[list[int]],
) -> tuple[int, float, float]:
    """Return the (c1, c2, c3) ordering vector for *node*.

    The three criteria induce a total order that prefers lower generalization
    and is used consistently throughout the algorithm to guarantee stable,
    input-independent traversal.

    c1 — sum of all per-column generalization levels (= lattice level).
    c2 — average fractional generalization across quasi-identifiers.
    c3 — 1 minus the average fraction of distinct values remaining (more
         generalized → fewer distinct values → higher c3).
    """
    j = len(node.values)
    if j == 0:
        return (0, 0.0, 0.0)

    # c1: lattice level
    c1: int = node.sum()

    # c2: average normalized generalization level
    c2: float = sum(node.values[i] / max_levels[i] for i in range(j) if max_levels[i] > 0) / j

    # c3: 1 – (average fraction of distinct values that remain)
    distinct_fractions: list[float] = []
    for i in range(j):
        level_counts = distinct_counts[i]
        base = level_counts[0] if level_counts[0] > 0 else 1
        level = min(node.values[i], len(level_counts) - 1)
        distinct_fractions.append(level_counts[level] / base)
    c3: float = 1.0 - (sum(distinct_fractions) / j)

    return (c1, c2, c3)


# ---------------------------------------------------------------------------
# Flash lattice
# ---------------------------------------------------------------------------


class FlashLattice:
    """Generalization lattice with Flash traversal.

    Builds the full lattice once and then applies the Flash algorithm to find
    the globally optimal anonymous node (minimal information loss while still
    satisfying all privacy constraints within the suppression budget).

    Args:
        anonymity_checker: Evaluates suppression rate and information loss.
        column_information: Per-column metadata.
        suppression: Maximum allowed suppression percentage.
    """

    def __init__(
        self,
        anonymity_checker: AnonymityChecker,
        column_information: list[ColumnInformation],
        suppression: float,
    ) -> None:
        self._checker = anonymity_checker
        self._column_information = column_information
        self._suppression = suppression

        self._quasi_columns: list[int] = [
            idx for idx, c_i in enumerate(column_information) if c_i.column_type == ColumnType.QUASI
        ]

        # Per quasi-identifier: maximum level index and hierarchy
        self._max_levels: list[int] = []
        self._hierarchies: list[GeneralizationHierarchy] = []

        for qi_idx in self._quasi_columns:
            c_i = column_information[qi_idx]
            hierarchy = c_i.hierarchy
            if hierarchy is None:
                raise ValueError(f"Missing hierarchy for column {qi_idx}")
            self._max_levels.append(len(hierarchy) - 1)
            self._hierarchies.append(hierarchy)

        n_qi = len(self._quasi_columns)

        # Precompute distinct value counts per (qi, level) for c3 criterion.
        # distinct_counts[i][l] = number of distinct generalized values at level l
        self._distinct_counts: list[list[int]] = []
        for i, hierarchy in enumerate(self._hierarchies):
            max_lv = self._max_levels[i]
            counts: list[int] = []
            for lv in range(max_lv + 1):
                # Count distinct values at this level by iterating over level-0 values
                generalized: set[Any] = set()
                for raw_val in anonymity_checker.dataset[
                    anonymity_checker.dataset.columns[self._quasi_columns[i]]
                ].unique():
                    generalized.add(hierarchy.encode(raw_val, lv))
                counts.append(len(generalized))
            self._distinct_counts.append(counts)

        # Build the full lattice: level → set[LatticeNode]
        levels_range: list[list[int]] = [list(range(self._max_levels[i] + 1)) for i in range(n_qi)]
        all_combos: list[list[int]] = _calculate_product(levels_range)

        self._lattice: dict[int, list[LatticeNode]] = {}
        self._node_map: dict[int, LatticeNode] = {}  # hash → node
        self._lattice_top_level: int = 0

        for values in all_combos:
            node = LatticeNode(values)
            lv = node.sum()
            self._lattice.setdefault(lv, []).append(node)
            self._node_map[hash(node)] = node
            if lv > self._lattice_top_level:
                self._lattice_top_level = lv

        # Sort each level according to the Flash traversal order (ascending c)
        for lv in self._lattice:
            self._lattice[lv].sort(key=self._priority)

        self._global_optimum: LatticeNode | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def explore(self) -> None:
        """Run the Flash algorithm over the lattice."""
        # Min-heap: (priority-tuple, node).  Python heapq is a min-heap.
        heap: list[tuple[tuple[int, float, float], LatticeNode]] = []

        all_levels = sorted(self._lattice.keys())

        for lv in all_levels:
            for node in self._lattice[lv]:
                if not node.tagged:
                    path = self._find_path(node)
                    self._check_path(path, heap)

            # Drain the heap: process successors of non-anonymous boundary nodes
            while heap:
                _, boundary_node = heapq.heappop(heap)
                for successor in self._successors_up(boundary_node):
                    if not successor.tagged:
                        path = self._find_path(successor)
                        self._check_path(path, heap)

    def optimal_node(self) -> LatticeNode | None:
        """Return the globally optimal anonymous node, or *None*."""
        return self._global_optimum

    # ------------------------------------------------------------------
    # Core Flash sub-procedures (Algorithms 1–3 in the paper)
    # ------------------------------------------------------------------

    def _find_path(self, start: LatticeNode) -> list[LatticeNode]:
        """Build a path of untagged nodes from *start* towards the top.

        Corresponds to FINDPATH in Algorithm 2.  At each step we greedily
        follow the first untagged successor (according to the Flash order).
        """
        path: list[LatticeNode] = []
        node = start
        while True:
            path.append(node)
            # Find the first (lowest-priority) untagged successor
            next_node: LatticeNode | None = None
            for candidate in self._successors_up(node):
                if not candidate.tagged:
                    next_node = candidate
                    break
            if next_node is None or next_node is node:
                break
            node = next_node
        return path

    def _check_path(
        self,
        path: list[LatticeNode],
        heap: list[tuple[tuple[int, float, float], LatticeNode]],
    ) -> None:
        """Binary-search a path for the optimal anonymous boundary node.

        Corresponds to CHECKPATH in Algorithm 3.
        """
        low, high = 0, len(path) - 1
        local_optimum: LatticeNode | None = None

        while low <= high:
            mid = (low + high) // 2
            node = path[mid]

            if self._check_and_tag(node):
                # Anonymous: candidate optimum, search lower half
                local_optimum = node
                high = mid - 1
            else:
                # Non-anonymous: push to heap for future path-building, search upper half
                heapq.heappush(heap, (self._priority(node), node))
                low = mid + 1

        self._store(local_optimum)

    def _check_and_tag(self, node: LatticeNode) -> bool:
        """Evaluate *node* and propagate predictive tags. Returns True if anonymous."""
        is_anonymous = self._check_anonymity(node)
        node.is_anonymous = is_anonymous
        node.tagged = True

        # Predictive tagging: propagate towards generalizations (if anonymous)
        # or towards specializations (if not anonymous).
        self._tag_upward(node) if is_anonymous else self._tag_downward(node)
        return is_anonymous

    def _store(self, local_optimum: LatticeNode | None) -> None:
        """Update the global optimum if *local_optimum* improves it."""
        if local_optimum is None:
            return
        if self._global_optimum is None:
            self._global_optimum = local_optimum
            return
        # Prefer lower total generalization level first, then lower info loss
        if local_optimum.sum() < self._global_optimum.sum():
            self._global_optimum = local_optimum
        elif local_optimum.sum() == self._global_optimum.sum():
            lo_loss = local_optimum.information_loss or math.inf
            go_loss = self._global_optimum.information_loss or math.inf
            if lo_loss < go_loss:
                self._global_optimum = local_optimum

    # ------------------------------------------------------------------
    # Lattice helpers
    # ------------------------------------------------------------------

    def _check_anonymity(self, node: LatticeNode) -> bool:
        """Compute suppression rate via the checker and record information loss."""
        suppression_rate = self._checker.calculate_suppression_rate(node)
        node.suppression_rate = suppression_rate
        return suppression_rate <= self._suppression

    def _tag_upward(self, node: LatticeNode) -> None:
        """Tag all generalizations (successors) of an anonymous node as anonymous."""
        for successor in self._successors_up(node):
            if not successor.tagged:
                successor.is_anonymous = True
                successor.tagged = True
                self._tag_upward(successor)

    def _tag_downward(self, node: LatticeNode) -> None:
        """Tag all specializations (predecessors) of a non-anonymous node as non-anonymous."""
        for predecessor in self._successors_down(node):
            if not predecessor.tagged:
                predecessor.is_anonymous = False
                predecessor.tagged = True
                self._tag_downward(predecessor)

    def _successors_up(self, node: LatticeNode) -> list[LatticeNode]:
        """Return direct generalizations of *node* (one level up), sorted by priority."""
        result: list[LatticeNode] = []
        for i in range(len(node.values)):
            if node.values[i] < self._max_levels[i]:
                new_values = list(node.values)
                new_values[i] += 1
                candidate = LatticeNode(new_values)
                existing = self._node_map.get(hash(candidate))
                if existing is not None:
                    result.append(existing)
        result.sort(key=self._priority)
        return result

    def _successors_down(self, node: LatticeNode) -> list[LatticeNode]:
        """Return direct specializations of *node* (one level down), sorted by priority."""
        result: list[LatticeNode] = []
        for i in range(len(node.values)):
            if node.values[i] > 0:
                new_values = list(node.values)
                new_values[i] -= 1
                candidate = LatticeNode(new_values)
                existing = self._node_map.get(hash(candidate))
                if existing is not None:
                    result.append(existing)
        result.sort(key=self._priority)
        return result

    def _priority(self, node: LatticeNode) -> tuple[int, float, float]:
        """Return the (c1, c2, c3) ordering tuple for *node*."""
        return _node_priority(node, self._max_levels, self._distinct_counts)


# ---------------------------------------------------------------------------
# Top-level algorithm
# ---------------------------------------------------------------------------


class Flash(AnonymizationAlgorithm):
    """Flash: Efficient, Stable and Optimal K-Anonymity.

    Finds the generalization with minimal information loss that satisfies all
    privacy constraints within the configured suppression budget, using the
    Flash lattice-traversal strategy described in:

        Kohlmayer et al. (2012). Flash: Efficient, Stable and Optimal
        K-Anonymity. IEEE SocialCom-PASSAT, pp. 708–714.

    Args:
        options: Algorithm configuration.
    """

    def __init__(self, options: FlashOptions) -> None:
        self._options = options

    def anonymize(
        self, dataset: DataFrame, column_information: list[ColumnInformation]
    ) -> tuple[DataFrame, AnonymizationReport]:
        """Anonymize the dataset using Flash.

        Args:
            dataset: The input DataFrame. Quasi-identifier columns will be
                generalized according to the optimal lattice node found.
            column_information: Per-column metadata.  Length must equal the
                number of columns in ``dataset``.

        Returns:
            A tuple of ``(anonymized_dataset, report)``.

        Raises:
            ValueError: If ``column_information`` length does not match the
                number of dataset columns.
            RuntimeError: If no suitable generalization can be found.
        """
        if len(column_information) != len(dataset.columns):
            raise ValueError(
                f"Dataset and column information are inconsistent in shape "
                f"{len(dataset.columns)} vs {len(column_information)}"
            )

        if dataset is None or len(dataset) == 0:
            return (dataset, AnonymizationReport(False))

        if not any(c_i.column_type == ColumnType.QUASI for c_i in column_information):
            return (dataset, AnonymizationReport(True, 0.0, []))

        checker = AnonymityChecker(
            dataset,
            column_information,
            self._options.privacy_constraints,
            self._options.information_loss,
        )
        lattice = FlashLattice(checker, column_information, self._options.suppression)
        lattice.explore()

        best_node = lattice.optimal_node()

        if best_node is None or not best_node.is_anonymous:
            raise RuntimeError("Flash: unable to find a suitable generalization")

        if best_node.suppression_rate and best_node.suppression_rate > 0.0:
            anonymized = self._anonymize_with_suppression(dataset, column_information, best_node, checker)
        else:
            anonymized = _generalized_dataset(dataset.copy(), column_information, best_node.values)

        return (
            anonymized,
            AnonymizationReport(
                True,
                best_node.suppression_rate or 0.0,
                best_node.values,
            ),
        )

    def _anonymize_with_suppression(
        self,
        dataset: DataFrame,
        column_information: list[ColumnInformation],
        node: LatticeNode,
        checker: AnonymityChecker,
    ) -> DataFrame:
        """Apply generalization then drop equivalence classes that still violate constraints."""
        result = _generalized_dataset(dataset.copy(), column_information, node.values)
        partitions = _partition_dataset(result, column_information)
        for _, partition in partitions:
            if not checker._check_constraints(partition):
                result = result.drop(index=list(partition.index))
        return result
