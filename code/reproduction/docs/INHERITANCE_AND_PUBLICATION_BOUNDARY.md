# Internal Development History and Component Provenance

## 1. Project Development Milestones

This research project investigates exact policy-aware regression diagnosis for precision-constrained threshold selectors as a single, unified study. During the iterative development of this study, several internal milestones and prototype implementations were produced:

1. **Initial Feasibility and Core Sweep Formulation:** Early internal development established candidate-frontier partitioning, heap sweep algorithms, and initial evaluation cases (including the simulated cold-chain telemetry monitoring dataset with $N=37{,}471$ and 50 comparison pairs).
2. **Streaming Certificate Consumer and Verification Protocol:** Subsequent development introduced input-bound streaming diagnostic certificates with SHA-256 digests, bounded $\mathcal{O}(1)$ memory consumption, and formal consumer verification obligations.
3. **Reproducibility Consolidation:** Later stages packaged the artifact into `Reproducibility_Artifact.zip` (SHA-256 `552d7fd4...`) with detached execution logging (`Reproducibility_Evidence.zip`, SHA-256 `f7fcc128...`) to ensure full end-to-end auditability without self-referential hash cycles.

## 2. Clarification on Workspace Labels and Bibliographic Scope

- **Internal Development Labels:** Workspace directory names such as `provenance/q2_reference` and earlier working document titles (such as *Exact Candidate Frontier Comparison...*) represent internal working milestones of this same research project. They do not represent separate, independent prior publications or external citations.
- **Experimental Subjects:** The 98 fixed input pairs (50 retained comparisons, 17 synthetic fixtures, one public WDBC pilot, and 30 fitted pipeline inputs) were assembled and preserved during the internal development stages of this study to maintain exact traceability across iterations. They do not originate from an external or separate publication.
- **Bibliographic Citations:** All 28 references in the manuscript refer to established peer-reviewed literature (parameter synthesis, certifying algorithms, metamorphic testing, SMT solvers) and official software release repositories.
- **Traceability of Historical Test Snapshots:** Test count variations across historical development snapshots (e.g., 31 tests in early prototype verification, 41 in intermediate verification, and 42 in the finalized test suite) reflect incremental additions (specifically CRLF and tamper verification tests) within this research study, as documented in detached evidence logs (`stage_logs/run_all_pytest.log` and `results/pytest.xml`).
