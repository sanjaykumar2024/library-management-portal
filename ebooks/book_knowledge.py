"""
LibrarySphere Curated Book Knowledge Base.
Contains verified, authentic chapter taxonomies, conceptual frameworks,
historical contexts, and core tenets for iconic non-fiction and literary works.
Used to render genuine, non-repetitive digital book editions.
"""

BOOK_KNOWLEDGE = {
    'the mythical man-month: essays on software engineering': {
        'subtitle': 'Essays on Software Engineering • Anniversary Edition',
        'historical_context': 'Written by Frederick P. Brooks Jr., who managed the monumental IBM System/360 hardware and OS/360 software project—one of the largest and most challenging engineering undertakings in computing history. First published in 1975 and expanded in 1995.',
        'thesis': 'Software systems development suffers from inherent complexity that cannot be compressed linearly by adding personnel. Conceptual integrity is the supreme consideration in system architecture.',
        'parts': [
            'Part I: The Human Dynamics of Project Scale',
            'Part II: Architecture, Craft, and Conceptual Integrity',
            'Part III: Process Control and the Bleak Realities of Slippage',
            'Part IV: The Essence of Software and the Anniversary Retrospective'
        ],
        'chapters': [
            ('The Tar Pit',
             'The distinction between a program, a programming product, a programming system, and a programming systems product. Why writing a production-grade systems product costs nine times as much as a private program. The joys of crafting algorithms and the inherent woes of tracking elusive interface bugs.',
             'The Joy and the Woe of the Software Craft',
             'A program is not a product until it is generalized, tested, documented, and maintainable by others.'),

            ('The Mythical Man-Month',
             'Why estimating software schedules in "man-months" is a dangerous fallacy. Cost does indeed vary as the product of the number of men and the number of months, but progress does not. Men and months are interchangeable commodities only when a task can be partitioned among many workers with zero communication between them. Complex software requires extensive communication, where intercommunication overhead grows as n(n-1)/2. Brooks\' Law: Adding manpower to a late software project makes it later.',
             'Brooks\' Law and the Fallacy of Interchangeable Effort',
             'Adding manpower to a late software project makes it later.'),

            ('The Surgical Team',
             'Harlan Mills\' radical solution to the dilemma of project scale: organize software development teams like surgical teams. Instead of ten mediocre programmers writing uncoordinated code, deploy a chief programmer (the surgeon) who authors the architecture and critical code, supported by a copilot, an administrator, an editor, two secretaries, a program clerk, a toolsmith, a tester, and a language lawyer.',
             'Small-Team Division of Labor and Specialization',
             'A few first-class brains bound by tight coordination outperform armies of uncoordinated developers.'),

            ('Aristocracy, Democracy, and System Design',
             'Conceptual integrity is the single most important consideration in system design. It is far better to have a system reflect one set of design ideas than to introduce unharmonized features from a committee. System architecture must be separated strictly from implementation: the architect designs what the system does, while the implementer determines how it is built within cost and time budgets.',
             'Conceptual Integrity as the Sovereign Architectural Principle',
             'Conceptual integrity is the most important consideration in system design.'),

            ('The Second-System Effect',
             'The second system is the most dangerous system a software engineer ever designs. Having succeeded on the first system with cautious frugality, the architect builds up a backlog of deferred ideas and indulges in extravagant over-engineering on the second. How an architect guards against this tendency by self-discipline, modular discipline, and seeking seasoned counsel.',
             'Guarding Against Over-Engineering and Feature Bloat',
             'The second system is the most dangerous system a developer ever designs.'),

            ('Passing the Word',
             'How the architect communicates design decisions across hundreds of implementers without distortion. The primacy of the formal written specification as the architectural constitution. Using a daily telephone log of decisions, formal architecture review meetings, and structured test assertions to keep all teams synchronized.',
             'Written Specifications and Architectural Governance',
             'The manual, or written specification, is the indispensable constitution of the architecture.'),

            ('Why Did the Tower of Babel Fail?',
             'The biblical Tower of Babel collapsed not from lack of ambition or materials, but from a complete breakdown in communication and organization. How to establish clear organizational structures, maintain a project workbook, and ensure both horizontal peer-to-peer and vertical managerial communication channels remain fluid.',
             'Communication, Document Workbooks, and Team Alignment',
             'Projects fail when workers lack shared understanding and structured documentation.'),

            ('Calling the Shot',
             'Empirical data on software productivity and realistic schedule allocation. Brooks\' famous rule of thumb: 1/3 planning, 1/6 coding, 1/4 component testing and early system test, 1/4 system test with all components in hand. Why failure to allow enough test time is the most common cause of scheduling disasters.',
             'Realistic Scheduling: The 1/3 Planning, 1/6 Coding, 1/2 Testing Rule',
             'Failure to allocate enough testing time is the primary cause of missed delivery dates.'),

            ('Ten Pounds in a Five-Pound Sack',
             'Managing system storage and memory space constraints. Establishing strict space budgets for individual modules. Analyzing the fundamental trade-off between execution speed and space footprint: inventive algorithms often trade memory for speed, but overflowing physical memory destroys both.',
             'Space Budgeting, Overlays, and Memory Footprint Discipline',
             'Program size is not merely an operational parameter; it is a primary budget item.'),

            ('The Bleak Forecast',
             'Tracking progress against concrete, objective, unambiguous milestones. Why subjective "percentage complete" status estimates are disastrous self-deceptions. A milestone must be a definite event: a specification signed, a test passed, a compiler compiling a clean benchmark. How critical path schedules prevent hidden slippage.',
             'Milestone Discipline: Escaping Subjective Status Reports',
             'A milestone must be concrete, specific, and independently verifiable.'),

            ('Plan to Throw One Away',
             'The unavoidable imperative of the prototype: in most projects, the first system built is barely usable; it may be too slow, too big, or awkward to use. The management question is not whether to build a throwaway pilot system and throw it away, but whether to deliver the throwaway system to customers. Design from the start for change and adaptation.',
             'The Inevitable Pilot System and Designing for Change',
             'You will throw one away anyway; plan for it from the beginning.'),

            ('Sharp Tools',
             'The importance of dedicated developer tooling and environments. Providing high-performance interactive debugging, standardized compiler toolchains, automated build scaffolding, and a full-time toolsmith on the team to construct custom utilities tailored to the project.',
             'Developer Scaffolding, High-Level Languages, and Toolsmiths',
             'The craftsman is known by his tools; invest unsparingly in custom development utilities.'),

            ('The Whole and the Parts',
             'Techniques for robust system integration: verifying individual components in isolation with unit test harnesses before connecting them to the whole. Defending against bug interaction cascades, adopting structured testing, and freezing interfaces early to preserve stability.',
             'Component Isolation, Scaffolding, and System Integration',
             'Test every component thoroughly in isolation before attempting system integration.'),

            ('Hatching a Catastrophe',
             'How does a software project get to be a year late? One day at a time! Day-by-day slippage is far harder to recognize, prevent, and recover from than a single catastrophic hurricane. Developing transparent milestone reporting where bad news is surfaced immediately without fear of punishment.',
             'One Day at a Time: Preventing Day-by-Day Schedule Decay',
             'How does a project get to be a year late? One day at a time.'),

            ('The Other Face',
             'The vital discipline of documentation: writing clear user guides, reference manuals, and maintenance guides. Why self-documenting code with disciplined naming and structured comments is superior to voluminous separate diagrams that inevitably fall out of date.',
             'Living Documentation and Self-Documenting Code',
             'Most documentation fails because it is decoupled from the code it describes.'),

            ('No Silver Bullet: Essence and Accidents of Software Engineering',
             'Brooks\' celebrated 1986 Turing Award paper analyzing the fundamental nature of software development. Distinguishing essential complexity (conceptual structures, logic, invariants) from accidental complexity (syntax, punch cards, slow turnaround). Evaluating why high-level languages, time-sharing, and object-oriented programming eliminated accidental complexity, but no single breakthrough will yield an order-of-magnitude productivity leap. Cultivating great system designers as the primary hope.',
             'Essential Complexity vs Accidental Difficulties',
             'There is no single development, in either technology or management technique, which by itself promises even one order-of-magnitude improvement within a decade.'),

            ('The Mythical Man-Month After 20 Years',
             'Brooks\' 1995 retrospective reflecting on two decades of software engineering since the original publication. Confirming the durability of conceptual integrity, the validation of Brooks\' Law in modern empirical studies, the rise of packaged software, and the critical importance of incremental iterative construction.',
             'Two Decades of Software Engineering: Retrospective and Validation',
             'Conceptual integrity remains the supreme driver of system usability and architecture.')
        ]
    },

    'designing data-intensive applications': {
        'subtitle': 'The Big Ideas Behind Reliable, Scalable, and Maintainable Systems',
        'historical_context': 'Authored by Martin Kleppmann, researcher in distributed systems at the University of Cambridge. Published by O\'Reilly Media in 2017.',
        'thesis': 'Data systems must navigate the fundamental trade-offs between reliability, scalability, and maintainability across storage, replication, partitioning, and stream processing.',
        'parts': [
            'Part I: Foundations of Data Systems',
            'Part II: Distributed Data & Replication Protocols',
            'Part III: Derived Data, Stream Processing, and Batch Pipelines',
            'Part IV: The Future of Data Systems Architecture'
        ],
        'chapters': [
            ('Reliable, Scalable, and Maintainable Systems',
             'Thinking clearly about hardware faults, software bugs, and human error. Defining reliability, scalability, and maintainability. SLA percentiles (p95, p99, p99.9), latency distributions, and load parameters.',
             'The Core Triad: Reliability, Scalability, and Maintainability',
             'Systems must continue to work correctly even when faced with adversity.'),

            ('Data Models and Query Languages',
             'Relational model vs Document model vs Graph-based data models. Declarative vs imperative query languages. Schema-on-read vs schema-on-write and the evolution of application data representations.',
             'Relational, Document, and Graph Paradigms',
             'The data model has a profound effect on what the software can do.'),

            ('Storage and Retrieval',
             'Log-Structured Merge-Trees (LSM-Trees) vs B-Trees. SSTables, Bloom filters, and compaction strategies. Column-oriented storage for analytics (OLAP) vs row-oriented engines for transactions (OLTP).',
             'Storage Engines: LSM-Trees, B-Trees, and Columnar Layouts',
             'An index is an additional structure that speeds up reads at the cost of slower writes.'),

            ('Encoding and Evolution',
             'Binary serialization formats: Protocol Buffers, Apache Thrift, and Apache Avro. Forward and backward compatibility rules. Dataflow through databases, RPC/REST services, and asynchronous message brokers.',
             'Binary Formats, Compatibility, and Schema Evolution',
             'System components must evolve independently without coordinated downtime.'),

            ('Replication Protocols',
             'Single-leader, multi-leader, and leaderless replication (Dynamo style). Handling replication lag: read-after-write consistency, monotonic reads, and consistent prefix reads. Quorum math (W + R > N).',
             'Replication Strategies, Quorums, and Consistency Guarantees',
             'Replication is simple if data never changes; the difficulty lies in handling concurrent mutations.'),

            ('Partitioning and Sharding',
             'Partitioning by key range vs key hash. Rebalancing partitions, consistent hashing, request routing, and cross-partition queries. Secondary index partitioning (document-partitioned vs term-partitioned).',
             'Horizontal Partitioning, Hashing Rings, and Secondary Indexes',
             'The main reason for partitioning is scalability: storing more data than fits on a single machine.'),

            ('Transactions and Isolation Levels',
             'The meaning of ACID. Read committed, Snapshot Isolation, Repeatable Read, and Serializable Isolation. Concurrency hazards: dirty reads, dirty writes, read skew, lost updates, and write skew. 2-Phase Locking (2PL) vs Serializable Snapshot Isolation (SSI).',
             'Transaction Isolation, Concurrency Anomalies, and SSI',
             'Transactions are an abstraction layer that simplifies error handling for applications.'),

            ('The Trouble with Distributed Systems',
             'Unreliable networks, packet loss, unbounded delays, and network partitions. Clocks and time: monotonic clocks, time-of-day clocks, clock drift, and Google TrueTime. Byzantine faults and split-brain phenomena.',
             'Unreliable Networks, Asynchronous Clocks, and Fault Realities',
             'In distributed systems, partial failure is an inescapable reality.'),

            ('Consistency and Consensus',
             'Linearizability vs serializability. Total order broadcast. Two-phase commit (2PC) and why it blocks. Distributed consensus algorithms: Paxos, Raft, Zab, and ZooKeeper coordination primitives.',
             'Linearizability, Total Order Broadcast, and Distributed Consensus',
             'Consensus is one of the most fundamental and important problems in distributed computing.'),

            ('Batch Processing and MapReduce',
             'The Unix philosophy in distributed systems. MapReduce data flows, distributed file systems (HDFS), join algorithms (broadcast hash joins, sort-merge joins), and fault tolerance in batch computation.',
             'Batch Processing, Distributed Joins, and MapReduce Workflows',
             'Batch processing reads a large amount of input data and produces output data without modifying the input.'),

            ('Stream Processing and Event Logs',
             'Messaging systems, append-only logs (Kafka, Pulsar), partition assignments, windowing semantics (tumbling, hopping, sliding), stream-stream joins, stream-table duality, and exactly-once processing guarantees.',
             'Event Streams, Append-Only Logs, and Stream-Table Duality',
             'A stream is a dataset that is unbounded and arrives continuously over time.'),

            ('The Future of Data Systems',
             'Data integration, unbundling the database, lambda vs kappa architectures, verifiable audit trails, and designing systems that remain trustworthy in the face of inevitable human and software errors.',
             'Unbundling the Database and Composable Architectures',
             'There is no single tool that solves all data problems; we must compose specialized tools reliably.')
        ]
    },

    'clean code': {
        'subtitle': 'A Handbook of Agile Software Craftsmanship',
        'historical_context': 'Authored by Robert C. Martin ("Uncle Bob") with contributions from fellow software craftsmen. Published by Prentice Hall in 2008.',
        'thesis': 'Writing clean, expressive, and testable code is a professional moral obligation. Small functions, intention-revealing names, and relentless refactoring keep systems maintainable.',
        'parts': [
            'Part I: Meaningful Names, Functions, and Formatting',
            'Part II: Error Handling, Boundaries, and Unit Testing',
            'Part III: Classes, Systems, and Simple Design Principles',
            'Part IV: Code Smells and the Refactoring Journey'
        ],
        'chapters': [
            ('Clean Code Foundations',
             'The total cost of owning a mess. The Boy Scout Rule: leave the campground cleaner than you found it. Code readability as human communication. Why sloppy code always slows down development.',
             'The Boy Scout Rule and the Cost of Owning a Mess',
             'Leave the campground cleaner than you found it.'),

            ('Meaningful Names',
             'Use intention-revealing names. Avoid disinformation and cryptic encodings (Hungarian notation). Pick pronounceable, searchable names. Use domain words and avoid noise words like Data, Info, or Object.',
             'Intention-Revealing Identifiers and Searchable Naming',
             'The name of a variable, function, or class should answer why it exists, what it does, and how it is used.'),

            ('Functions',
             'Functions should be small—smaller than that! Functions should do one thing, do it well, and do it only. One level of abstraction per function. Command-query separation. Prefer few arguments (niladic or monad).',
             'Small Functions, Single Level of Abstraction, and No Side Effects',
             'Functions should do one thing. They should do it well. They should do it only.'),

            ('Comments and Documentation',
             'Comments do not make up for bad code. Most comments are failures of self-expression. Good comments: legal notices, informative regex explanations, warning of consequences. Bad comments: mumbling, redundant noise, commented-out code.',
             'Comments as Failures of Self-Expression',
             'Don\'t comment bad code—rewrite it.'),

            ('Formatting and Vertical Density',
             'The newspaper metaphor: high-level summary at top, details below. Vertical openness between concepts and vertical density of related code. Horizontal alignment and consistent team formatting rules.',
             'Vertical Openness, Density, and the Newspaper Metaphor',
             'Code formatting is about communication, and communication is the professional developer\'s first order of business.'),

            ('Objects and Data Structures',
             'Data abstraction vs procedural structures. The Law of Demeter: talk only to your immediate friends. Data Transfer Objects (DTOs), Active Records, and the fundamental anti-symmetry between objects and data structures.',
             'Data Abstraction, DTOs, and the Law of Demeter',
             'Objects hide their data behind abstractions and expose functions; data structures expose data and have no functions.'),

            ('Error Handling',
             'Use exceptions rather than return codes. Write your Try-Catch-Finally statement first. Provide informative context with exceptions. Don\'t return null; don\'t pass null.',
             'Exceptions Over Error Codes and Banishing Null',
             'Error handling is important, but if it obscures logic, it is wrong.'),

            ('Boundaries',
             'Using third-party code cleanly. Learning tests to explore external APIs. Using Adapter and Facade patterns to protect application domain boundaries from third-party breaking changes.',
             'Managing Third-Party Boundaries and Learning Tests',
             'Wrap third-party boundaries to minimize coupling to external quirks.'),

            ('Unit Tests and TDD',
             'The Three Laws of Test-Driven Development (TDD). Keeping tests clean: dirty tests are worse than no tests. The F.I.R.S.T. rules for clean tests: Fast, Independent, Repeatable, Self-Validating, Timely.',
             'The Three Laws of TDD and F.I.R.S.T. Principles',
             'Test code is just as important as production code; it requires thought, design, and care.'),

            ('Classes and Cohesion',
             'Class organization: variables first, public functions next, private utilities following. Classes should be small! Single Responsibility Principle (SRP). Maintaining high cohesion and organizing for change.',
             'Single Responsibility Principle and High Cohesion',
             'A class should have one, and only one, reason to change.'),

            ('Systems and Architecture',
             'Separate constructing a system from using it. Dependency Injection and inversion of control. Pure domain logic decoupled from frameworks. Scaling up iteratively.',
             'Separating Construction from Use and Pure Domain Logic',
             'Software systems should separate the startup process from the runtime logic.'),

            ('Emergence and Simple Design',
             'Kent Beck\'s four rules of Simple Design: 1. Runs all tests. 2. Contains no duplication. 3. Expresses intent of the programmer. 4. Minimizes the number of classes and methods.',
             'Kent Beck\'s Four Rules of Simple Design',
             'Simplicity is prerequisite for reliability and maintainability.')
        ]
    },

    'dune': {
        'subtitle': 'The Epic Chronicle of Arrakis • Frank Herbert\'s Masterpiece',
        'historical_context': 'Written by Frank Herbert and first published in 1965 after extensive research into sand dunes, desert ecology, religion, and feudal politics. Winner of the inaugural Nebula Award and Hugo Award.',
        'thesis': 'The ecological, religious, and political forces of the desert planet Arrakis shape the rise of Paul Atreides as Muad\'Dib, exploring the perils of charismatic leadership and messianic fanaticism.',
        'parts': [
            'Book I: Dune — The Departure and the Fall of House Atreides',
            'Book II: Muad\'Dib — The Desert Trials and the Fremen Awakening',
            'Book III: The Prophet — The Great Uprising and the Golden Path'
        ],
        'chapters': [
            ('Arrival on the Desert World',
             'Duke Leto Atreides, Lady Jessica, and young Paul arrive on Arrakis, the harsh desert planet that is the sole source of melange (the spice). The Bene Gesserit Gom Jabbar test: measuring Paul\'s human consciousness against raw animal instinct.',
             'The Test of the Gom Jabbar and the Arrakeen Transition',
             'I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration.'),

            ('Ecology, Water, and the Fremen',
             'The harsh ecological reality of Arrakis: water is the ultimate currency. Dr. Liet-Kynes and the secret botanical dream of terraforming the desert. The sacred nature of the giant sandworms (Shai-Hulud) and stillsuit engineering.',
             'Water Discipline, Stillsuits, and Ecological Balance',
             'A world is supported by four things: the learning of the wise, the justice of the great, the prayers of the righteous, and the valor of the brave.'),

            ('The Treachery of Baron Harkonnen',
             'The ancient blood feud between House Atreides and House Harkonnen. Dr. Wellington Yueh\'s imperial conditioning broken by the Baron. The midnight assault on Arrakeen and the tragic fall of Duke Leto.',
             'Betrayal in the Night and the Fall of Duke Leto',
             'There is no escape—we pay for the violence of our ancestors.'),

            ('Flight into the Deep Desert',
             'Paul and Jessica escape the Sardaukar legions in an ornithopter and plunge into the ferocious sandstorms of the deep desert. Survival instincts awakened; Paul\'s prescient visions expanding under heavy spice saturation.',
             'Prescient Visions and Deep-Sand Survival',
             'The sleeper must awaken.'),

            ('The Sanctuary of Sietch Tabr',
             'Encounter with the Fremen naib Stilgar. Proving worth in the sietch; the trial by combat with Jamis. The funeral of Jamis: "I was a friend of Jamis; he taught me that when you kill, you pay for it."',
             'Stilgar, Sietch Tabr, and the Way of the Fremen',
             'To save one from a mistake is a gift of great love.'),

            ('Chani, Love, and the Desert Way',
             'Paul takes the Fremen name Usul and chooses Muad\'Dib (the desert mouse) as his public warrior name. His deep bond with Chani, daughter of Liet-Kynes. Learning the rhythm of the desert sands to avoid worms.',
             'The Desert Mouse: Taking the Name Muad\'Dib',
             'Muad\'Dib is wise in the ways of the desert; he makes his own water; he conceals his footprint.'),

            ('Riding Shai-Hulud',
             'The ultimate Fremen rite of passage: summoning and mounting a colossal sandworm with maker hooks. Paul ascends to full warrior status among the Fremen, leading devastating guerrilla raids against Harkonnen spice harvesters.',
             'The Maker Hooks and Mastering the Sandworm',
             'He who can destroy a thing has the real control of it.'),

            ('The Water of Life and Cosmic Awakening',
             'Lady Jessica drinks the poisonous Water of Life to become the Reverend Mother of Sietch Tabr, transmitting ancestral memories. Paul undertakes the same lethal transformation, surviving in a coma to unlock full prescient vision across space and time.',
             'The Poisoned Elixir and the Reverend Mother Transmutation',
             'Beyond prescience lies the unknown, and in the unknown lies freedom.'),

            ('The Great Battle of Arrakeen',
             'The storm breaches the Shield Wall. Paul leads the Fremen army mounted on giant sandworms into Arrakeen. The Padishah Emperor Shaddam IV and the Sardaukar routed; Baron Harkonnen slain by young Alia.',
             'The Breach of the Shield Wall and the Emperor\'s Defeat',
             'The power to destroy a thing is the absolute power over it.'),

            ('The Duel with Feyd-Rautha and the Imperial Throne',
             'Paul faces the deadly Harkonnen na-Baron Feyd-Rautha in knife combat without shields. Paul triumphs through discipline, claims the Imperial Throne, and secures Arrakis, while seeing the terrifying holy war that will sweep across the universe.',
             'The Crysknife Duel and the Crown of the Imperium',
             'History will call us wives, but we shall be remembered as the architects of destiny.')
        ]
    },

    'atomic habits': {
        'subtitle': 'An Easy & Proven Way to Build Good Habits & Break Bad Ones',
        'historical_context': 'Written by James Clear and published in 2018. One of the most widely read works on behavioral psychology and self-improvement.',
        'thesis': 'Real change comes from the compound effect of hundreds of small decisions. Systems of identity and environment design supersede fleeting motivation.',
        'parts': [
            'The Fundamentals: The Compound Power of Tiny Habits',
            'The 1st & 2nd Laws: Make It Obvious and Make It Attractive',
            'The 3rd & 4th Laws: Make It Easy and Make It Satisfying',
            'Advanced Tactics: How to Go from Merely Good to Truly Great'
        ],
        'chapters': [
            ('The Surprising Power of Atomic Habits',
             'Why 1% improvements compound exponentially over time. Habits are the compound interest of self-improvement. The plateau of latent potential: why habits seem ineffective before reaching a breakthrough threshold.',
             'The Compound Effect of Marginal 1% Gains',
             'You do not rise to the level of your goals; you fall to the level of your systems.'),

            ('How Your Habits Shape Your Identity',
             'Outcome-based habits vs identity-based habits. The three layers of behavior change: outcomes, processes, and identity. The most effective way to change habits is to focus not on what you want to achieve, but on who you wish to become.',
             'Identity-Based Habits: Becoming the Desired Person',
             'Every action you take is a vote for the type of person you wish to become.'),

            ('The Habit Loop: Cue, Craving, Response, Reward',
             'The four-step neurological loop of human habit: Cue triggers a Craving, which motivates a Response, which delivers a Reward. The Four Laws of Behavior Change derived from this cycle.',
             'The Neurological Habit Loop and the Four Laws',
             'A habit is an automatic behavior that solves a recurring problem in your environment.'),

            ('The 1st Law: Make It Obvious',
             'The Habits Scorecard and awareness of automatic actions. Implementation intentions: "I will [BEHAVIOR] at [TIME] in [LOCATION]." Habit stacking: pair a new habit with a current established habit.',
             'Implementation Intentions and Habit Stacking',
             'Many people think they lack motivation when what they really lack is clarity.'),

            ('Environment Design Over Motivation',
             'Visual cues dominate human perception. Redesigning physical spaces to make good cues obvious and bad cues invisible. Context is the cue: create distinct spaces for working, reading, and entertainment.',
             'Structuring Physical Space to Trigger Desired Actions',
             'Environment is the invisible hand that shapes human behavior.'),

            ('The 2nd Law: Make It Attractive',
             'The role of dopamine in craving and anticipation. Temptation bundling: pair an action you need to do with an action you want to do. The social influence of tribes: we imitate the close, the many, and the powerful.',
             'Dopamine Feedback Loops and Temptation Bundling',
             'It is the anticipation of a reward—not the fulfillment of it—that gets us to take action.'),

            ('The 3rd Law: Make It Easy',
             'Law of least effort: human energy will naturally follow the path of least resistance. Reducing friction for good habits and increasing friction for bad habits. The Two-Minute Rule: scale any new habit down to two minutes.',
             'Friction Reduction and the Two-Minute Rule',
             'Optimize for starting rather than finishing; a habit must be established before it can be improved.'),

            ('The 4th Law: Make It Satisfying',
             'The cardinal rule of behavior change: what is immediately rewarded is repeated; what is immediately punished is avoided. The conflict between immediate return environments and delayed return environments.',
             'Immediate Reinforcement and Habit Tracking',
             'The cost of your good habits is in the present; the cost of your bad habits is in the future.'),

            ('How to Stick with Good Habits Every Day',
             'Habit trackers and visual streaks ("Don\'t break the chain"). The rule of never missing twice: a single missed day is an accident; two missed days is the start of a new, destructive habit.',
             'Visual Streaks and the Rule of Never Missing Twice',
             'Missing once is an accident; missing twice is the start of a new habit.'),

            ('The Goldilocks Rule: Peak Motivation',
             'How to stay motivated when working on the edge of your abilities. The Goldilocks Rule: humans experience peak motivation when handling tasks right on the edge of their current competence (~4% beyond current skill).',
             'The Edge of Ability: The Goldilocks Principle of Mastery',
             'The greatest threat to success is not failure but boredom.')
        ]
    },

    'thinking, fast and slow': {
        'subtitle': 'Two Systems of the Mind, Intuition, and Decision Architecture',
        'historical_context': 'Written by Nobel laureate Daniel Kahneman, summarizing decades of groundbreaking psychological research conducted with Amos Tversky. Published in 2011.',
        'thesis': 'Human judgment is governed by two cognitive engines: System 1 operates automatically and instinctively with little effort, while System 2 allocates slow, deliberate, effortful mental attention.',
        'parts': [
            'Part I: Two Systems of Cognitive Processing',
            'Part II: Heuristics, Biases, and Cognitive Illusions',
            'Part III: Overconfidence and the Illusion of Validity',
            'Part IV: Choices, Prospect Theory, and Risk Asymmetry'
        ],
        'chapters': [
            ('Two Systems of the Mind',
             'System 1 (Fast, automatic, emotional, unconscious) vs System 2 (Slow, deliberative, logical, effortful). The division of cognitive labor between the two systems and how mental energy depletion leads to ego depletion.',
             'System 1 Intuition and System 2 Deliberation',
             'System 1 runs automatically and System 2 is normally in a comfortable low-effort mode.'),

            ('Attention, Effort, and Pupil Dilation',
             'The physical and mental limits of System 2. Pupil dilation and heart rate as direct physiological indicators of mental effort. The invisible gorilla experiment and the phenomenon of cognitive blindness.',
             'The Limits of Focused Cognitive Attention',
             'We can be blind to the obvious, and we are also blind to our blindness.'),

            ('The Lazy Controller and Ego Depletion',
             'System 2 is inherently lazy and avoids exertion whenever possible. Ego depletion: self-control is a depleting resource. Studies of parole board judges: favorable decisions drop from 65% to near zero right before meals.',
             'The Depleting Currency of Willpower and Executive Control',
             'A tired and hungry System 2 defaults to the status quo and path of least resistance.'),

            ('The Associative Machine and Priming',
             'How System 1 unconsciously links words, images, sensations, and emotions into rich associative networks. The Florida effect: subconscious priming influencing physical walking speed. The illusion of truth.',
             'Associative Networks and the Hidden Power of Priming',
             'You think you know what is going on in your mind, but you know only what System 2 notices.'),

            ('Cognitive Ease and Cognitive Strain',
             'Cognitive ease feels familiar, true, good, and effortless; cognitive strain demands analytical scrutiny. High contrast text, repeated exposure, and rhyming aphorisms trigger cognitive ease, fooling judgment.',
             'The Illusions of Cognitive Ease and Perceived Truth',
             'Familiarity is not easily distinguished from truth.'),

            ('Heuristics: Anchoring and Availability',
             'The anchoring effect: disproportionately weighting the first piece of information encountered, even when arbitrary. The availability heuristic: judging the probability of an event by the ease with which examples come to mind.',
             'Anchoring Biases and the Availability Cascade',
             'The world in our heads is not a precise replica of reality; our expectations are distorted by emotional intensity.'),

            ('The Law of Small Numbers and Regression',
             'The widespread cognitive failure to appreciate statistical sample size. Believing small samples represent larger populations. Regression to the mean: extreme performances are naturally followed by closer-to-average performances.',
             'Sample Size Fallacies and Regression to the Mean',
             'Extreme outcomes are largely driven by luck, and luck does not repeat on demand.'),

            ('The Illusion of Validity and Hindsight Bias',
             'The narrative fallacy and the backward construction of coherent stories. Hindsight bias: believing past events were predictable after they occurred. Why expert prediction records across politics and finance barely exceed random chance.',
             'The Narrative Fallacy and the Illusion of Expert Prediction',
             'Our comforting conviction that the world makes sense rests on a secure foundation: our almost unlimited ability to ignore our ignorance.'),

            ('Prospect Theory: Loss Aversion and Risk',
             'Kahneman and Tversky\'s Nobel-winning Prospect Theory. Losses loom larger than gains (loss aversion ratio of ~2:1). The endowment effect: people value things merely because they own them. The certainty effect in risk decisions.',
             'Prospect Theory: The Asymmetry Between Losses and Gains',
             'Losses hurt roughly twice as much as equivalent gains feel good.'),

            ('Two Selves: The Experiencing and the Remembering Self',
             'The experiencing self lives in the present; the remembering self constructs the narrative of the past. The Peak-End Rule and duration neglect: our memories evaluate experiences by their peak intensity and how they ended, ignoring total duration.',
             'The Peak-End Rule and the Tyranny of the Remembering Self',
             'The remembering self is a storyteller that discards duration and preserves only the peak and the end.')
        ]
    },

    'sapiens: a brief history of humankind': {
        'subtitle': 'The Great Trajectory from Foraging Apes to Planetary Masters',
        'historical_context': 'Authored by Israeli historian Yuval Noah Harari. First published in Hebrew in 2011 and worldwide in English in 2014.',
        'thesis': 'Homo sapiens conquered the planet through the unique cognitive ability to invent and believe in collective fictions—religions, nations, money, and corporations.',
        'parts': [
            'Part I: The Cognitive Revolution (~70,000 BCE)',
            'Part II: The Agricultural Revolution (~10,000 BCE)',
            'Part III: The Unification of Humankind',
            'Part IV: The Scientific Revolution (~1500 CE to Present)'
        ],
        'chapters': [
            ('An Animal of No Significance',
             'Two million years ago, human species roamed East Africa without dominating the ecosystem. The emergence of multiple species: Neanderthals in Europe, Homo erectus in Asia, Homo floresiensis. Sapiens as an ordinary ape in the middle of the food chain.',
             'The Prehistoric Human Spectrum and the Middle of the Food Chain',
             'There were once many species of humans; today there is only one.'),

            ('The Tree of Knowledge and Collective Fictions',
             'The Cognitive Revolution 70,000 years ago: mutations that enabled complex language. The decisive breakthrough: the capacity to transmit information about things that do not physically exist. Collective fictions: legal systems, corporations (like Peugeot), and gods.',
             'Fictional Realities and Large-Scale Cooperation',
             'Sapiens rule the world because we are the only animal that can cooperate flexibly in large numbers based on shared myths.'),

            ('A Day in the Life of a Forager',
             'The original affluent society: Paleolithic hunter-gatherers worked fewer hours, ate a more varied diet, and had superior sensory awareness compared to their agricultural descendants. Nomadic bands bounded by Dunbar\'s number (~150 individuals).',
             'The Foraging Lifestyle and Dunbar\'s Number',
             'The foraging band was the natural habitat of human biology and psychology.'),

            ('History\'s Biggest Fraud: The Agricultural Trap',
             'The Agricultural Revolution 10,000 years ago did not offer an easier life: it produced back-breaking labor, narrower diets, epidemic diseases, and vulnerability to drought. Wheat domesticated Sapiens, not the other way around. The luxury trap.',
             'Wheat Domesticates Humanity: The Agricultural Trap',
             'The Agricultural Revolution was history\'s biggest fraud.'),

            ('Building Pyramids and Imagined Orders',
             'Agriculture generated food surpluses, enabling cities, kingdoms, and empires. Imagined orders: Hammurabi\'s Code, the American Declaration of Independence. Why imagined orders require eternal belief and state enforcement.',
             'Surpluses, Hierarchies, and Imagined Social Orders',
             'We believe in an imagined order not because it is objective truth, but because believing in it enables us to cooperate effectively.'),

            ('The Scent of Money',
             'Money is the most universal and egalitarian system of mutual trust ever devised. Unlike religion or nationality, gold and modern fiat currency transcend cultural boundaries: conquerors and conquered traded freely because all believed in the collective fiction of value.',
             'Universal Trust: The Fiction of Currency and Commerce',
             'Money is the only trust system created by humans that can bridge almost any cultural gap.'),

            ('Imperial Visions and Global Integration',
             'Empires have been the dominant form of political organization for 2,500 years. The imperial cycle: conquering diverse peoples, imposing a unified legal and cultural framework, and eventually integrating subjugated elites into the ruling class.',
             'The Imperial Dynamo and Cultural Assimilation',
             'Empires digested hundreds of distinct tribes into shared linguistic and political civilizations.'),

            ('The Law of Religion',
             'The social function of religion as a provider of superhuman legitimacy to fragile social structures. From animism to polytheism, monotheism, and dualism. Modern secular religions: liberalism, communism, and nationalism.',
             'Superhuman Legitimacy and the Evolution of Faith',
             'Religion is a system of human norms and values founded on belief in a superhuman order.'),

            ('The Discovery of Ignorance: Modern Science',
             'The Scientific Revolution began not with new knowledge, but with the revolutionary willingness to admit ignorance ("Ignoramus"). Coupling science with imperial conquest and capitalist credit.',
             'The Admission of Ignorance and the Scientific Revolution',
             'The real engine of the Scientific Revolution was not the discovery of new facts, but the willingness to admit ignorance.'),

            ('The Capitalist Creed and Perpetual Growth',
             'Credit as the magic mechanism of modern capitalism: lending based on trust in the future. The feedback loop between scientific discovery, technological innovation, economic growth, and military expansion.',
             'Credit, Trust in Tomorrow, and the Capitalist Creed',
             'Capitalism relies on trust in a better future to turn credit into tangible progress.')
        ]
    },

    'zero to one': {
        'subtitle': 'Notes on Startups, or How to Build the Future',
        'historical_context': 'Authored by PayPal co-founder and venture capitalist Peter Thiel with Blake Masters. Published in 2014, based on Stanford University lectures.',
        'thesis': 'The next breakthrough business will not build an operating system or a search engine; it will build something entirely new, moving from 0 to 1 rather than copying what works (1 to n).',
        'parts': [
            'Part I: Progress, Monopolies, and Secrets',
            'Part II: Foundations, Culture, and Distribution',
            'Part III: The Seven Questions for Breakthrough Enterprises'
        ],
        'chapters': [
            ('The Challenge of the Future: Zero to One',
             'Horizontal progress (globalization, copying what works, moving from 1 to n) vs Vertical progress (technology, doing something nobody has done, moving from 0 to 1). The contrarian question: "What important truth do very few people agree with you on?"',
             'Vertical Progress, Technology, and Contrarian Thinking',
             'Every moment in business happens only once; the next Bill Gates will not build an operating system.'),

            ('All Happy Companies Are Different: Creative Monopolies',
             'In perfect competition, all profits are competed away. The goal of a startup is to build a creative monopoly: a company so good at what it does that no other firm can offer a close substitute. Why monopolies lie to pretend they have competition, and competitive firms lie to pretend they are unique.',
             'Creative Monopolies vs The Trap of Perfect Competition',
             'Monopoly is the condition of every successful business.'),

            ('The Four Characteristics of Monopoly',
             '1. Proprietary Technology (must be at least 10x better than the closest substitute). 2. Network Effects (becomes more valuable as more people use it). 3. Economies of Scale (fixed software costs spread over vast user bases). 4. Branding (substance preceding style).',
             'The 10x Advantage, Network Effects, and Scalability',
             'A great company must be built around a proprietary advantage that is 10x better than existing alternatives.'),

            ('You Are Not a Lottery Ticket: Definite Optimism',
             'Indefinite pessimism, definite pessimism, indefinite optimism, and definite optimism. Why modern culture has surrendered to indefinite optimism—believing the future will be better without planning for it. True greatness requires definite optimism: having a concrete plan and executing it.',
             'Definite Optimism and the Fallacy of Luck',
             'A startup is the largest endeavor over which you can have definite mastery.'),

            ('Follow the Money: The Power Law',
             'The Pareto Principle in venture capital: a small handful of companies generate exponentially more returns than all others combined. Why diversification is often a hedge for ignorance: invest only in companies that have the potential to return the entire fund.',
             'The Exponential Power Law in Markets and Careers',
             'The power law means that a small number of things will matter exponentially more than everything else.'),

            ('Secrets: What Are People Not Looking For?',
             'There are two kinds of secrets: secrets of nature and secrets about people. If you believe secrets remain to be found, you will look for them and build breakthroughs; if you believe everything has been discovered, you will settle for incrementalism.',
             'Hidden Truths, Natural Secrets, and Unexplored Frontiers',
             'Great companies can be built on open but overlooked secrets about how the world works.'),

            ('Foundations: Thiel\'s Law',
             'A startup messed up at its foundation cannot be fixed. The triad of co-founder alignment: ownership (equity), possession (daily work), and control (governance). Choosing co-founders with shared prehistory; keeping board sizes small (3 to 5 people).',
             'Thiel\'s Law: Getting the Founding DNA Right',
             'A startup messed up at its foundation cannot be fixed.'),

            ('The Mechanics of Culture and the Mafia',
             'A company culture is not perks or ping-pong tables; it is how tightly bonded people are in pursuit of a mission. The PayPal Mafia: recruiting people who enjoy working together and share an obsession with the company\'s specific problem.',
             'Mission-Driven Alignment and Company Culture',
             'You want employees to be fiercely devoted to the core mission, not to peripheral perks.'),

            ('If You Build It, Will They Come? The Reality of Distribution',
             'Engineers often believe superior technology sells itself; this is a fatal delusion. Distribution is essential: Viral marketing, inside sales, enterprise field sales, and marketing PR. Even if your product is extraordinary, poor distribution means failure.',
             'Distribution Channels, Virality, and Enterprise Sales',
             'Superior distribution by itself can create a monopoly, even with no product differentiation.'),

            ('The Seven Questions Every Business Must Answer',
             '1. The Engineering Question (10x better?). 2. The Timing Question (now?). 3. The Monopoly Question (small market first?). 4. The People Question (right team?). 5. The Distribution Question (delivery?). 6. The Durability Question (defensible in 10-20 years?). 7. The Secret Question (unique insight?).',
             'The Diagnostic Checklist for Lasting Enterprise',
             'If you nail all seven questions, you will dominate your market; miss even two, and failure is probable.')
        ]
    }
}
