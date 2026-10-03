The plan replaces the 5-minute cron poll with change data capture. Debezium streams each change to `orders` into Kafka, and a new Go service, `notifier`, sends the notifications. **Approve phase 0, but with conditions.** Phase 0 also changes the live cron job and the primary database, but its row in the rollout table names only the new parts.

**For standup:** "I approve phase 0 with conditions. The shadow notifier writes no Redis keys, the slot alert has an owner, and the primary has disk room and wal_level set to logical. Before phase 2, notifier must write the key after the send."

**Get these answers before you approve phase 0:**

- Make sure that `notifier` writes no Redis keys while sends are disabled. From phase 0, cron reads the same keys. A key from the shadow notifier makes cron skip the real send (sections 4.3, 5).
- Find the `wal_level` and the free disk of the primary. Debezium needs `logical`, and a change to it needs a Postgres restart. The plan does not mention it.
- Make sure that the orders team accepts the Kafka pager from week 1. The replication slot is live in phase 0, but the plan settles on-call only before phase 2 (9, 10).
- Ask if Kafka Connect is a current cluster (4.1) or a new cost of approximately $1,400 a month (7). The plan says both.

**Fix before phase 2:**

- `notifier` writes the Redis key before the provider call. After a crash between the two, the replay finds the key and skips the event. The notification is lost, and section 3.2 calls that not acceptable.
- The plan does not say that `notifier` obeys the feature flag. If it sends for all merchants, the 10% step reaches every merchant, and a rollback does not stop it.
- A key lives 72 h, but Kafka keeps events for 7 days. A replay of older events sends them again.
- At the 50 GB cap, Postgres removes WAL that the slot needs. The disk stays safe, but Debezium cannot continue, and those events are lost.

On the good side: the cron key check in phase 0 should stop the duplicate sends of INC-2291, INC-2304 and INC-2342 by itself.

The sheet is at `notification-migration-review.html`. Sheet 1 has the bottom line, a pipeline diagram with the weak points marked, and the risk table. Each risk has its plan sections and the phase to fix it by. Sheet 2 shows what phase 0 touches, the rollout gates and the numbers. It is checked at five widths and in print, and each sheet prints on one page.

The `wal_level` and failover points come from the PostgreSQL docs. The plan does not cover them.
