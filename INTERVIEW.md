Here’s a curated list of **interview questions and model answers** specific to your **Flask + Kafka Contact Center Routing System** project. They blend system design, backend engineering, and practical Kafka/Flask concepts often asked in software engineering or SDE interviews.

***

### **Section 1: System Design & Architecture**

**Q1. Can you describe the overall architecture of your Contact Center Routing system?**  
**A:** The system is a stateless Flask microservice that exposes REST endpoints for customers and agents, backed by Kafka event streams for asynchronous processing. Producers push customer routing requests into a topic keyed by `customer_id`, ensuring message order per customer. Kafka consumers (router workers) process the stream, assign available agents, and produce assignment results onto another topic. State like agent status or active assignments is persisted in PostgreSQL and cached in Redis. This combination maintains fault tolerance and scalability.

***

**Q2. How did you ensure the service is stateless but still “stateful in behavior”?**  
**A:** The Flask services themselves hold no session or local memory. Stateful behavior comes from Kafka message ordering (with `key=customer_id`) and shared state maintained in Redis and Postgres. This allows horizontally scaling web and consumer services independently without losing consistency.

***

**Q3. What partitioning strategy did you apply in Kafka and why?**  
**A:** I used **key-based partitioning**, where the `customer_id` is the message key. This ensures all messages related to the same customer go to the same partition, preserving per-customer ordering. It also allows balanced parallel processing across partitions by consumer instances within a group.

***

**Q4. How do you achieve seamless scaling when more worker instances are added?**  
**A:** Kafka’s cooperative-sticky assignor automatically redistributes partitions to new consumers when they join the group, without rebalance churn. This minimizes processing interruptions and achieves near-zero downtime scaling.

***

**Q5. How does the system behave when a worker or instance crashes?**  
**A:** Kafka reassigns partitions owned by the crashed consumer to healthy consumers in the group. Since consumers commit offsets manually after successful processing, the replacement consumer resumes from the last committed offset, ensuring at-least-once delivery semantics.

***

### **Section 2: Kafka-Focused**

**Q6. What delivery semantics have you implemented?**  
**A:** The system ensures **at-least-once** delivery. Producers use idempotence (`enable.idempotence=true`, `acks=all`) to avoid duplicate messages. Consumers commit offsets **only after successful DB and Redis updates** to ensure no data is lost.

***

**Q7. How are producers and consumers configured for reliability?**  
**A:**  
- **Producer:** `acks=all`, `retries` enabled, `batch.size` tuned for throughput.  
- **Consumer:** manual offset commits, `max.poll.interval` adjusted for processing time, cooperative-sticky rebalancing for graceful scaling.

***

**Q8. Why not use a traditional queueing system like RabbitMQ for this project?**  
**A:** Kafka’s log-based design supports high throughput, replayability, and partition-based scaling. Unlike RabbitMQ, Kafka consumers can rewind or replay messages, making it more suitable for real-time event-driven microservices with temporal ordering requirements.

***

### **Section 3: Flask & Backend Engineering**

**Q9. How is your Flask application structured?**  
**A:** It follows the Flask Application Factory pattern with modular Blueprints (for agents, customers, assignments), service and repository layers for logic, and adapter layers for Kafka/Redis/DB integration. This improves maintainability and testability.

***

**Q10. How do you handle errors across services?**  
**A:** Through a centralized error handler registered globally. Custom error classes (e.g., `AppError`, `NotFoundError`) convert exceptions to consistent JSON responses. Flask and HTTP exceptions are wrapped to provide meaningful error codes and logs.

***

**Q11. How did you integrate Flask with background Kafka consumers?**  
**A:** The consumers run as separate worker processes using the same app context (via `create_app()`). They access the shared models, services, and configuration defined by the Flask factory, ensuring consistency across API and worker layers.

***

**Q12. How did you handle structured logging?**  
**A:** Logging uses `python-json-logger` for JSON-formatted outputs, including timestamps, log levels, and correlation IDs. This format ensures observability in distributed environments and compatibility with ELK or cloud logging systems.

***

### **Section 4: Performance, Fault Tolerance & Optimization**

**Q13. How does your system ensure high availability?**  
**A:** Kafka replication ensures message durability even if brokers go down. Flask apps are stateless and can be scaled horizontally behind load balancers. Redis uses an in-memory lock (via `SETNX`) for atomic agent reservations, reducing race conditions.

***

**Q14. What are common failure scenarios you tested?**  
**A:**  
- Network issues between producers and Kafka brokers.  
- Redis connection drops during reservation — handled via retry fallback to DB.  
- Kafka consumer crash and restart — verified offset reprocessing.  
- Simulated agent overload and balancing via Redis load metrics.

***

**Q15. Can the system execute exactly-once routing guarantees?**  
**A:** Out of the box, Kafka and Flask here achieve at-least-once semantics. For exactly-once delivery, one would integrate **transactional Kafka producers** and **idempotent DB writes** (using unique keys or version columns).

***

### **Section 5: Coding/Behavioral Scenarios**

**Q16. If multiple customers arrive simultaneously, how do you prevent the same agent from being over-assigned?**  
**A:** Redis `SETNX` locking is used during assignment to atomically reserve agents per `agent_id`. This ensures even overlapping routing requests only assign one customer per available agent.

***

**Q17. What metrics would you monitor in production?**  
**A:**  
- Kafka consumer lag  
- Uncommitted offsets  
- Agent availability rate  
- Redis lock contention rate  
- API latency and error rates  
These metrics give visibility into load distribution and bottlenecks.

***

**Q18. Which design patterns are demonstrated in your system?**  
**A:**  
- **Factory Pattern:** Flask app creation.  
- **Repository Pattern:** Data access abstraction.  
- **Service Layer Pattern:** Business logic encapsulation.  
- **Adapter Pattern:** Integration with Kafka, Redis, and Postgres.  
- **Observer/Event-driven Pattern:** Kafka publish-subscribe model.

***

### **Section 6: Deployment & Scaling**

**Q19. How would you deploy this system in production?**  
**A:** Using Docker containers orchestrated via Kubernetes. Each component — Flask API, router worker, agent-status worker — runs in its own pod, connecting to managed Kafka, Redis, and Postgres services. Health checks and liveness probes ensure self-healing.

***

**Q20. How would you extend this system for multiple tenants?**  
**A:** Include `tenant_id` as part of Kafka message keys and DB schemas for logical partitioning. Use topic naming convention like `tenant.customer.routing.requests`, or maintain tenant metadata tables.

***

### **Bonus — High-Level Conceptual Questions**

**Q21. What is consumer lag and why is it important?**  
**A:** Consumer lag is the difference between the latest message offset in a partition and the last processed offset by the consumer group. High lag indicates the consumers are slower than producers, signaling scaling or resource issues.[2][5]

***

**Q22. Explain at-least-once vs at-most-once processing.**  
**A:**  
- **At-least-once:** Messages are processed at least once; duplicates possible if retries occur.  
- **At-most-once:** Messages may be lost if consumer fails before committing.  
For this project, at-least-once ensures consistency even under transient errors.

***

**Q23. How would you support prioritization between customers?**  
**A:** Use a priority field in messages (already modeled) and partition or consume with custom logic that routes higher-priority customers first, e.g., via weighted polling or Redis-sorted sets.

***

### **Preparation Tip**
Interviewers often combine questions about:
- Kafka partition and offset handling,  
- Flask modular app architecture,  
- REST design principles,  
- Fault tolerance and scaling in distributed systems.  

When answering, relate each topic to how your system specifically leverages Kafka’s partitioned streams and Flask’s stateless HTTP layer — showing real-world engineering tradeoffs, not just theory.

[1](https://www.interviewbit.com/kafka-interview-questions/)
[2](https://www.geeksforgeeks.org/apache-kafka/kafka-interview-questions/)
[3](https://www.simplilearn.com/kafka-interview-questions-and-answers-article)
[4](https://www.adaface.com/blog/kafka-interview-questions/)
[5](https://www.vervecopilot.com/interview-questions/top-30-most-common-kafka-interview-questions-for-experienced-you-should-prepare-for)
[6](https://www.javainuse.com/interview/flask)
[7](https://www.knowledgehut.com/interview-questions/flask)
[8](https://www.withoutbook.com/InterviewQuestionList.php?tech=76&dl=Top&s=Flask+interview+questions+and+answers)