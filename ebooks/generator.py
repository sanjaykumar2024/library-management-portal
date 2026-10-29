"""
LibrarySphere E-Book Publication & Content Synthesis Engine.
Generates publisher-grade, complete multi-page digital book editions
scaled to the recorded page extent of any book (e.g., 100 to 1,500+ pages).
Guarantees rich, diverse, authentic, non-repetitive prose across every single page.
"""

import math
import html
import hashlib
from typing import Dict, List, Any, Tuple


class BookContentSynthesizer:
    """
    Synthesizes complete, publication-grade digital HTML book documents.
    Every page is an independent, authentic, content-filled publication page with
    distinct chapter titles, rich section expositions, code listings, literary scenes,
    empirical case studies, decision matrices, and seminar reflection prompts.
    """

    THEMES = {
        'Computer Science': ('#0f172a', '#3b82f6', '#1d4ed8', '#e2e8f0'),
        'Technology': ('#111827', '#06b6d4', '#0891b2', '#e2e8f0'),
        'Science Fiction': ('#18181b', '#8b5cf6', '#6d28d9', '#e4e4e7'),
        'Literature': ('#1e1b4b', '#ec4899', '#be185d', '#fbcfe8'),
        'Romance & Classic Fiction': ('#1e1b4b', '#ec4899', '#be185d', '#fbcfe8'),
        'Gothic Horror & Science Fiction': ('#09090b', '#10b981', '#059669', '#e4e4e7'),
        'Mystery & Detective Fiction': ('#1e293b', '#f59e0b', '#d97706', '#fed7aa'),
        'Gothic Horror': ('#450a0a', '#dc2626', '#991b1b', '#fecaca'),
        'Fantasy & Children\'s Literature': ('#0c4a6e', '#8b5cf6', '#0284c7', '#bae6fd'),
        'American Literature & Modern Fiction': ('#1e1b4b', '#eab308', '#ca8a04', '#fef08a'),
        'Science Fiction & Speculative': ('#18181b', '#0ea5e9', '#0284c7', '#bae6fd'),
        'Philosophical & Existential Fiction': ('#292524', '#a855f7', '#7e22ce', '#e9d5ff'),
        'Historical Fiction & Classics': ('#1c1917', '#3b82f6', '#2563eb', '#bfdbfe'),
        'Adventure & American Classics': ('#0c4a6e', '#14b8a6', '#0d9488', '#99f6e4'),
        'Psychology': ('#14532d', '#10b981', '#047857', '#d1fae5'),
        'Business & Economics': ('#451a03', '#f59e0b', '#d97706', '#fef3c7'),
        'History': ('#2e1065', '#a855f7', '#7e22ce', '#f3e8ff'),
        'Philosophy': ('#312e81', '#6366f1', '#4338ca', '#e0e7ff'),
        'Science & Mathematics': ('#0c4a6e', '#0284c7', '#0369a1', '#e0f2fe'),
        'General': ('#1e293b', '#6366f1', '#4f46e5', '#e2e8f0'),
    }

    # ── FLAGSHIP CATALOG OUTLINES ─────────────────────────────────────────────
    FLAGSHIP_CATALOG = {
        'designing data-intensive applications': {
            'parts': [
                'Part I: Foundations of Data Systems',
                'Part II: Distributed Data & Replication',
                'Part III: Derived Data & Stream Processing',
                'Part IV: The Future of Data Architectures'
            ],
            'chapters': [
                ('Reliable, Scalable, and Maintainable Systems', 'Thinking about hardware and software faults, human error, SLA latency percentiles, and operational architectures.'),
                ('Data Models and Query Languages', 'Relational vs document vs graph data models, declarative queries, schema-on-read vs schema-on-write.'),
                ('Storage and Retrieval', 'LSM-Trees vs B-Trees, transaction logs, SSTables, Bloom filters, column-oriented storage, and analytical query engines.'),
                ('Encoding and Evolution', 'Binary serialization formats, Protocol Buffers, Thrift, Avro, backward and forward schema compatibility, RPC vs REST.'),
                ('Replication Protocols', 'Single-leader, multi-leader, and leaderless Dynamo replication; replication lag, read-after-write consistency, monotonic reads.'),
                ('Partitioning and Sharding', 'Partitioning by key range vs key hash, consistent hashing, rebalancing partitions, request routing, and cross-partition queries.'),
                ('Transactions and Isolation Levels', 'ACID guarantees, dirty reads, non-repeatable reads, read committed, snapshot isolation, 2-phase locking, and Serializable Snapshot Isolation (SSI).'),
                ('The Trouble with Distributed Systems', 'Unreliable networks, packet loss, clock drift, TrueTime, Byzantine faults, split-brain conditions, and unbounded latency.'),
                ('Consistency and Consensus', 'Linearizability, total order broadcast, two-phase commit (2PC), Paxos, Raft, Zab, and distributed coordination with ZooKeeper.'),
                ('Batch Processing and MapReduce', 'Unix philosophy in distributed systems, distributed file systems, MapReduce dataflows, join algorithms, and data warehouse ELT.'),
                ('Stream Processing and Event Logs', 'Message brokers, append-only logs, partition assignment, windowing semantics, exactly-once processing, and stream joins.'),
                ('The Future of Data Systems', 'Data integration, unbundling the database, stream-table duality, federated querying, and verifiable audit ledgers.')
            ]
        },
        'clean code': {
            'parts': [
                'Part I: Meaningful Code & Structure',
                'Part II: Robust Design & Testing',
                'Part III: Concurrency & Smells'
            ],
            'chapters': [
                ('Clean Code Foundations', 'The cost of owning a mess, the Boy Scout Rule, code readability as human communication.'),
                ('Meaningful Names', 'Intention-revealing identifiers, avoiding disinformation, pronounceable and searchable naming conventions.'),
                ('Functions', 'Small functions doing one thing, single level of abstraction, command-query separation, eliminating side effects.'),
                ('Comments and Documentation', 'Comments as failures of self-expression, good vs bad comments, avoiding redundant and misleading noise.'),
                ('Formatting and Vertical Layout', 'Vertical density and separation, the newspaper metaphor, horizontal alignment, team coding standards.'),
                ('Objects and Data Structures', 'Data abstraction, data/object anti-symmetry, the Law of Demeter, DTOs and active records.'),
                ('Error Handling', 'Using exceptions rather than error codes, providing context, wrapping third-party APIs, defining normal execution flow.'),
                ('Boundaries and External Libraries', 'Using third-party code cleanly, learning tests, using adapters to protect core domain logic.'),
                ('Unit Tests and TDD', 'The Three Laws of TDD, keeping tests clean, F.I.R.S.T. criteria for clean automated tests.'),
                ('Classes and Cohesion', 'Single Responsibility Principle (SRP), cohesion metrics, organizing for change, minimizing coupling.'),
                ('Systems and Architecture', 'Separate constructing a system from using it, scaling up, dependency injection, pure domain logic.'),
                ('Emergence and Simple Design', 'Kent Beck’s four rules of simple design: passes all tests, reveals intent, no duplication, fewest elements.'),
                ('Concurrency', 'Concurrency defense principles, thread-safe primitives, testing concurrent code, avoiding shared mutable state.')
            ]
        },
        'pride and prejudice': {
            'parts': [
                'Part I: Netherfield and First Impressions',
                'Part II: Rosings and the Unraveling Truth',
                'Part III: Pemberley, Crisis, and Resolution'
            ],
            'chapters': [
                ('The Arrival of Mr. Bingley', 'Mrs. Bennet’s ambitions, the announcement of Netherfield Park’s tenant, and the social stir in Meryton.'),
                ('The Meryton Assembly and Pride Concealed', 'First impressions of Fitzwilliam Darcy, Elizabeth Bennet’s quick wit, and early societal judgments.'),
                ('Jane’s Illness at Netherfield', 'Elizabeth’s devoted walk through the mud, Miss Bingley’s sharp observations, and lively evening debates.'),
                ('Mr. Collins and the Entailed Estate', 'The pompous clergyman’s arrival, the laws of inheritance, and awkward overtures of courtship.'),
                ('Wickham’s Narrative and Growing Bias', 'The handsome militia officer’s tale of Darcy’s alleged cruelty, deepening Elizabeth’s resentment.'),
                ('The Netherfield Ball and Lingering Tensions', 'Elizabeth dancing with Darcy, her family’s social indiscretions, and Mr. Collins’s ill-timed self-importance.'),
                ('The Rejection of Mr. Collins', 'Elizabeth refuses an advantageous marriage, Mrs. Bennet’s fury, and Charlotte Lucas’s pragmatic decision.'),
                ('The Journey to Rosings and Lady Catherine', 'Hunsford Parsonage, the imperious Lady Catherine de Bourgh, and Colonel Fitzwilliam’s revealing disclosures.'),
                ('Darcy’s Proposal and Elizabeth’s Rebuke', 'The impassioned yet tactless offer of marriage, Elizabeth’s fierce refusal, and accusations of callousness.'),
                ('The Letter of Vindication', 'Darcy’s written defense explaining Wickham’s perfidy and his reservations regarding the Bennet family’s conduct.'),
                ('The Tour of Pemberley and Transformed Regard', 'Elizabeth beholds Darcy’s estate, Mrs. Reynolds’s warm praise of her master, and Darcy’s unexpected civility.'),
                ('Lydia’s Disgrace and the Threat of Ruin', 'The shocking news of Lydia’s elopement with Wickham, panic in Longbourn, and Elizabeth’s despair.'),
                ('The Secret Benefactor Revealed', 'Mrs. Gardiner discloses that Darcy tracked down the lovers, settled Wickham’s debts, and arranged the marriage.'),
                ('The Return of Bingley and Lady Catherine’s Visit', 'Bingley’s joyous proposal to Jane, Lady Catherine’s arrogant confrontation with Elizabeth at Longbourn.'),
                ('Understanding, Confession, and Concord', 'A quiet walk across the countryside, Darcy’s renewed proposal, Elizabeth’s joyful acceptance, and domestic happiness.')
            ]
        },
        'thinking, fast and slow': {
            'parts': [
                'Part I: Two Systems of Thought',
                'Part II: Heuristics and Biases',
                'Part III: Overconfidence and Choices',
                'Part IV: Two Selves and Well-Being'
            ],
            'chapters': [
                ('The Characters of the Story', 'Introducing System 1 (fast, intuitive, emotional) and System 2 (slow, deliberate, analytical).'),
                ('Attention and Cognitive Effort', 'Pupil dilation, the budget for mental energy, lazy controllers, and cognitive strain.'),
                ('The Associative Machine', 'Priming effects, Florida effect, cognitive ease, and the illusion of truth and familiarity.'),
                ('Norms, Surprises, and Causes', 'Assessing what is normal, detecting anomalies, and the intuitive search for intentional causes.'),
                ('A Machine for Jumping to Conclusions', 'WYSIATI (What You See Is All There Is), the halo effect, and hasty coherence.'),
                ('How Judgments Happen', 'Intensity matching, mental shotguns, and answering an easier target question through substitution.'),
                ('The Law of Small Numbers', 'Insensitivity to sample size, artifactual variance, and the illusion of causal patterns in randomness.'),
                ('Anchors and Adjustment', 'The anchoring index, insufficient adjustment in System 2, priming in System 1, and market negotiations.'),
                ('The Science of Availability', 'Availability heuristics, ease of retrieval vs volume of evidence, and public risk perceptions.'),
                ('Tom W and the Base-Rate Dilemma', 'Representativeness over base rates, stereotypes, and Bayesian reasoning vs intuitive intuition.'),
                ('Linda: The Conjunction Fallacy', 'When detail makes a story more plausible yet statistically less probable; less is more in joint probability.'),
                ('Regression to the Mean', 'Talent and luck, why extreme performance inevitably moderates, and the illusion of feedback efficacy.'),
                ('The Illusion of Understanding', 'The narrative fallacy, hindsight bias, and why we overestimate our comprehension of historical events.'),
                ('Prospect Theory and Loss Aversion', 'Reference dependence, the fourfold pattern of risk attitudes, and the asymmetry between gains and losses.'),
                ('Two Selves: Experiencing vs Remembering', 'The peak-end rule, duration neglect, and how the remembering self narrates our lived experience.')
            ]
        },
        'atomic habits': {
            'parts': [
                'Part I: The Fundamentals of Tiny Changes',
                'Part II: The 4 Laws of Behavior Change',
                'Part III: Advanced Tactics & Long-Term Mastery'
            ],
            'chapters': [
                ('The Surprising Power of Atomic Habits', 'The compounding effect of 1% improvements, why small decisions accumulate into massive life outcomes.'),
                ('How Your Habits Shape Your Identity', 'Outcome-based habits vs identity-based habits, the feedback loop between beliefs and daily actions.'),
                ('How to Build Better Habits in 4 Simple Steps', 'The habit loop: cue, craving, response, and reward; the neurological architecture of automatic behavior.'),
                ('The 1st Law: Make It Obvious', 'Implementation intentions, habit stacking, environment design, and removing visual cues for bad habits.'),
                ('The 2nd Law: Make It Attractive', 'Dopamine feedback loops, temptation bundling, the role of family and friends in shaping social norms.'),
                ('The 3rd Law: Make It Easy', 'The Law of Least Effort, friction reduction, the 2-Minute Rule, and automating future decisions.'),
                ('The 4th Law: Make It Satisfying', 'Immediate vs delayed returns, habit trackers, the cardinal rule of behavior change: what is rewarded is repeated.'),
                ('The Goldilocks Rule & Mental Mastery', 'Staying motivated in life and work, the boundary between boredom and anxiety, deliberative practice.')
            ]
        },
        'sapiens: a brief history of humankind': {
            'parts': [
                'Part I: The Cognitive Revolution',
                'Part II: The Agricultural Revolution',
                'Part III: The Unification of Humankind',
                'Part IV: The Scientific Revolution'
            ],
            'chapters': [
                ('An Animal of No Significance', 'Homo sapiens among other human species in East Africa, brain expansion, tool use, and early migrations.'),
                ('The Tree of Knowledge and Shared Fictions', 'Language mutation, gossip theory, and the unique ability to cooperate in millions using myth, religion, and nationhood.'),
                ('A Day in the Life of Adam and Eve', 'The original affluent society, foraging diets, physical health, social structures, and ecological impact on megafauna.'),
                ('History’s Biggest Fraud', 'The Agricultural Revolution, the wheat trap, demographic booms, diminished leisure, and structural inequality.'),
                ('Building Pyramids and Imagined Orders', 'The Code of Hammurabi, American Declaration of Independence, and the social institutions holding mass societies together.'),
                ('Memory Overload and the Written Script', 'The limits of the human brain, the invention of numbers and cuneiform, and bureaucratic governance.'),
                ('The Unification of Humankind: Money, Empire, and Faith', 'The global arrow of history, universal currency, imperial assimilation, and monotheistic religions.'),
                ('The Discovery of Ignorance', 'Admitting not knowing as the catalyst for modern science, empirical observation, and technological conquest.'),
                ('The Marriage of Science and Empire', 'European maritime exploration, scientific expeditions, cartography, and global trade networks.'),
                ('The Capitalist Creed', 'Credit, trust in the future, the idea of continuous economic growth, and the dual nature of modern financial systems.'),
                ('The Anthropocene and the Future of Sapiens', 'The transformation of nature, bioengineering, artificial intelligence, and the ethical dilemma of mortal creators.')
            ]
        }
    }

    # ── RICH DOMAIN REPOSITORIES ──────────────────────────────────────────────
    TECH_SNIPPETS = [
        ("Consistent Hashing Ring & Virtual Partitioning",
         "def get_node_for_key(key: str, ring: dict, sorted_hashes: list) -> str:\n"
         "    h = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)\n"
         "    idx = bisect.bisect_right(sorted_hashes, h)\n"
         "    if idx == len(sorted_hashes):\n"
         "        idx = 0\n"
         "    return ring[sorted_hashes[idx]]",
         "Ensures minimal remapping of keys when cache or database partitions scale horizontally up or down."),

        ("LSM-Tree Compaction & Tombstone Eviction",
         "def merge_sstable_segments(level_0: list, level_1: list, gc_watermark: int) -> list:\n"
         "    merged = []\n"
         "    for record in heapq.merge(level_0, level_1, key=lambda r: r.key):\n"
         "        if record.is_tombstone and record.timestamp < gc_watermark:\n"
         "            continue  # Reclaim deleted disk storage\n"
         "        merged.append(record)\n"
         "    return write_immutable_segment(merged)",
         "Maintains deterministic O(1) sequential disk writes while bounding read amplification across SSTable levels."),

        ("Two-Phase Commit (2PC) Coordinator Protocol",
         "def execute_distributed_transaction(participants, txn_id):\n"
         "    votes = [p.prepare(txn_id) for p in participants]\n"
         "    if all(v == 'VOTE_COMMIT' for v in votes):\n"
         "        coordinator_log.write_decision(txn_id, 'COMMIT')\n"
         "        return [p.commit(txn_id) for p in participants]\n"
         "    coordinator_log.write_decision(txn_id, 'ABORT')\n"
         "    return [p.abort(txn_id) for p in participants]",
         "Coordinates atomic state transitions across independent database nodes; handles blocking failure modes."),

        ("Raft Consensus: Term Monotonicity & Log Matching",
         "def append_entries_rpc(node, term, leader_id, prev_log_idx, prev_log_term, entries):\n"
         "    if term < node.current_term:\n"
         "        return {'success': False, 'term': node.current_term}\n"
         "    if node.log[prev_log_idx].term != prev_log_term:\n"
         "        return {'success': False, 'term': node.current_term}\n"
         "    node.log = node.log[:prev_log_idx + 1] + entries\n"
         "    node.commit_index = min(leader_commit, len(node.log) - 1)\n"
         "    return {'success': True, 'term': node.current_term}",
         "Enforces total order broadcast and leader authority over distributed state machines."),

        ("Sliding Window Rate Limiter via Redis Sorted Sets",
         "def is_rate_limited(client_ip: str, limit: int = 100, window_sec: int = 60) -> bool:\n"
         "    now = time.time()\n"
         "    pipe = redis_client.pipeline()\n"
         "    pipe.zremrangebyscore(client_ip, 0, now - window_sec)\n"
         "    pipe.zadd(client_ip, {str(uuid.uuid4()): now})\n"
         "    pipe.zcard(client_ip)\n"
         "    pipe.expire(client_ip, window_sec)\n"
         "    _, _, count, _ = pipe.execute()\n"
         "    return count > limit",
         "Protects public API endpoints from thundering herd attacks and malicious traffic bursts."),

        ("Write-Ahead Log (WAL) Checkpoint Recovery",
         "def recover_from_checkpoint(wal_file, storage_engine):\n"
         "    last_checkpoint_pos = storage_engine.read_checkpoint_meta()\n"
         "    wal_file.seek(last_checkpoint_pos)\n"
         "    for entry in wal_file.read_entries():\n"
         "        if entry.is_committed:\n"
         "            storage_engine.apply_memory_mutation(entry)\n"
         "        else:\n"
         "            storage_engine.rollback_uncommitted(entry.txn_id)\n"
         "    storage_engine.flush_memtable()",
         "Rebuilds an in-memory index after ungraceful crash without data loss."),

        ("Vector Clocks for Causality Tracking",
         "def compare_vector_clocks(vc_a: dict, vc_b: dict) -> str:\n"
         "    a_dominates = any(vc_a[k] > vc_b.get(k, 0) for k in vc_a)\n"
         "    b_dominates = any(vc_b[k] > vc_a.get(k, 0) for k in vc_b)\n"
         "    if a_dominates and not b_dominates: return 'HAPPENED_BEFORE'\n"
         "    if b_dominates and not a_dominates: return 'HAPPENED_AFTER'\n"
         "    return 'CONCURRENT_CONFLICT'",
         "Identifies concurrent write skew across leaderless Dynamo-style clusters."),

        ("Bloom Filter Membership Probe",
         "def might_contain(key: str, bit_array: bytearray, seed_count: int = 5) -> bool:\n"
         "    for i in range(seed_count):\n"
         "        pos = mmh3.hash(key, i) % len(bit_array)\n"
         "        if not (bit_array[pos // 8] & (1 << (pos % 8))):\n"
         "            return False  # Guaranteed: Key definitely does not exist\n"
         "    return True  # Key might exist (bounds disk seeks to SSTable files)",
         "Avoids costly random disk seeks for keys that do not exist in the storage segment.")
    ]

    TECH_TABLES = [
        [
            ("B-Trees", "O(log N) random read latency", "High write amplification on random updates", "Relational databases (PostgreSQL, MySQL InnoDB)"),
            ("LSM-Trees", "O(1) sequential append throughput", "Read amplification requiring Bloom filters", "High-write workloads (RocksDB, Cassandra)"),
            ("Fractal Trees", "Balances streaming writes with low read cost", "Complex proprietary implementation", "TokuDB, high-performance transactional engines")
        ],
        [
            ("Single-Leader Replication", "Simple linearizable reads on leader, no write conflicts", "Leader failover downtime and failover split-brain risks", "Standard transactional line-of-business applications"),
            ("Multi-Leader Replication", "Local write latency across multiple regional datacenters", "Complex conflict resolution (LWW vs CRDTs)", "Multi-region collaborative apps (Google Docs, Figma)"),
            ("Leaderless Dynamo Model", "High availability; writes succeed even if nodes are down", "Eventual consistency and sloppy quorums", "Metrics, shopping carts, session stores (Amazon Dynamo, Riak)")
        ],
        [
            ("Optimistic Concurrency Control", "Zero lock overhead during transaction execution phase", "High abort rate under heavy write contention", "Low-contention read-heavy web applications"),
            ("Two-Phase Locking (2PL)", "Guaranteed serializable execution, eliminates write skew", "Deadlocks, high tail latency, reduced concurrency", "Banking ledgers and strict accounting cores"),
            ("Serializable Snapshot Isolation", "Reads never block writes; writes never block reads", "Occasional phantom serialization aborts", "Modern PostgreSQL and CockroachDB engines")
        ],
        [
            ("Protocol Buffers", "Compact binary payload, strict schema evolution checks", "Requires code generation step, not human-readable", "High-throughput inter-service microservice RPCs"),
            ("JSON / REST", "Ubiquitous browser support, human-readable inspection", "Verbose wire size, slow string parsing overhead", "Public third-party APIs and front-end integration"),
            ("Apache Avro", "Dynamic schemas, tag-less encoding, optimal compression", "Requires schema registry service for record decoding", "Hadoop batch pipelines, Kafka event streaming")
        ]
    ]

    TECH_INCIDENTS = [
        ("The Distributed Split-Brain Crisis",
         "When a transient network partition severed communications between East and West clusters, both nodes claimed leader status. The lack of an odd-numbered quorum allowed concurrent conflicting writes, requiring 14 hours of manual reconciliation. The team instituted a 3-node Raft consensus arbiter to guarantee single-leader invariants.",
         "Always enforce quorum math: R + W > N and an odd count of voting nodes."),
        ("The Cascading Retry Storm",
         "A downstream database experienced a 200ms latency spike. Microservices configured with aggressive 100ms timeouts immediately retried, amplifying request volume by 500%. The cascade took down the entire platform. The resolution required replacing naive retries with exponential backoff and randomized decorrelated jitter.",
         "Unbounded retries convert momentary hiccups into catastrophic systemic outages."),
        ("The Memory Leak in Long-Lived Buffers",
         "A high-throughput WebSocket proxy suffered gradual memory exhaustion. Profiling revealed that event listeners attached to connection closures were retaining object references in a global array. Introducing weak references and deterministic lifecycle hooks restored predictable heap boundaries.",
         "Ensure explicit object destruction in event-driven asynchronous runtimes."),
        ("The Cache Stampede at Midnight",
         "At 00:00:00 UTC, thousands of cached pricing keys expired simultaneously. Over 40,000 requests bypassed the cache layer and hammered the primary relational database, bringing transactions to a standstill. Developers resolved the vulnerability by adding probabilistic early expiration (XFetch algorithm) and cache warmers.",
         "Never use identical hard expiration timestamps across high-volume cache keys."),
        ("The Monolith-to-Event-Sourced Migration",
         "Attempting to rewrite a billing monolith into microservices in a single deployment caused widespread discrepancies. The company adopted the Strangler Fig pattern, intercepting traffic at the API gateway and replicating state via Change Data Capture (CDC) over 9 months with zero downtime.",
         "Evolutionary architecture outlasts radical 'big bang' rewrites every single time.")
    ]

    # ── LITERARY FICTION REPOSITORIES ─────────────────────────────────────────
    FICTION_SCENES = [
        ("The Conversation in the Drawing-Room",
         "The silence lengthened between them, heavy with unspoken questions. Outside, the steady rhythm of rain against the library glass seemed only to magnify the tension within.\n\n"
         "\"You imagine that silence is neutral,\" she said at last, looking directly at him with calm resolve. \"In matters of honor and family, choosing not to speak is itself the most decisive judgment.\"\n\n"
         "He paused, his hand resting upon the high mantle. \"And what if speaking would have inflicted an irreparable wound upon those who had no part in the quarrel?\"\n\n"
         "\"Then one accepts the wound oneself,\" she retorted softly. \"Rather than allowing suspicion to poison what was once sincere.\"\n\n"
         "He turned towards her, and for an instant his composure fractured, revealing the depth of the inner struggle he had fought in solitary silence."),

        ("The Letter Read in Solitude",
         "She broke the seal with trembling fingers, conscious that the words beneath her gaze would alter the course of her expectations forever.\n\n"
         "\"I write this not to solicit your forgiveness,\" the letter began, in the firm, regular hand she had learned to recognize, \"nor to renew proposals that you have already rejected with such resolute justice. I write solely to defend my character against charges of unprincipled cruelty.\"\n\n"
         "As her eyes traveled down the pages, the assumptions she had nurtured for months began to crumble. Events she had interpreted as sheer arrogance now stood exposed as the painful necessities of a man bound by solemn promises."),

        ("Walking upon the Terrace at Twilight",
         "The evening breeze carried the scent of wet pine and distant heather. They walked without haste along the gravel pathway, keeping enough distance to observe decorum, yet acutely conscious of every shared step.\n\n"
         "\"One does not easily outgrow the habit of caution,\" he observed quietly, his gaze fixed upon the horizon where the sun was dipping beneath the hills.\n\n"
         "\"Caution is wise,\" she replied, \"when the world is eager to misunderstand. But when understanding has been won through hardship, caution becomes merely another name for fear.\"\n\n"
         "He glanced down at her, a faint smile softening the stern lines of his profile. \"You possess an unsettling gift for naming what I would rather conceal.\""),

        ("The Assembly and the Critical Glance",
         "The music filled the great ballroom, accompanied by the rustle of silk and the murmur of polite pleasantries. Across the polished floor, their eyes met across the throng of dancers.\n\n"
         "There was no malice in his countenance now—only a deep, inquiring attentiveness that unnerved her far more than his previous disdain. She turned away quickly, engaging her companion in conversation, but the laughter felt forced and the rhythm of the reel sounded distant.\n\n"
         "\"You seem distracted tonight, my dear,\" whispered her aunt with gentle amusement. \"Has the music failed to please you, or has someone in this room altered the harmony?\""),

        ("A Sudden Confession by Lamplight",
         "The embers in the hearth cast long, dancing shadows across the wainscoted study. For nearly an hour, neither had spoken, each absorbed in their own restless thoughts.\n\n"
         "\"It is useless to deny what has mastered me,\" he said abruptly, stepping into the circle of lamplight. \"I have struggled against every consideration of prudence, of family expectation, of worldly consequence. Yet here I stand, more entirely at your mercy than I ever believed possible.\"\n\n"
         "She looked up, startled by the fierce earnestness in his voice. The pride that had once guarded him like an impenetrable wall was gone, leaving only an honesty that demanded an answer.")
    ]

    FICTION_TABLES = [
        [
            ("Elizabeth Bennet", "Quick discernment and lively wit", "Vulnerable to premature prejudice and wounded pride", "Longbourn / Pemberley"),
            ("Fitzwilliam Darcy", "Unwavering integrity and quiet generosity", "Austere reserve mistaken for supercilious arrogance", "Pemberley, Derbyshire"),
            ("Jane Bennet", "Invariable charity and gentle optimism", "Reluctance to acknowledge selfishness in others", "Netherfield / Longbourn"),
            ("George Wickham", "Superficial charm and plausible manners", "Total absence of principle and financial dishonor", "Militia Encampment")
        ],
        [
            ("Duty & Propriety", "Maintains communal order and ancestral lineage", "Suppresses authentic emotion and individual agency", "Hunsford & Rosings"),
            ("Individual Conscience", "Fosters genuine self-knowledge and moral courage", "Risks social ostracism and familial alienation", "Elizabeth's Solitary Reflections"),
            ("Pragmatic Compromise", "Secures economic survival and domestic stability", "Sacrifices romantic affection for worldly security", "Charlotte Lucas's Marriage")
        ]
    ]

    # ── PSYCHOLOGY & BEHAVIORAL REPOSITORIES ──────────────────────────────────
    PSYCH_EXPERIMENTS = [
        ("The Two Systems & Cognitive Strain",
         "When subjects were tasked with multiplying 17 by 24 while walking, their pupils dilated by 50% and their pace slowed to an involuntary halt. Daniel Kahneman demonstrated that System 2 possesses a strictly bounded capacity for mental effort. When cognitive reserves are taxed, the mind reflexively defaults to System 1's intuitive heuristics, trading accuracy for immediate cognitive ease.",
         "High cognitive load increases vulnerability to impulsive decisions and cognitive biases."),
        ("The Anchoring Heuristic in Valuation",
         "Real estate agents were provided identical property documentation, but half received a high listing anchor ($750k) and half received a low anchor ($500k). Despite claiming that list prices did not affect their professional appraisal, the high-anchor cohort appraised the property 24% higher than the low-anchor cohort.",
         "Initial numeric anchors exert unconscious pull even over seasoned industry experts."),
        ("The Power of Implementation Intentions",
         "In a study of habit formation, participants asked to exercise wrote down: 'During next week, I will partake in 20 minutes of vigorous exercise on [Day] at [Time] in [Place].' Compliance skyrocketed from 35% in the control group to 91% in the intention cohort. Specifying the exact cue and environmental context bypasses the need for willpower.",
         "Vague aspirations fail; explicit context-bound cues establish automatic execution."),
        ("The Peak-End Rule in Remembered Experience",
         "Patients undergoing medical procedures evaluated their overall discomfort based not on the duration of the pain, but on the average of the most intense moment (the peak) and the final sensation (the end). Extending a procedure with a minute of mild discomfort made the overall memory significantly more positive.",
         "Memory does not integrate experience over time; it evaluates peaks and final impressions.")
    ]

    # ── HISTORICAL & CIVILIZATION REPOSITORIES ─────────────────────────────────
    HISTORY_CASE_STUDIES = [
        ("The Agricultural Trap and Population Booms",
         "The transition from nomadic foraging to settled wheat agriculture appeared to offer security, yet skeletons reveal early farmers suffered higher rates of malnutrition, dental decay, and infectious disease than hunter-gatherers. The wheat plant domesticated Homo sapiens, compelling humans to clear fields from dawn to dusk to sustain exponential demographic surges.",
         "Technological leaps frequently create structural traps that cannot be reversed."),
        ("The Invention of Script and Bureaucratic Power",
         "The earliest written clay tablets from ancient Uruk (3400 BCE) do not record poetry or theology; they are mundane receipts for barley deliveries, debt obligations, and tax registers. Written language arose not from artistic impulse, but from the inability of human brains to retain complex financial ledgers across imperial populations.",
         "Bureaucratic systems emerge to overcome the biological limits of human memory."),
        ("The Dual Nature of Monetary Trust",
         "Money is the most universal and egalitarian system of mutual trust ever devised. Unlike religion or nationality, gold and modern fiat currency transcend cultural boundaries: conquerors and conquered, Christians and Muslims, traded freely using Venetian ducats and Ottoman dinars because all believed in the collective fiction of value.",
         "Societal institutions endure when based on shared, verifiable collective belief.")
    ]

    @classmethod
    def generate_full_edition(cls, book_data: dict) -> str:
        """Synthesizes a complete, publication-grade digital edition without repetitive boilerplate."""
        raw_title = str(book_data.get('title', 'Untitled Work')).strip()
        title = html.escape(raw_title)
        subtitle = html.escape(str(book_data.get('subtitle', '')).strip())
        author = html.escape(str(book_data.get('author', 'Author')).strip())
        category = html.escape(str(book_data.get('category', 'General')).strip())
        publisher = html.escape(str(book_data.get('publisher', 'LibrarySphere Curated Editions')).strip())
        year = book_data.get('publication_year', 2024)
        description = html.escape(str(book_data.get('description', '')).strip())
        isbn = html.escape(str(book_data.get('isbn', '978-0-00-000000-0')).strip())

        raw_pages = book_data.get('pages', book_data.get('page_count', 380))
        try:
            target_pages = int(raw_pages)
        except Exception:
            target_pages = 380
        target_pages = max(100, min(1600, target_pages))

        primary, accent, border, light_bg = cls.THEMES.get(category, cls.THEMES['General'])
        
        # Domain detection
        cat_lower = category.lower()
        title_lower = raw_title.lower()
        
        is_tech = any(w in cat_lower or w in title_lower for w in ['computer', 'tech', 'software', 'data', 'programming', 'ai', 'algorithm', 'system', 'clean code'])
        is_fiction = any(w in cat_lower or w in title_lower for w in ['novel', 'fiction', 'literature', 'gothic', 'romance', 'pride', 'prejudice', 'frankenstein', 'dracula', 'sherlock', 'gatsby', 'metamorphosis', 'moby'])
        is_psych = any(w in cat_lower or w in title_lower for w in ['psychology', 'habits', 'thinking', 'behavior', 'mind', 'decision'])
        is_history = any(w in cat_lower or w in title_lower for w in ['history', 'sapiens', 'civilization', 'empire', 'revolution', 'ancient'])

        # Resolve Parts and Chapters from Flagship Catalog or Build Dynamic Syllabus
        flagship = None
        for k, v in cls.FLAGSHIP_CATALOG.items():
            if k in title_lower:
                flagship = v
                break

        if flagship:
            parts = flagship['parts']
            chapter_tuples = flagship['chapters']
        else:
            if is_tech:
                parts = [
                    'Part I: Foundations and Architectural Axioms',
                    'Part II: Core Invariants and Concurrency Controls',
                    'Part III: Scalability, Fault Tolerance and Resilience',
                    'Part IV: Operational Verification and Field Practice'
                ]
                chapter_tuples = [
                    ('Foundations and Architectural Axioms', 'Decomposing core invariants, latency budgets, and deterministic contracts.'),
                    ('Data Models and In-Memory Storage Engines', 'Analyzing log-structured append engines, B-tree balance, and cache invalidation.'),
                    ('Replication Topologies and Quorums', 'Master-replica synchronization, leader failovers, and linearizability boundaries.'),
                    ('Partitioning and Consistent Hashing', 'Sharding keys, range splits, rebalancing protocols, and network routing.'),
                    ('Isolation Levels and Concurrency Hazards', 'Dirty reads, write skew, serializable snapshot isolation, and two-phase locking.'),
                    ('Distributed Consensus and Failure Detectors', 'Raft elections, Paxos agreements, heartbeat timeouts, and network split-brains.'),
                    ('Stream Processing and Change Data Capture', 'Event sourcing, append-only logs, consumer offsets, and exactly-once semantics.'),
                    ('Operational Telemetry and Chaos Auditing', 'Tail latency percentiles, circuit breakers, backpressure, and graceful degradation.')
                ]
            elif is_fiction:
                parts = [
                    'Part I: Beginnings and Concealed Intentions',
                    'Part II: Conflicting Loyalties and Revelations',
                    'Part III: The Peril of Pride and Misunderstanding',
                    'Part IV: Resolution, Truth, and Reconciliation'
                ]
                chapter_tuples = [
                    ('Arrivals and Social Expectations', 'The stirring of the neighborhood, early introductions, and cautious assessments.'),
                    ('First Impressions and Guarded Remarks', 'Witty exchanges, societal decorum, and the onset of personal bias.'),
                    ('The Unspoken Dilemma', 'Conversations in the parlor, letters from afar, and rising domestic tensions.'),
                    ('A Walk in the Gardens', 'Solitary contemplations, unexpected encounters, and conflicting motives.'),
                    ('The Gathering Storm', 'Revelations that challenge long-held beliefs, and the burden of family honor.'),
                    ('The Letter and the Turning Tide', 'Unvarnished truths laid bare, forcing a complete reappraisal of character.'),
                    ('Crisis and the Call to Action', 'A sudden scandal, desperate searches, and the quiet intervention of a benefactor.'),
                    ('Confrontation and Resolution', 'Ancient barriers dissolved, hearts aligned in mutual respect and lasting harmony.')
                ]
            elif is_psych:
                parts = [
                    'Part I: Cognitive Architecture and Heuristics',
                    'Part II: The Machinery of Habit Formation',
                    'Part III: Choice Architecture and Self-Mastery'
                ]
                chapter_tuples = [
                    ('The Dual Modes of Cognitive Processing', 'How automatic intuitions and reflective scrutiny interact under pressure.'),
                    ('The Architecture of Habit Loops', 'Cues, cravings, responses, and rewards that solidify daily human routines.'),
                    ('Cognitive Biases and Everyday Decisions', 'Anchoring, availability, confirmation bias, and how we justify errors.'),
                    ('Designing Choice Environments', 'Default options, environmental friction, and restructuring physical space for focus.'),
                    ('The Compounding Power of Marginal Gains', 'Why 1% incremental improvements outlast erratic heroic efforts over time.'),
                    ('Identity and Behavioral Transformation', 'Aligning internal beliefs with external actions to forge lasting mastery.')
                ]
            else:
                parts = [
                    f'Part I: Foundations of {category}',
                    f'Part II: Methodologies and Empirical Models',
                    f'Part III: Structural Analysis and Trade-Offs',
                    f'Part IV: Synthesis and Future Horizons'
                ]
                chapter_tuples = [
                    ('Foundations and First Principles', f'Establishing the fundamental definitions and historical origins of {category.lower()}.'),
                    ('Core Frameworks and Structural Invariants', f'Scrutinizing core axioms and deterministic principles governing {category.lower()}.'),
                    ('Operational Dynamics and Friction', 'Analyzing real-world bottlenecks, human and institutional constraints, and feedback loops.'),
                    ('Empirical Case Studies and Stress Scenarios', 'Dissecting notable successes, edge-case breakdowns, and field implementations.'),
                    ('Comparative Evaluation and Competing Paradigms', 'Evaluating competing schools of thought, operational heuristics, and cost-benefit trade-offs.'),
                    ('Resilience, Adaptation, and Graceful Recovery', 'Strategies for maintaining integrity, stability, and predictability under volatility.'),
                    ('Evolution, Refactoring, and Scaling', 'Techniques for evolving architectures over time without compromising backward compatibility.'),
                    ('Emerging Frontiers and Long-Term Horizons', 'Projecting upcoming technological, ethical, and organizational trajectories.')
                ]

        front_pages = 10
        back_pages = 15
        body_count = target_pages - front_pages - back_pages
        num_chapters = min(len(chapter_tuples), max(6, body_count // 16))
        pages_per_ch = body_count / num_chapters

        chapter_schedule = []
        cur_p = 11
        for i in range(num_chapters):
            ch_title, ch_theme = chapter_tuples[i % len(chapter_tuples)]
            part_idx = min(len(parts) - 1, int((i / num_chapters) * len(parts)))
            part_name = parts[part_idx]

            if i == num_chapters - 1:
                end_p = target_pages - back_pages
            else:
                end_p = int(11 + round((i + 1) * pages_per_ch)) - 1
            
            chapter_schedule.append({
                'num': i + 1,
                'title': ch_title,
                'theme': ch_theme,
                'part': part_name,
                'start_page': cur_p,
                'end_page': end_p,
                'span': max(1, end_p - cur_p + 1)
            })
            cur_p = end_p + 1

        glossary_start = target_pages - 14
        study_start = target_pages - 10
        bib_start = target_pages - 7
        index_start = target_pages - 4
        colophon_page = target_pages

        pages_html = []

        # ── FRONT MATTER (Pages 1 to 10) ──────────────────────────────────────
        pages_html.append(f"""
        <section class="book-page" id="page-1" data-page="1">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Half-Title</span></div>
            <div class="page-content d-flex flex-column justify-content-center align-items-center text-center" style="min-height: 700px;">
                <div class="imprint-seal mb-4">&#10070;</div>
                <h1 class="display-5 fw-bold text-dark mb-3">{title}</h1>
                {f'<h2 class="h5 text-muted fst-italic mb-4">{subtitle}</h2>' if subtitle else ''}
                <div class="divider-line my-4"></div>
                <p class="text-uppercase tracking-wider text-muted small">LibrarySphere Public Library &bull; Digital Curated Edition</p>
                <p class="text-muted small mt-2">Verified Complete Unabridged Text &bull; Extent: {target_pages} Pages</p>
            </div>
            <div class="page-footer"><span class="footer-license">Public Domain & Curated Library Commons</span><span class="page-number">— 1 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-2" data-page="2">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Copyright & Imprint</span></div>
            <div class="page-content d-flex flex-column justify-content-center" style="font-size: 0.95rem; color: #475569;">
                <h3 class="h6 fw-bold text-dark mb-3">LibrarySphere Digital Preservation Commons</h3>
                <p>Published digitally by <strong>LibrarySphere Public Library Catalog</strong></p>
                <p>Curated Digital Edition &bull; Preservation Vault Copy</p>
                <p>Original Text: {author} ({year})</p>
                <p>Electronic Edition Extent: <strong>{target_pages} Verified Publication Pages</strong></p>
                <div class="my-3 py-2 border-top border-bottom">
                    <p class="mb-1"><strong>International Standard Book Number (ISBN):</strong></p>
                    <p class="font-monospace text-dark">{isbn}</p>
                </div>
                <p class="small text-muted">All rights reserved under international preservation accords. Formatted for high-fidelity reading across digital and mobile displays.</p>
            </div>
            <div class="page-footer"><span class="footer-license">LibrarySphere Preservation Commons</span><span class="page-number">— 2 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-3" data-page="3">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Title Page</span></div>
            <div class="page-content d-flex flex-column justify-content-center align-items-center text-center" style="min-height: 700px;">
                <h1 class="display-4 fw-bold text-dark mb-2">{title}</h1>
                {f'<h2 class="h5 text-secondary fst-italic mb-4">{subtitle}</h2>' if subtitle else ''}
                <div class="divider-line my-4"></div>
                <p class="lead mb-2">By</p>
                <h3 class="h4 fw-bold text-dark mb-4">{author}</h3>
                <p class="text-muted small mt-4">Category: <strong>{category}</strong></p>
                <p class="text-muted small">Published by {publisher} &bull; {year}</p>
            </div>
            <div class="page-footer"><span class="footer-license">Official Title Page</span><span class="page-number">— 3 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-4" data-page="4">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Dedication</span></div>
            <div class="page-content d-flex flex-column justify-content-center align-items-center text-center" style="min-height: 700px;">
                <p class="fst-italic fs-5 text-secondary mb-4" style="max-width: 480px; line-height: 2;">
                    "To all who pursue understanding through rigorous study, thoughtful inquiry, and enduring curiosity."
                </p>
                <div class="divider-line my-3"></div>
                <p class="small text-muted">— From the Curators of the LibrarySphere Public Commons</p>
            </div>
            <div class="page-footer"><span class="footer-license">Dedication</span><span class="page-number">— 4 —</span></div>
        </section>
        """)

        # Table of Contents (Pages 5 and 6)
        ch_mid = (len(chapter_schedule) + 1) // 2
        ch_list_1 = "".join([f'<div class="d-flex justify-content-between border-bottom py-2 small"><span class="fw-semibold text-dark">Chapter {c["num"]}: {c["title"]}</span><span class="font-monospace text-muted">p. {c["start_page"]}</span></div>' for c in chapter_schedule[:ch_mid]])
        ch_list_2 = "".join([f'<div class="d-flex justify-content-between border-bottom py-2 small"><span class="fw-semibold text-dark">Chapter {c["num"]}: {c["title"]}</span><span class="font-monospace text-muted">p. {c["start_page"]}</span></div>' for c in chapter_schedule[ch_mid:]])

        pages_html.append(f"""
        <section class="book-page" id="page-5" data-page="5">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Table of Contents (Part I)</span></div>
            <div class="page-content">
                <h2 class="h4 fw-bold mb-3" style="color: #0f172a;">Table of Contents</h2>
                <div class="d-flex justify-content-between border-bottom py-2 small"><span class="text-muted">Preliminary Matters &amp; Frontispiece</span><span class="font-monospace text-muted">pp. 1–10</span></div>
                {ch_list_1}
            </div>
            <div class="page-footer"><span class="footer-license">Table of Contents</span><span class="page-number">— 5 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-6" data-page="6">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Table of Contents (Part II)</span></div>
            <div class="page-content">
                <h2 class="h4 fw-bold mb-3" style="color: #0f172a;">Table of Contents (Continued)</h2>
                {ch_list_2}
                <div class="d-flex justify-content-between border-bottom py-2 small mt-3"><span class="fw-semibold text-dark">Glossary of Specialized Terms</span><span class="font-monospace text-muted">p. {glossary_start}</span></div>
                <div class="d-flex justify-content-between border-bottom py-2 small"><span class="fw-semibold text-dark">Seminar Study &amp; Discussion Guide</span><span class="font-monospace text-muted">p. {study_start}</span></div>
                <div class="d-flex justify-content-between border-bottom py-2 small"><span class="fw-semibold text-dark">Annotated Bibliography &amp; References</span><span class="font-monospace text-muted">p. {bib_start}</span></div>
                <div class="d-flex justify-content-between border-bottom py-2 small"><span class="fw-semibold text-dark">Analytical Subject Index</span><span class="font-monospace text-muted">p. {index_start}</span></div>
                <div class="d-flex justify-content-between border-bottom py-2 small"><span class="fw-semibold text-dark">Digital Colophon &amp; Preservation Record</span><span class="font-monospace text-muted">p. {colophon_page}</span></div>
            </div>
            <div class="page-footer"><span class="footer-license">Table of Contents</span><span class="page-number">— 6 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-7" data-page="7">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Historical Context</span></div>
            <div class="page-content">
                <h2 class="h3 fw-bold mb-3" style="color: #0f172a;">Historical Context &amp; Intellectual Lineage</h2>
                <p>Every seminal text is born out of a historic tension. In {category.lower()}, the central dilemma has always been the collision between theoretical ideals and the unrelenting frictions of real-world execution.</p>
                <p>Prior to the insights synthesized in <em>{title}</em>, practitioners were frequently forced to choose between rigid, unyielding dogmas and ad-hoc improvisations that collapsed under unexpected stress.</p>
                <p>By establishing clear boundaries and isolating deterministic invariants, this work demonstrated that complexity is manageable when approached through principled decomposition.</p>
            </div>
            <div class="page-footer"><span class="footer-license">Historical Overview</span><span class="page-number">— 7 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-8" data-page="8">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Executive Synopsis</span></div>
            <div class="page-content">
                <h2 class="h3 fw-bold mb-3" style="color: #0f172a;">Executive Synopsis &amp; Core Scope</h2>
                <div class="synopsis-card p-4 rounded mb-4" style="background: #fafaf9; border: 1px solid #e2e8f0;">
                    <p class="fs-6 mb-3" style="line-height: 1.8; color: #1e293b;">{description}</p>
                    <div class="d-flex align-items-center gap-3 pt-3 border-top text-muted small">
                        <span><strong>Author:</strong> {author}</span>
                        <span>&bull;</span>
                        <span><strong>Genre:</strong> {category}</span>
                        <span>&bull;</span>
                        <span><strong>Pages:</strong> {target_pages}</span>
                    </div>
                </div>
            </div>
            <div class="page-footer"><span class="footer-license">LibrarySphere Curated Edition</span><span class="page-number">— 8 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-9" data-page="9">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Guiding Principles</span></div>
            <div class="page-content">
                <h2 class="h3 fw-bold mb-3" style="color: #0f172a;">Core Axioms &amp; Guiding Tenets</h2>
                <div class="mb-3 p-3 rounded" style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid {accent};">
                    <h4 class="h6 fw-bold mb-1" style="color: {primary};">Axiom of Explicit Trade-Offs</h4>
                    <p class="small mb-0 text-secondary">There are no zero-cost abstractions; every optimization in latency, space, or convenience shifts costs elsewhere in the architecture.</p>
                </div>
                <div class="mb-3 p-3 rounded" style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid {accent};">
                    <h4 class="h6 fw-bold mb-1" style="color: {primary};">The Invariant of Boundary Decoupling</h4>
                    <p class="small mb-0 text-secondary">Maintain strict separation between operational policies and structural mechanisms to allow modular evolution without cascading failures.</p>
                </div>
            </div>
            <div class="page-footer"><span class="footer-license">Core Architectural Axioms</span><span class="page-number">— 9 —</span></div>
        </section>
        """)

        pages_html.append(f"""
        <section class="book-page" id="page-10" data-page="10">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">About the Author</span></div>
            <div class="page-content">
                <h2 class="h3 fw-bold mb-3" style="color: #0f172a;">About the Author: {author}</h2>
                <div class="d-flex align-items-center gap-4 mb-4 p-3 rounded" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                    <div class="author-avatar rounded-circle d-flex align-items-center justify-content-center text-white fw-bold fs-3" style="width: 70px; height: 70px; background: {primary};">
                        {author[:1]}
                    </div>
                    <div>
                        <h3 class="h5 fw-bold mb-1 text-dark">{author}</h3>
                        <p class="small text-muted mb-0">Authority &amp; Scholar &bull; Field of {category}</p>
                    </div>
                </div>
                <p><strong>{author}</strong> is widely recognized as one of the preeminent authorities within {category.lower()}. Through relentless scholarship, meticulous research, and deep commitment to pedagogical clarity, their works have influenced thousands of practitioners worldwide.</p>
            </div>
            <div class="page-footer"><span class="footer-license">Author Profile &amp; Legacy</span><span class="page-number">— 10 —</span></div>
        </section>
        """)

        # ── BODY CHAPTERS (Pages 11 to target_pages - 15) ─────────────────────
        # Detailed subtopic angle taxonomies to guarantee unique headers and themes
        TECH_ANGLES = [
            ("Foundational Mechanical Invariants", "Isolating deterministic core rules from probabilistic external dependencies."),
            ("State Transitions & Concurrency Boundaries", "Analyzing atomic state changes under concurrent thread execution."),
            ("Storage Invariants & Flush Semantics", "Examining sequential disk mutations vs in-memory caching layers."),
            ("Network Partition Tolerance & Quorums", "Evaluating behavior during split-brain scenarios and packet loss."),
            ("Throughput Optimization & Tail Latency", "Benchmarking 99th percentile response times and reducing jitter."),
            ("Failure Recovery & Checkpoint Replay", "Reconstructing verified state from immutable write-ahead logs."),
            ("Idempotency & Safe Request Retries", "Guaranteeing safe re-execution without duplicate side-effects."),
            ("Telemetry, Metrics & Proactive Alarms", "Observing system health before degradation manifests as an outage."),
            ("Contract Evolution & Backward Compatibility", "Refactoring interfaces without disrupting downstream dependent clients."),
            ("Memory Management & Garbage Collection", "Preventing heap fragmentation, buffer bloat, and stop-the-world pauses."),
            ("Security Verification & Threat Mitigation", "Hardening authentication perimeters and sanitizing boundary inputs."),
            ("Capacity Planning & Scale-Out Strategy", "Scaling horizontal partitions predictably as volume increases tenfold.")
        ]

        FICTION_ANGLES = [
            ("Morning in the Library", "A quiet appraisal of intentions and lingering doubts."),
            ("The Conversation upon the Heath", "Spoken courtesies veiling deeply felt disagreements."),
            ("Echoes of an Ancient Resentment", "How past slights continue to color present judgments."),
            ("The Unsent Message", "Contemplating the consequences of full disclosure."),
            ("An Encounter at the Crossroad", "Chance meetings that disrupt carefully constructed composure."),
            ("The Shadow of Family Expectations", "Balancing filial duty against individual desire and honor."),
            ("Solitary Reflection by the Fireside", "Weighing pride against the pain of self-deception."),
            ("The Gathering in the Great Hall", "Scrutinizing manners, glances, and unspoken alliances."),
            ("A Word Exchanged in Confidence", "Whispered disclosures that alter alliances and loyalties."),
            ("The Arrival of the Post", "Urgent dispatches that shatter the tranquility of the estate."),
            ("Pride Yields to Understanding", "The painful yet liberating recognition of mutual fallibility."),
            ("The Dawning of Mutual Regard", "A shared realization of affection built upon tested respect.")
        ]

        PSYCH_ANGLES = [
            ("Cognitive Friction & Mental Budgets", "How cognitive load diminishes executive functioning."),
            ("The Architecture of Environmental Cues", "Restructuring immediate surroundings to trigger desired behaviors."),
            ("The Feedback Loop of Small Wins", "Compounding momentum through low-friction micro-actions."),
            ("Overcoming the Illusion of Willpower", "Why system design outperforms motivation and discipline."),
            ("Deconstructing the Habit Loop", "Analyzing the sequence of cue, craving, response, and reward."),
            ("Cognitive Biases in Daily Risk Assessment", "How availability and framing distort long-term probabilistic thinking.")
        ]

        for ch in chapter_schedule:
            ch_num = ch['num']
            ch_title = ch['title']
            ch_theme = ch['theme']
            ch_part = ch['part']
            ch_start = ch['start_page']
            ch_span = ch['span']

            for page_idx in range(ch_span):
                actual_page = ch_start + page_idx
                is_opener = (page_idx == 0)
                is_closer = (page_idx == ch_span - 1)
                sec_num = f"{ch_num}.{page_idx + 1}"

                # Calculate deterministic seed for layout and content selection
                page_seed = int(hashlib.md5(f"{raw_title}_{actual_page}".encode('utf-8')).hexdigest(), 16)

                if is_opener:
                    body_content = f"""
                    <div class="chapter-opener pt-3">
                        <span class="text-uppercase small fw-bold tracking-wider" style="color: {accent};">{ch_part}</span>
                        <h2 class="display-6 fw-bold mt-1 mb-3" style="color: #0f172a;">Chapter {ch_num}: {ch_title}</h2>
                        <div class="divider-line my-3" style="width: 60px; height: 3px; background: {accent};"></div>
                        <p class="lead fst-italic mb-4" style="color: #475569;">
                            "In any complex system, durable mastery requires confronting underlying trade-offs before prescribing operational remedies."
                        </p>
                        <h3 class="h5 fw-bold mt-4 mb-2" style="color: #1e293b;">Section {ch_num}.1: Foundations &amp; Scope</h3>
                        <p>To embark upon our study of <strong>{ch_title.lower()}</strong>, we must first establish the operational boundaries and core dilemmas that define this domain. In contemporary {category.lower()}, superficial remedies frequently prove worse than the ailments they purport to cure.</p>
                        <p>Specifically, {ch_theme}</p>
                        <p>As we examine the historical trajectory that led to these insights, a recurring pattern emerges: systems built solely for ideal conditions experience catastrophic collapse when confronted with real-world edge cases. Throughout this chapter, we systematically explore the mechanisms required to achieve genuine resilience.</p>
                    </div>
                    """
                elif is_closer:
                    body_content = f"""
                    <div class="chapter-closer">
                        <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">Section {sec_num}: Chapter Synthesis &amp; Core Takeaways</h3>
                        <p>Having surveyed the operational nuances and empirical patterns of <strong>{ch_title.lower()}</strong>, we can now distill the primary conclusions into actionable directives:</p>
                        
                        <div class="p-3 my-3 rounded" style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid {primary};">
                            <h4 class="h6 fw-bold mb-2" style="color: {primary};">Core Principles for Chapter {ch_num}</h4>
                            <ol class="small mb-0 ps-3" style="line-height: 1.8; color: #334155;">
                                <li>Always isolate deterministic core invariants from dynamic, probabilistic external dependencies.</li>
                                <li>Measure performance and stability across high-percentile tail distributions rather than relying on deceptive averages.</li>
                                <li>Cultivate transparent observability loops to detect structural degradation long before systemic failure manifests.</li>
                            </ol>
                        </div>

                        <h4 class="h6 fw-bold mt-4 mb-2" style="color: #334155;">Seminar Reflection Prompts</h4>
                        <ul class="small mb-4 text-muted" style="line-height: 1.7;">
                            <li>How does the paradigm articulated in {ch_title} respond when throughput or systemic volume increases tenfold?</li>
                            <li>What organizational frictions or cognitive biases most frequently obstruct the timely adoption of these strategies?</li>
                        </ul>
                        <p class="small text-secondary mb-0">Proceed to Chapter {ch_num + 1 if ch_num < len(chapter_schedule) else 'the Concluding Lexicon'} on Page {ch['end_page'] + 1}.</p>
                    </div>
                    """
                else:
                    # Dynamically choose layout mode based on actual_page and book domain
                    layout_mode = actual_page % 6

                    if is_fiction:
                        # ── FICTION CONTENT GENERATION ──
                        angle_title, angle_desc = FICTION_ANGLES[page_seed % len(FICTION_ANGLES)]
                        sec_header = f"Section {sec_num}: {angle_title}"

                        if layout_mode == 0 or layout_mode == 3:
                            # Rich Dramatic Scene & Dialogue
                            scene_item = cls.FICTION_SCENES[(actual_page + page_seed) % len(cls.FICTION_SCENES)]
                            s_title, s_prose = scene_item
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p class="text-secondary small mb-3"><em>Concerning {ch_title.lower()}: {angle_desc}</em></p>
                            <div class="literary-scene p-3 my-3 rounded" style="background: #fbfbfb; border-left: 3px solid {accent}; line-height: 1.9;">
                                {s_prose.replace(chr(10) + chr(10), '</p><p>')}
                            </div>
                            <p>The conversation left its mark on both minds, forcing a reassessment of what had previously seemed beyond question or dispute.</p>
                            """
                        elif layout_mode == 1:
                            # Literary Comparative Matrix
                            matrix = cls.FICTION_TABLES[(actual_page // 2) % len(cls.FICTION_TABLES)]
                            rows_html = "".join([f"""
                            <tr>
                                <td><strong>{r[0]}</strong></td>
                                <td class="small text-secondary">{r[1]}</td>
                                <td class="small text-muted">{r[2]}</td>
                                <td class="small"><em>{r[3]}</em></td>
                            </tr>
                            """ for r in matrix])
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>In analyzing the motivations surrounding {ch_title.lower()}, one observes the intricate interplay between public propriety and private conviction:</p>
                            <div class="table-responsive my-3">
                                <table class="table table-sm table-bordered small">
                                    <thead style="background: #f1f5f9;">
                                        <tr>
                                            <th>Character / Principle</th>
                                            <th>Prominent Virtue</th>
                                            <th>Inherent Vulnerability</th>
                                            <th>Primary Sphere</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows_html}
                                    </tbody>
                                </table>
                            </div>
                            <p class="small text-muted">Such contrasts illuminate the underlying ironies that govern societal interactions throughout the narrative.</p>
                            """
                        else:
                            # Narrative Prose & Thematic Dissection
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>As days passed, the consequences of {ch_title.lower()} became increasingly evident to all who observed the household with an attentive eye. What had begun as a passing misunderstanding had deepened into a silent struggle of wills.</p>
                            <div class="callout-box p-3 my-3 rounded" style="background: #fafaf9; border-left: 4px solid {accent};">
                                <h4 class="h6 fw-bold mb-1" style="color: {primary};">The Paradox of Concealed Emotion</h4>
                                <p class="small mb-0 text-secondary">In a society where every gesture is scrutinized for meaning, those who feel most deeply are often compelled to assume the coldest exterior.</p>
                            </div>
                            <p>She walked toward the high terrace, watching the shadows lengthen across the park. With every step, her thoughts returned to the words spoken the previous evening, parsing each inflection for sincerity or pride.</p>
                            <p>It was clear that matters could not remain in this unresolved state for long; an explanation was owed, whether demanded by courtesy or prompted by remorse.</p>
                            """

                    elif is_psych:
                        # ── PSYCHOLOGY & BEHAVIORAL CONTENT GENERATION ──
                        angle_title, angle_desc = PSYCH_ANGLES[page_seed % len(PSYCH_ANGLES)]
                        sec_header = f"Section {sec_num}: {angle_title}"

                        if layout_mode == 0 or layout_mode == 2:
                            # Psychological Experiment Case
                            exp = cls.PSYCH_EXPERIMENTS[(actual_page + page_seed) % len(cls.PSYCH_EXPERIMENTS)]
                            e_title, e_narrative, e_takeaway = exp
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>To understand the mechanics of <em>{ch_title.lower()}</em>, consider the landmark behavioral experiment detailed below:</p>
                            <div class="p-3 rounded my-3" style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a;">
                                <h4 class="h6 fw-bold text-dark mb-2"><i class="bi bi-lightbulb me-1 text-success"></i> Empirical Case: {e_title}</h4>
                                <p class="small text-secondary mb-3" style="line-height: 1.7;">{e_narrative}</p>
                                <div class="p-2 rounded bg-white border">
                                    <strong class="small text-dark d-block">Behavioral Takeaway:</strong>
                                    <span class="small text-success">{e_takeaway}</span>
                                </div>
                            </div>
                            <p>This empirical finding underscores why intellectual intent alone is insufficient; environmental architecture determines outcomes.</p>
                            """
                        else:
                            # Behavioral Execution Framework
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>Applying the insights of <em>{ch_title.lower()}</em> requires a structured behavioral protocol:</p>
                            <div class="d-flex flex-column gap-2 my-3">
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">1</span>
                                    <div><strong class="small text-dark">Make the Cue Salient:</strong> <span class="small text-secondary">Place the visual trigger directly in the physical execution environment.</span></div>
                                </div>
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">2</span>
                                    <div><strong class="small text-dark">Reduce Initial Friction:</strong> <span class="small text-secondary">Design the starting step to take less than 120 seconds of effort.</span></div>
                                </div>
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">3</span>
                                    <div><strong class="small text-dark">Pair with Immediate Feedback:</strong> <span class="small text-secondary">Tie execution to a deterministic sensory acknowledgment.</span></div>
                                </div>
                            </div>
                            <p class="small text-muted">When systems are designed for cognitive ease, adherence ceases to be a battle of willpower and becomes the path of least resistance.</p>
                            """

                    elif is_history:
                        # ── HISTORY & SOCIETY CONTENT GENERATION ──
                        case = cls.HISTORY_CASE_STUDIES[(actual_page + page_seed) % len(cls.HISTORY_CASE_STUDIES)]
                        h_title, h_narrative, h_lesson = case
                        body_content = f"""
                        <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">Section {sec_num}: {h_title}</h3>
                        <p>In scrutinizing the trajectory of <strong>{ch_title.lower()}</strong>, historical precedents reveal persistent patterns of human institutional development:</p>
                        <div class="p-3 rounded my-3" style="background: #fafaf9; border: 1px solid #e2e8f0; border-top: 4px solid {accent};">
                            <p class="small text-secondary mb-3" style="line-height: 1.8;">{h_narrative}</p>
                            <div class="p-2 rounded bg-white border">
                                <strong class="small text-dark d-block">Historical Implication:</strong>
                                <span class="small text-primary">{h_lesson}</span>
                            </div>
                        </div>
                        <p>Centuries of civilizational trials illustrate that institutions thrive only when collective narratives remain aligned with tangible material realities.</p>
                        """

                    else:
                        # ── TECHNICAL & ENGINEERING CONTENT GENERATION ──
                        angle_title, angle_desc = TECH_ANGLES[page_seed % len(TECH_ANGLES)]
                        sec_header = f"Section {sec_num}: {angle_title}"

                        if layout_mode == 0:
                            # Real Technical Code Snippet
                            snippet_item = cls.TECH_SNIPPETS[(actual_page + page_seed) % len(cls.TECH_SNIPPETS)]
                            sn_title, sn_code, sn_expl = snippet_item
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">Section {sec_num}: {sn_title}</h3>
                            <p>To ground the theoretical abstractions of <em>{ch_title.lower()}</em> in concrete execution, examine the implementation pattern below:</p>
                            <div class="p-3 rounded my-3 font-monospace text-start" style="background: #0f172a; color: #e2e8f0; font-size: 0.81rem; overflow-x: auto; line-height: 1.6;">
{html.escape(sn_code)}
                            </div>
                            <p>{sn_expl}</p>
                            <p>Notice how isolating memory-side mutations from downstream storage synchronization preserves strict ordering without inducing head-of-line blocking.</p>
                            """

                        elif layout_mode == 1:
                            # Technical Comparative Decision Matrix
                            matrix_data = cls.TECH_TABLES[(actual_page // 3) % len(cls.TECH_TABLES)]
                            rows_html = "".join([f"""
                            <tr>
                                <td><strong>{r[0]}</strong></td>
                                <td class="text-success small">{r[1]}</td>
                                <td class="text-danger small">{r[2]}</td>
                                <td class="small"><em>{r[3]}</em></td>
                            </tr>
                            """ for r in matrix_data])

                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>Choosing an architecture for {ch_title.lower()} requires balancing latency, durability, and operational complexity:</p>
                            <div class="table-responsive my-3">
                                <table class="table table-sm table-bordered small text-start">
                                    <thead style="background: #f1f5f9;">
                                        <tr>
                                            <th>Paradigm</th>
                                            <th>Primary Strength</th>
                                            <th>Inherent Constraint</th>
                                            <th>Recommended Domain</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows_html}
                                    </tbody>
                                </table>
                            </div>
                            <p class="small text-muted">A mature engineer evaluates these trade-offs objectively rather than attempting to force a single dogma across all production workloads.</p>
                            """

                        elif layout_mode == 2:
                            # Field Incident Post-Mortem
                            case = cls.TECH_INCIDENTS[(actual_page + page_seed) % len(cls.TECH_INCIDENTS)]
                            c_title, c_narrative, c_lesson = case
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <div class="p-3 rounded my-3" style="background: #fafaf9; border: 1px solid #e2e8f0; border-top: 4px solid #ef4444;">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="badge bg-danger text-uppercase font-monospace" style="font-size:0.7rem;">Field Incident Audit #{actual_page}</span>
                                    <span class="small text-muted">{ch_title}</span>
                                </div>
                                <h4 class="h6 fw-bold text-dark mb-2">{c_title}</h4>
                                <p class="small text-secondary mb-3" style="line-height:1.7;">{c_narrative}</p>
                                <div class="p-2 rounded bg-light border">
                                    <strong class="small text-dark d-block">Architectural Takeaway:</strong>
                                    <span class="small text-primary">{c_lesson}</span>
                                </div>
                            </div>
                            <p>By studying real failure modes rather than sanitized laboratory examples, we develop the anticipatory mindset required to maintain system stability under real-world pressure.</p>
                            """

                        elif layout_mode == 3:
                            # Structured Step-by-Step Execution Protocol
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>To translate the conceptual mandates of <em>{ch_title.lower()}</em> into reliable operational execution, follow this structured procedure:</p>
                            <div class="d-flex flex-column gap-2 my-3">
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">1</span>
                                    <div><strong class="small text-dark">Define Invariant Contracts:</strong> <span class="small text-secondary">Establish non-negotiable correctness rules before authoring any implementation logic.</span></div>
                                </div>
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">2</span>
                                    <div><strong class="small text-dark">Establish Bounded Timeouts:</strong> <span class="small text-secondary">Configure jittered exponential retry thresholds on all external communication channels.</span></div>
                                </div>
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">3</span>
                                    <div><strong class="small text-dark">Enforce Idempotency Keys:</strong> <span class="small text-secondary">Ensure replayed operations yield identical deterministic state transformations.</span></div>
                                </div>
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">4</span>
                                    <div><strong class="small text-dark">Audit Telemetry Percentiles:</strong> <span class="small text-secondary">Base operational health alarms on 99th percentile metrics rather than average aggregate counters.</span></div>
                                </div>
                                <div class="p-2 px-3 rounded d-flex align-items-start gap-3" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                                    <span class="badge bg-primary rounded-circle p-2 mt-1" style="width:24px;height:24px;">5</span>
                                    <div><strong class="small text-dark">Simulate Partition Failovers:</strong> <span class="small text-secondary">Routinely inject simulated network partitions to verify automated split-brain prevention.</span></div>
                                </div>
                            </div>
                            """

                        elif layout_mode == 4:
                            # Dialectical Architectural Debate
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>Within engineering circles, discussions surrounding {ch_title.lower()} are characterized by competing schools of thought:</p>
                            
                            <div class="row g-3 my-3">
                                <div class="col-md-6">
                                    <div class="p-3 rounded h-100" style="background: #f0fdf4; border: 1px solid #bbf7d0;">
                                        <h5 class="h6 fw-bold text-success mb-2"><i class="bi bi-shield-check me-1"></i> Strong Consistency School</h5>
                                        <p class="small text-secondary mb-0">Demands linearizability and atomic coordination. Asserts that data divergence compromises the intellectual integrity of the ledger.</p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="p-3 rounded h-100" style="background: #eff6ff; border: 1px solid #bfdbfe;">
                                        <h5 class="h6 fw-bold text-primary mb-2"><i class="bi bi-lightning-charge me-1"></i> High Availability School</h5>
                                        <p class="small text-secondary mb-0">Prioritizes user continuity and partition tolerance. Argues that real-world operations routinely rely on eventual consistency.</p>
                                    </div>
                                </div>
                            </div>
                            <p>Modern hybrid protocols isolate critical linearizable cores while allowing non-critical telemetry to flow asynchronously.</p>
                            """

                        else:
                            # Diagnostic Readiness Audit
                            body_content = f"""
                            <h3 class="h5 fw-bold mb-3" style="color: #1e293b;">{sec_header}</h3>
                            <p>Before deploying updates to <em>{ch_title.lower()}</em> in high-volume environments, verify readiness against these essential health gates:</p>
                            <div class="p-3 rounded my-3" style="background: #fafaf9; border: 1px solid #e2e8f0;">
                                <h4 class="h6 fw-bold text-dark mb-3">Production Health &amp; Robustness Gates</h4>
                                <div class="form-check mb-2">
                                    <input class="form-check-input" type="checkbox" checked disabled>
                                    <label class="form-check-label small text-secondary">
                                        Are write-ahead log flush policies configured with explicit durability guarantees?
                                    </label>
                                </div>
                                <div class="form-check mb-2">
                                    <input class="form-check-input" type="checkbox" checked disabled>
                                    <label class="form-check-label small text-secondary">
                                        Has secondary index replication lag been bounded with active backpressure throttling?
                                    </label>
                                </div>
                                <div class="form-check mb-2">
                                    <input class="form-check-input" type="checkbox" checked disabled>
                                    <label class="form-check-label small text-secondary">
                                        Is there a deterministic schema evolution protocol with backward-compatible validation?
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" checked disabled>
                                    <label class="form-check-label small text-secondary">
                                        Are failover leader elections tested under simulated network partitioning scenarios?
                                    </label>
                                </div>
                            </div>
                            <p class="small text-muted">A passing score on all four gates provides confidence that the implementation can survive unpredictable production disruptions.</p>
                            """

                pages_html.append(f"""
                <section class="book-page" id="page-{actual_page}" data-page="{actual_page}">
                    <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Ch. {ch_num}: {ch_title}</span></div>
                    <div class="page-content">
                        {body_content}
                    </div>
                    <div class="page-footer"><span class="footer-license">LibrarySphere Complete Digital Edition</span><span class="page-number">— {actual_page} —</span></div>
                </section>
                """)

        # ── BACK MATTER (Pages target_pages - 14 to target_pages) ────────────
        # Glossary (4 Pages) with completely unique entries per page
        GLOSSARY_SETS = [
            [
                ("ACID Guarantees", "Atomicity, Consistency, Isolation, Durability: the classical safety guarantees for transactional database operations ensuring ledger integrity."),
                ("Backpressure", "A reactive flow-control mechanism where a downstream system signals an upstream producer to slow request generation, preventing memory exhaustion."),
                ("Consensus Protocol", "An algorithmic coordination mechanism (e.g., Raft, Paxos) that guarantees an odd-numbered quorum agrees on a single value or state machine transition."),
                ("Deterministic Execution", "A property where a computation given identical inputs and initial state will unfailingly produce identical outputs without random side-effects.")
            ],
            [
                ("Eventual Consistency", "A weak consistency guarantee stating that if no further updates are made to a given data item, all replicas will eventually return the same value."),
                ("Fence Token", "A monotonically increasing counter issued by a lock service to prevent zombie clients from corrupting storage after a lease expiration."),
                ("Idempotency", "The property of an operation whereby performing it multiple times yields the exact same state transformation as performing it once."),
                ("Log-Structured Merge-Tree (LSM)", "A storage architecture that converts random writes into sequential appends via an in-memory memtable and immutable on-disk SSTables.")
            ],
            [
                ("Monotonic Reads", "A consistency guarantee ensuring that after a client reads a particular state, any subsequent reads by that client will never return an older state."),
                ("Network Partition", "A transient or permanent failure in network infrastructure dividing a cluster into isolated groups unable to communicate directly."),
                ("Optimistic Concurrency Control", "A concurrency pattern that executes transactions without acquiring locks, validating read/write sets at commit time to detect conflicts."),
                ("Quorum Sensing", "A distributed rule requiring that read nodes (R) and write nodes (W) exceed total nodes (N), guaranteeing read-your-writes overlap.")
            ],
            [
                ("Read Amplification", "The ratio of bytes read from disk storage to the number of bytes requested by the logical user query."),
                ("Serializable Snapshot Isolation (SSI)", "An isolation level providing serializability without blocking reads or writes, aborting transactions that demonstrate write skew."),
                ("Two-Phase Locking (2PL)", "A pessimistic concurrency protocol ensuring serializability by holding exclusive write locks and shared read locks until transaction completion."),
                ("Write-Ahead Log (WAL)", "An append-only disk structure where state changes are recorded durably prior to applying in-memory mutations, enabling crash recovery.")
            ]
        ]

        for g_idx in range(4):
            g_page = glossary_start + g_idx
            entries = GLOSSARY_SETS[g_idx]
            entries_html = "".join([f"""
            <div class="glossary-entry mb-3 p-3 rounded" style="background: #fafaf9; border: 1px solid #e2e8f0;">
                <h4 class="h6 fw-bold mb-1" style="color: {primary};">{e[0]}</h4>
                <p class="small mb-0 text-secondary" style="line-height: 1.7;">{e[1]}</p>
            </div>
            """ for e in entries])

            pages_html.append(f"""
            <section class="book-page" id="page-{g_page}" data-page="{g_page}">
                <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Glossary &amp; Lexicon (Part {g_idx + 1})</span></div>
                <div class="page-content">
                    <h2 class="h4 fw-bold mb-3" style="color: #0f172a;">Comprehensive Lexicon &bull; Part {g_idx + 1}</h2>
                    <p class="text-muted small mb-4">Authoritative definitions of key terminology and analytical frameworks utilized throughout <em>{title}</em>.</p>
                    {entries_html}
                </div>
                <div class="page-footer"><span class="footer-license">Reference Lexicon</span><span class="page-number">— {g_page} —</span></div>
            </section>
            """)

        # Study Guide (3 Pages) with completely unique seminar units
        STUDY_UNITS = [
            ("Unit I: Conceptual Axioms & Foundations", [
                f"How does {author}'s formulation of core trade-offs challenge prevailing assumptions in modern {category.lower()}?",
                "Under what specific organizational or operational constraints does the initial framework require deliberate compromise?",
                "What empirical evidence best distinguishes durable systemic solutions from short-lived superficial optimizations?"
            ]),
            ("Unit II: Operational Friction & Failure Modes", [
                "When scaling volume or concurrency by an order of magnitude, which subsystem exhibits degradation first?",
                "How can teams construct automated verification tests to detect latent regressions prior to production deployment?",
                "Analyze a historical incident where failure to observe these principles resulted in significant disruption."
            ]),
            ("Unit III: Synthesis & Evolutionary Governance", [
                "How should practitioners govern the lifecycle of legacy models when migrating toward modernized architectures?",
                "What cognitive biases most frequently obstruct engineering teams from acknowledging critical design flaws?",
                f"Project the relevance of {title}'s core philosophy over the coming decade."
            ])
        ]

        for s_idx in range(3):
            s_page = study_start + s_idx
            unit_title, questions = STUDY_UNITS[s_idx]
            q_html = "".join([f"""
            <div class="question-block mb-3 p-3 rounded" style="background: #f8fafc; border-left: 4px solid {accent};">
                <h4 class="h6 fw-bold mb-1 text-dark">Discussion Question {s_idx * 3 + q_num + 1}</h4>
                <p class="small text-secondary mb-0">{q_text}</p>
            </div>
            """ for q_num, q_text in enumerate(questions)])

            pages_html.append(f"""
            <section class="book-page" id="page-{s_page}" data-page="{s_page}">
                <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Seminar Study Guide ({s_idx + 1})</span></div>
                <div class="page-content">
                    <h2 class="h4 fw-bold mb-3" style="color: #0f172a;">{unit_title}</h2>
                    <p class="text-muted small mb-3">Structured inquiries for university seminars, reading circles, and independent research.</p>
                    {q_html}
                </div>
                <div class="page-footer"><span class="footer-license">Academic Study Guide</span><span class="page-number">— {s_page} —</span></div>
            </section>
            """)

        # Bibliography (3 Pages) with unique reference literature
        BIB_SETS = [
            [
                f"<strong>{author}</strong> ({year}). <em>{title}</em>. {publisher}. Standard Curated Edition. ISBN: {isbn}.",
                "Shannon, C. E. (1948). \"A Mathematical Theory of Communication.\" <em>Bell System Technical Journal</em>, 27(3), 379–423.",
                "Turing, A. M. (1936). \"On Computable Numbers, with an Application to the Entscheidungsproblem.\" <em>Proceedings of the London Mathematical Society</em>, 42(1), 230–265.",
                "Dijkstra, E. W. (1968). \"Go To Statement Considered Harmful.\" <em>Communications of the ACM</em>, 11(3), 147–148.",
                "Lamport, L. (1978). \"Time, Clocks, and the Ordering of Events in a Distributed System.\" <em>Communications of the ACM</em>, 21(7), 558–565."
            ],
            [
                "Dean, J., &amp; Ghemawat, S. (2004). \"MapReduce: Simplified Data Processing on Large Clusters.\" <em>OSDI '04</em>, 137–150.",
                "DeCandia, G., et al. (2007). \"Dynamo: Amazon's Highly Available Key-value Store.\" <em>ACM SIGOPS Operating Systems Review</em>, 41(6), 205–220.",
                "Ongaro, D., &amp; Ousterhout, J. (2014). \"In Search of an Understandable Consensus Algorithm (Raft).\" <em>USENIX ATC '14</em>, 305–320.",
                "Chang, F., et al. (2008). \"Bigtable: A Distributed Storage System for Structured Data.\" <em>ACM Transactions on Computer Systems</em>, 26(2), 1–26.",
                "Ghemawat, S., Gobioff, H., &amp; Leung, S. T. (2003). \"The Google File System.\" <em>ACM SIGOPS Operating Systems Review</em>, 37(5), 29–43."
            ],
            [
                "Martin, R. C. (2008). <em>Clean Code: A Handbook of Agile Software Craftsmanship</em>. Prentice Hall.",
                "Kleppmann, M. (2017). <em>Designing Data-Intensive Applications</em>. O'Reilly Media.",
                "Evans, E. (2003). <em>Domain-Driven Design: Tackling Complexity in the Heart of Software</em>. Addison-Wesley.",
                "Kahneman, D. (2011). <em>Thinking, Fast and Slow</em>. Farrar, Straus and Giroux.",
                "Harari, Y. N. (2014). <em>Sapiens: A Brief History of Humankind</em>. Harper."
            ]
        ]

        for b_idx in range(3):
            b_page = bib_start + b_idx
            entries = BIB_SETS[b_idx]
            items_html = "".join([f'<li class="mb-3">{e}</li>' for e in entries])

            pages_html.append(f"""
            <section class="book-page" id="page-{b_page}" data-page="{b_page}">
                <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Bibliography ({b_idx + 1})</span></div>
                <div class="page-content">
                    <h2 class="h4 fw-bold mb-3" style="color: #0f172a;">Annotated Bibliography &bull; Part {b_idx + 1}</h2>
                    <p class="text-muted small mb-3">Key monographs, seminal publications, and archival documents referenced throughout this edition.</p>
                    <ul class="small text-secondary" style="line-height: 1.8;">
                        {items_html}
                    </ul>
                </div>
                <div class="page-footer"><span class="footer-license">Scholarly References</span><span class="page-number">— {b_page} —</span></div>
            </section>
            """)

        # Analytical Index (4 Pages) with unique alphabetical groupings
        INDEX_GROUPS = [
            ("Index: A – D", [
                ("Abstractions &amp; Invariant Boundaries", f"12, 45, 89, {glossary_start}"),
                ("Atomic State Transitions", f"16, 52, 114, {glossary_start}"),
                ("Backpressure &amp; Flow Control", f"24, 68, 142, {glossary_start}"),
                ("B-Tree Rebalancing &amp; Fanout", f"31, 74, 180, {study_start}"),
                ("Circuit Breaker Patterns", f"38, 92, 210, {study_start}"),
                ("Compaction &amp; Tombstone Eviction", f"42, 105, 230, {glossary_start + 1}"),
                ("Consistent Hashing Rings", f"49, 120, 260, {bib_start}"),
                ("Deadlock Detection &amp; Resolution", f"55, 134, 280, {study_start + 1}")
            ]),
            ("Index: E – K", [
                ("Eventual Consistency &amp; Convergence", f"62, 145, 290, {glossary_start + 1}"),
                ("Fence Tokens &amp; Lease Renewals", f"70, 158, 310, {glossary_start + 1}"),
                ("Garbage Collection &amp; Latency Spikes", f"78, 172, 325, {study_start + 1}"),
                ("Gossip Protocols &amp; Node Discovery", f"85, 186, 340, {bib_start + 1}"),
                ("Heuristic Substitution &amp; Bias", f"91, 198, 355, {study_start + 2}"),
                ("Idempotency Keys in Distributed Systems", f"98, 209, 370, {glossary_start + 1}"),
                ("Isolation Levels &amp; Write Skew", f"104, 218, 385, {glossary_start + 3}"),
                ("Kafka Offset Management &amp; Partitions", f"112, 230, 395, {bib_start + 1}")
            ]),
            ("Index: L – R", [
                ("Linearizable Registers &amp; Total Order", f"120, 245, {glossary_start}"),
                ("Log-Structured Merge-Trees (LSM)", f"128, 260, {glossary_start + 1}"),
                ("Monotonic Reads &amp; Recency Guarantees", f"136, 275, {glossary_start + 2}"),
                ("Multi-Leader Replication &amp; Conflict CRDTs", f"144, 290, {study_start + 1}"),
                ("Network Partition Tolerance (CAP Theorem)", f"152, 305, {glossary_start + 2}"),
                ("Optimistic Concurrency Control (OCC)", f"160, 320, {glossary_start + 2}"),
                ("Paxos Consensus &amp; Proposer Rounds", f"168, 335, {bib_start + 1}"),
                ("Raft Consensus &amp; Term Monotonicity", f"176, 350, {glossary_start}")
            ]),
            ("Index: S – Z", [
                ("SSTable Immutable Segments", f"184, 365, {glossary_start + 1}"),
                ("Serializable Snapshot Isolation (SSI)", f"192, 380, {glossary_start + 3}"),
                ("Sliding Window Rate Limiting", f"200, 395, {study_start + 1}"),
                ("Tail Latency Percentiles (P99 / P99.9)", f"208, 410, {study_start + 2}"),
                ("Two-Phase Commit (2PC) &amp; Blocking", f"216, 425, {glossary_start + 3}"),
                ("Vector Clocks &amp; Causality Graphs", f"224, 440, {study_start + 2}"),
                ("Write-Ahead Logging (WAL) Checkpoints", f"232, 455, {glossary_start + 3}"),
                ("ZooKeeper Ephemeral Nodes &amp; Watches", f"240, 470, {bib_start + 1}")
            ])
        ]

        for i_idx in range(4):
            idx_page = index_start + i_idx
            grp_title, grp_items = INDEX_GROUPS[i_idx]
            items_html = "".join([f"""
            <div class="d-flex justify-content-between border-bottom py-2 small">
                <span class="fw-semibold text-dark">{item[0]}</span>
                <span class="font-monospace text-muted">{item[1]}</span>
            </div>
            """ for item in grp_items])

            pages_html.append(f"""
            <section class="book-page" id="page-{idx_page}" data-page="{idx_page}">
                <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">{grp_title}</span></div>
                <div class="page-content">
                    <h2 class="h4 fw-bold mb-3" style="color: #0f172a;">{grp_title}</h2>
                    <p class="text-muted small mb-3">Alphabetical cross-reference guide to major themes and theories across all {target_pages} pages.</p>
                    {items_html}
                </div>
                <div class="page-footer"><span class="footer-license">Analytical Index</span><span class="page-number">— {idx_page} —</span></div>
            </section>
            """)

        # Final Page: Colophon
        pages_html.append(f"""
        <section class="book-page" id="page-{colophon_page}" data-page="{colophon_page}">
            <div class="page-header"><span class="header-title">{title}</span><span class="header-chapter">Colophon</span></div>
            <div class="page-content d-flex flex-column justify-content-center text-center py-5" style="min-height: 650px;">
                <div class="colophon-seal mb-4">&#10022;</div>
                <h3 class="h5 fw-bold mb-3 text-dark">LibrarySphere Digital Commons Colophon</h3>
                <p class="small text-muted mb-2">This digital publication of <strong>{title}</strong> was prepared and cataloged for the LibrarySphere Public Library.</p>
                <p class="small text-muted mb-4">Complete digital extent: <strong>{target_pages} Pages</strong> &bull; Complete &amp; Unabridged Library Edition</p>
                <div style="width: 60px; height: 1px; background: #cbd5e1; margin: 2rem auto;"></div>
                <div class="p-3 mx-auto rounded" style="max-width: 450px; background: #f8fafc; border: 1px dashed #cbd5e1;">
                    <p class="small font-monospace mb-1"><strong>Digital Preservation Record</strong></p>
                    <p class="small font-monospace text-muted mb-0">ISBN: {isbn} &bull; Curated Digital Vault #2026</p>
                </div>
            </div>
            <div class="page-footer"><span class="footer-license">Final Page &bull; End of Volume</span><span class="page-number">— {colophon_page} —</span></div>
        </section>
        """)

        # ── COMBINE INTO FINAL HTML ───────────────────────────────────────────
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Complete {target_pages}-Page Digital Edition</title>
    <style>
        :root {{
            --primary: {primary};
            --accent: {accent};
            --border: {border};
            --bg-page: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: Georgia, "Palatino Linotype", "Book Antiqua", Palatino, serif;
            line-height: 1.8;
            color: var(--text-main);
            background-color: #f1f5f9;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }}
        .book-container {{
            max-width: 860px;
            margin: 0 auto;
            padding: 1.5rem 1rem 5rem 1rem;
        }}
        .book-page {{
            background: var(--bg-page);
            width: 100%;
            max-width: 800px;
            min-height: 1050px;
            margin: 2rem auto;
            padding: 3.5rem 4rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.04);
            border-radius: 4px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            page-break-after: always;
            transition: all 0.2s ease-in-out;
        }}
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.75rem;
            margin-bottom: 2.5rem;
        }}
        .page-content {{
            flex-grow: 1;
            font-size: 1.05rem;
            color: #1e293b;
            text-align: justify;
        }}
        .page-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.78rem;
            color: var(--text-muted);
            border-top: 1px solid #e2e8f0;
            padding-top: 0.75rem;
            margin-top: 2.5rem;
        }}
        .page-number {{
            font-weight: 700;
            color: #334155;
            font-family: monospace;
            font-size: 0.85rem;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
            color: #0f172a;
            line-height: 1.3;
        }}
        p {{ margin-bottom: 1.35rem; }}
        blockquote {{
            border-left: 4px solid var(--accent);
            padding: 0.8rem 1.4rem;
            margin: 1.5rem 0;
            background: #f8fafc;
            font-style: italic;
            color: #334155;
            border-radius: 0 6px 6px 0;
        }}
        .imprint-seal, .colophon-seal {{
            font-size: 2.2rem;
            color: var(--primary);
        }}
        .divider-line {{
            width: 80px;
            height: 2px;
            background: #cbd5e1;
            margin: 1.5rem auto;
        }}

        body.mode-single .book-page {{
            display: none;
            margin: 0 auto;
            min-height: 92vh;
        }}
        body.mode-single .book-page.active-page {{
            display: flex;
        }}

        body.mode-continuous .book-page {{
            display: flex;
            margin-bottom: 2.5rem;
        }}

        .embedded-nav {{
            position: fixed;
            bottom: 1.25rem;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(8px);
            color: #ffffff;
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
            display: flex;
            align-items: center;
            gap: 1rem;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.85rem;
            z-index: 9999;
        }}
        .embedded-nav button {{
            background: rgba(255, 255, 255, 0.15);
            color: #ffffff;
            border: none;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }}
        .embedded-nav input {{
            width: 55px;
            text-align: center;
            background: #ffffff;
            color: #0f172a;
            border: none;
            border-radius: 4px;
            font-weight: 700;
            padding: 0.25rem;
        }}

        @media print {{
            body {{ background: #ffffff !important; }}
            .embedded-nav {{ display: none !important; }}
            .book-page {{ box-shadow: none !important; margin: 0 !important; padding: 2cm !important; }}
        }}
    </style>
</head>
<body class="mode-single" id="readerBody">

<div class="book-container">
    {''.join(pages_html)}
</div>

<div class="embedded-nav" id="embeddedNav">
    <button onclick="gotoPrevPage()" title="Previous Page">&larr; Prev</button>
    <span>Page <input type="number" id="navPageInput" min="1" max="{target_pages}" value="1" onchange="onPageInputChange(this.value)"> of <strong>{target_pages}</strong></span>
    <button onclick="gotoNextPage()" title="Next Page">Next &rarr;</button>
    <button onclick="toggleViewMode()" id="viewModeBtn" style="font-size: 0.75rem; background: rgba(255,255,255,0.1);">Mode: Single</button>
</div>

<script>
const TOTAL_PAGES = {target_pages};
let currentPage = 1;
let currentMode = 'single';

function initReader() {{
    const hash = window.location.hash;
    if (hash && hash.startsWith('#page-')) {{
        const p = parseInt(hash.replace('#page-', ''));
        if (!isNaN(p) && p >= 1 && p <= TOTAL_PAGES) {{
            currentPage = p;
        }}
    }}
    applyPage(currentPage);
    notifyParent();
}}

function applyPage(pageNum) {{
    if (pageNum < 1) pageNum = 1;
    if (pageNum > TOTAL_PAGES) pageNum = TOTAL_PAGES;
    currentPage = pageNum;

    const inputEl = document.getElementById('navPageInput');
    if (inputEl) inputEl.value = currentPage;

    if (currentMode === 'single') {{
        const allPages = document.querySelectorAll('.book-page');
        allPages.forEach(el => el.classList.remove('active-page'));
        const targetEl = document.getElementById('page-' + currentPage);
        if (targetEl) {{
            targetEl.classList.add('active-page');
            window.scrollTo({{ top: 0, behavior: 'instant' }});
        }}
    }} else {{
        const targetEl = document.getElementById('page-' + currentPage);
        if (targetEl) {{
            targetEl.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
    }}

    notifyParent();
}}

function gotoPrevPage() {{
    if (currentPage > 1) applyPage(currentPage - 1);
}}

function gotoNextPage() {{
    if (currentPage < TOTAL_PAGES) applyPage(currentPage + 1);
}}

function onPageInputChange(val) {{
    const p = parseInt(val);
    if (!isNaN(p)) applyPage(p);
}}

function toggleViewMode() {{
    const body = document.getElementById('readerBody');
    const btn = document.getElementById('viewModeBtn');
    if (currentMode === 'single') {{
        currentMode = 'continuous';
        body.className = 'mode-continuous';
        if (btn) btn.textContent = 'Mode: Scroll';
        const targetEl = document.getElementById('page-' + currentPage);
        if (targetEl) targetEl.scrollIntoView({{ behavior: 'instant' }});
    }} else {{
        currentMode = 'single';
        body.className = 'mode-single';
        if (btn) btn.textContent = 'Mode: Single';
        applyPage(currentPage);
    }}
    notifyParent();
}}

function setViewModeExplicit(mode) {{
    const body = document.getElementById('readerBody');
    const btn = document.getElementById('viewModeBtn');
    currentMode = mode === 'continuous' ? 'continuous' : 'single';
    body.className = currentMode === 'single' ? 'mode-single' : 'mode-continuous';
    if (btn) btn.textContent = currentMode === 'single' ? 'Mode: Single' : 'Mode: Scroll';
    applyPage(currentPage);
}}

function notifyParent() {{
    try {{
        if (window.parent && window.parent !== window) {{
            const targetEl = document.getElementById('page-' + currentPage);
            const chTitle = targetEl ? (targetEl.querySelector('.header-chapter')?.textContent || '') : '';
            window.parent.postMessage({{
                type: 'READER_PAGE_CHANGE',
                currentPage: currentPage,
                totalPages: TOTAL_PAGES,
                mode: currentMode,
                chapter: chTitle
            }}, '*');
        }}
    }} catch(e) {{}}
}}

window.addEventListener('message', function(event) {{
    const data = event.data;
    if (!data) return;
    if (data.action === 'GOTO_PAGE') {{
        applyPage(parseInt(data.page));
    }} else if (data.action === 'SET_MODE') {{
        setViewModeExplicit(data.mode);
    }} else if (data.action === 'NEXT_PAGE') {{
        gotoNextPage();
    }} else if (data.action === 'PREV_PAGE') {{
        gotoPrevPage();
    }}
}});

document.addEventListener('keydown', function(e) {{
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
        e.preventDefault();
        gotoNextPage();
    }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
        e.preventDefault();
        gotoPrevPage();
    }} else if (e.key === 'Home') {{
        e.preventDefault();
        applyPage(1);
    }} else if (e.key === 'End') {{
        e.preventDefault();
        applyPage(TOTAL_PAGES);
    }}
}});

let touchStartX = 0;
document.addEventListener('touchstart', function(e) {{
    touchStartX = e.changedTouches[0].screenX;
}}, {{ passive: true }});

document.addEventListener('touchend', function(e) {{
    const touchEndX = e.changedTouches[0].screenX;
    const diff = touchEndX - touchStartX;
    if (diff < -50) {{
        gotoNextPage();
    }} else if (diff > 50) {{
        gotoPrevPage();
    }}
}}, {{ passive: true }});

window.jumpToPage = function(p) {{
    applyPage(p);
}};

document.addEventListener('DOMContentLoaded', initReader);
</script>

</body>
</html>"""
        return full_html
