# Rejected first execution, before the accepted source freeze

The first 145–147 primary campaign completed 54 workers. Its audit failed on the
first guard-route worker, 0-guard-0, at the raw-log versus Worker.json record
equality assertion. The initial in-memory record retained the mutable proof
object; later accepted cost updates changed its model/cost headers after the
initial raw record had already been flushed. This is a recording ownership bug,
not evidence that the two records describe the same initial certificate.

Both first primary and first replica directory contents, including their source
freezes and raw logs, are retained under rejected-record-ownership in the larger
inquiry archive. All their performance and answer records are excluded from
headline counts and tables, even for unaffected cold/basis workers. The replica
was already running when the primary audit failed and was allowed to finish;
neither rejected directory counts as an accepted replication.

The fix copies every record at append time, after writing the same serialized
record to the raw log. A regression check compares all raw records with every
returned worker record in all three development routes. Headline inputs, routes,
guards and mathematical admission remain the same; the accepted source freeze
records the repaired worker before rerunning both fresh empty directories. This
is a new freeze and a full rerun, not a silent edit of the rejected evidence.
