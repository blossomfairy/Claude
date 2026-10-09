const DRIVE = id => `https://drive.google.com/file/d/${id}/view`;
const EPISODES = [];

/* ================= ACT I ================= */
EPISODES.push({
  id: 'ep01', act: 1, label: 'Ep 1', title: 'The Will', topic: 'Computational thinking: the 4 pillars', unit: 'Unit 1 · Section 1', video: DRIVE('1EXcYCMQu3W79Cm06o6PNPhM8LfS-_Hfa'),
  steps: [
    { t: 'story', eyebrow: 'Previously: nothing. This is the start.', lines: [
      ['scene', 'A lawyer’s office. Nadia’s father built Lovelace Labs and its AI, ORACLE. He has just died.'],
      ['L', 'You inherit everything… _if_ you pass the Board’s test in 16 weeks. 50 questions, 90 minutes, closed book.'],
      ['V', 'And if she fails, the company is mine. I sell ORACLE.'],
      ['N', 'I have never written a line of code.'],
    ] },
    { t: 'idea', eyebrow: 'Why this story', h: 'Nadia’s test is your exam', p: 'Your COMP 200 final is the same: **50 multiple-choice questions in 90 minutes, closed book**. The course runs **16 weeks**. You learn each topic right alongside her.', hook: 'Every episode = one week of the course.' },
    { t: 'story', lines: [
      ['scene', 'Puzzle one: rebuild ORACLE’s launch plan in one night. There are 400 pages of notes.'],
      ['V', 'Start reading. You’ll be done by next year.'],
      ['N', 'I’m not going to read it all. I’m going to think like him.'],
    ] },
    { t: 'idea', h: 'Step 1: Decomposition', p: '**Decomposition** means breaking a big, scary problem into smaller parts you can solve one at a time.', w: { type: 'split', root: 'Rebuild the launch plan (400 pages)', parts: ['Product', 'Budget', 'Team', 'Timeline', 'Marketing'] }, hook: 'De-COMPOSE = un-build it into pieces.' },
    { t: 'idea', h: 'The 4 pillars of computational thinking', p: 'Decomposition is pillar one. Tap each card to see what the other three mean, using Nadia’s launch plan.', w: { type: 'flip', items: [
      ['1. Decomposition', 'Break the problem into smaller parts. _Launch plan → product, budget, team, timeline._'],
      ['2. Pattern recognition', 'Spot what’s similar so you can reuse a solution. _Every past launch followed the same 3 phases._'],
      ['3. Abstraction', 'Keep the important details, ignore the rest. _Skip the font choices; keep the dates and costs._'],
      ['4. Algorithm design', 'Write the solution as clear, ordered steps. _Step 1 fix budget, step 2 hire team…_'],
    ] }, hook: '**D**on’t **P**anic, **A**bstract **A**lways = **D**ecomposition, **P**attern, **A**bstraction, **A**lgorithm.' },
    { t: 'check', q: 'Which one is **not** a computational-thinking pillar?', o: ['Decomposition', 'Pattern recognition', 'Compilation', 'Abstraction'], a: 2, why: 'Compilation is how code gets translated (that’s Ep 10). The four pillars are decomposition, pattern recognition, abstraction and algorithm design.' },
    { t: 'idea', h: 'Bonus pillar: thinking recursively', p: 'Unit 1 adds a fifth idea: **solve a problem by solving smaller copies of the same problem**, until you reach a piece so small the answer is obvious (the **base case**).', p2: 'You’ll see this properly in Ep 3, "Boxes Inside Boxes".', hook: 'Same problem, just smaller, until it’s tiny.' },
    { t: 'idea', h: 'What Wing says about it', p: 'Jeannette Wing (2006) wrote that computational thinking is:', w: { type: 'flip', items: [
      ['For everyone', 'A fundamental skill for **everyone**, not just computer scientists.'],
      ['Conceptualizing', 'About **thinking**, not about programming.'],
      ['Human', 'A way **humans** think, not a way to make humans think like computers.'],
    ] } },
    { t: 'idea', h: 'Three history names to know', p: 'These show up as easy exam marks.', w: { type: 'flip', items: [
      ['Alan Turing, 1936', 'Introduced the **Turing machine**, the formal model of computation.'],
      ['Claude Shannon, mid-1900s', 'Founded **information theory**, the maths of data.'],
      ['FORTRAN & COBOL, 1950s', 'Early programming languages that led to modern software.'],
    ] }, hook: 'Turing = machine. Shannon = information. 1950s = FORTRAN/COBOL.' },
    { t: 'check', q: 'Machine learning is best described as:', o: ['A separate field unrelated to AI', 'A subset of AI where computers learn from data without being explicitly programmed', 'The study of hardware', 'A database language'], a: 1 },
    { t: 'recap', items: ['**Computational thinking** = decomposition, pattern recognition, abstraction, algorithm design (+ thinking recursively).', 'Wing: it’s for **everyone**, it’s about **concepts**, and it’s **human**.', 'Turing 1936 (machine) · Shannon (information) · FORTRAN/COBOL (1950s).'], next: 'The laptop locks. The screen reads: 10 QUESTIONS. 1024 FILES. ONE IS TRUE.' },
  ],
  quiz: [
    ['Which of these is **not** one of the computational-thinking elements listed in Unit 1?', ['Decomposition', 'Pattern recognition', 'Compilation', 'Abstraction'], 2, 'Unit 1 lists decomposition, pattern recognition, abstraction, algorithm design and thinking recursively.'],
    ['Breaking a complex problem into smaller, more manageable parts and solving each part individually is called:', ['Abstraction', 'Decomposition', 'Algorithm design', 'Pattern recognition'], 1],
    ['In programming, _abstraction_ most closely means:', ['Writing code without comments', 'Focusing on the important details and ignoring irrelevant information', 'Repeating the same logic in several places', 'Converting source code into machine code'], 1],
    ['Who introduced the "Turing Machine" in 1936, formalizing the principles of computation?', ['Charles Babbage', 'Claude Shannon', 'Alan Turing', 'Tim Berners-Lee'], 2],
    ['Whose mid-20th-century work established the mathematical foundations of information theory?', ['Claude Shannon', 'Alan Turing', 'Charles Babbage', 'Vint Cerf'], 0],
    ['Which early programming languages from the 1950s paved the way for modern software?', ['Python and Java', 'FORTRAN and COBOL', 'C and C++', 'HTML and SQL'], 1],
    ['Machine learning is best described as:', ['A separate field unrelated to AI', 'A subset of AI that teaches computers to learn from data and improve without explicit programming', 'The study of computer hardware design', 'A database query language'], 1],
    ['According to Wing (2006), computational thinking is:', ['A skill only for professional programmers', 'A way to make humans think like computers', 'A fundamental skill for everyone, not just computer scientists', 'The same thing as computer programming'], 2],
    ['In a recursive algorithm, decomposition divides a problem into subproblems that are:', ['Of a completely different type', 'Of the same type but smaller, until a base case is reached', 'Solved in parallel by different computers', 'Larger than the original problem'], 1],
    ['Which core area of CS studies the mathematical foundations of computation, like complexity and the limits of what computers can solve?', ['Software engineering', 'Human-computer interaction', 'Theoretical computer science', 'Computer architecture'], 2],
  ],
  notes: [
    '**Study Q: skills for success in CS** (Zhang R1 §1.4): problem-solving, programming proficiency, mathematical foundations, critical thinking, collaboration & communication, adaptability.',
    '**Try it:** take a messy task (a week of meals on a budget). Decompose it into 4–6 parts, mark shared patterns, strike out details that don’t matter, then write 5 numbered steps.',
    '**Discussion spark:** pick a job with nothing to do with computers. Where does one of the 4 pillars already show up? Write your post in your own words.',
  ],
});

EPISODES.push({
  id: 'ep02', act: 1, label: 'Ep 2', title: 'Ten Questions', topic: 'Bits, binary questions, RTNs', unit: 'Unit 1 · Section 2', video: DRIVE('1AVzzbXGM0D1jCTfRvSGNSv6XZd7jPoh2'),
  steps: [
    { t: 'story', lines: [
      ['scene', 'The locked laptop. 1,024 files. Only one is real.'],
      ['A', 'Ten yes/no questions to find the true file. Or the drive wipes.'],
      ['V', 'Is it file number one? … Number two?'],
    ] },
    { t: 'idea', h: 'Play Victor vs Nadia', p: 'Victor asks "Is it file #1?" Nadia asks "Is it above the middle?" Try both and watch the pile.', w: { type: 'halving' } },
    { t: 'idea', h: 'Why Nadia wins', p: 'A good yes/no question cuts the pile **in half**. 1024 → 512 → 256 → … → 1. That takes exactly **10** halvings, because **2¹⁰ = 1,024**.', p2: 'Victor’s question only removes **one** file. He wastes almost every question.', hook: 'Best question = both answers equally likely.' },
    { t: 'idea', h: 'That halving question is a bit', p: 'One **bit** = the answer to one fair yes/no question. It cuts the uncertainty in half. **n bits can tell apart 2ⁿ values.**', w: { type: 'bits', n: 3 }, hook: 'Each extra bit doubles what you can count.' },
    { t: 'check', q: 'How many bits do you need to tell apart **1,000** different values?', o: ['8', '10', '100', '1,000'], a: 1, why: '2⁹ = 512 is too small. 2¹⁰ = 1,024 is enough. So 10 bits.' },
    { t: 'idea', h: 'The rule: log₂', p: 'To tell apart **k** values you need **log₂ k** bits (round up). A die has 6 outcomes: log₂ 6 ≈ 2.58, so **3** questions.', hook: 'log₂ asks: "how many times can I halve it?"' },
    { t: 'idea', h: 'How do we measure a computer’s power?', p: 'Not watts or horsepower. Evans uses two things: **how much information** it can process, and **how fast**.', p2: 'And a computer is a machine that can **accept input, run a mechanical procedure, and produce output**.' },
    { t: 'story', lines: [
      ['scene', 'The real file is password-locked. On the whiteboard, her father drew circles and arrows.'],
      ['N', 'It’s not a doodle. It’s a machine that writes passwords.'],
    ] },
    { t: 'idea', h: 'Recursive transition networks (RTNs)', p: 'An **RTN** is a diagram that defines a language. Start at the start node, follow arrows, and each arrow adds a word. Reach the final node and you have a valid sentence.', w: { type: 'rtn' } },
    { t: 'idea', h: 'Count the paths', p: 'No loop: 2 choices × 2 choices = **4 sentences**. Add one more name ("Colleen") and you get **2 more**.', p2: 'Add a **loop** back to the start and the network can make **infinitely many** sentences from a tiny drawing. That loop is recursion.', hook: 'A loop in the drawing = infinite language.' },
    { t: 'check', q: 'An "and" arrow goes from the final node S back to Noun. Now the RTN makes:', o: ['5 strings', '8 strings', 'Infinitely many strings', 'No strings'], a: 2 },
    { t: 'recap', items: ['**1 bit** = one fair yes/no answer = halves the uncertainty.', '**n bits → 2ⁿ values.** k values need **log₂ k** bits. 1,000 values → 10 bits.', 'Computer power = **how much** information, **how fast**.', '**RTN** = start node, labelled arrows, final node. A **cycle** makes the language infinite.'], next: 'The RTN loops back into itself. The password could be infinitely long.' },
  ],
  quiz: [
    ['One bit of information is equivalent to:', ['One decimal digit', 'Answering a yes/no question where both answers are equally likely', 'One byte', 'One keystroke'], 1],
    ['How many different values can 3 bits distinguish?', ['3', '6', '8', '9'], 2, '2 × 2 × 2 = 8.'],
    ['A six-sided die has six equally likely outcomes. How many binary questions are needed to identify the outcome?', ['2', '3', '5', '6'], 1, 'log₂ 6 ≈ 2.58, so round up to 3.'],
    ['For a die roll, which first question gives the most information?', ['"Is it 6?"', '"Is it 1?"', '"Is the value at least 4?"', '"Is it even and greater than 5?"'], 2, 'It splits the outcomes 3 and 3, so both answers are equally likely.'],
    ['To distinguish among _k_ possible values you need:', ['k bits', 'k² bits', 'log₂ k bits', '2ᵏ bits'], 2],
    ['How many bits are needed to tell apart 1,000 different values?', ['8', '10', '100', '1,000'], 1, '2¹⁰ = 1,024 ≥ 1,000 > 512 = 2⁹.'],
    ['In an RTN, a string is in the language if:', ['Every node is visited', 'Some path from the start node to a final node produces it along the edge labels', 'It uses every edge exactly once', 'It has no repeated words'], 1],
    ['The RTN Noun → Verb → S, with edges "Alice"/"Bob" then "jumps"/"runs", produces how many strings?', ['2', '4', '6', 'Infinitely many'], 1],
    ['Adding an "and" edge from the final node S back to Noun makes the RTN produce:', ['5 strings', '8 strings', 'Infinitely many strings', 'No strings'], 2],
    ['Evans names two properties for measuring the power of a computing machine:', ['Price and size', 'How much information it can process, and how fast', 'Number of cores and screen resolution', 'Energy use and weight'], 1],
    ['According to Evans, a computer is a machine that can:', ['Only do arithmetic', 'Accept input, execute a mechanical procedure, and produce output', 'Think like a human', 'Store files'], 1],
    ['In the Alice/Bob RTN, adding one more Noun → Verb edge labelled "Colleen" adds how many new strings?', ['1', '2', '3', '4'], 1, 'Colleen jumps, Colleen runs.'],
  ],
  notes: [
    '**Study Q4: using RTNs for recursive procedures** (Evans §2.3): a cycle lets the same structure repeat, so a finite drawing describes infinitely many strings. Without cycles, count the start-to-final paths.',
    '**Study Q2 (“why think about bits at higher levels of abstraction?”)** is word-for-word **A1 Part I Q2**, which is graded. Write it yourself.',
    '**Try it:** draw an RTN for {c, b} + {a, o} + t. How many words? (4: cat, cot, bat, bot.) Then add a loop on the vowel.',
  ],
});

EPISODES.push({
  id: 'ep02b', act: 1, label: 'Ep 2½', title: 'The Grammar', topic: 'Replacement grammars and BNF', unit: 'Unit 1 S2 / Unit 2', video: DRIVE('1T75MD7CaUBUmIaITR1f81DwFHBdLJ41_'),
  steps: [
    { t: 'story', lines: [['N', 'The RTN is a drawing. Is there a way to write the same rules as text?'], ['A', 'Yes. It’s called BNF.']] },
    { t: 'idea', h: 'BNF = Backus-Naur Form', p: 'A way to write a language’s rules as text. **John Backus** invented it while defining **Fortran**.', p2: 'Each rule has the shape: **nonterminal ::⇒ replacement**', hook: 'Backus → BNF → Fortran. Three Fs and Bs.' },
    { t: 'idea', h: 'Terminals vs nonterminals', p: '', w: { type: 'flip', items: [
      ['Nonterminal', 'A placeholder that must be **replaced**. It appears on the **left** of a rule. _Sentence, Noun, Verb._'],
      ['Terminal', 'A real output word. It **never** appears on the left of a rule. _Alice, Bob, jumps, runs._'],
      ['The | bar', 'Means **"or"**: pick one alternative. _Noun ::⇒ Alice | Bob_'],
    ] }, hook: 'TERMINAL = the END of the line. It can’t be replaced.' },
    { t: 'idea', h: 'Watch a derivation', p: 'Start with the start symbol. Replace one nonterminal at a time until only terminals are left.', w: { type: 'steps', frames: [
      { html: '<pre class="code">Sentence ::⇒ Noun Verb\nNoun     ::⇒ Alice | Bob\nVerb     ::⇒ jumps | runs</pre>', cap: 'The grammar: 3 rules.' },
      { html: '<div class="bigstat"><span class="kw">Sentence</span></div>', cap: 'Start with the start symbol.' },
      { html: '<div class="bigstat"><span class="kw">Noun</span> Verb</div>', cap: 'Replace Sentence using rule 1.' },
      { html: '<div class="bigstat">Alice <span class="kw">Verb</span></div>', cap: 'Replace Noun: pick Alice.' },
      { html: '<div class="bigstat">Alice runs</div>', cap: 'Replace Verb: pick runs. Only terminals left. Done.' },
    ] } },
    { t: 'idea', h: 'Parse tree', p: 'Draw the derivation as a tree. The **root** is the start symbol. The **leaves** are the terminals, read left to right.', w: { type: 'code', html: '        Sentence          ← root (start nonterminal)\n        /      \\\n     Noun      Verb\n      |          |\n    Alice      runs        ← leaves (terminals)' } },
    { t: 'check', q: 'Sentence ::⇒ Noun Verb, Noun ::⇒ Alice | Bob, Verb ::⇒ jumps | runs. How many sentences?', o: ['2', '4', '6', 'Infinitely many'], a: 1, why: '2 nouns × 2 verbs = 4. Same as the RTN in Ep 2.' },
    { t: 'idea', h: 'Recursion in a grammar', p: 'Add **Sentence ::⇒ Sentence and Sentence** and the language becomes **infinite**.', p2: 'But a rule that only refers to itself never finishes. You need a **base case**: a rule with no nonterminal left, like **MoreDigits ::⇒ ε** (ε = empty). That turns a _circular_ definition into a _recursive_ one.', hook: 'Circular = never ends. Recursive = has a way out (base case).' },
    { t: 'idea', h: 'RTN vs BNF', p: 'They are **exactly as powerful** as each other. BNF is just **easier to write down** as text.' },
    { t: 'recap', items: ['**BNF** = Backus-Naur Form, from **Fortran**. Rule: nonterminal ::⇒ replacement.', '**Terminal** = output word, never on the left. **|** = "or".', 'Parse tree: root = start symbol, leaves = terminals.', 'A base case (like **ε**) makes recursion finish. **RTN = BNF in power.**'] },
  ],
  quiz: [
    ['BNF stands for:', ['Binary Node Format', 'Backus-Naur Form', 'Basic Network Function', 'Boolean Normal Form'], 1],
    ['BNF was invented by John Backus while defining which language?', ['Scheme', 'Python', 'Fortran', 'Java'], 2],
    ['A BNF rule has the form:', ['terminal ::⇒ nonterminal', 'nonterminal ::⇒ replacement', 'start → end', 'if … then …'], 1],
    ['A **terminal** symbol:', ['Appears on the left side of rules', 'Is an output symbol that never appears on the left side of a rule', 'Must be replaced', 'Is always empty'], 1],
    ['Compared to recursive transition networks, BNF grammars are:', ['More powerful', 'Less powerful', 'Exactly as powerful, but easier to write down', 'Unrelated'], 2],
    ['In a parse tree for a derivation, the root is ___ and the leaves are ___.', ['A terminal; nonterminals', 'The start nonterminal; the terminals forming the string', 'The last rule; the first rule', 'Empty; full'], 1],
    ['Sentence ::⇒ Noun Verb, Noun ::⇒ Alice | Bob, Verb ::⇒ jumps | runs. How many sentences?', ['2', '4', '6', 'Infinitely many'], 1],
    ['Adding the rule Sentence ::⇒ Sentence and Sentence makes the language:', ['Empty', '8 sentences', 'Infinite', 'Unchanged'], 2],
    ['In the whole-numbers grammar, MoreDigits ::⇒ ε is important because it:', ['Adds a digit', 'Is the base case that turns a circular definition into a recursive one', 'Removes recursion', 'Defines Digit'], 1],
    ['Digit ::⇒ 0 | 1 | 2 | … | 9 uses the vertical bar to mean:', ['"or": alternative replacements', 'Division', 'A comment', 'A pipe to another rule'], 0],
  ],
  notes: ['**A2 Part I** asks you to explain how RTNs and BNFs relate and the advantages of each. Use Ep 2 and this one as background; write it yourself.', '**Try it:** Greeting ::⇒ Word Name; Word ::⇒ hi | hello; Name ::⇒ Ada | Nadia. How many strings? (4.) Add Greetings ::⇒ Greeting | Greeting Greetings. Which rule is the base case? (Greetings ::⇒ Greeting.)'],
});

EPISODES.push({
  id: 'ep03', act: 1, label: 'Ep 3', title: 'Boxes Inside Boxes', topic: 'Recursion and higher-order procedures', unit: 'Unit 1 · Section 3', video: DRIVE('1lkD338hHFuFuGrZFuZYU12uxuR0ETroO'),
  steps: [
    { t: 'story', lines: [['scene', 'A box. Inside it, a box. Inside that, another box. The key is "somewhere inside".'], ['T', 'I’ll just keep opening them by hand.'], ['N', 'Or I write one rule that opens all of them.']] },
    { t: 'idea', h: 'Recursion = one rule, used on smaller and smaller copies', p: 'Nadia’s rule: **if there’s no box inside, stop and take what’s there (base case). Otherwise, open the inner box the same way (recursive case).**', w: { type: 'boxes' } },
    { t: 'idea', h: 'The two parts every recursion needs', p: '', w: { type: 'flip', items: [
      ['Base case', 'An input so simple the answer is **already known**. It stops the recursion.'],
      ['Recursive case', 'Call the same procedure on a **smaller** input. Each call must make **progress toward the base case**.'],
    ] }, hook: 'Base case = brakes. No brakes, no stopping.' },
    { t: 'check', q: '`(define f (lambda (n) (f n)))` will:', code: '(define f (lambda (n) (f n)))', o: ['Return n', 'Return 0', 'Never stop: each call calls f again with the same input', 'Cause a parse error'], a: 2, why: 'The input never gets smaller and there’s no base case. It loops forever.' },
    { t: 'idea', h: 'Factorial: the classic example', p: '5! = 5 × 4 × 3 × 2 × 1. Step through it: it goes **down** to the base case, then results travel **back up**.', w: { type: 'steps', frames: [
      { html: '<pre class="code">(define (factorial n)\n  (if (= n 0)\n      1                          ; base case\n      (* n (factorial (- n 1)))))  ; smaller self-call</pre>', cap: 'The base case is **n = 0 returns 1**.' },
      { html: '<pre class="code">(factorial 3)\n= 3 * (factorial 2)</pre>', cap: 'Going down: 3 is not 0, so call factorial on 2.' },
      { html: '<pre class="code">(factorial 3)\n= 3 * (factorial 2)\n      = 2 * (factorial 1)</pre>', cap: 'Still going down.' },
      { html: '<pre class="code">(factorial 3)\n= 3 * (factorial 2)\n      = 2 * (factorial 1)\n            = 1 * (factorial 0)\n                  = <span class="hl">1</span>   ← base case</pre>', cap: 'Hit the base case. Now come back up.' },
      { html: '<pre class="code">1 * 1 = 1\n2 * 1 = 2\n3 * 2 = <span class="hl">6</span></pre>', cap: 'Results pass **back up** through each waiting call. (factorial 5) = 120 the same way.' },
    ] } },
    { t: 'idea', h: 'Reading Scheme', p: 'In `(+ 1 2)` the **first** thing is the procedure, the rest are operands. Nested expressions are evaluated **inside out**.', w: { type: 'steps', frames: [
      { html: '<div class="bigstat" style="font-family:var(--f-mono)">(* (+ 1 2) (- 9 4))</div>', cap: 'First evaluate the subexpressions.' },
      { html: '<div class="bigstat" style="font-family:var(--f-mono)">(* <span class="kw">3</span> <span class="kw">5</span>)</div>', cap: '(+ 1 2) = 3 and (- 9 4) = 5.' },
      { html: '<div class="bigstat" style="font-family:var(--f-mono)">15</div>', cap: 'Then multiply: 3 × 5 = **15**.' },
    ] } },
    { t: 'idea', h: 'Higher-order procedures', p: 'A **higher-order procedure** takes a procedure as input, or **returns a new procedure** as output. `make-adder` is a machine that builds adding-machines.', w: { type: 'adder' }, hook: 'A procedure factory.' },
    { t: 'check', q: '`(define add-three (make-adder 3))`. What is `(add-three 4)`?', o: ['3', '4', '7', '12'], a: 2 },
    { t: 'recap', items: ['**Recursion** = base case + smaller self-call that makes progress.', 'No base case (or no progress) → never stops.', 'Results pass **back up** through each pending call.', '**Higher-order procedure** = takes or returns a procedure (make-adder).', '`(* (+ 1 2) (- 9 4))` = 15. First item in ( ) is the procedure.'], next: 'The innermost box holds a USB drive labelled STACK.' },
  ],
  quiz: [
    ['In a recursive procedure, the **base case** is:', ['The first line of the program', 'An input simple enough that the answer is already known', 'The largest possible input', 'A syntax error'], 1],
    ['`(define f (lambda (n) (f n)))` will:', ['Return n', 'Return 0', 'Never stop: each application calls f again with the same input', 'Cause a parse error'], 2],
    ['For a recursive procedure to finish, each recursive application must:', ['Use a larger input', 'Make progress toward the base case input', 'Print its result', 'Call a different procedure'], 1],
    ['A **higher-order procedure** is one that:', ['Runs faster', 'Takes procedures as inputs or produces a procedure as output', 'Has more than three parameters', 'Is defined at the top of a file'], 1],
    ['Given make-adder and `(define add-three (make-adder 3))`, what is `(add-three 4)`?', ['3', '4', '7', '12'], 2],
    ['What is the value of `(* (+ 1 2) (- 9 4))`?', ['10', '15', '12', '20'], 1],
    ['When evaluating `(* (+ 1 2) (- 9 4))`, Scheme first:', ['Multiplies 1 by 9', 'Evaluates the subexpressions (+ 1 2) and (- 9 4)', 'Evaluates left to right without nesting', 'Returns the operator'], 1],
    ['In `(if (= n 0) 1 (* n (factorial (- n 1))))`, what is the base case?', ['n = 1 returns 0', 'n = 0 returns 1', 'n − 1', 'There is none'], 1],
    ['In the recursion "spiral", after the base case is reached, results are:', ['Discarded', 'Passed back up through each pending application', 'Printed immediately', 'Stored in a file'], 1],
    ['In a Scheme application like `(+ 1 2)`, the first subexpression is:', ['An operand', 'The procedure to apply', 'Always a number', 'A comment'], 1],
  ],
  notes: ['**Define a procedure:** `(define square (lambda (x) (* x x)))` or `(define (square x) (* x x))`. `(square 5)` → 25.', '**Parse trees:** practise on Evans Ex 3.1 `(+ 100 (* 5 (+ 5 5)))`. A1 Part II uses a different expression: draw that one yourself.', '**Try it:** write recursive `sum-to n` (Evans calls it gauss-sum) and a `make-multiplier`. A1 Part III’s tax procedure is yours to write.'],
});

EPISODES.push({
  id: 'ep04', act: 1, label: 'Ep 4', title: 'Last In, First Out', topic: 'Abstract data types and the Stack', unit: 'Unit 1 · Section 4', video: DRIVE('1gZE54CwDHLzA6rwOcD6fNSZkVcK9Nkz6'),
  steps: [
    { t: 'story', lines: [['scene', 'The USB holds every email her father ever sent, stacked.'], ['A', 'Pop the wrong one and the rest burn.'], ['V', 'Just pop them all off until you find it.']] },
    { t: 'idea', h: 'A stack is a pile of plates', p: 'You can only touch the **top**. The **last** thing you put on is the **first** thing you take off: **LIFO** (Last In, First Out).', w: { type: 'stack' }, hook: 'Plates, browser Back button, Ctrl+Z undo: all stacks.' },
    { t: 'idea', h: 'The five stack operations', p: '', w: { type: 'flip', items: [
      ['push(x)', 'Put x on **top**.'],
      ['pop()', '**Remove and return** the top item.'],
      ['peek()', '**Look** at the top item **without removing** it.'],
      ['isEmpty()', 'Is the stack empty? true/false.'],
      ['size()', 'How many items are on it.'],
    ] }, hook: 'PEEK = just a peek, no touching.' },
    { t: 'check', q: 'Push 1, 2, 3, 4 in that order. What does the first **pop** return?', o: ['1', '2', '3', '4'], a: 3, why: 'LIFO: 4 went in last, so it comes out first.' },
    { t: 'idea', h: 'Why Nadia used peek', p: 'Victor wanted to **pop** everything, destroying evidence. Nadia used **peek** and **isEmpty**: she read the top without removing anything.' },
    { t: 'idea', h: 'Abstract Data Type (ADT)', p: 'An **ADT** is defined by **what operations you can do**, not **how it’s built inside**. A stack doesn’t tell you if it’s an array or a linked list underneath, and you don’t need to know.', w: { type: 'compare', cols: [
      { h: 'What you see (the interface)', lines: ['push, pop, peek', 'isEmpty, size'] },
      { h: 'What’s hidden (the implementation)', lines: ['an array?', 'a linked list?', 'something else?'] },
    ] }, hook: 'ADT = a TV remote. Use the buttons, ignore the circuits.' },
    { t: 'idea', h: 'Why abstraction helps', p: 'Zhang lists four benefits of data abstraction:', w: { type: 'flip', items: [['Modularity', 'Separate parts you can work on alone.'], ['Maintainability', 'Change the inside without breaking users.'], ['Reusability', 'Use the same stack everywhere.'], ['Security', 'Inside data is protected.']] } },
    { t: 'idea', h: 'Encapsulation and 3 abstractions', p: '**Encapsulation** (in OOP) hides an object’s internal state; you interact only through its interface. That’s a form of abstraction.', p2: 'Zhang’s three fundamental abstractions in programming languages: **data, procedure, control**.' },
    { t: 'check', q: 'Which operation returns the top item **without removing it**?', o: ['push', 'pop', 'peek', 'size'], a: 2 },
    { t: 'recap', items: ['**ADT** = defined by its operations, not its implementation.', '**Stack = LIFO.** push, pop (remove + return), peek (look only), isEmpty, size.', 'Benefits: modularity, maintainability, reusability, security.', 'Three abstractions: **data, procedure, control**.'], next: 'The top item is a photo: Mr. Gill and her father in 1987, captioned "co-founders".' },
  ],
  quiz: [
    ['An abstract data type (ADT) is defined by:', ['The programming language it is written in', 'The operations that can be performed on it, without specifying the implementation', 'Its memory address', 'The number of items it holds'], 1],
    ['A stack follows which principle?', ['FIFO', 'LIFO', 'Random access', 'Sorted order'], 1],
    ['Which stack operation returns the top item **without removing it**?', ['push', 'pop', 'peek', 'size'], 2],
    ['Which operation removes **and returns** the top item?', ['push', 'pop', 'peek', 'isEmpty'], 1],
    ['Items 1, 2, 3, 4 are pushed in that order. What does the first pop return?', ['1', '2', '3', '4'], 3],
    ['According to Zhang, a stack ADT "doesn’t reveal whether the stack is implemented as":', ['A class or an object', 'An array, a linked list, or something else', 'Python or Java', 'Public or private'], 1],
    ['Which is **not** a benefit of data abstraction listed by Zhang?', ['Modularity', 'Maintainability', 'Reusability', 'Faster typing speed'], 3],
    ['In OOP, encapsulation is a form of abstraction because it:', ['Makes every variable global', 'Hides an object’s internal state, allowing interaction only through a defined interface', 'Removes all methods', 'Prints the internal state'], 1],
    ['In Zhang’s array-based stack (Fig 1-2), `peek()` on an empty stack:', ['Crashes', 'Returns "Stack is empty"', 'Returns 0', 'Pushes a default item'], 1],
    ['Zhang’s three fundamental abstractions in programming languages are:', ['Data, procedure, control', 'Input, output, storage', 'Class, object, method', 'Array, stack, queue'], 0],
  ],
  notes: ['**Try it:** on an empty stack do push(A), push(B), peek(), push(C), pop(), size(). (Answer: [A] → [A,B] → peek returns B → [A,B,C] → pop returns C → size returns 2.)', '**A1 Part IV** asks you to add a Swap method. Design it yourself, following Zhang Fig 1-2.', '**Discussion spark:** name an everyday stack. What would "peek" be there?'],
});
