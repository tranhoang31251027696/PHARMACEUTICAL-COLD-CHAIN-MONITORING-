# Consolidation evidence scope

The original executed V11 ZIP and its 33-stage report remain unchanged under release/ and reproduction_evidence/. They describe that exact original archive, not this later checkout.

This checkout merges build and validation code into two real Python files, retaining every section assertion. Verification comprises 42 passing core tests, all ten validation sections replayed on recorded results, unchanged generated main/supplement Markdown and the same 33-stage order with nine validation commands redirected to --section. The benchmarks have not been rerun through all 33 stages after this consolidation. See consolidation_checks/FINAL_CHECK.json and associated logs.

Scientific algorithms, corpus and benchmark protocols are unchanged; source-integrity bindings and the checkout manifest are updated for the merged files. No earlier build/validate modules are imported from hidden folders or archives.
