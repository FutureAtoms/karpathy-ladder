A mutex is a lock with an owner. It lets one thread at a time use a resource. A semaphore is a counter with no owner. It lets up to N threads in. Any thread can signal it.

**Mutex**
- It has 2 states: locked and unlocked.
- The thread that locks the mutex owns it. Only that thread can unlock it.
- Use it to protect shared data, so that only one thread changes the data at a time.

**Semaphore**
- It keeps a count. `wait` decreases the count. If the count is 0, the thread stops until the count increases.
- `signal` increases the count. Any thread can do a `signal`.
- Use it to limit access to a pool, for example 5 database connections.
- Also use it to tell one thread that a different thread finished a task.

**A semaphore with a count of 1**
It also lets only one thread in. But it has no owner, so a different thread can release it. For a lock, use a mutex.
