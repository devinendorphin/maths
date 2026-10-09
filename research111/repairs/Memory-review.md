# Preserved audit failure and correction

The original `code/audit.py` rejected `max_observed_processes >= 2` for R119. Both original result sets report one observed process. Initial suspicion was that the 2 ms sampler missed brief children. A held successful checker probe instead showed a live child with positive VmRSS, while `/proc/parent/task/parent/children` was absent. The frozen sampler catches FileNotFoundError and returns only the runner. Its tree-labelled fields are therefore invalid as combined memory, not just noisy peaks.

Those Results.json records, frozen sampler and original auditor remain unchanged. The final auditor does not assert the original sampler passed. It requires the separately frozen successful child-plus-runner checkpoint in Memory-repair.json and verifies its proof/model independently. This supports a narrower memory claim, explicitly stated in the synthesis and alignment.

The first supplemental attempt also failed because it used the same child-discovery function. Before rerunning that supplement, the amendment was updated to the diagnosed cause and a PPid observer was frozen. No previously valid timing, native-certificate or admission run was repeated. The final supplement discovers descendants from `/proc/*/status`, verifies the held child's parent, checks positive RSS for both processes, records RSS/PSS, and releases the checker. There are no sleeps or artificial memory allocations in the checker. The checker retains its real globals after completing verification; this is not an unmodified peak measurement.

These failures are methodological evidence. The separately named final auditor and amendment preserve the distinction between failed initial coverage and accepted narrower coverage.
