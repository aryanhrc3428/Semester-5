# Comprehensive Study Guide & Exam Notes: Chapter 1 — Introduction to Machine Learning

---

## Module 1: What is Machine Learning? (Foundations & Core Logic)

### 1. The Core Paradigm Shift: Traditional Programming vs. Machine Learning

* **Traditional Computing (Algorithm-Driven):**
* **Input:** Data + Algorithm (Explicit instructions) $\to$ **Output:** Result.
* **Requirements:** We must fully understand the exact mechanism mapping input to output (e.g., sorting an array of numbers).


* **Machine Learning (Data-Driven Induction):**
* **Input:** Data + Desired Output (or observations) $\to$ **Output:** Learned Model/Algorithm.
* **Logic:** For many real-world tasks (e.g., spam detection, face recognition), humans can recognize patterns effortlessly but cannot articulate the explicit, deterministic rule set in code. Where human algorithmic knowledge is lacking, data bridges the gap.



```
Traditional Programming:
  [Data] + [Hand-Coded Algorithm] --------> [Output]

Machine Learning:
  [Data] + [Observed Targets / Experience] -> [Learner] -> [Learned Model / Algorithm]

```

### 2. Formal Definition of Machine Learning

> **Definition:** Machine learning is programming computers to optimize a performance criterion using example data or past experience.

* **Structural Decomposition:**
* **Model Family $g(x \mid \theta)$:** A mathematical function family chosen prior to training (e.g., linear model, polynomial, neural network).
* **Parameters $\theta$:** The adjustable dials of the model adjusted during training.
* **Learning Algorithm:** The optimization routine that searches the parameter space to minimize a loss function (error criterion) over sample data.
* **Inference:** Evaluating $g(x \mid \theta^*)$ on unseen inputs $x$ using the optimal parameters $\theta^*$.



### 3. The Underlying Assumption: The Data-Generating Process

* **Why can machines learn from past data?**
* Data is **not completely random**. Physical, economic, and behavioral phenomena follow underlying probabilistic laws (e.g., consumers buying beer frequently buy chips; temperatures drop in winter).
* **Stationarity / Continuity Assumption:** The near future will behave similarly to the past when the training sample was collected ($P_{\text{future}} \approx P_{\text{past}}$).
* **Approximation Theory:** Even if the true process is excessively complex or partially obscured, a sufficiently expressive mathematical model can construct a useful approximation that captures key regularities.



### 4. Dual Role of Computer Science & Statistics in ML

* **Statistics:** Supplies the mathematics of **inference from finite samples** (estimation, hypothesis testing, confidence bounds).
* **Computer Science:**
* **Training Phase:** Provides scalable data structures and optimization algorithms (computational and memory efficiency) to process large datasets.
* **Inference Phase:** Ensures the learned model evaluates fast enough in deployment, meeting real-time latency and storage constraints.



---

### Brain Teaser 1: The Sorting vs. Filtering Paradox

> **Question:** We have thousands of examples of unsorted lists and their correctly sorted counterparts. Why do we not train a Machine Learning model to learn sorting?
> **Logical Solution:**
> 1. We already possess optimal, exact deterministic algorithms for sorting (e.g., Merge Sort with $O(n \log n)$ time and 100% mathematical guarantees).
> 2. An ML model is an inductive approximation that relies on statistical correlations. It risks outputting an unsorted or hallucinated element with non-zero error probability.
> 3. Machine learning is needed when an exact algorithm is **unknown, non-viable, or non-stationary**, not when provably optimal deterministic solutions exist.
> 
> 

---

## Module 2: The Major Learning Paradigms

```
                           Machine Learning
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    ▼                             ▼                             ▼
Supervised Learning     Unsupervised Learning         Reinforcement Learning
 • Target outputs $y$    • No labels / supervisor      • Sequential decisions
 • Learn $x \to y$       • Find structure/density      • Policy optimization
 ├─ Classification       ├─ Clustering                 • Delayed rewards
 └─ Regression           ├─ Density Estimation         • Exploitation vs.
                         └─ Dimensionality Reduction     Exploration

```

---

## Module 3: Supervised Learning — Classification & Regression

### 1. Classification

* **Objective:** Map an input feature vector $\mathbf{x} \in \mathbb{R}^d$ to a discrete class label $y \in \{C_1, C_2, \dots, C_K\}$.
* **The Discriminant Function:** A surface or rule separating regions assigned to different classes:

$$\text{Assign } \mathbf{x} \to C_i \quad \text{if } g_i(\mathbf{x}) > g_j(\mathbf{x}) \quad \forall j \neq i$$


* **Example — Credit Scoring (2-Class):**
* Inputs: $\mathbf{x} = [\text{Income}, \text{Savings}]^T$.
* Rule:

$$\text{IF } \text{income} > \theta_1 \text{ AND } \text{savings} > \theta_2 \text{ THEN Low-Risk } (+) \text{ ELSE High-Risk } (-)$$


* The decision boundary in the 2D feature space is an orthogonal threshold step aligned with the axes:



```
Savings
  ^
  │          High-Risk (-)    │    Low-Risk (+)
  │                           │
θ2┼───────────────────────────┘
  │
  │          High-Risk (-)
  │
  └───────────────────────────┼───────────────> Income
                              θ1

```

* **Probabilistic Classification:** Rather than a hard $0/1$ decision, estimate posterior probabilities $P(Y = C_k \mid \mathbf{X} = \mathbf{x})$.
* **Logic:** Allows pairing statistical predictions with **decision theory / loss matrices** (e.g., the economic cost of approving a defaulter is much worse than denying a solvent applicant).



### 2. Regression

* **Objective:** Map input $\mathbf{x}$ to a continuous numeric output $y \in \mathbb{R}$.
* **Model:** $y = g(\mathbf{x} \mid \theta) + \epsilon$, where $\epsilon$ is unexplained random noise with zero mean.
* **Linear Case (Univariate):**

$$g(x \mid w, w_0) = w x + w_0$$


* **Polynomial Extension (Nonlinear):**

$$g(x \mid \mathbf{w}) = w_k x^k + \dots + w_1 x + w_0$$


* **Optimization Criterion:** Minimize mean squared error over the training set of size $N$:

$$E(\mathbf{w}) = \frac{1}{2N} \sum_{t=1}^N \left( y^t - g(x^t \mid \mathbf{w}) \right)^2$$



### 3. Key Classification Applications & Domain Challenges

1. **Optical Character Recognition (OCR):**
* *Challenge:* Infinite variations in handwriting stroke, pen thickness, slant, size.
* *Logic:* Individual characters have stroke invariants; human language contains redundant sequential transitions ($P(w_{t} \mid w_{t-1})$) allowing contextual correction of ambiguous glyphs.


2. **Face Recognition:**
* *Challenge:* 3D face projections vary drastically with illumination, pose, expression, and occlusions (glasses, facial hair).
* *Logic:* Faces have symmetric structural topologies (eyes relative to nose and mouth).


3. **Medical Diagnosis:**
* *Challenge:* Missing features (expensive/invasive tests not performed) and asymmetric misclassification costs.
* *Logic:* Introduces a **rejection option**—if confidence is below a safety threshold, the model declines prediction and defers to a physician.


4. **Speech Recognition:**
* *Challenge:* Temporal signal length variation, acoustic variations across accents and genders.
* *Logic:* Combines an acoustic model (phoneme identification) with a statistical language model.



### 4. Value-Added Uses of Supervised Models

* **Knowledge Extraction:** Inspecting the learned weights or decision rules reveals which features drive the underlying process.
* **Compression:** Replacing millions of raw data points with a compact parameterized formula $g(\mathbf{x} \mid \theta^*)$ compresses data into a functional representation.
* **Outlier / Anomaly Detection:** Instances where observed reality conflicts with model predictions ($\vert{}y - g(\mathbf{x})\vert{} > \tau$) indicate rare events or fraud.

---

### Brain Teaser 2: The Asymmetric Medical Diagnosis Dilemma

> **Question:** A machine learning classifier predicts whether a patient has a benign cyst ($y=0$) or a malignant tumor ($y=1$). The classifier achieves 99% overall accuracy by predicting $y=0$ for every single patient. Why is this model unacceptable, and how must the optimization objective change?
> **Logical Solution:**
> 1. In malignant tumor screening, the dataset is typically imbalanced (e.g., 99% benign, 1% malignant).
> 2. Zero-rule predictions yield high accuracy while failing entirely on the critical minority class.
> 3. **Asymmetric Loss Logic:** The cost of a False Negative (classifying a malignant tumor as benign, delaying life-saving treatment) is orders of magnitude higher than a False Positive (classifying a benign cyst as malignant, resulting in a confirmatory biopsy).
> 4. The objective must minimize **Expected Risk** using a loss matrix $L_{ij}$ (cost of predicting class $i$ when true class is $j$):
> 
> $$\mathcal{R}(\alpha_i \mid \mathbf{x}) = \sum_j L_{ij} P(C_j \mid \mathbf{x})$$
> 
> 
> 
> 

---

## Module 4: Unsupervised Learning & Pattern Discovery

### 1. Definition and Goal

* **Definition:** Learning in the absence of external supervisor targets ($y$ is not provided). Given a dataset $\mathcal{X} = \{\mathbf{x}^t\}_{t=1}^N$, find internal patterns, clusters, or probability distributions.
* **Density Estimation:** Inferring the probability density function $p(\mathbf{x})$ to quantify which regions of the feature space are dense versus sparse.

### 2. Clustering & Its Variants

* **Customer Segmentation:** Grouping customers by shared transactional and demographic traits without predefined group names; used for targeted marketing and Customer Relationship Management (CRM).
* **Vector Quantization / Image Compression:**
* Raw pixel: 24-bit RGB space ($2^{24} \approx 16.7$ million possible colors).
* Clustering identifies the $K$ dominant color centroids in the image (e.g., $K=64 \implies 6\text{ bits}$).
* Storing the centroid codebook and assigning each pixel a 6-bit index compresses the image footprint fourfold ($24 \to 6$ bits per pixel).


* **Document Clustering (Bag of Words Model):**
* Vocabulary dictionary $\mathcal{V}$ of size $D$ (ignoring stop words like "the", "and", and applying morphological stemming).
* Vector representation: $\mathbf{x} \in \{0, 1\}^D$, where $x_i = 1$ if word $i$ appears in the text.
* Distance metrics (e.g., Cosine similarity or Jaccard index) cluster articles by topic (politics, sports, science).


* **Bioinformatics:**
* **Motif Discovery:** Unsupervised discovery of recurring short amino acid sequences across proteins that correspond to essential functional or structural binding domains.



---

## Module 5: Reinforcement Learning (Sequential Decision Making)

### 1. Core Architecture

* **Agent & Environment:** An agent interacts with an environment via actions $a_t$, receives observations/states $s_t$, and collects scalar rewards $r_t$.

```
                 ┌───────────────────────────┐
                 │        Environment        │
                 └──────┬─────────────▲──────┘
                        │             │
        Reward $r_{t}$  │             │ Action $a_{t}$
        State $s_{t}$   │             │
                        ▼             │
                 ┌────────────────────┴──────┐
                 │           Agent           │
                 │      (Learns Policy $\pi$) │
                 └───────────────────────────┘

```

### 2. The Nature of the Policy $\pi$

* An action's value cannot be judged in isolation; it matters only through its contribution to the long-term goal.
* **Policy $\pi(s)$:** A mapping from states to actions $\pi: \mathcal{S} \to \mathcal{A}$ that maximizes expected cumulative discounted reward:

$$R_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k+1}, \quad \gamma \in [0, 1)$$



### 3. Key Challenges

* **Credit Assignment Problem:** When a reward arrives late (e.g., winning a game of chess after 50 moves), determining which earlier intermediate move was responsible.
* **Exploration vs. Exploitation Dilemma:** Balancing trying unknown actions to discover better outcomes with taking known high-reward actions.
* **Partial Observability:** Sensors provide incomplete or noisy information (Partially Observable Markov Decision Processes — POMDPs).

---

## Module 6: Historical Foundations & Theoretical Cross-Currents

| Scientific Field | ML Terminology / Perspective | Key Contributions |
| --- | --- | --- |
| **Statistics** | Inference, Estimation, Discriminant Analysis | Parametric models, hypothesis testing, sampling theory, mathematically tractable small-sample regimes. |
| **Computer Science / AI** | Machine Learning, Heuristic Search | Adaptability, agent learning, representation of concepts, decision trees. |
| **Engineering / Pattern Recognition** | Pattern Classification | Non-parametric methods, empirical validation, sensor integration. |
| **Signal Processing / Electrical Eng.** | Adaptive Filtering, State Estimation | Hidden Markov Models (HMMs) for time series and acoustic processing. |
| **Neuroscience / Cybernetics** | Artificial Neural Networks | Distributed parallel processing, connectionism, multilayer perceptrons. |
| **Database Systems** | Knowledge Discovery in Databases (KDD), Data Mining | Scalable indexing, association rules, processing gigabyte/terabyte data streams. |

### The Core Modern Insight: Data & Compute vs. Algorithmic Novelty

Historical breakthroughs in machine learning often stemmed from scaling simpler statistical learning models (linear bounds, nearest neighbors, kernel machines) using larger datasets and sufficient computing power, rather than discovering wholly new paradigms.

---

## Module 7: Complete, Rigorous Solutions to Chapter 1 Exercises

### Exercise 1: Faxing vs. Optical Character Recognition (OCR)

> **Problem:** Discuss the advantages and disadvantages of faxing an image of a document versus converting it with an OCR system and sending the resulting text file. When is one preferable over the other?

#### 1. Detailed Comparison

| Dimension | Faxing (Raw Bitmap Image) | OCR Processing (Text File Conversion) |
| --- | --- | --- |
| **Bandwidth & Storage** | **Very High:** Transmits uncompressed/compressed 2D pixel grids. A page requires hundreds of kilobytes. | **Extremely Low:** Transmits ASCII/Unicode character codes. A page requires only $2 - 5\text{ KB}$. |
| **Information Fidelity** | Preserves layout, handwritten notes, signatures, drawings, stamps, and typographical nuances. | Strips graphical context; drops non-text sketches, margin notes, and original styling unless stored as rich metadata. |
| **Vulnerability to Noise** | Graceful degradation. If transmission encounters noise, humans can still read damaged visual characters. | Brittleness. A misrecognized character directly corrupts word spelling or numerical values (e.g., reading a check amount). |
| **Searchability & Editability** | Static image. Cannot be queried, searched by keywords, or programmatically manipulated. | Highly actionable. The text can be indexed, searched, edited in a word processor, or fed to downstream pipelines. |

#### 2. Preferred Scenarios

* **Faxing is preferable when:** Legal verification demands physical signatures, visual seals, hand annotations, or when layout preservation is mandatory.
* **OCR is preferable when:** Channel bandwidth is constrained, or the receiving system needs to search, index, or store the documents compactly.

---

### Exercise 2: Template-Matching OCR vs. Barcodes

> **Problem:** Let us say we are building an OCR and for each character, we store the bitmap of that character as a template that we match with the read character pixel by pixel. Explain when such a system would fail. Why are barcode readers still used?

#### 1. Failure Modes of Exact Bitmap Template Matching

* **Geometric Transformations:** Translations, rotations, scaling, and shear alter pixel alignment. A 1-pixel shift can drop pixel-by-pixel correlation to near zero:

$$\text{Similarity}(I, T) = \sum_{x,y} I(x,y) \cdot T(x,y)$$

* **Font & Style Diversity:** Serifs, font weights, italicization, and kerning alter the active pixels for the same character class.
* **Handwriting Variability:** Non-uniform stroke thickness, slant angles, and character sizes prevent fixed-grid alignment.
* **Sensor Noise & Degradation:** Ink bleeding, broken lines, paper texture, or scanning artifacts cause false mismatches.

#### 2. Why Barcodes Remain Essential

* **Purpose-Built Constrained Representations:** Barcodes (1D UPC or 2D QR codes) are designed for machine reading, avoiding the open-ended ambiguity of human writing.
* **Integrated Self-Clocking & Error Correction:** Standard barcodes include guard patterns for scale/orientation invariance and use Reed-Solomon error correction to recover data even if partly damaged or dirty.
* **Deterministic Decoding:** Barcodes decode with near-zero error rates at low computational cost.

---

### Exercise 3: Junk E-mail (Spam) Detection Systems

> **Problem:** Distinguish junk e-mail. What indicates spam? How can the computer detect junk through syntactic analysis? What should the computer do upon detecting junk (delete, quarantine, or highlight)?

#### 1. Indicators of Spam

* **Header & Metadata Inconsistencies:** Mismatched SPF/DKIM records, spoofed senders, open relays, or unusual routing hops.
* **Lexical & Syntactic Indicators:** Frequent urgency cues ("ACT NOW", "EXCLUSIVE OFFER"), excessive punctuation ("$$$", "!!!"), unnatural capitalization, and hidden text designed to bypass simple filters.
* **Structural Anomalies:** Heavy reliance on external links to low-reputation domains, obfuscated URLs, or single large images that hide text from basic string parsers.

#### 2. Detection via Syntactic & Textual Analysis

* **Tokenization & Morphological Analysis:** Parsing email text into normalized n-grams.
* **Bag of Words / Naive Bayes Modeling:** Estimating posterior spam probabilities via token occurrences:

$$P(\text{Spam} \mid w_1, w_2, \dots, w_n) \propto P(\text{Spam}) \prod_{i=1}^n P(w_i \mid \text{Spam})$$


* **Structural Parsing:** Inspecting HTML syntax for hidden tables, zero-font text, or URL redirects.

#### 3. Handling Detected Spam: Action Policy & Decision Theory

* **Automatic Deletion:** Too risky. The cost of a False Positive (permanently losing a critical work or personal email) is unacceptably high.
* **Direct Highlighting in Inbox:** Leaves clutter in the user's primary view, increasing cognitive load.
* **Quarantine (Junk/Spam Folder):** The optimal balance. High-probability spam is removed from view, while allowing the user to recover legitimate emails flagged by mistake.

---

### Exercise 4: Autonomous Taxi Design

> **Problem:** Define the constraints, inputs, outputs, passenger communication, and inter-vehicle communication ("language") for an automated taxi.

```
Sensory Inputs (Cameras, LiDAR, Radar, GPS, IMU) 
                  │
                  ▼
   ┌─────────────────────────────┐
   │ Autonomous Perception Engine │
   └──────────────┬──────────────┘
                  │ State Vector
                  ▼
   ┌─────────────────────────────┐
   │ Path Planning & Controller  │
   └──────────────┬──────────────┘
                  │ Control Actuation
                  ▼
   Actuator Outputs (Steering Angle, Throttle, Brake, Turn Indicators)

```

#### 1. System Constraints

* **Safety & Timing:** Real-time latency bounds ($<50\text{ ms}$ reaction times); zero tolerance for collisions.
* **Legal & Environmental:** Strict adherence to traffic codes under variable lighting, weather, and road conditions.
* **Kinematic Limits:** Acceleration and braking profiles must stay within comfortable limits for passengers.

#### 2. Inputs & Outputs

* **Sensory Inputs:** High-resolution cameras (object recognition), LiDAR point clouds (3D geometry), Radar (velocity sensing), GNSS/GPS (global localization), IMU (inertial pose), and wheel odometry.
* **Actuator Outputs:** Steering angle, throttle position, braking pressure, gear selection, and turn/hazard lighting.

#### 3. Passenger Communication

* Natural Language Processing (speech synthesis and recognition) alongside an interactive touchscreen for destination selection, route preferences, and emergency stop requests.

#### 4. Inter-Vehicle Communication (V2V / V2X "Language")

* **Need for Protocol:** Direct vehicle-to-vehicle telemetry transmits intent (e.g., planned lane changes, emergency deceleration, junction negotiation) more reliably than visual inferencing alone.
* **Architecture:** Dedicated Short-Range Communications (DSRC) or C-V2X broadcasting structured packets: `[VehicleID, Timestamp, Coordinate, Heading, Velocity, PlannedTrajectoryVector]`.

---

### Exercise 5: Association Analysis Generalization

> **Problem:** In basket analysis, how do you find dependence between items $X$ and $Y$ from transaction databases? How do you generalize this to more than two items?

#### 1. Two-Item Associations

Given transactions $\mathcal{D} = \{T_1, T_2, \dots, T_N\}$:

* **Support:** The probability that both items appear together in a transaction:

$$\text{Support}(X \to Y) = P(X \cap Y) = \frac{\text{Count}(X \cup Y)}{N}$$


* **Confidence:** The conditional probability that a basket contains $Y$ given it contains $X$:

$$\text{Confidence}(X \to Y) = P(Y \mid X) = \frac{P(X \cap Y)}{P(X)} = \frac{\text{Count}(X \cup Y)}{\text{Count}(X)}$$


* **Lift (Measuring True Dependence):**

$$\text{Lift}(X \to Y) = \frac{P(Y \mid X)}{P(Y)} = \frac{P(X \cap Y)}{P(X)P(Y)}$$


* $\text{Lift} = 1 \implies X$ and $Y$ are statistically independent.
* $\text{Lift} > 1 \implies$ Positive association (buying $X$ increases likelihood of buying $Y$).
* $\text{Lift} < 1 \implies$ Negative association (substitutes).



#### 2. Generalization to $K$-Itemsets ($X_1, X_2, \dots, X_m \to Y$)

* Evaluates conditional relationships for broader item combinations:

$$P(Y \mid X_1, X_2, \dots, X_m) = \frac{P(X_1, X_2, \dots, X_m, Y)}{P(X_1, X_2, \dots, X_m)}$$


* **Combinatorial Challenge:** A catalog of $d$ distinct products yields $2^d$ candidate itemsets.
* **Algorithmic Solution (Apriori Principle):**
* *Monotonicity Property:* Any subset of a frequent itemset must also be frequent. If $\{X, Y\}$ is infrequent, any larger set $\{X, Y, Z\}$ is guaranteed to be infrequent and can be pruned without scanning the entire database.



---

### Exercise 6: Predicting User Commands or Web Navigation

> **Problem:** How can you predict the next command typed by a user or the next webpage to be downloaded? When is such prediction useful, and when is it annoying?

#### 1. Prediction Mechanics

* **Markov Chains / Sequence Models:** Estimate transition probabilities across states:

$$P(S_{t+1} = s_j \mid S_t = s_i, S_{t-1} = s_{k}, \dots)$$


* **Feature-Based Classifiers:** Predict actions from context (current application, time of day, active directory, historical user workflows).
* **N-gram Language Models:** Condition character or token sequences on the trailing prefix.

#### 2. Utility vs. Friction

* **High Utility:**
* Auto-completing long terminal commands or complex paths.
* Web browser resource prefetching: Pre-caching predicted target links speeds up page loads over slow connections.


* **High Friction / Annoyance:**
* **False Intrusions:** Aggressive auto-correct that replaces intentional, specialized terms.
* **Bandwidth Waste:** Prefetching heavy media over metered mobile connections when predictions are wrong.
* **Interface Instability:** Dynamically rearranging UI elements or menu orders based on predictions breaks human spatial muscle memory.



---

### Exercise 7: Text Categorization via Lexical Features

> **Problem:** Analyze news categories (politics, sports, arts) using vocabulary frequencies. Address ambiguous terms (e.g., "goal").

#### 1. Category-Specific Feature Signatures

* **Politics:** High probability density over vocabulary $\mathcal{V}_{\text{pol}} = \{\text{cabinet, legislation, senator, election, treaty, fiscal}\}$.
* **Sports:** High probability density over vocabulary $\mathcal{V}_{\text{sprt}} = \{\text{tournament, championship, inning, striker, score, playoffs}\}$.
* **Arts:** High probability density over vocabulary $\mathcal{V}_{\text{arts}} = \{\text{exhibition, gallery, curator, choreography, premiere, canvas}\}$.

#### 2. Disambiguating Polysemous Words (e.g., "goal")

* The word *"goal"* appears in both sports (scoring in football/hockey) and politics/business (policy objectives).
* **Resolution via Contextual Co-occurrence:**

$$P(\text{Sports} \mid \text{"goal"}, \text{"goalkeeper"}, \text{"offside"}) \gg P(\text{Politics} \mid \text{"goal"}, \text{"goalkeeper"}, \text{"offside"})$$


$$P(\text{Politics} \mid \text{"goal"}, \text{"legislation"}, \text{"deficit"}) \gg P(\text{Sports} \mid \text{"goal"}, \text{"legislation"}, \text{"deficit"})$$


* **Formal Solution:** Rather than relying on unigrams (single words), use **bi-grams / n-grams** (e.g., "scored a goal" vs. "fiscal goal") or dense embeddings (e.g., Word2Vec, Transformer-based representations) that capture broader context.

---

### Exercise 8: High-Dimensional Vector Shifts in Face Recognition

> **Problem:** A $100 \times 100$ image in row-major order forms a 10,000-dimensional vector. Shifting the image by 1 pixel to the right creates a distant vector in $\mathbb{R}^{10000}$. How can we build recognizers robust to such distortions?

#### 1. Why Raw Euclidean Distance Fails

Let vector $\mathbf{x}_1$ be an unshifted image and $\mathbf{x}_2$ be the identical image shifted right by 1 pixel:

$$\Vert{}\mathbf{x}_1 - \mathbf{x}_2\Vert{}_2^2 = \sum_{p} (I(x, y) - I(x-1, y))^2$$

In edge-heavy regions (high spatial gradients), adjacent pixel values differ substantially. Even though the visual content is identical, the Euclidean distance in pixel space is large:

```
Pixel Array 1:  [ 0,  0, 255, 255,  0]
Pixel Array 2:  [ 0,  0,   0, 255, 255] (Shifted by 1)
Squared Diff:   (0) + (0) + (255)^2 + (0) + (255)^2  ---> Very large distance!

```

#### 2. Engineering Invariance

* **Shift-Invariant Representations:**
* Compute spatial features that pool over local regions rather than relying on exact pixel locations (e.g., Convolutional Neural Networks with local pooling).
* Extract gradient distributions that tolerate minor offsets (e.g., HOG — Histogram of Oriented Gradients, or SIFT descriptors).


* **Face Alignment & Canonical Normalization:**
* Detect facial landmarks (pupils, tip of nose, corners of mouth).
* Use an affine transform to map the image into a standardized coordinate system before calculating similarities.


* **Data Augmentation:**
* Introduce shifted, scaled, and rotated variations into the training set, forcing the classifier to learn features that ignore translation noise.



---

### Exercise 9: Handwriting Feature Extraction

> **Problem:** Identify features that discriminate between two individuals writing the same word (e.g., "machine").

#### Measurable Handwriting Invariants

1. **Geometric & Spatial Ratios:**
* Aspect ratio of characters (height-to-width proportions).
* Slant/tilt angle (measured as the dominant angle of vertical strokes relative to the baseline).
* Ratio of ascenders/descenders (e.g., the vertical extent of 'h' relative to 'a', 'c', or 'e').


2. **Topological Structural Features:**
* Loop closure characteristics: Are loops in 'a' and 'e' open or closed?
* Dot placement: Horizontal and vertical offset of the dot over 'i' relative to its stem.


3. **Stroke Curvature & Connection Dynamics:**
* Pen-up events: Is the script cursive (continuous strokes) or printed (discrete glyphs)?
* Terminal stroke behavior: Tapering, hooks, or abrupt endings at the tails of letters like 'e'.



---

### Exercise 10: Depreciation Percentage vs. Absolute Used Car Prices

> **Problem:** In estimating the price of a used car, why does it make more sense to estimate percent depreciation over original price rather than absolute price?

#### 1. Mathematical Heteroscedasticity

* The variance of absolute car price errors scales with vehicle tier:
* A $\$3,000$ prediction error on an entry-level $\$6,000$ car is a $50\%$ error, skewing customer decisions.
* A $\$3,000$ error on an exotic $\$150,000$ vehicle is negligible ($2\%$).


* Modeling absolute price directly produces **heteroscedasticity** (variance of the error term depends on the input features), violating standard Ordinary Least Squares assumptions:

$$\text{Var}(\epsilon \mid X) \neq \sigma^2$$

#### 2. Scale Invariance & Generalization

* Let $P_0$ be the manufacturer's suggested retail price (MSRP), and $y \in$ be the fractional depreciation:

$$\text{Price}_{\text{used}} = P_0 \cdot (1 - y)$$


* Depreciation curves follow consistent physical patterns driven by wear, age, and mileage, regardless of baseline retail price:

```
Value ($)
 ^
 │ $100k MSRP ──┐
 │               └───┐
 │                   └───  High absolute drop ($)
 │
 │  $20k MSRP ──┐
 │               └───┐     Lower absolute drop ($)
 │                   └───
 └─────────────────────────> Age / Mileage
  (Both follow similar proportional depreciation curves: ~15% per year)

```

* Modeling depreciation as a percentage normalizes the target variable, stabilizing regression variance and improving generalization across economy and luxury tiers alike.

---

## Module 8: Exam Preparation — Core Theoretical Questions

### Question 1: Induction vs. Deduction

> **Question:** Distinguish between **Deduction** and **Induction**. Which one forms the core of Machine Learning, and what fundamental risk does it carry?

* **Answer:**
* **Deduction:** Deriving specific conclusions from known, general axioms or deterministic premises (e.g., "All humans are mortal; Socrates is human; therefore Socrates is mortal"). Deductive conclusions are guaranteed to be true if the premises hold.
* **Induction:** Formulating general rules or models from finite empirical observations (e.g., "Every swan observed so far is white; therefore all swans are white").
* Machine learning is fundamentally **inductive** (generalizing a model from training data).
* **Fundamental Risk:** Inductive leaps do not guarantee universal truth. Models can overfit spurious patterns in the training set or fail when encountering unobserved domains (the Black Swan problem).



---

### Question 2: Parametric vs. Non-parametric Modeling

> **Question:** In Section 1.3, the text contrasts early statistical models with engineering pattern recognition. Detail the structural difference between **parametric** and **non-parametric** methods.

* **Answer:**
* **Parametric Methods:**
* Assume a fixed functional form for the distribution or target mapping (e.g., Gaussian distribution, linear discriminant $g(x) = \mathbf{w}^T\mathbf{x} + w_0$).
* The number of parameters $\vert{}\theta\vert{}$ is fixed and independent of the training sample size $N$.
* *Advantage:* Computationally efficient, low sample complexity if the distributional assumption holds.
* *Disadvantage:* High bias if the true process deviates from the chosen functional form.


* **Non-parametric Methods:**
* Make minimal assumptions about the underlying distribution (e.g., $k$-Nearest Neighbors, Parzen windows).
* The effective parameters scale with the size of the training dataset.
* *Advantage:* Highly flexible; can fit complex, arbitrary decision boundaries.
* *Disadvantage:* Higher computational cost during inference and prone to overfitting if not regularized.




---

### Question 3: The Role of Inductive Bias

> **Question:** What is **Inductive Bias**, and why is it impossible for a machine learning algorithm to learn without it?

* **Answer:**
* **Definition:** Inductive bias is the set of prior assumptions a learner uses to predict outputs for unseen inputs beyond the observed data.
* **Why It Is Indispensable:**
* For a finite set of $N$ training points, there are infinitely many mathematical functions that can interpolate them perfectly.
* Without prior assumptions (such as preferring smoother functions, lower-degree polynomials, or margin maximization), a model has no basis to favor one interpolation over any other for a new test point.
* Under the **No Free Lunch Theorem**, an algorithm with no prior assumptions performs no better than random guessing over all possible data distributions. Inductive bias is what enables learning to generalize.


---
---
---

# Linear Regression & Regression Evaluation Metrics

*(Comprehensive Analytical & Exam Preparation Guide)*

---

## Module 1: Foundational Architecture & The Seven Core Inquiries

### 1. The Core Philosophy of Linear Regression

* **Supervised Learning for Continuous Responses:** Linear regression is a supervised parametric learning method designed to predict a quantitative (continuous) response variable $Y \in \mathbb{R}$ from a vector of features $X = (X_1, X_2, \dots, X_p)^T$.
* **The Best Linear Approximation:** In physical, biological, and economic domains, the true mapping $Y = f(X) + \epsilon$ is rarely perfectly linear. Linear regression acts as the optimal first-order Taylor-like approximation to the conditional expectation function:

$$\mathbb{E}[Y \mid X] \approx \beta_0 + \beta_1 X_1 + \dots + \beta_p X_p$$



It provides an interpretable baseline that directly informs regularized models (Ridge, Lasso), generalized linear models (GLMs), and deep linear layers.

---

### 2. The Seven Core Regression Inquiries

When analyzing datasets (such as the classical Advertising case study with predictors $X = \{\text{TV}, \text{Radio}, \text{Newspaper}\}$ and target $Y = \text{Sales}$), linear regression systematically answers seven structural questions:

1. **Existence of an Association:** Does any linear relationship exist between the predictors and the response? Tested via the omnibus hypothesis:

$$H_0: \beta_1 = \beta_2 = \dots = \beta_p = 0$$


2. **Strength of the Relationship:** How closely do the observed values scatter around the fitted surface? Quantified via the Residual Standard Error (RSE) and Mean Squared Error (MSE).
3. **Feature Attribution (Variable Selection):** Which specific subsets of predictors drive the response, and which are superfluous noise? Resolved via partial $F$-tests, information criteria (AIC, BIC, Mallows' $C_p$), and stepwise selection.
4. **Magnitude of the Effect:** What is the marginal rate of change in $Y$ for each additional unit of $X_j$? Quantified by the partial slope parameter $\beta_j$ and its associated confidence interval.
5. **Prediction Accuracy & Bounding:** Given a novel configuration $\mathbf{x}_0$, what is the predicted response $\hat{y}_0$, and what are its probabilistic error bounds? Resolved via confidence intervals for the mean response versus prediction intervals for an individual observation.
6. **Linearity Assessment:** Does the marginal return remain constant across all scales of $X_j$? Diagnosed via residual vs. fitted value plots, residual curvature tests, and polynomial extensions.
7. **Synergy / Interaction Effects:** Does spending simultaneously on two channels yield a super-additive effect?

$$\text{Synergy} \implies \frac{\partial^2 \mathbb{E}[Y \mid X]}{\partial X_j \partial X_k} \neq 0$$



Modeled mathematically by including multiplicative product terms $\beta_{jk}(X_j X_k)$.

---

### 3. Population Regression Line vs. Sample Least Squares Line

A fundamental statistical distinction exists between the unobservable population reality and our sample-based estimate:

```
        True (Unobservable) State of Nature               Empirical Sample (Observed)
    ┌──────────────────────────────────────────┐      ┌─────────────────────────────────┐
    │ Population Regression Function (PRF):    │      │ Sample Regression Function (SRF):│
    │        Y = β₀ + β₁X + ε                  │      │        ŷ = β̂₀ + β̂₁X             │
    │  • β₀, β₁ are fixed, unknown constants.  │ ───> │  • β̂₀, β̂₁ are random variables │
    │  • ε represents irreducible random error │ OLS  │    computed from sample data.   │
    │    with E[ε] = 0, Var(ε) = σ².           │      │  • Varies from sample to sample.│
    └──────────────────────────────────────────┘      └─────────────────────────────────┘

```

* **The Logic of Unbiasedness:**
The sample estimators $\hat{\beta}_0$ and $\hat{\beta}_1$ are random variables because they inherit the stochastic sampling variability of $Y$. An estimator is **unbiased** if its sampling distribution is centered on the true parameter:

$$\mathbb{E}[\hat{\beta}_0] = \beta_0 \quad \text{and} \quad \mathbb{E}[\hat{\beta}_1] = \beta_1$$



A single dataset of size $n$ may produce an overestimate or an underestimate. However, if an experiment is repeated across 10,000 independent samples of size $n$, the arithmetic average of those 10,000 empirical lines matches the true population line.

---

## Module 2: Simple Linear Regression & Ordinary Least Squares (OLS)

### 1. Mathematical Formulation

Given a single scalar predictor $X$, the theoretical data-generating process is:


$$Y = \beta_0 + \beta_1 X + \epsilon$$

* **$\beta_0$ (Intercept):** $\mathbb{E}[Y \mid X = 0]$. The baseline level of the response when the predictor is completely absent.
* **$\beta_1$ (Slope):** $\frac{\Delta \mathbb{E}[Y]}{\Delta X}$. The expected incremental change in $Y$ per 1-unit increase in $X$.
* **$\epsilon$ (Error Term):** An unobserved random variable acting as a surrogate for omitted causal factors, measurement noise, and fundamental environmental stochasticity. Assumed to satisfy:

$$\mathbb{E}[\epsilon \mid X] = 0, \quad \text{Var}(\epsilon \mid X) = \sigma^2$$



---

### 2. Residuals & The Least Squares Objective

Given $n$ paired training instances $\{(x_i, y_i)\}_{i=1}^n$, the predicted value for instance $i$ is:


$$\hat{y}_i = \hat{\beta}_0 + \hat{\beta}_1 x_i$$


The $i$-th **residual** $e_i$ measures the vertical prediction error:


$$e_i = y_i - \hat{y}_i = y_i - (\hat{\beta}_0 + \hat{\beta}_1 x_i)$$

The Ordinary Least Squares (OLS) criterion seeks the parameter vector $(\hat{\beta}_0, \hat{\beta}_1)$ that minimizes the **Residual Sum of Squares (RSS)**:


$$\text{RSS}(\hat{\beta}_0, \hat{\beta}_1) = \sum_{i=1}^n e_i^2 = \sum_{i=1}^n (y_i - \hat{\beta}_0 - \hat{\beta}_1 x_i)^2$$

* **Why Square the Residuals? (The Underlying Logic):**
1. **Cancellation Prevention:** Minimizing $\sum e_i$ is degenerate; huge positive and negative errors would sum to zero, allowing wildly inaccurate lines to appear "optimal."
2. **Differentiability:** Absolute deviations $|e_i|$ have non-differentiable cusps at $e_i = 0$, requiring linear programming. Squared deviations yield smooth, convex parabolas with clean, closed-form analytic derivatives.
3. **Maximum Likelihood Equivalence:** Under the assumption that the noise is Gaussian ($\epsilon_i \overset{\text{iid}}{\sim} \mathcal{N}(0, \sigma^2)$), minimizing the sum of squared residuals is mathematically identical to maximizing the Gaussian log-likelihood function.
4. **Heavy Penalty for Outliers:** Squaring penalizes large deviations quadratically, forcing the line to accommodate points sitting far from the central mass.



---

### 3. Step-by-Step Calculus Derivation of the OLS Normal Equations

```
   Y ^
     │                           ● (x_i, y_i)
     │                          /│
     │                         / │ e_i = y_i - ŷ_i (Residual)
     │                        /  ▼
     │                       /───● (x_i, ŷ_i) Fitted point
     │                      /
     │                     /  Regression line: ŷ = β̂₀ + β̂₁X
     │                    /
     │                   /
     └──────────────────/──────────────────────> X

```

To find the global minimizers, calculate the gradient of $\text{RSS}$ with respect to $\hat{\beta}_0$ and $\hat{\beta}_1$, and set each partial derivative to zero.

#### Derivation of $\hat{\beta}_0$:

$$\frac{\partial \text{RSS}}{\partial \hat{\beta}_0} = \sum_{i=1}^n 2(y_i - \hat{\beta}_0 - \hat{\beta}_1 x_i)(-1) = -2 \sum_{i=1}^n (y_i - \hat{\beta}_0 - \hat{\beta}_1 x_i) = 0$$


Divide by $-2n$:


$$\frac{1}{n}\sum_{i=1}^n y_i - \hat{\beta}_0 - \hat{\beta}_1 \left(\frac{1}{n}\sum_{i=1}^n x_i\right) = 0 \implies \bar{y} - \hat{\beta}_0 - \hat{\beta}_1 \bar{x} = 0$$

$$\mathbf{\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}}$$

> **Fundamental Geometric Invariant:** The OLS regression line **must pass through the center of mass (centroid)** of the dataset, $(\bar{x}, \bar{y})$. At $X = \bar{x}$, $\hat{Y} = (\bar{y} - \hat{\beta}_1 \bar{x}) + \hat{\beta}_1 \bar{x} = \bar{y}$.

#### Derivation of $\hat{\beta}_1$:

$$\frac{\partial \text{RSS}}{\partial \hat{\beta}_1} = \sum_{i=1}^n 2(y_i - \hat{\beta}_0 - \hat{\beta}_1 x_i)(-x_i) = -2 \sum_{i=1}^n x_i (y_i - \hat{\beta}_0 - \hat{\beta}_1 x_i) = 0$$


Substitute $\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}$ into the equation:


$$\sum_{i=1}^n x_i \left[ (y_i - \bar{y}) - \hat{\beta}_1 (x_i - \bar{x}) \right] = 0$$

$$\sum_{i=1}^n x_i (y_i - \bar{y}) = \hat{\beta}_1 \sum_{i=1}^n x_i (x_i - \bar{x})$$

Using the algebraic properties of sample deviations around the mean:


$$\sum_{i=1}^n (y_i - \bar{y}) = 0 \implies \bar{x} \sum_{i=1}^n (y_i - \bar{y}) = 0$$


Subtracting zero from the left-hand side:


$$\sum_{i=1}^n x_i (y_i - \bar{y}) - \bar{x} \sum_{i=1}^n (y_i - \bar{y}) = \sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})$$


Similarly, for the right-hand side:


$$\sum_{i=1}^n x_i (x_i - \bar{x}) - \bar{x} \sum_{i=1}^n (x_i - \bar{x}) = \sum_{i=1}^n (x_i - \bar{x})^2$$

Equating the two yields the OLS slope estimator:


$$\mathbf{\hat{\beta}_1 = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^n (x_i - \bar{x})^2} = \frac{\text{Cov}(X, Y)}{\text{Var}(X)} = r_{XY} \frac{s_Y}{s_X}}$$


where $r_{XY}$ is the sample Pearson correlation coefficient, $s_Y$ is the sample standard deviation of $Y$, and $s_X$ is the sample standard deviation of $X$.

---

### Brain Teaser 1: The Asymmetry of Inverted Regressions

> **Question:** Suppose you regress $Y$ onto $X$ and obtain an estimated slope $\hat{\beta}_1 = 0.5$. If you now take the exact same dataset and regress $X$ onto $Y$ to obtain slope $\hat{\alpha}_1$, will $\hat{\alpha}_1 = \frac{1}{0.5} = 2.0$? Why or why not?
> **Logical Solution:**
> **No, $\hat{\alpha}_1$ will not equal $2.0$ (unless the correlation is perfect, $|r_{XY}| = 1$).**
> **Proof:**
> 
> $$\hat{\beta}_1 = r_{XY} \frac{s_Y}{s_X}, \quad \hat{\alpha}_1 = r_{XY} \frac{s_X}{s_Y}$$
> 
> 
> 
> Multiply the two estimated slopes together:
> 
> $$\hat{\beta}_1 \cdot \hat{\alpha}_1 = \left(r_{XY} \frac{s_Y}{s_X}\right) \left(r_{XY} \frac{s_X}{s_Y}\right) = r_{XY}^2$$
> 
> 
> 
> Since $r_{XY}^2 \le 1$ for any real-world dataset with scatter:
> 
> $$\hat{\alpha}_1 = \frac{r_{XY}^2}{\hat{\beta}_1} \le \frac{1}{\hat{\beta}_1}$$
> 
> 
> 
> **The Underlying Geometry:** Regressing $Y$ on $X$ minimizes vertical squared distances $\sum (y_i - \hat{y}_i)^2$, treating $X$ as an exact coordinate. Regressing $X$ on $Y$ minimizes horizontal squared distances $\sum (x_i - \hat{x}_i)^2$, treating $Y$ as exact. Because the two objectives project errors onto orthogonal dimensions, the slopes are not algebraic inverses of each other.

---

## Module 3: Statistical Inference & Standard Errors

### 1. The Classical Gauss-Markov Assumptions

The Gauss-Markov theorem states that under four conditions, the OLS estimator is **BLUE** (Best Linear Unbiased Estimator — lowest variance among all linear unbiased estimators):

1. **Linearity in Parameters:** $Y = \beta_0 + \sum_{j=1}^p \beta_j X_j + \epsilon$.
2. **Strict Exogeneity:** $\mathbb{E}[\epsilon_i \mid \mathbf{X}] = 0$. The error term has zero conditional expectation given the design matrix (no unmodeled confounding).
3. **Homoscedasticity:** $\text{Var}(\epsilon_i \mid \mathbf{X}) = \sigma^2 < \infty$ for all $i = 1, \dots, n$. The variance of the error is constant across all predictor levels.
4. **No Autocorrelation:** $\text{Cov}(\epsilon_i, \epsilon_j \mid \mathbf{X}) = 0$ for all $i \neq j$. Observations are mutually uncorrelated.
5. *(For exact hypothesis testing)* **Normality of Errors:** $\epsilon_i \overset{\text{iid}}{\sim} \mathcal{N}(0, \sigma^2)$.

---

### 2. Sampling Variance of OLS Estimators

$$\text{SE}(\hat{\beta}_1)^2 = \frac{\sigma^2}{\sum_{i=1}^n (x_i - \bar{x})^2}$$

$$\text{SE}(\hat{\beta}_0)^2 = \sigma^2 \left[ \frac{1}{n} + \frac{\bar{x}^2}{\sum_{i=1}^n (x_i - \bar{x})^2} \right]$$


where $\sigma^2 = \text{Var}(\epsilon)$.

* **The Logic of $\text{SE}(\hat{\beta}_1)$:**
* **Noise Scale ($\sigma^2$):** Higher irreducible noise directly inflates parameter estimation error.
* **Leverage of the Predictor ($\sum (x_i - \bar{x})^2$):** The spread of $X$ appears in the denominator. Spreading the observations farther along the horizontal axis provides greater mechanical leverage, making it harder for random noise in $Y$ to tilt the estimated slope.


* **The Logic of $\text{SE}(\hat{\beta}_0)$:**
* If $\bar{x} = 0$, then $\text{SE}(\hat{\beta}_0)^2 = \frac{\sigma^2}{n}$, which matches the variance of the sample mean $\bar{y}$.
* As the center of the data $\bar{x}$ shifts away from zero, any slight tilt in the slope $\hat{\beta}_1$ pivots the line over the distance $\bar{x}$, magnifying the intercept's estimation uncertainty by $\bar{x}^2 / \sum (x_i - \bar{x})^2$.



---

### 3. Estimating $\sigma^2$: The Residual Standard Error (RSE)

Because the population error variance $\sigma^2$ is unknown, it must be estimated from the observed sample residuals:


$$\mathbf{\hat{\sigma}^2 = s^2 = \frac{\text{RSS}}{n - 2} = \frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{n - 2}}$$

$$\mathbf{\text{RSE} = \sqrt{\frac{\text{RSS}}{n - 2}}}$$

* **Why divide by $n - 2$? (The Degrees-of-Freedom Logic):**
* The sample residuals $e_i$ are constrained by the two OLS normal equations: $\sum e_i = 0$ and $\sum e_i x_i = 0$.
* Estimating two parameters ($\hat{\beta}_0, \hat{\beta}_1$) imposes two linear constraints on the $n$-dimensional residual vector $\mathbf{e}$, confining it to an $(n - 2)$-dimensional subspace.
* Dividing by $n - 2$ corrects for this constraint, ensuring that the estimator is strictly unbiased: $\mathbb{E}[\text{RSE}^2] = \sigma^2$. Dividing by $n$ would systematically underestimate the true variance.



---

### 4. Hypothesis Testing on Coefficients ($t$-Test & Confidence Intervals)

To determine if the predictor has a statistically significant linear association with $Y$:

* **Null Hypothesis:** $H_0: \beta_1 = 0$ (no relationship; model simplifies to $Y = \beta_0 + \epsilon$).
* **Alternative Hypothesis:** $H_a: \beta_1 \neq 0$ (a significant linear association exists).

Under $H_0$ and the Gaussian error assumption, the standardized test statistic follows a Student's $t$-distribution with $n - 2$ degrees of freedom:


$$t = \frac{\hat{\beta}_1 - 0}{\text{SE}(\hat{\beta}_1)} \sim t_{n-2}$$

* **$p$-Value Interpretation:** The probability of observing an estimate as large as or larger than $\vert{}\hat{\beta}_1\vert{}$ by pure chance, assuming the true slope $\beta_1$ is zero. A small $p$-value ($p < 0.05$ or $p < 0.01$) warrants rejecting $H_0$.
* **Confidence Intervals:** A $95\%$ confidence interval for the true slope is:

$$\hat{\beta}_1 \pm t_{n-2, \, 0.975} \cdot \text{SE}(\hat{\beta}_1)$$



If $n > 30$, $t_{n-2, \, 0.975} \approx 2$, yielding the standard approximation: $\hat{\beta}_1 \pm 2 \cdot \text{SE}(\hat{\beta}_1)$.

---

## Module 4: Multiple Linear Regression & Matrix Algebra

### 1. Model Formulation & Partial Regression Slopes

When predicting $Y$ with $p$ distinct features:


$$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \dots + \beta_p X_p + \epsilon$$

* **Interpretation of $\beta_j$ (Partial Regression Coefficient):**

$$\beta_j = \frac{\partial \mathbb{E}[Y \mid X_1, \dots, X_p]}{\partial X_j}$$



$\beta_j$ represents the average change in $Y$ per unit increase in $X_j$, **holding all other predictors $X_{k \neq j}$ strictly constant**.

---

### 2. Matrix Formulation of OLS

For $n$ observations and $p$ features, define the system as $\mathbf{Y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}$:


$$\mathbf{Y} = \begin{bmatrix} y_1 \\ y_2 \\ \vdots \\ y_n \end{bmatrix}_{n \times 1}, \quad  \mathbf{X} = \begin{bmatrix} 1 & x_{11} & \dots & x_{1p} \\ 1 & x_{21} & \dots & x_{2p} \\ \vdots & \vdots & \ddots & \vdots \\ 1 & x_{n1} & \dots & x_{np} \end{bmatrix}_{n \times (p+1)}, \quad  \boldsymbol{\beta} = \begin{bmatrix} \beta_0 \\ \beta_1 \\ \vdots \\ \beta_p \end{bmatrix}_{(p+1) \times 1}, \quad  \boldsymbol{\epsilon} = \begin{bmatrix} \epsilon_1 \\ \epsilon_2 \\ \vdots \\ \epsilon_n \end{bmatrix}_{n \times 1}$$

* **RSS in Matrix Quadratic Form:**

$$\text{RSS}(\boldsymbol{\beta}) = (\mathbf{Y} - \mathbf{X}\boldsymbol{\beta})^T (\mathbf{Y} - \mathbf{X}\boldsymbol{\beta}) = \mathbf{Y}^T\mathbf{Y} - 2\boldsymbol{\beta}^T\mathbf{X}^T\mathbf{Y} + \boldsymbol{\beta}^T\mathbf{X}^T\mathbf{X}\boldsymbol{\beta}$$


* **Matrix Calculus Minimization:**

$$\nabla_{\boldsymbol{\beta}} \text{RSS} = -2\mathbf{X}^T\mathbf{Y} + 2\mathbf{X}^T\mathbf{X}\boldsymbol{\beta} = \mathbf{0}$$


$$\mathbf{X}^T\mathbf{X}\boldsymbol{\beta} = \mathbf{X}^T\mathbf{Y} \quad (\text{The Normal Equations})$$


$$\mathbf{\hat{\boldsymbol{\beta}} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{Y}}$$


* **The Projection ("Hat") Matrix $\mathbf{H}$:**

$$\mathbf{\hat{Y}} = \mathbf{X}\hat{\boldsymbol{\beta}} = \mathbf{X}(\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{Y} = \mathbf{H}\mathbf{Y}$$



$\mathbf{H} = \mathbf{X}(\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T$ projects the observed vector $\mathbf{Y} \in \mathbb{R}^n$ orthogonally onto the $(p+1)$-dimensional column space $\text{Col}(\mathbf{X})$.
* **Symmetric:** $\mathbf{H}^T = \mathbf{H}$
* **Idempotent:** $\mathbf{H}^2 = \mathbf{H}$
* **Trace (Degrees of Freedom):** $\text{tr}(\mathbf{H}) = \text{rank}(\mathbf{X}) = p + 1$


* **The Residual Projection Matrix $(\mathbf{I} - \mathbf{H})$:**

$$\mathbf{e} = \mathbf{Y} - \mathbf{\hat{Y}} = (\mathbf{I} - \mathbf{H})\mathbf{Y}$$



It projects $\mathbf{Y}$ onto the orthogonal complement of $\text{Col}(\mathbf{X})$.

$$\text{tr}(\mathbf{I} - \mathbf{H}) = n - (p + 1) = n - p - 1$$



This directly produces the denominator degrees of freedom for multiple regression:

$$\mathbf{\text{RSE} = \sqrt{\frac{\text{RSS}}{n - p - 1}} = \sqrt{\frac{\mathbf{e}^T\mathbf{e}}{n - p - 1}}}$$



---

## Module 5: Multicollinearity & The Surrogate Variable Effect

### 1. The Surrogate Variable Phenomenon (Omitted Variable Bias)

A counterintuitive outcome often arises when transitioning from simple to multiple linear regression:

* **The Advertising Paradox:**
* *Simple Regression:* $\text{Sales} \approx 12.35 + 0.055 \times \text{Newspaper}$ ($p = 0.00115 \implies$ highly significant).
* *Multiple Regression:* $\text{Sales} \approx 2.94 + 0.046 \times \text{TV} + 0.189 \times \text{Radio} - 0.001 \times \text{Newspaper}$ ($p = 0.86 \implies$ entirely insignificant).


* **The Underlying Logic:**
* As shown in the empirical correlation matrix, $\text{Cor}(\text{Radio}, \text{Newspaper}) = 0.354$.
* Markets with high radio advertising budgets also received larger newspaper budgets.
* In the simple model, $\text{Newspaper}$ acted as a **surrogate** for $\text{Radio}$, receiving credit for sales gains driven by radio advertising.
* Once the multiple regression controls for $\text{Radio}$ (holding it constant), the true unique association of newspaper advertising is revealed to be zero.


* **The Real-World Analog (Confounding):**
A simple regression shows that higher ice cream consumption at beaches strongly predicts shark attacks ($p < 0.001$). Ice cream does not cause shark attacks; rather, hot summer temperatures drive both beach attendance (and shark encounters) and ice cream sales. Adding temperature to the regression drives the ice cream coefficient to zero.

---

### Brain Teaser 2: Perfect Multicollinearity & Matrix Singularity

> **Question:** An analyst models employee compensation using experience ($X_1$, in years), age ($X_2$, in years), and birth year ($X_3$). The model is fit on a single day such that $\text{Age} + \text{Birth Year} = 2026$. What happens to the matrix $(\mathbf{X}^T\mathbf{X})^{-1}$, the estimated coefficients, and the standard errors?
> **Logical Solution:**
> 1. The third column is an exact linear combination of the intercept column and the second column:
> 
> $$\mathbf{x}_3 = 2026 \cdot \mathbf{x}_0 - \mathbf{x}_2$$
> 
> 
> 2. The columns of the design matrix $\mathbf{X}$ are linearly dependent, so its rank is strictly less than $p + 1$:
> 
> $$\text{rank}(\mathbf{X}) < p + 1$$
> 
> 
> 3. The square matrix $(\mathbf{X}^T\mathbf{X})$ has a determinant of zero ($\det(\mathbf{X}^T\mathbf{X}) = 0$), making it non-invertible (singular).
> 4. The normal equations have infinitely many solutions that yield the exact same minimum RSS. The parameter estimates are mathematically non-identifiable, and their estimated standard errors diverge to infinity ($\text{SE}(\hat{\beta}_j) \to \infty$).
> 
> 

---

## Module 6: Hypothesis Testing in Multiple Regression ($F$-Tests vs. $t$-Tests)

### 1. The Overall Omnibus $F$-Test

To test whether *any* predictor in the model is related to the response:

* **Null Hypothesis:** $H_0: \beta_1 = \beta_2 = \dots = \beta_p = 0$
* **Alternative Hypothesis:** $H_a: \text{at least one } \beta_j \neq 0$
* **The $F$-Statistic:**

$$\mathbf{F = \frac{(\text{TSS} - \text{RSS}) / p}{\text{RSS} / (n - p - 1)}}$$



where $\text{TSS} = \sum_{i=1}^n (y_i - \bar{y})^2$ is the Total Sum of Squares, and $\text{RSS} = \sum_{i=1}^n (y_i - \hat{y}_i)^2$.
* **Expectation Analysis Under $H_0$ and $H_a$:**
* Under standard assumptions:

$$\mathbb{E}\left[\frac{\text{RSS}}{n - p - 1}\right] = \sigma^2$$


* If $H_0$ is true:

$$\mathbb{E}\left[\frac{\text{TSS} - \text{RSS}}{p}\right] = \sigma^2 \implies \mathbf{\mathbb{E}[F] \approx 1}$$


* If $H_a$ is true:

$$\mathbb{E}\left[\frac{\text{TSS} - \text{RSS}}{p}\right] = \sigma^2 + \frac{f(\boldsymbol{\beta})}{p} > \sigma^2 \implies \mathbf{F > 1}$$





---

### 2. Why Individual $t$-Tests Fail When $p$ is Large (The Multiple Testing Problem)

Why look at the overall $F$-statistic if statistical software already outputs individual $t$-tests and $p$-values for every coefficient?

* **The Fallacy of Component-Wise Testing:**
Suppose a model has $p = 100$ candidate features, and the null hypothesis holds for all of them ($\beta_1 = \dots = \beta_{100} = 0$).
* If each coefficient is tested at $\alpha = 0.05$, the probability of a false rejection (Type I error) on a single test is:

$$P(\text{Type I Error}) = 0.05$$


* The probability that all 100 tests correctly fail to reject is:

$$P(\text{No False Discoveries}) = (1 - 0.05)^{100} = (0.95)^{100} \approx 0.0059$$


* The **Family-Wise Error Rate (FWER)** is:

$$\text{FWER} = 1 - 0.0059 = \mathbf{0.9941 \quad (99.41\%)}$$




* **The Logic of the $F$-Test:**
Testing 100 features individually makes finding several "significant" $p$-values ($100 \times 0.05 \approx 5$ on average) almost certain by pure chance. The overall $F$-test evaluates all $p$ predictors jointly in a single test, maintaining the overall Type I error rate at exactly $\alpha = 0.05$, regardless of how large $p$ is.

---

### 3. Testing Subsets of Predictors (Partial $F$-Test)

To test whether a specific group of $q$ variables can be dropped from a larger model:

* **Full Model:** Uses all $p$ variables; produces residual sum of squares $\text{RSS}_{\text{full}}$ with $n - p - 1$ degrees of freedom.
* **Reduced Model:** Drops the $q$ chosen variables, retaining $p - q$ predictors; produces residual sum of squares $\text{RSS}_{\text{reduced}}$ with $n - (p - q) - 1$ degrees of freedom.
* **Partial $F$-Statistic:**

$$\mathbf{F = \frac{(\text{RSS}_{\text{reduced}} - \text{RSS}_{\text{full}}) / q}{\text{RSS}_{\text{full}} / (n - p - 1)} \sim F_{q, \, n - p - 1}}$$


* **Equivalence to the $t$-Test for a Single Variable ($q = 1$):**
When testing the exclusion of a single variable $X_j$ ($q = 1$), the partial $F$-test is mathematically equivalent to the square of its individual $t$-test statistic:

$$\mathbf{F_{1, \, n - p - 1} = t_{n - p - 1}^2}$$



---

## Module 7: Variable Selection & High-Dimensional Breakdown ($p > n$)

### 1. The Combinatorial Bottleneck

Identifying the optimal subset of predictors by fitting every possible combination requires testing $2^p$ distinct models:

* If $p = 2 \implies 2^2 = 4$ models.
* If $p = 30 \implies 2^{30} = 1,073,741,824$ models (computationally infeasible).

### 2. Classical Stepwise Selection Algorithms

1. **Forward Selection:**
* Begins with the null model (intercept-only: $\hat{y} = \bar{y}$).
* Fits $p$ separate simple regressions; adds the predictor that yields the lowest RSS.
* At each subsequent step, adds the predictor that produces the greatest reduction in RSS for the expanded model.
* Stops when all remaining variables fail to meet a performance threshold (e.g., based on AIC, BIC, or partial $F$ $p$-value).
* **Advantage:** Computationally tractable ($O(p^2)$ model fits) and works even in high-dimensional settings where $p > n$.


2. **Backward Elimination:**
* Starts with the full model containing all $p$ variables.
* Removes the variable with the largest $p$-value (least statistically significant).
* Refits the $(p - 1)$-variable model and repeats the process.
* Stops when all retained predictors have $p$-values below a chosen threshold (e.g., $\alpha = 0.05$).
* **Critical Limitation:** Fails completely when $p > n$, because $(\mathbf{X}^T\mathbf{X})$ is singular, preventing the initial full model from being fit via OLS.


3. **Mixed Selection (Bidirectional Elimination):**
* Begins like forward selection, adding variables sequentially based on fit improvements.
* However, as new variables enter the model, shared correlations can inflate the $p$-values of previously added predictors.
* At each step, mixed selection checks the significance of all currently included variables, removing any whose $p$-values rise above a removal threshold.
* Continues until all included variables are significant and no excluded variable offers a significant improvement.



---

### 3. The High-Dimensional Setting ($p > n$)

When the number of candidate predictors exceeds the sample size ($p > n$):

1. **Rank Deficiency:** $\text{rank}(\mathbf{X}) \le \min(n, p+1) = n < p + 1$. The matrix $(\mathbf{X}^T\mathbf{X})$ has zero determinant and cannot be inverted.
2. **Interpolation & Overfitting:** With more parameters than data points, the linear system is underdetermined. Infinitely many hyperplanes can interpolate all $n$ observations perfectly, resulting in $\text{RSS} = 0$.
3. **Metric Breakdown:** The residual degrees of freedom $n - p - 1$ becomes negative or zero. Formulas with $n - p - 1$ in the denominator (such as RSE and the $F$-statistic) divide by zero or negative values, making standard OLS diagnostics unusable without regularization (Ridge, Lasso) or screening.

---

## Module 8: Prediction Uncertainty (Confidence vs. Prediction Intervals)

When using a fitted model to make predictions at a new target point $\mathbf{x}_0 = (1, x_{01}, \dots, x_{0p})^T$, there are three distinct sources of uncertainty:

1. **Reducible Parameter Estimation Error:** The estimated coefficient vector $\hat{\boldsymbol{\beta}}$ is a sample-based approximation of the true population vector $\boldsymbol{\beta}$.
2. **Reducible Model Bias:** Assuming a linear functional form is almost always an approximation of a more complex reality.
3. **Irreducible Random Error ($\epsilon$):** Even if the true population parameters $\boldsymbol{\beta}$ were known with complete certainty, individual observations still deviate from the line due to intrinsic random noise $\epsilon_0 \sim \mathcal{N}(0, \sigma^2)$.

```
   Y ^
     │                                 Prediction Interval (Y₀)
     │                           ┌─────────────────────────────────┐
     │                           │                                 │
     │                 Confidence│Interval [E(Y|x₀)]               │
     │                   ┌───────┴───────┐                         │
     │                   │       ●       │                         │
     │                   └───────┬───────┘                         │
     │                           │   ŷ₀ = x₀ᵀβ̂                     │
     │                           │                                 │
     │                           └─────────────────────────────────┘
     │                                   
     └───────────────────────────────────●─────────────────────────> X
                                         x₀

```

### 1. Confidence Interval for the Mean Response $\mathbb{E}[Y \mid X = \mathbf{x}_0]$

* **Target:** The unobservable average outcome over a large population of instances at $\mathbf{x}_0$:

$$f(\mathbf{x}_0) = \mathbf{x}_0^T \boldsymbol{\beta}$$


* **Sampling Variance:**

$$\text{Var}(\hat{f}(\mathbf{x}_0)) = \text{Var}(\mathbf{x}_0^T \hat{\boldsymbol{\beta}}) = \sigma^2 \mathbf{x}_0^T (\mathbf{X}^T\mathbf{X})^{-1} \mathbf{x}_0$$


* **$95\%$ Confidence Interval:**

$$\mathbf{\hat{y}_0 \pm t_{n - p - 1, \, 0.975} \cdot \text{RSE} \sqrt{\mathbf{x}_0^T (\mathbf{X}^T\mathbf{X})^{-1} \mathbf{x}_0}}$$



---

### 2. Prediction Interval for an Individual Future Observation $Y_0$

* **Target:** The specific response value for a single new entity:

$$Y_0 = \mathbf{x}_0^T \boldsymbol{\beta} + \epsilon_0$$


* **Total Prediction Variance:**

$$\text{Var}(\hat{y}_0 - Y_0) = \text{Var}(\mathbf{x}_0^T \hat{\boldsymbol{\beta}} - \mathbf{x}_0^T \boldsymbol{\beta} - \epsilon_0) = \underbrace{\text{Var}(\hat{f}(\mathbf{x}_0))}_{\text{Reducible}} + \underbrace{\sigma^2}_{\text{Irreducible}} = \sigma^2 \left[ 1 + \mathbf{x}_0^T (\mathbf{X}^T\mathbf{X})^{-1} \mathbf{x}_0 \right]$$


* **$95\%$ Prediction Interval:**

$$\mathbf{\hat{y}_0 \pm t_{n - p - 1, \, 0.975} \cdot \text{RSE} \sqrt{1 + \mathbf{x}_0^T (\mathbf{X}^T\mathbf{X})^{-1} \mathbf{x}_0}}$$



> **Core Difference:** The prediction interval includes the $+1$ term under the square root to account for the irreducible variance $\sigma^2$ of the single observation. As a result, **a prediction interval is always strictly wider than a confidence interval** around the same point.

---

## Module 9: Comprehensive Regression Evaluation Metrics

*(Covering all primary regression loss functions, scale-dependent errors, scale-independent errors, robust losses, and information-theoretic model selection criteria.)*

### 1. Residual Sum of Squares (RSS)

$$\mathbf{\text{RSS} = \sum_{i=1}^n (y_i - \hat{y}_i)^2 = \mathbf{e}^T\mathbf{e}}$$

* **Logic:** The foundational objective function minimized by OLS. It measures the total unmodeled variance across the dataset.
* **Limitation:** Scale-dependent and grows linearly with sample size $n$, making it unsuitable for comparing fits across datasets of different sizes.

---

### 2. Mean Squared Error (MSE)

$$\mathbf{\text{MSE} = \frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2 = \frac{\text{RSS}}{n}}$$

* **Logic:** Normalizes RSS by sample size $n$, representing the expected squared loss $\mathbb{E}[(Y - \hat{Y})^2]$.
* **Characteristics:** Heavily penalizes large outlier errors because deviations are squared. Expressed in squared units of the target variable ($[Y]^2$), which limits direct real-world interpretability.

---

### 3. Root Mean Squared Error (RMSE)

$$\mathbf{\text{RMSE} = \sqrt{\text{MSE}} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}}$$

* **Logic:** Taking the square root converts the error back into the natural units of the response variable $Y$.
* **Characteristics:** Maintains the quadratic penalty on large errors while providing an intuitive measure of the typical magnitude of prediction errors.

---

### 4. Residual Standard Error (RSE)

$$\mathbf{\text{RSE} = \sqrt{\frac{\text{RSS}}{n - p - 1}} = \sqrt{\frac{n}{n - p - 1} \cdot \text{MSE}}}$$

* **Logic:** While RMSE divides by $n$ (the maximum likelihood estimator of error variance, which is biased downward), RSE divides by the residual degrees of freedom $n - p - 1$.
* **Important Behavior:** When adding an uninformative predictor to a regression model, RSS may drop slightly, but $p$ increases by 1. If the decrease in RSS is smaller than the loss of a degree of freedom, **RSE will actually increase**. This makes RSE a simple check against adding useless features.

---

### 5. Mean Absolute Error (MAE)

$$\mathbf{\text{MAE} = \frac{1}{n} \sum_{i=1}^n \vert{}y_i - \hat{y}_i\vert{}}$$

* **Logic:** Evaluates the average $L_1$ distance between observations and predictions. Corresponds to maximum likelihood estimation when the errors follow a Laplace (double exponential) distribution rather than a Gaussian distribution.
* **Comparison with RMSE:** MAE weights all errors linearly, making it much more robust to extreme outliers than RMSE.

```
Error Penalty
  ^
  │              / Squared Loss (MSE / RMSE penalty)
  │   \         / 
  │    \       /  
  │     \     /   
  │      \   /    Linear Loss (MAE penalty)
  │       \_/     
  └───────────────────────────────> Residual (y - ŷ)

```

---

### 6. Median Absolute Error (MedAE)

$$\mathbf{\text{MedAE} = \text{median}\left(\vert{}y_1 - \hat{y}_1\vert{}, \vert{}y_2 - \hat{y}_2\vert{}, \dots, \vert{}y_n - \hat{y}_n\vert{}\right)}$$

* **Logic:** Uses the sample median of the absolute residuals instead of the mean.
* **Robustness:** Completely unaffected by anomalous outliers. Even if up to 50% of the sample contains corrupted extreme values, MedAE reflects the typical prediction error of the central data mass.

---

### 7. Mean Absolute Percentage Error (MAPE) & Symmetric MAPE (sMAPE)

* **MAPE Formula:**

$$\mathbf{\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^n \left\vert{} \frac{y_i - \hat{y}_i}{y_i} \right\vert{}}$$


* **Advantage:** Scale-independent, expressing errors as intuitive percentage deviations.
* **Critical Limitations:**
1. Undefined if any true value $y_i = 0$ (division by zero).
2. Strongly asymmetric: It penalizes overestimates far more heavily than underestimates. An estimate can be at most 100% too low ($\hat{y} = 0 \implies \text{error} = 100\%$), but can be infinitely too high ($\hat{y} = 10y \implies \text{error} = 900\%$).




* **Symmetric MAPE (sMAPE):**

$$\mathbf{\text{sMAPE} = \frac{100\%}{n} \sum_{i=1}^n \frac{\vert{}y_i - \hat{y}_i\vert{}}{(\vert{}y_i\vert{} + \vert{}\hat{y}_i\vert{}) / 2}}$$



Bounds individual percentage errors between $0\%$ and $200\%$, providing a symmetric penalty for over- and under-predictions.

---

### 8. Robust Regression Losses (Huber Loss & Log-Cosh)

* **Huber Loss:** Blends the smoothness of MSE for small residuals with the outlier robustness of MAE for large residuals:

$$L_\delta(e_i) = \begin{cases}    \frac{1}{2} e_i^2 & \text{for } \vert{}e_i\vert{} \le \delta \\   \delta \left(\vert{}e_i\vert{} - \frac{1}{2}\delta\right) & \text{for } \vert{}e_i\vert{} > \delta    \end{cases}$$


* Smooth and differentiable everywhere, including at $e_i = 0$.
* Transitions to a linear penalty once errors exceed the threshold $\delta$, preventing outliers from dominating parameter estimation.


* **Log-Cosh Loss:**

$$L(e_i) = \ln(\cosh(y_i - \hat{y}_i))$$


* Behaves approximately like $\frac{1}{2}e_i^2$ for small errors and like $\vert{}e_i\vert{} - \ln(2)$ for large errors.
* Twice-differentiable everywhere, making it well-suited for second-order gradient-based optimization.



---

### 9. Information-Theoretic & Penalized Metrics

#### Mallows' $C_p$

For a model with $p$ predictors selected from a larger pool:


$$\mathbf{C_p = \frac{1}{n} (\text{RSS} + 2p\hat{\sigma}^2)}$$


where $\hat{\sigma}^2$ is an unbiased estimate of error variance from the full model containing all candidate features.

* **Logic:** Penalizes RSS by adding $2p\hat{\sigma}^2$ to account for the optimism of training error. A model with low bias will have $C_p \approx p$.

#### Akaike Information Criterion (AIC)

Derived from the empirical Kullback-Leibler divergence between the true data-generating distribution and the fitted model:


$$\text{AIC} = -2\ln(\hat{L}) + 2k$$


Under a Gaussian linear regression model with unknown $\sigma^2$, the number of parameters is $k = p + 2$ (including the intercept and error variance). Dropping constants:


$$\mathbf{\text{AIC} \propto n \ln\left(\frac{\text{RSS}}{n}\right) + 2p}$$

#### Bayesian Information Criterion (BIC / Schwarz Criterion)

Derived from a Laplace approximation to the Bayesian posterior model probability:


$$\text{BIC} = -2\ln(\hat{L}) + k \ln(n)$$


For a Gaussian linear regression model:


$$\mathbf{\text{BIC} \propto n \ln\left(\frac{\text{RSS}}{n}\right) + \ln(n)p}$$

* **Comparative Analysis (AIC vs. BIC):**
* For any dataset where $\ln(n) > 2$ (i.e., $n \ge 8$ observations), the penalty term $\ln(n)p$ in BIC is larger than the $2p$ penalty in AIC.
* Consequently, **BIC penalizes model complexity more heavily than AIC**, favoring simpler, sparser models as sample size grows.



---

## Module 10: Master Exam Question Bank

### Question 1: Deriving the Expectation of the Slope Estimator

> **Exam Question:** Prove that under the Gauss-Markov assumptions, the Ordinary Least Squares slope estimator $\hat{\beta}_1$ is an unbiased estimator of the true population parameter $\beta_1$ ($\mathbb{E}[\hat{\beta}_1] = \beta_1$).

#### Analytical Proof:

The OLS slope estimator is:


$$\hat{\beta}_1 = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^n (x_i - \bar{x})^2}$$


Define the deterministic weights:


$$k_i = \frac{x_i - \bar{x}}{\sum_{j=1}^n (x_j - \bar{x})^2}$$


Note two algebraic properties of these weights:

1. $\sum_{i=1}^n k_i = \frac{\sum (x_i - \bar{x})}{\sum (x_i - \bar{x})^2} = 0$
2. $\sum_{i=1}^n k_i x_i = \frac{\sum x_i(x_i - \bar{x})}{\sum (x_i - \bar{x})^2} = \frac{\sum (x_i - \bar{x})^2}{\sum (x_i - \bar{x})^2} = 1$

Express $\hat{\beta}_1$ as a linear combination of the observed responses $y_i$:


$$\hat{\beta}_1 = \sum_{i=1}^n k_i (y_i - \bar{y}) = \sum_{i=1}^n k_i y_i - \bar{y}\sum_{i=1}^n k_i = \sum_{i=1}^n k_i y_i$$


Substitute the true population model $y_i = \beta_0 + \beta_1 x_i + \epsilon_i$:


$$\hat{\beta}_1 = \sum_{i=1}^n k_i (\beta_0 + \beta_1 x_i + \epsilon_i) = \beta_0 \sum_{i=1}^n k_i + \beta_1 \sum_{i=1}^n k_i x_i + \sum_{i=1}^n k_i \epsilon_i$$


Applying the algebraic properties $\sum k_i = 0$ and $\sum k_i x_i = 1$:


$$\hat{\beta}_1 = \beta_0(0) + \beta_1(1) + \sum_{i=1}^n k_i \epsilon_i = \beta_1 + \sum_{i=1}^n k_i \epsilon_i$$


Take expectations conditioned on the fixed predictors $\mathbf{X}$:


$$\mathbb{E}[\hat{\beta}_1 \mid \mathbf{X}] = \beta_1 + \sum_{i=1}^n k_i \mathbb{E}[\epsilon_i \mid \mathbf{X}]$$


Under the strict exogeneity assumption, $\mathbb{E}[\epsilon_i \mid \mathbf{X}] = 0$. Therefore:


$$\mathbf{\mathbb{E}[\hat{\beta}_1] = \beta_1} \quad \blacksquare$$

---

### Question 2: Resolving Inconsistencies Between $t$-Tests and the Omnibus $F$-Test

> **Exam Question:** In a multiple linear regression model with two highly correlated predictors $X_1$ and $X_2$ ($\text{Cor}(X_1, X_2) = 0.98$), the overall $F$-test yields a tiny $p$-value ($p < 0.0001$), but the individual $t$-tests for both $\hat{\beta}_1$ and $\hat{\beta}_2$ have large $p$-values ($p = 0.42$ and $p = 0.38$). Explain the statistical mechanism driving this apparent contradiction.

#### Analytical Solution:

1. **The Role of the Overall $F$-Test:**
The omnibus test evaluates the joint null hypothesis:

$$H_0: \beta_1 = 0 \text{ and } \beta_2 = 0$$



A significant $F$-test ($p < 0.0001$) confirms that the two predictors together explain a substantial amount of variation in $Y$.
2. **The Role of the Individual $t$-Tests:**
Each $t$-statistic tests the *partial* effect of adding that predictor to a model that already contains the other:

$$H_0: \beta_1 = 0 \mid X_2 \text{ is in the model}$$



Because $X_1$ and $X_2$ share $98\%$ of their information, either variable is largely redundant once the other is included.
3. **Variance Inflation via Multicollinearity:**
The variance of an individual slope estimator in multiple regression is:

$$\text{Var}(\hat{\beta}_j) = \frac{\sigma^2}{(1 - r_{12}^2) \sum_{i=1}^n (x_{ij} - \bar{x}_j)^2}$$



As $r_{12} \to 0.98$, the denominator term $(1 - r_{12}^2) = 1 - (0.98)^2 = 0.0396$ becomes very small. This inflates the variance by a Variance Inflation Factor ($\text{VIF}$) of:

$$\text{VIF} = \frac{1}{1 - 0.98^2} \approx 25.25$$



Inflating the standard error $\text{SE}(\hat{\beta}_j)$ depresses the $t$-statistic ($t = \hat{\beta}_j / \text{SE}(\hat{\beta}_j)$), resulting in large individual $p$-values even though the features are collectively informative.

---

### Question 3: Numerical Computation of Model Diagnostics

> **Exam Question:** An applied researcher fits a multiple linear regression model with $p = 3$ predictors on a sample of $n = 64$ observations.
> The calculated Total Sum of Squares is $\text{TSS} = 400.0$, and the Residual Sum of Squares is $\text{RSS} = 100.0$.
> 1. Calculate the Residual Standard Error (RSE).
> 2. Calculate the Root Mean Squared Error (RMSE).
> 3. Calculate the omnibus $F$-statistic and state its degrees of freedom.
> 4. Under $H_0: \beta_1 = \beta_2 = \beta_3 = 0$, what is the expected value of the $F$-statistic?
> 
> 

#### Step-by-Step Solution:

1. **Residual Standard Error (RSE):**

$$\text{RSE} = \sqrt{\frac{\text{RSS}}{n - p - 1}} = \sqrt{\frac{100.0}{64 - 3 - 1}} = \sqrt{\frac{100.0}{60}} = \sqrt{1.6667} \approx \mathbf{1.291}$$


2. **Root Mean Squared Error (RMSE):**

$$\text{RMSE} = \sqrt{\frac{\text{RSS}}{n}} = \sqrt{\frac{100.0}{64}} = \sqrt{1.5625} = \mathbf{1.250}$$


3. **Omnibus $F$-Statistic:**

$$F = \frac{(\text{TSS} - \text{RSS}) / p}{\text{RSS} / (n - p - 1)} = \frac{(400.0 - 100.0) / 3}{100.0 / (64 - 3 - 1)} = \frac{300.0 / 3}{100.0 / 60} = \frac{100.0}{1.6667} = \mathbf{60.0}$$


* **Degrees of Freedom:** Follows an $F$-distribution with $\mathbf{df_1 = 3}$ numerator degrees of freedom and $\mathbf{df_2 = 60}$ denominator degrees of freedom.


4. **Expected Value of the $F$-Statistic Under $H_0$:**
For an $F$-distribution with $d_2 > 2$ denominator degrees of freedom:

$$\mathbb{E}[F] = \frac{d_2}{d_2 - 2} = \frac{60}{60 - 2} = \frac{60}{58} \approx \mathbf{1.034}$$



Because the observed value $F = 60.0$ is far larger than $1.034$, the null hypothesis is decisively rejected.

---

### Question 4: Partial $F$-Test for a Multi-Variable Nested Model

> **Exam Question:** A model predicting patient blood pressure uses demographic factors: Age ($X_1$) and Weight ($X_2$), giving $\text{RSS}_{\text{reduced}} = 250.0$ on $n = 54$ patients.
> A cardiologist proposes adding three genetic biomarkers ($X_3, X_4, X_5$). The expanded model ($p = 5$) yields $\text{RSS}_{\text{full}} = 190.0$.
> Test the null hypothesis $H_0: \beta_3 = \beta_4 = \beta_5 = 0$ at significance level $\alpha = 0.05$. (Use critical value $F_{3, \, 48, \, 0.05} \approx 2.80$).

#### Step-by-Step Solution:

1. **Identify the Test Parameters:**
* Full model predictors: $p = 5$
* Number of omitted predictors: $q = 3$
* Sample size: $n = 54$
* Denominator degrees of freedom: $n - p - 1 = 54 - 5 - 1 = 48$


2. **Compute the Partial $F$-Statistic:**

$$F = \frac{(\text{RSS}_{\text{reduced}} - \text{RSS}_{\text{full}}) / q}{\text{RSS}_{\text{full}} / (n - p - 1)} = \frac{(250.0 - 190.0) / 3}{190.0 / 48} = \frac{60.0 / 3}{3.9583} = \frac{20.0}{3.9583} \approx \mathbf{5.053}$$


3. **Statistical Decision:**
* Critical Value: $F_{\text{crit}} = 2.80$.
* Since $F_{\text{observed}} = 5.053 > 2.80$, we **reject $H_0$** at $\alpha = 0.05$.
* **Conclusion:** The three genetic biomarkers collectively provide statistically significant explanatory power for blood pressure beyond what is captured by age and weight alone.



---

### Question 5: Evaluation Metric Diagnostics & Outlier Vulnerability

> **Exam Question:** A regression model is evaluated on a validation test set of $n = 5$ samples. The ground truth values and model predictions are:
> * $y = [10.0, 12.0, 14.0, 11.0, 13.0]$
> * $\hat{y} = [10.5, 11.5, 13.5, 11.0, 23.0]$
> 
> 
> 1. Calculate the MAE, MSE, and RMSE.
> 2. Calculate the Median Absolute Error (MedAE).
> 3. Discuss the effect of the single outlier in the fifth observation on these metrics.
> 
> 

#### Step-by-Step Calculations:

1. **Compute Residuals and Absolute/Squared Errors:**
* Observation 1: $e_1 = 10.0 - 10.5 = -0.5 \implies \vert{}e_1\vert{} = 0.5, \quad e_1^2 = 0.25$
* Observation 2: $e_2 = 12.0 - 11.5 = +0.5 \implies \vert{}e_2\vert{} = 0.5, \quad e_2^2 = 0.25$
* Observation 3: $e_3 = 14.0 - 13.5 = +0.5 \implies \vert{}e_3\vert{} = 0.5, \quad e_3^2 = 0.25$
* Observation 4: $e_4 = 11.0 - 11.0 = 0.0 \implies \vert{}e_4\vert{} = 0.0, \quad e_4^2 = 0.00$
* Observation 5: $e_5 = 13.0 - 23.0 = -10.0 \implies \vert{}e_5\vert{} = 10.0, \quad e_5^2 = 100.00$


2. **Compute Summary Metrics:**
* **MAE:**

$$\text{MAE} = \frac{0.5 + 0.5 + 0.5 + 0.0 + 10.0}{5} = \frac{11.5}{5} = \mathbf{2.30}$$


* **MSE:**

$$\text{MSE} = \frac{0.25 + 0.25 + 0.25 + 0.00 + 100.00}{5} = \frac{100.75}{5} = \mathbf{20.15}$$


* **RMSE:**

$$\text{RMSE} = \sqrt{20.15} \approx \mathbf{4.489}$$


* **MedAE:**
The sorted absolute errors are $\{0.0, 0.5, \mathbf{0.5}, 0.5, 10.0\}$.

$$\text{MedAE} = \mathbf{0.50}$$




3. **Diagnostic Analysis of the Outlier:**
* On the first four points, the model is highly accurate, with absolute errors never exceeding $0.5$.
* A single severe prediction error on observation 5 ($\vert{}e_5\vert{} = 10.0$) produces an error of $e_5^2 = 100.0$, which accounts for $\frac{100}{100.75} = \mathbf{99.26\%}$ of the total MSE.
* As a result, RMSE ($\approx 4.49$) is nearly double MAE ($2.30$), reflecting RMSE's quadratic sensitivity to extreme errors.
* By contrast, MedAE remains at **$0.50$**, cleanly isolating the typical performance of the model on the primary data mass from the isolated anomaly.

---
---
---

# Comprehensive Exam Revision Notes: Machine Learning

---

## Master Table of Contents

1. **Topic 1: Regression Evaluation Metrics**
* Conceptual Foundations & Error Modeling
* Scale-Dependent Error Metrics (RSS, MSE, RMSE, RSE, MAE, MedAE)
* Percentage & Relative Metrics (MAPE, sMAPE)
* Goodness-of-Fit Metrics ($R^2$ and Adjusted $R^2$)
* Information Criteria & Penalized Metrics (Mallows' $C_p$, AIC, BIC)
* Robust Regression Loss Functions (Huber Loss, Log-Cosh)
* Brain Teasers & Deep Logic
* High-Yield Exam Questions & Numerical Solutions


2. **Topic 2: Bayesian Learning & The Naive Bayes Classifier**
* Epistemological Foundations of Bayesian Learning
* Bayes' Theorem & The MAP vs. ML Principles
* The Bayes Optimal Classifier vs. MAP Predictions
* The Gibbs Sampling Classifier & Error Bounds
* The Naive Bayes Model: Structural Architecture & Derivation
* The Zero-Frequency Problem & The $m$-Estimate (Laplace Smoothing)
* Continuous-Valued Features: Gaussian Naive Bayes
* Text Classification: Multi-variate Bernoulli vs. Multinomial Models
* Brain Teasers & Deep Logic
* High-Yield Exam Questions & Step-by-Step Numerical Walkthroughs


3. **Topic 3: Instance-Based Learning & $k$-Nearest Neighbors ($k$-NN)**
* Lazy vs. Eager Learning Paradigm Comparison
* The $k$-NN Classifier: Mathematical Formalism
* 1-NN Decision Surfaces & Voronoi Tessellations
* $k$-NN for Continuous Targets (Locally Constant Regression)
* Distance-Weighted $k$-NN & Shepard’s Global Interpolation
* Distance Metrics: Euclidean, Manhattan, Minkowski, Mahalanobis
* Pre-Processing Mandate: Feature Scaling & Normalization
* The Curse of Dimensionality & Metric Degradation
* Computational Acceleration: $kd$-Trees & Ball Trees
* Brain Teasers & Deep Logic
* High-Yield Exam Questions & Proofs



---

# Topic 1: Regression Evaluation Metrics

---

## 1.1 Conceptual Foundations & Error Modeling

In regression, the target variable is continuous ($y_i \in \mathbb{R}$). Unlike classification—where errors are binary ($0$ or $1$)—regression errors possess **varying magnitudes, directions, and units of measurement**.

* **The Regression Residual:** For an observed data point $(x_i, y_i)$ and a model prediction $\hat{y}_i = f(x_i)$, the $i$-th residual $e_i$ is:

$$e_i = y_i - \hat{y}_i$$


* **The Goal of an Evaluation Metric:** A regression metric aggregates the $n$-dimensional residual vector $\mathbf{e} = [e_1, e_2, \dots, e_n]^T$ into a single scalar that quantifies model inadequacy, generalizability, and goodness-of-fit.

---

## 1.2 Scale-Dependent Error Metrics

```
                            Residual Vector: e = y - ŷ
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
      Squared Norm (L₂)                                     Absolute Norm (L₁)
    • Penalizes large errors                              • Robust to outliers
    • Differentiable everywhere                           • Not smooth at zero
    • Closely linked to Gaussian noise                    • Linked to Laplace noise
            │                                                     │
     ┌──────┴──────┐                                       ┌──────┴──────┐
     ▼             ▼                                       ▼             ▼
    MSE           RMSE                                    MAE          MedAE
 (Units: y²)   (Units: y)                              (Units: y)    (Units: y, 50%
                                                                     breakdown point)

```

### 1. Residual Sum of Squares (RSS)

$$\text{RSS} = \sum_{i=1}^n (y_i - \hat{y}_i)^2 = \mathbf{e}^T\mathbf{e}$$

* **Logic:** Foundational optimization objective in Ordinary Least Squares (OLS). It represents the unmodeled variance in the response variable.
* **Limitation:** Strongly scale-dependent and grows monotonically with sample size $n$, making it useless for comparing models evaluated across datasets of different sizes.

### 2. Mean Squared Error (MSE)

$$\text{MSE} = \frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2 = \frac{\text{RSS}}{n}$$

* **Logic:** Normalizes RSS by dividing by sample size $n$. It corresponds to the empirical expectation $\mathbb{E}[(Y - \hat{Y})^2]$. Under an unbiased estimator ($\mathbb{E}[\hat{y}] = \mathbb{E}[y]$), MSE equals the variance of the residuals: $\text{MSE} = \text{Var}(e)$.
* **Sensitivity:** Because errors are squared, a residual of $10$ contributes $100$ to the sum, whereas a residual of $1$ contributes $1$. It heavily penalizes models that make rare, catastrophic prediction errors.
* **Unit Issue:** Measured in the *squared units* of the response variable ($[y]^2$), which obscures intuitive real-world interpretation.

### 3. Root Mean Squared Error (RMSE)

$$\text{RMSE} = \sqrt{\text{MSE}} = \sqrt{\frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2}$$

* **Logic:** Taking the square root restores the metric to the natural scale of the target variable $y$.
* **Mathematical Bound:** For any sample:

$$\text{MAE} \le \text{RMSE} \le \sqrt{n} \cdot \text{MAE}$$



The equality $\text{RMSE} = \text{MAE}$ occurs if and only if all individual error magnitudes are identical ($\vert{}e_1\vert{} = \vert{}e_2\vert{} = \dots = \vert{}e_n\vert{}$). The divergence between RMSE and MAE directly reflects the variance of the error distribution.

### 4. Residual Standard Error (RSE)

$$\text{RSE} = \hat{\sigma} = \sqrt{\frac{\text{RSS}}{n - p - 1}} = \sqrt{\frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{n - p - 1}}$$


where $n$ is the sample size and $p$ is the number of predictors (excluding the intercept).

* **The Degrees-of-Freedom Logic:**
* In OLS, estimating $p + 1$ coefficients ($\beta_0, \beta_1, \dots, \beta_p$) imposes $p + 1$ linear constraints on the residuals: $\mathbf{X}^T\mathbf{e} = \mathbf{0}$.
* This restricts the residual vector to an $(n - p - 1)$-dimensional subspace. Dividing by $n - p - 1$ ensures that $\text{RSE}^2$ is an **unbiased estimator** of the true population noise variance $\sigma^2$:

$$\mathbb{E}[\text{RSE}^2] = \sigma^2$$


* *Crucial Behavior:* Adding an uninformative predictor lowers RSS slightly on the training set, but increases $p$ by $1$. If the drop in RSS does not offset the loss of a degree of freedom, **RSE will increase**, penalizing model over-parameterization.



### 5. Mean Absolute Error (MAE)

$$\text{MAE} = \frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|$$

* **Logic:** Evaluates the $L_1$ distance between predictions and actual values. It corresponds to Maximum Likelihood Estimation under the assumption of **Laplacian (double-exponential) distributed noise**:

$$p(\epsilon) = \frac{1}{2b}\exp\left(-\frac{|\epsilon|}{b}\right)$$


* **Outlier Robustness:** The penalty scales linearly with error size. Large outliers do not dominate the total loss.
* **Optimization Challenge:** The absolute value function has a non-differentiable sharp corner at $e_i = 0$, meaning standard gradient descent requires sub-gradient methods or linear programming.

### 6. Median Absolute Error (MedAE)

$$\text{MedAE} = \text{median}\left( |y_1 - \hat{y}_1|, |y_2 - \hat{y}_2|, \dots, |y_n - \hat{y}_n| \right)$$

* **Logic:** Calculates the middle value of the sorted absolute residuals.
* **Breakdown Point:** Possesses an asymptotic breakdown point of **$50\%$**. Up to half the dataset can be corrupted with arbitrary outliers without shifting the metric away from the central cluster of typical errors.

---

## 1.3 Percentage & Relative Error Metrics

### 1. Mean Absolute Percentage Error (MAPE)

$$\text{MAPE} = \frac{100\%}{n}\sum_{i=1}^n \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$

* **Advantage:** Dimensionless and scale-free; expresses error as a percentage, facilitating comparisons across disparate domains (e.g., comparing home prices in Tokyo vs. small-town rentals).
* **Structural Flaws:**
1. **Singularity at Zero:** If any $y_i = 0$, the formula divides by zero and fails.
2. **Asymmetric Penalty:** Severe over-predictions face no upper bound (e.g., $y = 10, \hat{y} = 100 \implies \text{error} = 900\%$), while under-predictions can never exceed $100\%$ (e.g., $y = 10, \hat{y} = 0 \implies \text{error} = 100\%$). This introduces an inherent bias toward models that under-predict.



### 2. Symmetric Mean Absolute Percentage Error (sMAPE)

$$\text{sMAPE} = \frac{100\%}{n}\sum_{i=1}^n \frac{|y_i - \hat{y}_i|}{(|y_i| + |\hat{y}_i|) / 2}$$

* **Logic:** Places the average of the actual and predicted values in the denominator, bounding each term between $0\%$ and $200\%$ and mitigating the penalty asymmetry of traditional MAPE.

---

## 1.4 Goodness-of-Fit Metrics: $R^2$ and Adjusted $R^2$

### 1. The Sum of Squares Partition Identity

The total variability in the response breaks down into explained and unexplained components:


$$\sum_{i=1}^n (y_i - \bar{y})^2 = \sum_{i=1}^n (\hat{y}_i - \bar{y})^2 + \sum_{i=1}^n (y_i - \hat{y}_i)^2$$

$$\mathbf{\text{TSS} = \text{ESS} + \text{RSS}}$$

* **TSS (Total Sum of Squares):** Total sample variation in $Y$ before fitting any predictors. Measures variance from the baseline model $\hat{y} = \bar{y}$.
* **ESS (Explained / Model Sum of Squares):** Variation captured by the fitted regression model.
* **RSS (Residual Sum of Squares):** Variation left unexplained by the regression model.

```
Total Variation (TSS) = Distance from Mean (y_i - ȳ)
 ┌─────────────────────────────────────────────────────────────────┐
 │                                                                 │
 │   Explained by Model (ESS)            Unexplained Error (RSS)   │
 │   Distance from Mean to Fit           Distance from Fit to Data │
 │         (ŷ_i - ȳ)                             (y_i - ŷ_i)       │
 └─────────────────────────────────────────────────────────────────┘
   (Valid only when the model includes an intercept, ensuring residuals sum to zero)

```

#### Analytical Proof of Orthogonality:

Rewrite:


$$(y_i - \bar{y}) = (\hat{y}_i - \bar{y}) + (y_i - \hat{y}_i)$$


Squaring both sides and summing over all $i$:


$$\sum_{i=1}^n (y_i - \bar{y})^2 = \sum_{i=1}^n (\hat{y}_i - \bar{y})^2 + \sum_{i=1}^n (y_i - \hat{y}_i)^2 + 2\sum_{i=1}^n (\hat{y}_i - \bar{y})(y_i - \hat{y}_i)$$


Expand the cross-product term:


$$\sum_{i=1}^n (\hat{y}_i - \bar{y})e_i = \sum_{i=1}^n \hat{y}_i e_i - \bar{y}\sum_{i=1}^n e_i$$


Under OLS with an intercept term:

1. The residuals sum to zero: $\sum_{i=1}^n e_i = 0$.
2. The fitted values and residuals are orthogonal: $\sum_{i=1}^n \hat{y}_i e_i = \mathbf{\hat{Y}}^T\mathbf{e} = (\mathbf{H}\mathbf{Y})^T(\mathbf{I} - \mathbf{H})\mathbf{Y} = \mathbf{Y}^T\mathbf{H}(\mathbf{I} - \mathbf{H})\mathbf{Y} = \mathbf{0}$ (since $\mathbf{H}$ is idempotent: $\mathbf{H}^2 = \mathbf{H}$).
Because the cross-product term vanishes identically:

$$\text{TSS} = \text{ESS} + \text{RSS} \quad \blacksquare$$



---

### 2. The Coefficient of Determination ($R^2$)

$$R^2 = 1 - \frac{\text{RSS}}{\text{TSS}} = \frac{\text{ESS}}{\text{TSS}}$$

* **Conceptual Definition:** The proportion of total variance in the dependent variable explained by the linear combination of predictors.
* **Range on Training Set (with Intercept):** $0 \le R^2 \le 1$.
* **Connection to Correlation:** In simple linear regression with one predictor:

$$R^2 = r_{XY}^2$$



In multiple linear regression, $R^2$ equals the squared Pearson correlation between observed and predicted values:

$$R^2 = \text{Cor}(Y, \hat{Y})^2$$


* **Fundamental Flaw of $R^2$:** Adding an additional predictor expands the column space of $\mathbf{X}$. The projection vector $\mathbf{\hat{Y}}$ cannot move farther from $\mathbf{Y}$ in Euclidean space. Thus, **training RSS never increases, and $R^2$ monotonically increases or remains flat** when new variables are added, even if they consist entirely of random noise.

---

### 3. Adjusted $R^2$

$$R_{\text{adj}}^2 = 1 - \left[ \frac{\text{RSS} / (n - p - 1)}{\text{TSS} / (n - 1)} \right] = 1 - (1 - R^2)\frac{n - 1}{n - p - 1}$$

* **Logic:** Penalizes the inclusion of unnecessary predictors by comparing the estimated residual variance ($\text{RSE}^2$) to the sample variance of $Y$.
* **Behavior:** $R_{\text{adj}}^2$ increases if and only if an added predictor reduces RSS by an amount that exceeds what would be expected by random chance (specifically, if the partial $t$-statistic of the added predictor satisfies $\vert{}t\vert{} > 1$).
* **Negative Values:** Unlike standard $R^2$, **$R_{\text{adj}}^2$ can turn negative** if the model fits worse than a simple horizontal line at $\bar{y}$ after accounting for the degrees-of-freedom penalty.

---

## 1.5 Information Criteria & Penalized Metrics

```
Criteria           Penalty Term        Behavior / Model Preference
─────────────────────────────────────────────────────────────────────────────
Mallows' C_p       + 2p σ̂²             Balances fit and parameter count; targets C_p ≈ p
AIC                + 2p                Minimizes KL divergence; favors predictive accuracy
BIC                + p · ln(n)         Stronger penalty when n ≥ 8; selects sparser, true models

```

### 1. Mallows' $C_p$

For a sub-model with $p$ predictors chosen from a total pool of $K$ available features:


$$C_p = \frac{\text{RSS}_p}{\hat{\sigma}_{\text{full}}^2} + 2p - n = \frac{1}{n}\left( \text{RSS}_p + 2p\hat{\sigma}_{\text{full}}^2 \right)$$


where $\hat{\sigma}_{\text{full}}^2$ is the unbiased estimate of error variance from the full model with all $K$ predictors.

* **Logic:** Measures the total standardized mean squared error of prediction. An unbiased model produces an expected value of $\mathbb{E}[C_p] \approx p$. Models where $C_p \gg p$ suffer from substantial omitted variable bias.

### 2. Akaike Information Criterion (AIC)

Derived from information theory to minimize the relative Kullback-Leibler (KL) divergence between the true data-generating distribution and the candidate parametric model:


$$\text{AIC} = -2\ln(\hat{L}) + 2k$$


where $\hat{L}$ is the maximized likelihood and $k$ is the total number of estimated parameters (including intercept and $\sigma^2$). Under Gaussian errors:


$$\text{AIC} = n \ln\left(\frac{\text{RSS}}{n}\right) + 2p + \text{constant}$$

### 3. Bayesian Information Criterion (BIC)

Derived from an asymptotic approximation of the integrated log-likelihood in a Bayesian framework:


$$\text{BIC} = -2\ln(\hat{L}) + k \ln(n) = n \ln\left(\frac{\text{RSS}}{n}\right) + \ln(n)p + \text{constant}$$

* **Comparison with AIC:** Since $\ln(n) > 2$ for all $n \ge 8$, **BIC applies a much heavier penalty on additional predictors than AIC**, favoring sparser, more parsimonious models.

---

## 1.6 Robust Loss Functions: Huber Loss & Log-Cosh

### 1. Huber Loss

Combines the mathematical differentiability of MSE for small residuals with the outlier robustness of MAE for large residuals:


$$L_\delta(e_i) = \begin{cases} 
\frac{1}{2} e_i^2 & \text{for } |e_i| \le \delta \\
\delta \left( |e_i| - \frac{1}{2}\delta \right) & \text{for } |e_i| > \delta 
\end{cases}$$

* **Gradient:**

$$\frac{\partial L_\delta}{\partial e_i} = \begin{cases} 
e_i & \text{for } |e_i| \le \delta \\
\delta \cdot \text{sgn}(e_i) & \text{for } |e_i| > \delta 
\end{cases}$$



The gradient remains bounded by $[-\delta, +\delta]$, preventing extreme outliers from destabilizing parameter updates.

### 2. Log-Cosh Loss

$$L(e_i) = \ln(\cosh(y_i - \hat{y}_i))$$

* **Logic:** For small errors, $\cosh(e) \approx 1 + \frac{e^2}{2} \implies \ln(1 + \frac{e^2}{2}) \approx \frac{e^2}{2}$ (behaves like MSE). For large errors, $\ln(\cosh(e)) \approx \vert{}e\vert{} - \ln(2)$ (behaves like MAE).
* **Advantage:** Smooth and twice-differentiable everywhere, making it well-suited for second-order optimization methods (e.g., Newton-Raphson, BFGS).

---

### Brain Teaser 1: The Negative $R^2$ Paradox

> **Question:** An engineer fits a regression model on a training set, applies the model to an unseen test set, and calculates $R^2 = -0.45$. A colleague argues: "Since $R^2$ is the square of a correlation, it cannot be negative; there must be a code bug." Who is correct? Under what exact mathematical conditions does $R^2 < 0$ occur?
> **Logical Solution:**
> The engineer is correct; $R^2$ can be negative.
> **Mathematical Proof:**
> On an evaluation set, $R^2$ is defined as:
> 
> $$R^2 = 1 - \frac{\sum_{i=1}^{n_{\text{test}}} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n_{\text{test}}} (y_i - \bar{y}_{\text{test}})^2} = 1 - \frac{\text{RSS}_{\text{test}}}{\text{TSS}_{\text{test}}}$$
> 
> 
> 
> $R^2 < 0$ occurs whenever:
> 
> $$\text{RSS}_{\text{test}} > \text{TSS}_{\text{test}}$$
> 
> 
> 
> This means the model's predictions $\hat{y}_i$ perform worse than a naive horizontal line at the test set mean $\bar{y}_{\text{test}}$. This typically happens when:
> 1. A severely overfitted model is evaluated on out-of-sample test data.
> 2. A linear regression model is fit without an intercept ($\beta_0 = 0$), which invalidates the $\text{TSS} = \text{ESS} + \text{RSS}$ decomposition on the training data itself.
> 
> 

---

## 1.7 High-Yield Exam Questions: Regression Metrics

### Question 1: Mathematical Equivalence of $R^2$ and $r_{XY}^2$

> **Exam Question:** Prove that in simple linear regression with an intercept, the coefficient of determination $R^2$ equals the squared Pearson correlation coefficient $r_{XY}^2$.

#### Analytical Proof:

In simple linear regression:


$$\hat{y}_i = \hat{\beta}_0 + \hat{\beta}_1 x_i = (\bar{y} - \hat{\beta}_1 \bar{x}) + \hat{\beta}_1 x_i = \bar{y} + \hat{\beta}_1 (x_i - \bar{x})$$


Subtracting $\bar{y}$:


$$\hat{y}_i - \bar{y} = \hat{\beta}_1 (x_i - \bar{x})$$


Substituting into the Explained Sum of Squares ($\text{ESS}$):


$$\text{ESS} = \sum_{i=1}^n (\hat{y}_i - \bar{y})^2 = \hat{\beta}_1^2 \sum_{i=1}^n (x_i - \bar{x})^2$$


Recall the OLS formula for the slope:


$$\hat{\beta}_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}$$


Substituting $\hat{\beta}_1$:


$$\text{ESS} = \left[ \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2} \right]^2 \sum (x_i - \bar{x})^2 = \frac{\left[ \sum (x_i - \bar{x})(y_i - \bar{y}) \right]^2}{\sum (x_i - \bar{x})^2}$$


Dividing by $\text{TSS} = \sum (y_i - \bar{y})^2$:


$$R^2 = \frac{\text{ESS}}{\text{TSS}} = \frac{\left[ \sum (x_i - \bar{x})(y_i - \bar{y}) \right]^2}{\left[ \sum (x_i - \bar{x})^2 \right] \left[ \sum (y_i - \bar{y})^2 \right]}$$


The right-hand side is the definition of the squared sample Pearson correlation:


$$r_{XY}^2 = \left[ \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2}\sqrt{\sum (y_i - \bar{y})^2}} \right]^2$$


Therefore:


$$\mathbf{R^2 = r_{XY}^2} \quad \blacksquare$$

---

### Question 2: Numerical Calculation of Model Diagnostics

> **Exam Question:** A multiple regression model with $p = 4$ predictors is fit to $n = 45$ observations. The calculated Total Sum of Squares is $\text{TSS} = 800$, and the Residual Sum of Squares is $\text{RSS} = 160$.
> 1. Compute the $R^2$ and Adjusted $R^2$.
> 2. Compute the Residual Standard Error (RSE) and the Root Mean Squared Error (RMSE).
> 3. Compute the omnibus $F$-statistic and determine its degrees of freedom.
> 
> 

#### Step-by-Step Solution:

1. **$R^2$ and Adjusted $R^2$:**

$$R^2 = 1 - \frac{\text{RSS}}{\text{TSS}} = 1 - \frac{160}{800} = 1 - 0.20 = \mathbf{0.80}$$


$$R_{\text{adj}}^2 = 1 - \left[ \frac{\text{RSS} / (n - p - 1)}{\text{TSS} / (n - 1)} \right] = 1 - \left[ \frac{160 / (45 - 4 - 1)}{800 / (45 - 1)} \right] = 1 - \left[ \frac{160 / 40}{800 / 44} \right]$$


$$R_{\text{adj}}^2 = 1 - \left[ \frac{4.00}{18.1818} \right] = 1 - 0.2200 = \mathbf{0.7800}$$


2. **RSE vs. RMSE:**

$$\text{RSE} = \sqrt{\frac{\text{RSS}}{n - p - 1}} = \sqrt{\frac{160}{40}} = \sqrt{4.0} = \mathbf{2.00}$$


$$\text{RMSE} = \sqrt{\frac{\text{RSS}}{n}} = \sqrt{\frac{160}{45}} = \sqrt{3.5556} \approx \mathbf{1.8856}$$


3. **Omnibus $F$-Statistic:**

$$F = \frac{(\text{TSS} - \text{RSS}) / p}{\text{RSS} / (n - p - 1)} = \frac{(800 - 160) / 4}{160 / 40} = \frac{640 / 4}{4.0} = \frac{160}{4.0} = \mathbf{40.0}$$



The degrees of freedom are $\mathbf{df_1 = 4}$ (numerator) and $\mathbf{df_2 = 40}$ (denominator). Since $F = 40.0 \gg 1$, the null hypothesis $H_0: \beta_1 = \dots = \beta_4 = 0$ is rejected.

---

# Topic 2: Bayesian Learning & The Naive Bayes Classifier

---

## 2.1 Epistemological Foundations of Bayesian Learning

Bayesian reasoning provides a quantitative framework for updating beliefs based on evidence:

1. **Probabilistic Hypotheses:** Quantities of interest are modeled by underlying probability distributions.
2. **Prior Integration:** Background domain knowledge is mathematically combined with incoming empirical data.
3. **Incremental Belief Revision:** Each new observation shifts the probability distribution over candidate hypotheses, providing a flexible learning process compared to hard rejection rules.
4. **Standard of Optimality:** Serves as a theoretical upper bound (the Bayes Optimal Classifier) against which practical heuristics can be compared.

---

## 2.2 Bayes' Theorem & Core Decision Criteria

```
                                Bayes' Theorem
                    P(h|D) = [ P(D|h) · P(h) ] / P(D)
                                  │
      ┌───────────────────────────┴───────────────────────────┐
      ▼                                                       ▼
Maximum A Posteriori (MAP)                             Maximum Likelihood (ML)
• Uses prior knowledge P(h)                            • Assumes uniform prior P(h_i) = P(h_j)
• Target: argmax P(D|h) · P(h)                         • Target: argmax P(D|h)
• Regularized by prior belief                          • Prone to overfitting on small samples

```

### 1. Mathematical Definitions

* **$P(h)$ (Prior Probability):** The initial degree of belief that hypothesis $h$ is correct, before observing dataset $D$.
* **$P(D)$ (Evidence / Marginal Likelihood):** The overall probability of observing dataset $D$ across all possible mutually exclusive hypotheses:

$$P(D) = \sum_{h_i \in H} P(D \mid h_i) P(h_i)$$


* **$P(D \mid h)$ (Likelihood):** The probability of observing dataset $D$ given that hypothesis $h$ holds.
* **$P(h \mid D)$ (Posterior Probability):** The updated probability of hypothesis $h$ after observing training data $D$.

$$\mathbf{P(h \mid D) = \frac{P(D \mid h) P(h)}{P(D)}}$$

### 2. Maximum A Posteriori (MAP) Hypothesis

$$h_{\text{MAP}} = \arg\max_{h \in H} P(h \mid D) = \arg\max_{h \in H} \frac{P(D \mid h) P(h)}{P(D)} = \arg\max_{h \in H} P(D \mid h) P(h)$$

* **Logic:** The marginal probability $P(D)$ is strictly positive and independent of $h$, meaning it can be dropped from the optimization step.

### 3. Maximum Likelihood (ML) Hypothesis

If all candidate hypotheses are equally probable *a priori* ($P(h_i) = P(h_j) \, \forall i, j$), the prior $P(h)$ acts as a uniform scaling constant:


$$h_{\text{ML}} = \arg\max_{h \in H} P(D \mid h)$$

---

## 2.3 The Bayes Optimal Classifier vs. MAP Predictions

### 1. The Core Conceptual Conflict

A common misconception is that the optimal way to classify a new query point $x$ is to evaluate it using the MAP hypothesis: $\hat{y} = h_{\text{MAP}}(x)$. **This is incorrect.**

> **Fundamental Insight:** The most probable hypothesis ($h_{\text{MAP}}$) is not guaranteed to produce the most probable classification. The true Bayes optimal prediction is formed by a **weighted ensemble vote across the entire hypothesis space $H$**, where each hypothesis casts a vote proportional to its posterior probability.

$$\mathbf{v_{\text{Bayes Optimal}} = \arg\max_{v_j \in V} \sum_{h_i \in H} P(v_j \mid h_i) P(h_i \mid D)}$$


where $V$ is the set of possible target classes, and $P(v_j \mid h_i) \in \{0, 1\}$ denotes the classification assigned to $x$ by hypothesis $h_i$.

### 2. Demonstration: Where MAP Fails

Consider a hypothesis space $H = \{h_1, h_2, h_3\}$ with target classes $V = \{+, -\}$:

* Posterior probabilities: $P(h_1 \mid D) = 0.40, \quad P(h_2 \mid D) = 0.30, \quad P(h_3 \mid D) = 0.30$
* **The MAP Hypothesis:** $h_{\text{MAP}} = h_1$ (since $0.40 > 0.30$).
* A new instance $x$ is evaluated:

$$h_1(x) = +, \quad h_2(x) = -, \quad h_3(x) = -$$


* **Evaluating the Class-Wise Probabilities:**

$$P(+ \mid D) = P(+ \mid h_1)P(h_1 \mid D) + P(+ \mid h_2)P(h_2 \mid D) + P(+ \mid h_3)P(h_3 \mid D) = 1(0.40) + 0(0.30) + 0(0.30) = \mathbf{0.40}$$


$$P(- \mid D) = P(- \mid h_1)P(h_1 \mid D) + P(- \mid h_2)P(h_2 \mid D) + P(- \mid h_3)P(h_3 \mid D) = 0(0.40) + 1(0.30) + 1(0.30) = \mathbf{0.60}$$


* **Conclusion:** The MAP prediction is **$+$** (with $40\%$ confidence), but the Bayes Optimal classification is **$-$** (with $60\%$ confidence).
* **Properties of Bayes Optimal:**
* **Minimizes Error:** No other classifier using the same hypothesis space and prior knowledge can outperform it on average.
* **Enlarged Decision Space:** The decision boundary formed by the ensemble vote can separate regions that no individual hypothesis $h \in H$ can separate on its own.



---

## 2.4 The Gibbs Algorithm

* **Problem:** Computing the Bayes Optimal classification requires marginalizing over every hypothesis in $H$, which is computationally intractable when $\vert{}H\vert{}$ is large or infinite.
* **The Gibbs Sampling Procedure:**
1. Sample a single hypothesis $h \in H$ at random according to the posterior distribution $P(h \mid D)$.
2. Use the chosen $h$ to classify the new instance $x$.


* **Theoretical Error Bound (Haussler et al.):**
Under a uniform prior, the expected error rate of the Gibbs algorithm is bounded by at most **twice the error rate of the Bayes Optimal classifier**:

$$\mathbb{E}[\text{Error}_{\text{Gibbs}}] \le 2 \cdot \mathbb{E}[\text{Error}_{\text{Bayes Optimal}}]$$



---

## 2.5 The Naive Bayes Classifier

### 1. The Full Joint Likelihood Bottleneck

Consider an instance described by $d$ categorical attributes: $\mathbf{x} = \langle a_1, a_2, \dots, a_d \rangle$. The MAP target value is:


$$v_{\text{MAP}} = \arg\max_{v_j \in V} P(v_j \mid a_1, a_2, \dots, a_d) = \arg\max_{v_j \in V} P(a_1, a_2, \dots, a_d \mid v_j) P(v_j)$$

* **The Combinatorial Explosion:**
Estimating $P(a_1, a_2, \dots, a_d \mid v_j)$ directly from training frequencies requires estimating:

$$\vert{}V\vert{} \times \left( \prod_{i=1}^d \vert{}Values(A_i)\vert{} - 1 \right) \text{ parameters}$$



For 30 binary attributes and 2 classes, this requires estimating $2 \times (2^{30} - 1) \approx 2.14 \times 10^9$ parameters. Reliably populating this joint probability space would require vast amounts of training data.

### 2. The Conditional Independence Assumption

The Naive Bayes classifier resolves this bottleneck by assuming that **attributes are conditionally independent given the target class**:


$$\mathbf{P(a_1, a_2, \dots, a_d \mid v_j) = \prod_{i=1}^d P(a_i \mid v_j)}$$

* **The Decision Rule:**

$$\mathbf{v_{\text{NB}} = \arg\max_{v_j \in V} P(v_j) \prod_{i=1}^d P(a_i \mid v_j)}$$


* **Parameter Reduction:** The number of parameters to estimate drops from exponential ($O(\vert{}V\vert{} \cdot k^d)$) to linear:

$$O\left(\vert{}V\vert{} \sum_{i=1}^d \vert{}Values(A_i)\vert{}\right)$$



```
Full Joint Likelihood Model                   Naive Bayes Graphical Model
      (Exponential: O(kᵈ))                           (Linear: O(d · k))

          ┌───────┐                                     ┌───────┐
          │   Y   │                                     │   Y   │
          └───┬───┘                                     └───┬───┘
              │                                  ┌──────────┼──────────┐
    ┌─────────┴─────────┐                        ▼          ▼          ▼
    ▼         ▼         ▼                     ┌────┐     ┌────┐     ┌────┐
 ┌────┐    ┌────┐    ┌────┐                   │ A₁ │     │ A₂ │     │ A_d│
 │ A₁ ├───►│ A₂ ├───►│ A_d│                   └────┘     └────┘     └────┘
 └────┘    └────┘    └────┘             (Attributes conditionally independent given Y)

```

---

## 2.6 The Zero-Frequency Problem & The $m$-Estimate

### 1. The Zero-Probability Breakdown

If attribute value $A_i = a_k$ never co-occurs with class $v_j$ in the training data, the empirical maximum likelihood frequency estimate yields:


$$\hat{P}(A_i = a_k \mid v_j) = \frac{n_c}{n} = \frac{0}{n} = 0$$


Because the Naive Bayes decision rule relies on multiplication:


$$P(v_j) \prod_{i=1}^d P(a_i \mid v_j) = P(v_j) \cdot P(a_1 \mid v_j) \cdots 0 \cdots P(a_d \mid v_j) = \mathbf{0}$$


A single unseen attribute-class pairing completely zeroes out the class probability, overriding all other informative attributes.

### 2. The $m$-Estimate of Probability (Bayesian Smoothing)

$$\mathbf{\hat{P}(a_i \mid v_j) = \frac{n_c + m p}{n + m}}$$

* $n$: Total number of training instances with class $v_j$.
* $n_c$: Number of training instances with class $v_j$ where attribute $A = a_i$.
* $p$: Prior estimate of the probability (assuming a uniform distribution over $k$ possible attribute values, $p = \frac{1}{k}$).
* $m$: **Equivalent Sample Size**. A hyperparameter that sets the weight of the prior relative to the observed data.
* **Laplace Smoothing (Add-1 Smoothing):** Setting $m = k$ and $p = \frac{1}{k}$:

$$\mathbf{\hat{P}(a_i \mid v_j) = \frac{n_c + 1}{n + k}}$$



---

## 2.7 Continuous Features: Gaussian Naive Bayes

When an attribute $X_i$ is continuous, its conditional distribution within class $v_j$ can be modeled as a Gaussian density:


$$P(X_i = x \mid v_j) = \frac{1}{\sqrt{2\pi \sigma_{ji}^2}} \exp\left( -\frac{(x - \mu_{ji})^2}{2\sigma_{ji}^2} \right)$$

* Parameters $\mu_{ji}$ and $\sigma_{ji}^2$ are estimated from the training data for class $v_j$:

$$\hat{\mu}_{ji} = \frac{1}{N_j}\sum_{k \in v_j} x_{ki}, \quad \hat{\sigma}_{ji}^2 = \frac{1}{N_j - 1}\sum_{k \in v_j} (x_{ki} - \hat{\mu}_{ji})^2$$



---

## 2.8 Numerical Underflow & The Log-Sum-Exp Solution

Multiplying dozens of small probabilities ($P(a_i \mid v_j) \in$) causes floating-point registers to underflow to zero. In practice, the classification rule is evaluated in log-space:


$$\mathbf{v_{\text{NB}} = \arg\max_{v_j \in V} \left[ \ln P(v_j) + \sum_{i=1}^d \ln P(a_i \mid v_j) \right]}$$

---

### Brain Teaser 2: Correlated Features in Naive Bayes

> **Question:** Suppose a spam classifier uses two features: $X_1 = \text{"Free"}$ and $X_2 = \text{"F.r.e.e"}$. In truth, whenever $X_1$ appears, $X_2$ also appears ($P(X_1 \mid X_2) = 1$). What happens to the posterior probability ratio $\frac{P(\text{Spam} \mid X_1, X_2)}{P(\text{Ham} \mid X_1, X_2)}$ under Naive Bayes? Does the classification boundary change?
> **Logical Solution:**
> 1. The true likelihood ratio for the two features is:
> 
> $$\frac{P(X_1, X_2 \mid \text{Spam})}{P(X_1, X_2 \mid \text{Ham})} = \frac{P(X_1 \mid \text{Spam}) \cdot 1}{P(X_1 \mid \text{Ham}) \cdot 1} = \frac{P(X_1 \mid \text{Spam})}{P(X_1 \mid \text{Ham})}$$
> 
> 
> 2. Under the conditional independence assumption, Naive Bayes factors the joint probability:
> 
> $$\frac{P(X_1 \mid \text{Spam}) P(X_2 \mid \text{Spam})}{P(X_1 \mid \text{Ham}) P(X_2 \mid \text{Ham})} = \left( \frac{P(X_1 \mid \text{Spam})}{P(X_1 \mid \text{Ham})} \right)^2$$
> 
> 
> 3. **The Consequence:** Naive Bayes **double-counts the evidence**, squaring the odds in favor of the favored class. While the predicted probabilities become overconfident (drifting toward 0 or 1), the classification decision does not flip unless conflicting correlated features are present.
> 
> 

---

## 2.9 High-Yield Exam Questions: Bayesian Learning

### Question 1: Medical Diagnosis & The False Positive Paradox

> **Exam Question:** A rare disease has a population incidence rate of $0.8\%$ ($P(\text{Disease}) = 0.008$). A diagnostic test has a sensitivity (true positive rate) of $98\%$ and a false positive rate of $3\%$.
> A randomly selected patient tests positive ($+$).
> 1. Formulate the MAP classification problem.
> 2. Compute the unnormalized joint probabilities for both hypotheses.
> 3. Compute the exact posterior probability $P(\text{Disease} \mid +)$.
> 
> 

#### Step-by-Step Solution:

1. **Identify the Given Probabilities:**
* $P(D) = 0.008 \implies P(\neg D) = 1 - 0.008 = 0.992$
* Sensitivity: $P(+ \mid D) = 0.98$
* False Positive Rate: $P(+ \mid \neg D) = 0.03$


2. **Compute Unnormalized Joint Probabilities:**
* For the hypothesis $h_1 = \text{Disease}$:

$$P(+ \mid D) \cdot P(D) = 0.98 \times 0.008 = \mathbf{0.00784}$$


* For the hypothesis $h_2 = \neg \text{Disease}$:

$$P(+ \mid \neg D) \cdot P(\neg D) = 0.03 \times 0.992 = \mathbf{0.02976}$$


* **MAP Classification:** Since $0.02976 > 0.00784$, the MAP decision is **No Disease ($\neg D$)**.


3. **Compute the Exact Posterior Probability:**

$$P(+) = P(+ \mid D)P(D) + P(+ \mid \neg D)P(\neg D) = 0.00784 + 0.02976 = 0.03760$$


$$P(\text{Disease} \mid +) = \frac{0.00784}{0.03760} = \mathbf{0.2085 \quad (20.85\%)}$$


* **Interpretation:** Even with a positive test result, the patient has only a $\approx 21\%$ chance of having the disease because the condition is rare in the general population.



---

### Question 2: Step-by-Step Training of a Naive Bayes Classifier

> **Exam Question:** Consider the training dataset below with 10 instances for target concept $Y \in \{\text{Yes}, \text{No}\}$.
> | ID | Outlook | Humidity | Wind | Play ($Y$) |
> | --- | --- | --- | --- | --- |
> | 1 | Sunny | High | Weak | No |
> | 2 | Sunny | High | Strong | No |
> | 3 | Overcast | High | Weak | Yes |
> | 4 | Rain | High | Weak | Yes |
> | 5 | Rain | Normal | Weak | Yes |
> | 6 | Rain | Normal | Strong | No |
> | 7 | Overcast | Normal | Strong | Yes |
> | 8 | Sunny | High | Weak | No |
> | 9 | Sunny | Normal | Weak | Yes |
> | 10 | Rain | Normal | Weak | Yes |
> 
> 
> Classify the test query $\mathbf{x}_q = \langle \text{Outlook}=\text{Sunny}, \text{Humidity}=\text{Normal}, \text{Wind}=\text{Strong} \rangle$:
> 1. Using standard Maximum Likelihood frequency estimates.
> 2. Using Laplace smoothing ($m$-estimate with $m = k$ and $p = 1/k$).
> 
> 

#### Step-by-Step Solution:

#### 1. Baseline Counts:

* Total instances: $N = 10$
* Class counts: $N_{\text{Yes}} = 6$, $N_{\text{No}} = 4$
* Prior Probabilities:

$$P(\text{Yes}) = \frac{6}{10} = 0.6, \quad P(\text{No}) = \frac{4}{10} = 0.4$$



#### 2. Conditional Likelihoods (Maximum Likelihood):

* **Class = Yes ($N = 6$):**
* $P(\text{Sunny} \mid \text{Yes}) = \frac{1}{6}$ (Only ID 9)
* $P(\text{Normal} \mid \text{Yes}) = \frac{4}{6}$ (IDs 5, 7, 9, 10)
* $P(\text{Strong} \mid \text{Yes}) = \frac{1}{6}$ (ID 7)


* **Class = No ($N = 4$):**
* $P(\text{Sunny} \mid \text{No}) = \frac{3}{4}$ (IDs 1, 2, 8)
* $P(\text{Normal} \mid \text{No}) = \frac{1}{4}$ (ID 6)
* $P(\text{Strong} \mid \text{No}) = \frac{2}{4}$ (IDs 2, 6)



#### 3. Classification via Maximum Likelihood:

* **Score(Yes):**

$$P(\text{Yes}) \cdot P(\text{Sunny} \mid \text{Yes}) \cdot P(\text{Normal} \mid \text{Yes}) \cdot P(\text{Strong} \mid \text{Yes}) = 0.6 \times \frac{1}{6} \times \frac{4}{6} \times \frac{1}{6} = 0.1 \times \frac{4}{36} = \frac{0.4}{36} \approx \mathbf{0.01111}$$


* **Score(No):**

$$P(\text{No}) \cdot P(\text{Sunny} \mid \text{No}) \cdot P(\text{Normal} \mid \text{No}) \cdot P(\text{Strong} \mid \text{No}) = 0.4 \times \frac{3}{4} \times \frac{1}{4} \times \frac{2}{4} = 0.3 \times \frac{2}{16} = \frac{0.6}{16} = \mathbf{0.03750}$$


* Normalizing:

$$P(\text{No} \mid \mathbf{x}_q) = \frac{0.03750}{0.03750 + 0.01111} = \frac{0.03750}{0.04861} \approx \mathbf{77.15\%}$$


* **Prediction:** $\mathbf{v_{\text{NB}} = \text{No}}$.

#### 4. Re-Evaluating with Laplace Smoothing:

* Distinct values: $\vert{}Values(\text{Outlook})\vert{} = 3$, $\vert{}Values(\text{Humidity})\vert{} = 2$, $\vert{}Values(\text{Wind})\vert{} = 2$.
* Formula: $\hat{P}(a_i \mid v) = \frac{n_c + 1}{n + k}$
* **Class = Yes ($N = 6$):**
* $\hat{P}(\text{Sunny} \mid \text{Yes}) = \frac{1 + 1}{6 + 3} = \frac{2}{9}$
* $\hat{P}(\text{Normal} \mid \text{Yes}) = \frac{4 + 1}{6 + 2} = \frac{5}{8}$
* $\hat{P}(\text{Strong} \mid \text{Yes}) = \frac{1 + 1}{6 + 2} = \frac{2}{8} = \frac{1}{4}$
* Score(Yes):

$$0.6 \times \frac{2}{9} \times \frac{5}{8} \times \frac{1}{4} = \frac{6}{10} \times \frac{10}{288} = \frac{60}{2880} \approx \mathbf{0.02083}$$




* **Class = No ($N = 4$):**
* $\hat{P}(\text{Sunny} \mid \text{No}) = \frac{3 + 1}{4 + 3} = \frac{4}{7}$
* $\hat{P}(\text{Normal} \mid \text{No}) = \frac{1 + 1}{4 + 2} = \frac{2}{6} = \frac{1}{3}$
* $\hat{P}(\text{Strong} \mid \text{No}) = \frac{2 + 1}{4 + 2} = \frac{3}{6} = \frac{1}{2}$
* Score(No):

$$0.4 \times \frac{4}{7} \times \frac{1}{3} \times \frac{1}{2} = \frac{4}{10} \times \frac{4}{42} = \frac{16}{420} \approx \mathbf{0.03810}$$




* **Smoothed Prediction:** Since $0.03810 > 0.02083$, the predicted class remains **No**.

---

# Topic 3: Instance-Based Learning & $k$-Nearest Neighbors ($k$-NN)

---

## 3.1 Lazy vs. Eager Learning Paradigm

```
Comparison Dimension    Eager Learning (e.g., Decision Trees)   Lazy Learning (e.g., k-NN)
──────────────────────────────────────────────────────────────────────────────────────────
Training Phase          Constructs global hypothesis h(x);     Stores training samples in memory;
                        discards raw data; high compute.       zero training compute: O(1).
Inference Phase         Fast lookup: O(depth) or O(p).         High compute: scans and sorts
                                                               dataset: O(n · d).
Hypothesis Scope        Single global decision surface         Local approximation custom-built
                        over entire instance space.            around each query point x_q.
Adaptability            Requires complete refit to             Seamlessly incorporates streaming
                        assimilate new data points.            samples by appending to memory.

```

---

## 3.2 The $k$-NN Classifier: Mathematical Formalism

Let an instance $\mathbf{x} \in \mathbb{R}^d$ be defined by a vector of real-valued features $\mathbf{x} = \langle a_1(\mathbf{x}), a_2(\mathbf{x}), \dots, a_d(\mathbf{x}) \rangle$.

* **Euclidean Distance:** The distance between instances $\mathbf{x}_i$ and $\mathbf{x}_j$ is:

$$d(\mathbf{x}_i, \mathbf{x}_j) = \sqrt{\sum_{r=1}^d \left( a_r(\mathbf{x}_i) - a_r(\mathbf{x}_j) \right)^2} = \Vert{}\mathbf{x}_i - \mathbf{x}_j\Vert{}_2$$


* **Classification Rule:** Given query instance $\mathbf{x}_q$, let $\mathcal{N}_k(\mathbf{x}_q) = \{\mathbf{x}_1, \dots, \mathbf{x}_k\}$ denote the $k$ training points closest to $\mathbf{x}_q$. The predicted discrete class label $\hat{f}(\mathbf{x}_q) \in V$ is:

$$\mathbf{\hat{f}(\mathbf{x}_q) = \arg\max_{v \in V} \sum_{i \in \mathcal{N}_k(\mathbf{x}_q)} \delta(v, f(\mathbf{x}_i))}$$



where $\delta(a, b) = 1$ if $a = b$, and $0$ otherwise.

---

## 3.3 1-NN Decision Surfaces & Voronoi Tessellations

```
         Voronoi Tessellation of Instance Space (1-NN)
      ┌─────────────────────────────────────────────────┐
      │         \                  /                    │
      │          \      ● (x₁)    /       ● (x₂)        │
      │           \              /                      │
      │            \            /                       │
      │             \__________/                        │
      │             /          \                        │
      │            /   ● (x₃)   \                       │
      │           /              \        ● (x₄)        │
      │          /                \                     │
      └─────────────────────────────────────────────────┘
    (Each convex polygon represents the region closest to that training point)

```

* **The Voronoi Cell:** For a training instance $\mathbf{x}_i$, its Voronoi cell $V(\mathbf{x}_i)$ is the set of all points in $\mathbb{R}^d$ closer to $\mathbf{x}_i$ than to any other training point:

$$V(\mathbf{x}_i) = \{ \mathbf{x} \in \mathbb{R}^d \mid d(\mathbf{x}, \mathbf{x}_i) \le d(\mathbf{x}, \mathbf{x}_j), \quad \forall j \neq i \}$$


* **Geometric Properties:**
1. Each cell is a **convex polyhedron** formed by the intersection of half-spaces defined by the perpendicular bisectors between point pairs.
2. The overall decision surface of 1-NN is piecewise linear, separating adjacent regions assigned to different classes.
3. **Cover's Theorem on 1-NN Risk:** As $n \to \infty$, the asymptotic error rate of the 1-NN classifier $R_{\text{1-NN}}$ is bounded relative to the Bayes optimal error rate $R^*$ by:

$$R^* \le R_{\text{1-NN}} \le 2R^*(1 - R^*) \le 2R^*$$



*A 1-NN classifier with infinite data has an error rate at most twice the irreducible Bayes error rate.*



---

## 3.4 $k$-NN for Continuous Targets (Regression)

To predict a continuous response $f: \mathbb{R}^d \to \mathbb{R}$, calculate the sample mean of the $k$ nearest neighbors:


$$\mathbf{\hat{f}(\mathbf{x}_q) = \frac{1}{k}\sum_{i \in \mathcal{N}_k(\mathbf{x}_q)} f(\mathbf{x}_i)}$$

---

## 3.5 Distance-Weighted $k$-NN

To prevent distant neighbors from diluting the influence of close points:

* **The Weighting Kernel:**

$$w_i = \frac{1}{d(\mathbf{x}_q, \mathbf{x}_i)^2}$$



*(If $d(\mathbf{x}_q, \mathbf{x}_i) = 0$, set $\hat{f}(\mathbf{x}_q) = f(\mathbf{x}_i)$).*
* **Weighted Classification Rule:**

$$\mathbf{\hat{f}(\mathbf{x}_q) = \arg\max_{v \in V} \sum_{i \in \mathcal{N}_k(\mathbf{x}_q)} w_i \cdot \delta(v, f(\mathbf{x}_i))}$$


* **Weighted Regression Rule:**

$$\mathbf{\hat{f}(\mathbf{x}_q) = \frac{\sum_{i=1}^k w_i f(\mathbf{x}_i)}{\sum_{i=1}^k w_i}}$$


* **Shepard's Method (Global Interpolation):** Setting $k = n$ allows every point in the training set to contribute to the prediction, weighted inversely by distance. This produces a smooth, continuous global interpolation surface:

```
Step-like (Standard k-NN)                   Smooth (Distance-Weighted Shepard)
    ŷ ^                                         ŷ ^
      │    ┌───┐                                  │       ╭───╮
      │────┘   └───                               │──────╯     ╰──────
      └─────────────> X                           └─────────────────> X

```

---

## 3.6 The Inductive Bias of $k$-NN

* **The Inductive Bias:** The assumption that the label of a query point $\mathbf{x}_q$ is most similar to the labels of nearby points under the chosen distance metric.
* **Locality & Smoothness:** Assumes that the underlying data-generating function varies smoothly across space, meaning points close together in feature space are likely to share the same class label.

---

## 3.7 Distance Metrics & Feature Scaling

### 1. The Metric Suite

| Metric | Formula | Geometry / Use Case |
| --- | --- | --- |
| **Euclidean ($L_2$)** | $\sqrt{\sum_{r=1}^d (a_r(\mathbf{x}_i) - a_r(\mathbf{x}_j))^2}$ | Direct straight-line distance; isotropic space. |
| **Manhattan ($L_1$)** | $\sum_{r=1}^d \Vert{}a_r(\mathbf{x}_i) - a_r(\mathbf{x}_j)\Vert{}$ | Grid/city-block paths; more robust to outliers in high dimensions. |
| **Minkowski ($L_p$)** | $\left( \sum_{r=1}^d \Vert{}a_r(\mathbf{x}_i) - a_r(\mathbf{x}_j)\Vert{}^p \right)^{1/p}$ | Generalized metric space ($p=1 \implies L_1, p=2 \implies L_2$). |
| **Mahalanobis** | $\sqrt{(\mathbf{x}_i - \mathbf{x}_j)^T \mathbf{\Sigma}^{-1} (\mathbf{x}_i - \mathbf{x}_j)}$ | Accounts for covariance $\mathbf{\Sigma}$ and varying feature scales. |

### 2. Feature Scaling: A Practical Requirement

If feature $A_1$ (e.g., Annual Income in dollars) ranges from $10,000$ to $1,000,000$, while feature $A_2$ (e.g., Age in years) ranges from $18$ to $80$:


$$d(\mathbf{x}_1, \mathbf{x}_2) = \sqrt{(100,000 - 50,000)^2 + (45 - 25)^2} = \sqrt{2,500,000,000 + 400} \approx 50,000.004$$


The distance is dominated entirely by the feature with the larger numerical range, making Age irrelevant to the neighbor calculations.

* **Z-score Standardization:**

$$a_r' = \frac{a_r - \mu_r}{\sigma_r}$$


* **Min-Max Normalization:**

$$a_r' = \frac{a_r - \min(A_r)}{\max(A_r) - \min(A_r)}$$



---

## 3.8 The Curse of Dimensionality

As feature dimensionality $d$ increases:

```
Dimensionality (d)      Geometric Consequence
─────────────────────────────────────────────────────────────────────────────
Distance Concentration  lim_{d → ∞} [ (d_max - d_min) / d_min ] → 0.
                        All pairwise distances converge to nearly the same value.
Exponential Sparsity    To capture a fraction s of total volume, edge length
                        scales as e = s^(1/d). Capturing 10% of volume in d = 10
                        requires spanning e = (0.10)^(0.10) ≈ 79.4% of each axis!
Noise Dominance         Adding irrelevant attributes adds random noise to the sum
                        d = √(d_relevant² + d_irrelevant²), washing out true similarities.

```

* **Mitigation Strategies:**
1. **Feature Weighting:** Scale each axis by a weight $z_r$:

$$d_z(\mathbf{x}_i, \mathbf{x}_j) = \sqrt{\sum_{r=1}^d z_r^2 (a_r(\mathbf{x}_i) - a_r(\mathbf{x}_j))^2}$$



Optimize weights $z_r$ using leave-one-out cross-validation.
2. **Dimensionality Reduction:** Apply Principal Component Analysis (PCA) or Linear Discriminant Analysis (LDA) prior to neighbor search.



---

## 3.9 Fast Retrieval: $kd$-Trees

* **Structure:** A binary space-partitioning tree where each node splits data along one axis based on the median coordinate value, cycling through the dimensions ($x \to y \to z \to x$).
* **Computational Complexity:**
* Construction: $O(d \cdot n \log n)$
* Nearest Neighbor Search: Average query time is **$O(d \cdot \log n)$** (compared to $O(d \cdot n)$ for a brute-force scan).


* **High-Dimensional Breakdown:** When $d > 20$, the search must backtrack through nearly every branch of the tree, causing query performance to degrade toward a linear scan $O(n)$.

---

### Brain Teaser 3: The Odd vs. Even $k$ Dilemma

> **Question:** In a binary classification problem ($V \in \{+1, -1\}$), a data scientist always chooses an odd value for $k$ ($k = 1, 3, 5, \dots$) to prevent ties. Can a tie still occur when using distance-weighted $k$-NN?
> **Logical Solution:**
> **Yes, ties can still occur.**
> In standard unweighted $k$-NN, an odd $k$ guarantees that the sum of binary votes $\sum_{i=1}^k y_i$ is non-zero, preventing a tie.
> In distance-weighted $k$-NN, each vote is weighted by a real number: $w_i = 1 / d(\mathbf{x}_q, \mathbf{x}_i)^2$. A tie occurs whenever the weighted sums for the two classes match:
> 
> $$\sum_{i \in \text{Class } +} w_i = \sum_{j \in \text{Class } -} w_j$$
> 
> 
> 
> For example, if a query point sits equidistant from two opposite-class points with the third neighbor farther away:
> 
> $$d_1 = 2 \, (+), \quad d_2 = 2 \, (-), \quad d_3 = 4 \, (-)$$
> 
> 
> 
> The weights are $w_1 = 0.25$, $w_2 = 0.25$, and $w_3 = 0.0625$. While Class $-$ wins here ($0.3125 > 0.25$), any symmetric arrangement between class subsets can produce identical weighted sums, regardless of whether $k$ is odd or even.

---

## 3.10 High-Yield Exam Questions: Instance-Based Learning

### Question 1: Manual Calculation of $k$-NN Classification and Regression

> **Exam Question:** A 2-dimensional dataset contains 5 labeled training instances:
> * $A = (1, 2)$ with Class $-1$ and Target $y = 10$
> * $B = (2, 5)$ with Class $+1$ and Target $y = 20$
> * $C = (3, 1)$ with Class $-1$ and Target $y = 12$
> * $D = (6, 4)$ with Class $+1$ and Target $y = 25$
> * $E = (4, 3)$ with Class $+1$ and Target $y = 22$
> 
> 
> For a new query point $\mathbf{x}_q = (3, 3)$:
> 1. Compute Euclidean distances to all training points and identify the $k=3$ nearest neighbors.
> 2. Predict the discrete class label using standard 3-NN majority voting.
> 3. Predict the discrete class label using distance-weighted 3-NN ($w_i = 1/d_i^2$).
> 4. Predict the continuous target value using standard 3-NN regression and distance-weighted 3-NN regression.
> 
> 

#### Step-by-Step Solution:

1. **Compute Squared and Euclidean Distances to $\mathbf{x}_q = (3, 3)$:**
* Point $A(1, 2)$:

$$d^2 = (1-3)^2 + (2-3)^2 = (-2)^2 + (-1)^2 = 4 + 1 = 5 \implies d = \sqrt{5} \approx 2.236$$


* Point $B(2, 5)$:

$$d^2 = (2-3)^2 + (5-3)^2 = (-1)^2 + (2)^2 = 1 + 4 = 5 \implies d = \sqrt{5} \approx 2.236$$


* Point $C(3, 1)$:

$$d^2 = (3-3)^2 + (1-3)^2 = 0 + (-2)^2 = 4 \implies d = \sqrt{4} = 2.000$$


* Point $D(6, 4)$:

$$d^2 = (6-3)^2 + (4-3)^2 = 3^2 + 1^2 = 9 + 1 = 10 \implies d = \sqrt{10} \approx 3.162$$


* Point $E(4, 3)$:

$$d^2 = (4-3)^2 + (3-3)^2 = 1^2 + 0 = 1 \implies d = \sqrt{1} = 1.000$$




**Ranked Distances:**
1. $E$: $d = 1.000, \quad d^2 = 1$
2. $C$: $d = 2.000, \quad d^2 = 4$
3. Tied for 3rd: $A$ ($d^2 = 5$) and $B$ ($d^2 = 5$).
*(Selecting $A$ to break the tie for the 3rd nearest neighbor yields the neighborhood: $\{E, C, A\}$.)*


2. **Standard 3-NN Majority Vote:**
* Neighborhood: $E \, (+1), \quad C \, (-1), \quad A \, (-1)$
* Vote tally: Class $+1$ has 1 vote; Class $-1$ has 2 votes.
* **Prediction:** $\mathbf{\hat{y} = -1}$.


3. **Distance-Weighted 3-NN Classification:**
* Neighborhood weights ($w_i = 1/d_i^2$):
* $w_E = \frac{1}{1} = 1.000$
* $w_C = \frac{1}{4} = 0.250$
* $w_A = \frac{1}{5} = 0.200$


* Class $+1$ weight: $w_E = 1.000$
* Class $-1$ weight: $w_C + w_A = 0.250 + 0.200 = 0.450$
* **Prediction:** Since $1.000 > 0.450$, distance weighting flips the prediction to $\mathbf{\hat{y} = +1}$.


4. **Continuous Target Regression:**
* **Standard 3-NN Mean:**

$$\hat{f}(\mathbf{x}_q) = \frac{y_E + y_C + y_A}{3} = \frac{22 + 12 + 10}{3} = \frac{44}{3} \approx \mathbf{14.67}$$


* **Distance-Weighted 3-NN Mean:**

$$\hat{f}(\mathbf{x}_q) = \frac{w_E y_E + w_C y_C + w_A y_A}{w_E + w_C + w_A} = \frac{1.0(22) + 0.25(12) + 0.20(10)}{1.0 + 0.25 + 0.20} = \frac{22 + 3.0 + 2.0}{1.45} = \frac{27.0}{1.45} \approx \mathbf{18.62}$$





---

### Question 2: The Impact of $k$ on the Bias-Variance Tradeoff

> **Exam Question:** Analyze the effect of the hyperparameter $k$ on the bias-variance tradeoff in $k$-NN. What occurs at the extreme values $k = 1$ and $k = n$?

#### Analytical Explanation:

* **Case 1: $k = 1$ (Extreme Flexibility, Maximum Overfitting):**
* Training Error is zero: Each training point serves as its own nearest neighbor, giving $e_i = 0$.
* The decision boundary conforms to every individual data point, capturing noise and localized anomalies.
* **Statistical Profile:** **Minimum Bias, Maximum Variance**.


* **Case 2: $k = n$ (Extreme Rigidity, Maximum Underfitting):**
* The neighborhood spans the entire dataset for every query point $\mathbf{x}_q$.
* For classification, it predicts the majority class of the training set everywhere.
* For regression, it predicts the global sample mean $\bar{y}$ everywhere.
* The decision boundary is completely flat, ignoring local feature variations.
* **Statistical Profile:** **Maximum Bias, Minimum Variance**.


* **Effective Degrees of Freedom:** The effective parameter count of $k$-NN scales as $n/k$. Increasing $k$ smooths the decision boundary, reducing variance at the cost of higher bias.

```
Model Complexity & The Role of k
  ^
  │  Variance (High at k=1)
  │   \                                 / Bias (High at k=n)
  │    \                               /
  │     \        Optimal k            /
  │      \           │               /
  │       \          ▼              /
  │        ╰───────────────────────╯ Total Expected Error
  │
  └─────────────────────────────────────────────────────────> k (Neighborhood Size)
    (k = 1: Low Bias, High Var)         (k = n: High Bias, Low Var)

```

---
---
---

# Comprehensive Study Notes: Approaches for Clustering, Distance Metrics & Hierarchical Clustering

---

## Module 1: Approaches for Clustering & Foundational Philosophy

### 1. The Unsupervised Learning Paradigm

In supervised learning, every training instance $\mathbf{x}_i \in \mathbb{R}^p$ is paired with a supervisor target $y_i$ (a class label or continuous response), and the goal is to learn a predictive mapping $\hat{y} = f(\mathbf{x})$.

In **unsupervised learning**, we observe only a collection of features $\mathbf{x}_1, \mathbf{x}_2, \dots, \mathbf{x}_n$ measured on $n$ observations. There is **no response variable $Y$**, no supervisor, and no ground-truth error metric to train against.

* **Core Objective:** Discover latent patterns, subgroup structures, and intrinsic geometric organization directly from the input space.
* **Definition of Clustering:** An unsupervised learning task that partitions $n$ heterogeneous observations into distinct groups (clusters) such that:
1. **High Intra-Cluster Homogeneity:** Observations within the same cluster are as similar as possible.
2. **High Inter-Cluster Heterogeneity:** Observations belonging to different clusters are as dissimilar as possible.



```
       Supervised Learning                     Unsupervised Clustering
   (Input Features + Class Labels)             (Input Features Only, No Labels)
        X₂ ^                                      X₂ ^
           │   ▲   ▲                                 │   ●   ●
           │  ▲  ▲   ■ ■                             │  ●  ●   ● ●
           │        ■   ■                            │        ●   ●
           │   ●   ●                                 │   ●   ●
           │  ●  ●   ●                               │  ●  ●   ●
           └─────────────> X₁                        └─────────────> X₁
    Goal: Learn decision boundary             Goal: Discover natural groupings

```

---

### 2. Taxonomy of Clustering Approaches

```
                             Clustering Approaches
                                       │
      ┌────────────────────────────────┼────────────────────────────────┐
      ▼                                ▼                                ▼
Partitioning Methods         Hierarchical Methods             Density-Based Methods
• Flat, un-nested clusters   • Nested tree of clusters        • Forms arbitrary shapes
• Requires specifying K      • No upfront K required          • Identifies noise/outliers
• Example: K-Means           • Generates a Dendrogram         • Example: DBSCAN
                             • Agglomerative vs. Divisive

```

* **Partitioning Methods (e.g., $K$-Means):**
* Divides the $n$ observations into a pre-specified number of $K$ non-overlapping, flat clusters.
* *Disadvantages:* Requires fixing $K$ prior to running the algorithm; sensitive to initialization; can get trapped in local optima; forces every point into a cluster even if it is an outlier.


* **Hierarchical Methods:**
* Constructs a multi-level, nested hierarchy of clusters represented as an upside-down tree called a **dendrogram**.
* Does not require pre-specifying $K$; a single run produces all partitionings from $1$ to $n$ clusters.


* **Density-Based Methods (e.g., DBSCAN):**
* Discovers clusters as dense regions of points separated by sparse regions; can identify clusters of arbitrary non-spherical shapes and isolate noise points.



---

### 3. The Hierarchical Nestedness Assumption & Its Fundamental Flaw

Hierarchical clustering imposes a strict mathematical assumption: **clusters obtained at a lower cut height are strictly nested within the clusters obtained at a higher cut height.**

```
          Nested Assumption                          True Non-Nested Reality
          ┌──────────────┐                        ┌──────────────┬──────────────┐
          │   Cluster    │                        │  Gender:     │  Gender:     │
          │ ┌──────────┐ │                        │   Male       │   Female     │
          │ │Sub-clust │ │                        ├──────────────┼──────────────┤
          │ └──────────┘ │                        │ American     │ Japanese     │
          └──────────────┘                        └──────────────┴──────────────┘
    (Child cluster must live entirely         (Best 2-split: Gender. Best 3-split:
     inside parent cluster)                    Nationality. These cross-cut!)

```

* **The Reality Check:** In many real-world datasets, true underlying groupings are **not hierarchical**.
* *The Demographic Counterexample:* Suppose a study surveys men and women evenly distributed across American, Japanese, and French nationalities.
* The most natural division into **two groups** splits by **Gender** (Male vs. Female).
* The most natural division into **three groups** splits by **Nationality** (American vs. Japanese vs. French).


* Because Nationality cross-cuts Gender rather than nesting inside it, a hierarchical tree cannot represent both groupings simultaneously.
* In scenarios where natural groupings do not nest, hierarchical clustering can yield worse (less natural) partitions than partitioning methods like $K$-means for a given choice of $K$.



---

## Module 2: Hierarchical Clustering Architecture & Dendrograms

### 1. Agglomerative (Bottom-Up) vs. Divisive (Top-Down)

* **Agglomerative (Bottom-Up):**
* Starts at the bottom with $n$ distinct singleton clusters (each observation is its own cluster).
* Iteratively merges the two most similar clusters step-by-step until all points merge into one single cluster at the trunk.
* By far the most widely used hierarchical method.


* **Divisive (Top-Down):**
* Starts at the top with a single global cluster containing all $n$ observations.
* Recursively splits clusters into smaller sub-clusters until every observation forms an isolated leaf node.



---

### 2. Anatomy of a Dendrogram

A dendrogram is a 2D tree diagram that visualizes the sequence of merges or splits in a hierarchical clustering:

* **Leaves:** Placed along the horizontal axis at vertical height $0$. Each leaf represents an individual observation ($i = 1, \dots, n$).
* **Internal Fusion Nodes (Cross-Bars):** Horizontal lines connecting two branches. The vertical height of a cross-bar represents the **inter-cluster dissimilarity** at which those two branches were fused.
* **Root / Trunk:** The topmost fusion uniting all observations into a single group.

```
Dissimilarity (Height)
  ^
  │                     ┌───────────────────────────┐  <--- Root (All merged)
10┼─────────────────────┤                           │
  │                     │                           │
 8┼─────────────────────┼──────────────┐            │
  │                     │              │            │
 5┼───────┐             │              │            │  <--- Cut at Height = 5
  │       │             │              │            │       (Yields 3 clusters)
 3┼───────┼───────┐     │              │            │
  │       │       │     │              │            │
 1┼───┐   │   ┌───┤     │          ┌───┴───┐        │
  │   │   │   │   │     │          │       │        │
 0└───┴───┴───┴───┴─────┴──────────┴───────┴────────┴──────> Observations
      1   6   4   3     9          8       5        7
      └─┬─┘
     Fused early: highly similar

```

---

### 3. The Fundamental Rule of Dendrogram Interpretation: The Horizontal Fallacy

> **The Most Common Error:** Concluding that two observations are similar because they sit adjacent to each other along the horizontal axis of a dendrogram.

#### The Mathematical Logic:

1. **Vertical Axis Measures Dissimilarity:** The dissimilarity between any two observations is given by the **height on the vertical axis where their containing branches first fuse**.
* If observation $A$ and observation $B$ fuse at height $1.2$, their dissimilarity is $1.2$.
* If observation $B$ and observation $C$ fuse at height $8.5$, their dissimilarity is $8.5$, regardless of where they sit along the horizontal axis.


2. **$2^{n-1}$ Equivalent Horizontal Orderings:**
* A dendrogram containing $n$ leaves has exactly $n - 1$ internal fusion nodes.
* At each internal node, the left and right sub-branches can be swapped (rotated like a mobile hanging from a ceiling) without changing the tree topology, the fusion heights, or the mathematical meaning of the clustering:

$$\text{Number of equivalent leaf orderings} = 2^{n-1}$$


* For $n = 9$ observations, there are $2^8 = 256$ different valid horizontal orderings. A point can sit right next to another on the page simply because of how the plotting software happened to draw the tree, even if they only merge at the very top of the diagram.



---

### 4. Extracting Partitions by Cutting the Dendrogram

A dendrogram provides clusterings at every scale simultaneously. To extract a specific partition:

* Draw a horizontal cut line across the dendrogram at height $h$.
* Each disjoint branch intersected by the cut line forms a separate cluster.
* **The Role of Cut Height:**
* The height $h$ plays the same role as the parameter $K$ in partitioning algorithms.
* Cutting near the top (high $h$) yields a few large, heterogeneous clusters.
* Cutting near the bottom (low $h$) yields many small, tightly focused clusters.
* Setting $h = 0$ yields $n$ singleton clusters; no cut yields $1$ global cluster.



---

### Brain Teaser 1: The Misleading Neighbor

> **Question:** In a complete-linkage dendrogram of nine observations, observations $9$ and $2$ are drawn right next to each other along the bottom axis. However, their branches only meet at the very top of the tree (height $h = 10.5$). Meanwhile, observation $5$ is drawn far away on the opposite side of the page, but its branch fuses with observation $7$ at height $h = 0.8$. Which pair of points is more similar: $(9, 2)$ or $(5, 7)$? Can you redraw the tree to place $9$ and $2$ on opposite ends of the plot?
> **Logical Solution:**
> 1. **Similarity Evaluation:** Points **$5$ and $7$ are far more similar** to each other than $9$ and $2$. Their branch fuses at height $0.8$, whereas the branch uniting $9$ and $2$ fuses at height $10.5$.
> 2. **Horizontal Manipulation:** Yes. Because each of the $n - 1$ internal nodes can be freely rotated, we can flip the branches at the root node. This moves the branch containing observation $9$ to the far left of the page while keeping observation $2$ on the right, without altering the clustering result in any way.
> 
> 

---

## Module 3: The Agglomerative Clustering Algorithm

### Mathematical Specification of Algorithm 12.3

```
  Step 1: Start with n singleton clusters. 
          Compute all n(n-1)/2 pairwise distances.
                            │
                            ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Step 2: Loop for i = n, n-1, ..., 2:                    │
 │   a. Search distance matrix for the two clusters with   │
 │      the minimum inter-cluster dissimilarity.           │
 │   b. Fuse these two clusters into a single cluster.     │
 │   c. Record the fusion height as this minimum distance. │
 │   d. Update the distance matrix between the new cluster │
 │      and all remaining clusters using a LINKAGE RULE.   │
 └─────────────────────────┬───────────────────────────────┘
                           │
                           ▼
  Step 3: Stop when all points belong to 1 single cluster.

```

* **Inputs:** A set of $n$ observations and a pairwise distance metric $d(\mathbf{x}_i, \mathbf{x}_j)$ (such as Euclidean distance).
* **Step 1 (Initialization):**
* Treat each observation as its own cluster: $C_1 = \{\mathbf{x}_1\}, C_2 = \{\mathbf{x}_2\}, \dots, C_n = \{\mathbf{x}_n\}$.
* Compute the initial symmetric dissimilarity matrix $\mathbf{D} \in \mathbb{R}^{n \times n}$, containing $\binom{n}{2} = \frac{n(n-1)}{2}$ unique pairwise distances.


* **Step 2 (Iterative Merging Loop):**
* For iteration $i = n, n-1, \dots, 2$:
1. Scan the current dissimilarity matrix to identify the pair of clusters $(A, B)$ with the smallest inter-cluster dissimilarity:

$$(A^*, B^*) = \arg\min_{A, B} D(A, B)$$


2. Fuse $A^*$ and $B^*$ into a new composite cluster: $C_{\text{new}} = A^* \cup B^*$.
3. Place the cross-bar connecting $A^*$ and $B^*$ in the dendrogram at height $h = D(A^*, B^*)$.
4. Remove rows and columns for $A^*$ and $B^*$ from the dissimilarity matrix.
5. Compute the dissimilarity between the new cluster $C_{\text{new}}$ and every remaining cluster $J$ using a **linkage criterion** $D(C_{\text{new}}, J)$.




* **Step 3 (Termination):** The algorithm terminates after $n - 1$ steps when all observations belong to a single cluster.

---

## Module 4: Linkage Criteria (Inter-Cluster Dissimilarity)

While the distance $d(\mathbf{x}_i, \mathbf{x}_j)$ between two individual points is well-defined, how do we measure the distance $D(A, B)$ between two **sets** of points? This choice is governed by the **linkage criterion**.

```
    Complete Linkage                     Single Linkage                      Average Linkage
  (Max Pairwise Distance)            (Min Pairwise Distance)              (Mean of All Pairs)
       Cluster A                          Cluster A                           Cluster A
     ┌───────────┐                      ┌───────────┐                       ┌───────────┐
     │  ●     ●  │                      │  ●     ●──┼─┐                     │  ●  \  /  │
     │     ●     │                      │     ●     │ │ d_min               │   \  ●  / │
     └─────┼─────┘                      └───────────┘ │                     └───┼──┼──┼─┘
           │ d_max                                    │                         │  │  │ d_avg
     ┌─────┼─────┐                      ┌───────────┐ │                     ┌───┼──┼──┼─┐
     │     ●     │                      │     ●─────┼─┘                     │  /   ●   \│
     │  ●     ●  │                      │  ●     ●  │                       │ /    ●    \
     └───────────┘                      └───────────┘                       └───────────┘
       Cluster B                          Cluster B                           Cluster B

```

---

### 1. Complete Linkage (Maximal Inter-Cluster Dissimilarity)

$$D_{\text{complete}}(A, B) = \max_{\mathbf{x} \in A, \, \mathbf{y} \in B} d(\mathbf{x}, \mathbf{y})$$

* **Operational Logic:** Two clusters are only as close as their **farthest pair of points**. A merge is penalized if even a single point in $A$ is far from a point in $B$.
* **Geometric Behavior:**
* Enforces an upper bound on cluster diameter ($\text{diam}(A \cup B) \le h$).
* Produces compact, spherical, tightly bound clusters of roughly equal diameter.
* Yields clean, well-balanced dendrograms.


* **Sensitivity:** Highly sensitive to outliers; a single distant outlier point inflates the maximal distance, preventing two otherwise close clusters from merging.

---

### 2. Single Linkage (Minimal Inter-Cluster Dissimilarity)

$$D_{\text{single}}(A, B) = \min_{\mathbf{x} \in A, \, \mathbf{y} \in B} d(\mathbf{x}, \mathbf{y})$$

* **Operational Logic:** Two clusters are as close as their **nearest pair of points** (a "nearest-neighbor" or "friends-of-friends" rule).
* **Geometric Behavior:** Can discover non-elliptical, elongated, concentric, or serpentine shapes.
* **The Chaining Phenomenon (Fatal Flaw):**
* If a sparse trail of intermediate noise points connects two distant clusters, single linkage will merge them step-by-step through the bridge points.
* Leads to long, straggly, "chain-like" clusters where isolated individual observations are absorbed one at a time.
* Produces highly unbalanced, comb-like dendrograms.



---

### 3. Average Linkage (Mean Inter-Cluster Dissimilarity)

$$D_{\text{average}}(A, B) = \frac{1}{\vert{}A\vert{} \cdot \vert{}B\vert{}} \sum_{\mathbf{x} \in A} \sum_{\mathbf{y} \in B} d(\mathbf{x}, \mathbf{y})$$

* **Operational Logic:** Computes the arithmetic mean of all pairwise distances between points in $A$ and points in $B$.
* **Geometric Behavior:**
* Strikes an effective balance between the conservative extremes of complete linkage (max) and single linkage (min).
* Relatively robust to noise and outliers.
* Tends to yield balanced, evenly structured dendrograms. Widely preferred by statisticians for general applications.



---

### 4. Centroid Linkage

$$D_{\text{centroid}}(A, B) = d(\bar{\mathbf{x}}_A, \bar{\mathbf{x}}_B) = \Vert{}\bar{\mathbf{x}}_A - \bar{\mathbf{x}}_B\Vert{}_2$$


where $\bar{\mathbf{x}}_A = \frac{1}{\vert{}A\vert{}}\sum_{\mathbf{x} \in A} \mathbf{x}$ is the centroid (mean vector) of cluster $A$.

* **Operational Logic:** Directly measures the distance between the two geometric centers of mass. Commonly used in genomics and biology.
* **The Inversion Problem (Fatal Flaw):**
* Centroid linkage violates the fundamental geometric condition of **monotonicity**.
* An **inversion** occurs when two clusters merge at a fusion height that is *lower* than the height at which one of the component clusters was formed:

$$h(A \cup B) < \max(h(A), h(B))$$


* When this happens, branches in the dendrogram point downward or cross backwards, making the tree difficult to interpret and invalidating horizontal cut-based partitioning.



```
Monotonic Dendrogram (Complete/Single/Average)     Non-Monotonic Dendrogram (Centroid Inversion)
        Height ^                                          Height ^
               │      ┌──────┐                                   │      ┌──────┐
            6.0┼──────┤      │                                6.0┼──────┤      │
               │      │      │                                   │      │      │
            4.0┼───┐  │      │                                4.0┼───┐  │      │ <─ Merged higher
               │   │  │      │                                   │   │  │   ┌──┤
            2.0┼───┴──┘      │                                2.0┼───┴──┼───┘  │ <─ Inversion! Merged
            0.0└───┴─────────┴─────>                          0.0└───┴──┴──────┴──> at a lower height

```

---

### Master Comparison of Linkage Criteria

| Linkage Type | Mathematical Definition | Cluster Geometry | Chaining Tendency | Outlier Sensitivity | Monotonicity (Inversions Possible?) |
| --- | --- | --- | --- | --- | --- |
| **Complete** | $\max_{\mathbf{x} \in A, \mathbf{y} \in B} d(\mathbf{x}, \mathbf{y})$ | Compact, spherical, balanced diameters. | None (strongly avoids chaining). | High (outliers inflate the maximum). | **Monotonic** (Inversions strictly impossible). |
| **Single** | $\min_{\mathbf{x} \in A, \mathbf{y} \in B} d(\mathbf{x}, \mathbf{y})$ | Extended, non-elliptical, arbitrary manifolds. | **Severe** (merges points along sparse bridges). | Low (ignores distant points). | **Monotonic** (Inversions strictly impossible). |
| **Average** | $\frac{1}{\Vert{}A\Vert{}\Vert{}B\Vert{}}\sum \sum d(\mathbf{x}, \mathbf{y})$ | Balanced, moderate compactness. | Minimal. | Moderate (averaging dampens outliers). | **Monotonic** (Inversions strictly impossible). |
| **Centroid** | $\Vert{}\bar{\mathbf{x}}_A - \bar{\mathbf{x}}_B\Vert{}_2$ | Grouped by centers of mass. | Low. | Moderate. | **Non-Monotonic** (**Inversions can occur**). |

---

### Brain Teaser 2: The Geometry of Centroid Inversions

> **Question:** Prove geometrically how an inversion can occur in Centroid Linkage. Construct a simple 1D example with three points where a merge occurs at a lower height than an earlier sub-merge.
> **Logical Solution:**
> Consider three points on a 1D real number line:
> 
> $$x_1 = 0, \quad x_2 = 10, \quad x_3 = 5$$
> 
> 
> 1. Compute pairwise Euclidean distances:
> * $d(x_1, x_2) = \vert{}0 - 10\vert{} = 10$
> * $d(x_1, x_3) = \vert{}0 - 5\vert{} = 5$
> * $d(x_2, x_3) = \vert{}10 - 5\vert{} = 5$
> 
> 
> 2. Suppose an algorithm first merges $x_1$ and $x_2$ into cluster $A = \{x_1, x_2\}$ at height $h = 10$ (for instance, if $x_3$ was added subsequently or evaluated in a constrained merge step).
> 3. The centroid of cluster $A$ is:
> 
> $$\bar{x}_A = \frac{0 + 10}{2} = 5$$
> 
> 
> 4. Now evaluate the distance from cluster $B = \{x_3\}$ to cluster $A$:
> 
> $$D_{\text{centroid}}(A, B) = \vert{}\bar{x}_A - x_3\vert{} = \vert{}5 - 5\vert{} = \mathbf{0}$$
> 
> 
> 5. **The Inversion:** The sub-cluster $A$ was formed at height $h = 10$, but it merges with $B$ at height **$h = 0$**! The new merge occurs *below* the existing branch, creating an inversion. Complete, single, and average linkage guarantee that inter-cluster distances never shrink as clusters grow, preventing this issue.
> 
> 

---

## Module 5: Distance Metrics & Variable Standardization

### 1. Euclidean vs. Correlation-Based Distance

The choice of dissimilarity metric shapes how similarity is defined:

* **Euclidean Distance (Magnitude-Sensitive):**

$$d_{\text{Euc}}(\mathbf{x}_i, \mathbf{x}_j) = \sqrt{\sum_{k=1}^p (x_{ik} - x_{jk})^2}$$



Measures absolute spatial separation in feature space.
* **Correlation-Based Distance (Profile/Shape-Sensitive):**

$$d_{\text{Cor}}(\mathbf{x}_i, \mathbf{x}_j) = 1 - r_{\mathbf{x}_i, \mathbf{x}_j} = 1 - \frac{\sum_{k=1}^p (x_{ik} - \bar{x}_i)(x_{jk} - \bar{x}_j)}{\sqrt{\sum_{k=1}^p (x_{ik} - \bar{x}_i)^2}\sqrt{\sum_{k=1}^p (x_{jk} - \bar{x}_j)^2}}$$


* *Unusual Application:* Pearson correlation is typically computed between two *features* across $n$ observations. Here, it is computed between two *observations* across $p$ features (comparing horizontal row profiles).
* Two observations with identical relative fluctuations across features will have $r = 1 \implies d_{\text{Cor}} = 0$, even if one observation's absolute values are 100 times larger than the other's.



```
       Observation Profiles in High-Dimensional Feature Space
       Feature Value
         ^
      100┼──────────────────●───────────● Target Profile A (High-volume shopper)
         │                 / \         /
       80┼──────●         /   \       /
         │     / \       /     \     /
       60┼────/───\─────/───────\───/───
         │   /     \   /         \ /
       10┼──●───────●─/───────────●───── Target Profile B (Low-volume shopper)
        0└───────────────────────────────> Features (Item Categories)
            F₁      F₂     F₃    F₄   F₅

  • Euclidean Distance: Extremely large (Values ~10 vs ~90 differ by ~80 at each point).
  • Correlation Distance: Exactly 0.0 (The shapes and trajectories are identical!).

```

#### Real-World Example: Customer Transaction Profiles

Consider an e-commerce platform clustering customer shopping baskets:

* Rows = Customers, Columns = Product Categories.
* Values = Number of lifetime purchases in each category.
* **If Euclidean distance is used:** High-volume shoppers cluster together simply because their transaction counts are high across all categories. Infrequent shoppers cluster together because their coordinates are all near zero. The model groups customers by spending volume rather than product interests.
* **If Correlation-based distance is used:** A shopper who bought 2 books, 1 movie, and 0 video games clusters with a power-buyer who bought 200 books, 100 movies, and 0 video games. The model groups customers by product preference profiles, regardless of overall spending level.

---

### 2. Variable Standardization (Scaling)

Should features be scaled to have empirical mean $0$ and standard deviation $1$ before computing dissimilarities?


$$x_{ik}' = \frac{x_{ik} - \bar{x}_k}{s_k}$$

* **The Scale Dominance Problem:**
* Suppose an online grocery store clusters customers using:
* $X_1$: Annual pairs of socks purchased ($\text{mean} = 12, \text{variance} = 36$).
* $X_2$: Annual desktop computers purchased ($\text{mean} = 0.2, \text{variance} = 0.15$).


* Socks are purchased far more frequently than computers.
* In unscaled Euclidean distance:

$$d^2 = (x_{i1} - x_{j1})^2 + (x_{i2} - x_{j2})^2$$



Differences in sock purchases $(\Delta X_1)^2$ will range from $10$ to $100$, while differences in computer purchases $(\Delta X_2)^2$ will rarely exceed $1$.
* Sock purchases will dominate the clustering, while computer purchases will be largely ignored, despite potentially being more informative.


* **Units of Measurement:** Measuring distance in kilometers versus centimeters scales variances by a factor of $(10^5)^2 = 10^{10}$. Without scaling, simply changing unit labels drastically alters the resulting dendrogram.
* **When NOT to Scale:** If all features are measured in identical physical units (e.g., pixel intensities in image processing, or gene expression levels on a standardized microarray) and absolute magnitude carries genuine real-world meaning, scaling can inadvertently amplify measurement noise in low-variance features.

---

## Module 6: Master Exam Question Bank

### Question 1: Manual Calculation of Hierarchical Clustering

> **Exam Question:** A one-dimensional dataset consists of four points on the real number line:
> 
> $$x_1 = 2.0, \quad x_2 = 4.0, \quad x_3 = 9.0, \quad x_4 = 12.0$$
> 
> 
> 
> Using Euclidean distance, trace the agglomerative hierarchical clustering process step-by-step:
> 1. Using **Complete Linkage**.
> 2. Using **Single Linkage**.
> 3. Draw the resulting fusion heights and verify if the two trees match or diverge.
> 
> 

#### Step-by-Step Solution:

#### Initial Setup:

Compute the initial pairwise Euclidean distance matrix for the four singleton clusters $\{1\}, \{2\}, \{3\}, \{4\}$:


$$D = \begin{bmatrix}  & \{1\} & \{2\} & \{3\} & \{4\} \\ \{1\} & 0 & 2 & 7 & 10 \\ \{2\} & 2 & 0 & 5 & 8 \\ \{3\} & 7 & 5 & 0 & 3 \\ \{4\} & 10 & 8 & 3 & 0 \end{bmatrix}$$

---

#### 1. Complete Linkage Execution:

* **Iteration 1:**
* Find the global minimum distance: $\min(D) = d(x_1, x_2) = \vert{}2 - 4\vert{} = \mathbf{2.0}$.
* **Merge:** Fuse $\{1\}$ and $\{2\}$ into cluster $\{1, 2\}$ at **height $h = 2.0$**.
* Update distances using complete linkage ($D(A, B) = \max(d(x, y))$):
* $D(\{1, 2\}, \{3\}) = \max(d(x_1, x_3), d(x_2, x_3)) = \max(\vert{}2-9\vert{}, \vert{}4-9\vert{}) = \max(7, 5) = \mathbf{7.0}$
* $D(\{1, 2\}, \{4\}) = \max(d(x_1, x_4), d(x_2, x_4)) = \max(\vert{}2-12\vert{}, \vert{}4-12\vert{}) = \max(10, 8) = \mathbf{10.0}$
* $D(\{3\}, \{4\}) = \vert{}9 - 12\vert{} = \mathbf{3.0}$


* Updated distance matrix:

$$D_1 = \begin{bmatrix}      & \{1, 2\} & \{3\} & \{4\} \\     \{1, 2\} & 0 & 7 & 10 \\     \{3\} & 7 & 0 & 3 \\     \{4\} & 10 & 3 & 0     \end{bmatrix}$$




* **Iteration 2:**
* Find the minimum distance in $D_1$: $\min(D_1) = D(\{3\}, \{4\}) = \mathbf{3.0}$.
* **Merge:** Fuse $\{3\}$ and $\{4\}$ into cluster $\{3, 4\}$ at **height $h = 3.0$**.
* Update distance between the two remaining clusters:
* $D(\{1, 2\}, \{3, 4\}) = \max(d(x_1, x_3), d(x_1, x_4), d(x_2, x_3), d(x_2, x_4)) = \max(7, 10, 5, 8) = \mathbf{10.0}$




* **Iteration 3 (Final Merge):**
* **Merge:** Fuse $\{1, 2\}$ and $\{3, 4\}$ into the single global cluster $\{1, 2, 3, 4\}$ at **height $h = 10.0$**.



---

#### 2. Single Linkage Execution:

* **Iteration 1:**
* The initial minimum distance is identical: fuse $\{1\}$ and $\{2\}$ at **height $h = 2.0$**.
* Update distances using single linkage ($D(A, B) = \min(d(x, y))$):
* $D(\{1, 2\}, \{3\}) = \min(d(x_1, x_3), d(x_2, x_3)) = \min(7, 5) = \mathbf{5.0}$
* $D(\{1, 2\}, \{4\}) = \min(d(x_1, x_4), d(x_2, x_4)) = \min(10, 8) = \mathbf{8.0}$
* $D(\{3\}, \{4\}) = \mathbf{3.0}$


* Updated distance matrix:

$$D_1' = \begin{bmatrix}      & \{1, 2\} & \{3\} & \{4\} \\     \{1, 2\} & 0 & 5 & 8 \\     \{3\} & 5 & 0 & 3 \\     \{4\} & 8 & 3 & 0     \end{bmatrix}$$




* **Iteration 2:**
* Find the minimum distance in $D_1'$: $\min(D_1') = D(\{3\}, \{4\}) = \mathbf{3.0}$.
* **Merge:** Fuse $\{3\}$ and $\{4\}$ into cluster $\{3, 4\}$ at **height $h = 3.0$**.
* Update distance using single linkage:
* $D(\{1, 2\}, \{3, 4\}) = \min(d(x_1, x_3), d(x_1, x_4), d(x_2, x_3), d(x_2, x_4)) = \min(7, 10, 5, 8) = \mathbf{5.0}$




* **Iteration 3 (Final Merge):**
* **Merge:** Fuse $\{1, 2\}$ and $\{3, 4\}$ at **height $h = 5.0$**.



---

#### Comparison Summary:

* **Tree Topologies:** Both linkages yield identical merge orderings: $(\{1\}, \{2\})$ fuses first, followed by $(\{3\}, \{4\})$, and finally the two composite clusters merge.
* **Divergence in Root Fusion Height:**
* Complete Linkage root height $= \mathbf{10.0}$ (farthest pair: $\vert{}2 - 12\vert{}$).
* Single Linkage root height $= \mathbf{5.0}$ (nearest pair: $\vert{}4 - 9\vert{}$).
* Cutting at height $h = 6.0$ yields **$2$ clusters** under Complete Linkage ($\{1, 2\}$ and $\{3, 4\}$), but **$1$ single cluster** under Single Linkage.



---

### Question 2: The Ultrametric Inequality and Monotonic Growth

> **Exam Question:** What mathematical property ensures that dendrogram branches always grow upward without inversions? Prove that single linkage satisfies this condition.

#### Analytical Solution:

1. **The Monotonicity Condition:**
A hierarchical clustering algorithm is monotonic if the dissimilarity between merged clusters never decreases as the tree grows:

$$D(A \cup B, C) \ge D(A, B)$$



This ensures that every child node fuses at a height strictly lower than its parent, preventing inversions.
2. **Proof for Single Linkage:**
Let cluster $A$ merge with cluster $B$ at height $h_1 = D(A, B) = \min_{\mathbf{x} \in A, \mathbf{y} \in B} d(\mathbf{x}, \mathbf{y})$.
Let $C$ be any other existing cluster. When $A$ and $B$ fuse into $A \cup B$, the single linkage distance to $C$ is:

$$D(A \cup B, C) = \min_{\mathbf{u} \in A \cup B, \, \mathbf{v} \in C} d(\mathbf{u}, \mathbf{v}) = \min\left( \min_{\mathbf{x} \in A, \mathbf{v} \in C} d(\mathbf{x}, \mathbf{v}), \, \min_{\mathbf{y} \in B, \mathbf{v} \in C} d(\mathbf{y}, \mathbf{v}) \right)$$


$$D(A \cup B, C) = \min\left( D(A, C), \, D(B, C) \right)$$



Since $A$ and $B$ were chosen for merging specifically because their distance was minimal across the entire matrix:

$$D(A, B) \le D(A, C) \quad \text{and} \quad D(A, B) \le D(B, C)$$



Therefore:

$$D(A \cup B, C) = \min(D(A, C), D(B, C)) \ge D(A, B)$$



The merge distance cannot decrease, proving that **single linkage is strictly monotonic** ($\blacksquare$).

---

### Question 3: Choosing Between Euclidean and Correlation Distance

> **Exam Question:** A genomics laboratory clusters $n = 50$ cancer tissue samples based on expression levels across $p = 20,000$ genes. Patient A and Patient B have identical expression patterns, but Patient A's absolute signal intensities are consistently twice as large as Patient B's due to experimental dye concentration differences. Which distance metric should be used, and what would happen if the wrong metric were chosen?

#### Analytical Solution:

* **Recommended Metric:** **Correlation-Based Distance** ($d = 1 - r$).
* **Mechanism:**
Let $\mathbf{x}_A = 2 \cdot \mathbf{x}_B$.
Subtracting means and dividing by standard deviations normalizes the expression vectors:

$$r_{\mathbf{x}_A, \mathbf{x}_B} = \frac{\sum_k (x_{Ak} - \bar{x}_A)(x_{Bk} - \bar{x}_B)}{(p - 1) s_A s_B} = \frac{\sum_k 2(x_{Bk} - \bar{x}_B)(x_{Bk} - \bar{x}_B)}{(p - 1)(2 s_B)(s_B)} = \frac{2 \sum_k (x_{Bk} - \bar{x}_B)^2}{2(p - 1) s_B^2} = 1.0$$



This gives:

$$d_{\text{Cor}}(\mathbf{x}_A, \mathbf{x}_B) = 1 - 1.0 = \mathbf{0.0}$$



Correlation-based distance correctly identifies that both patients share the exact same biological profile, successfully factoring out the technical dye concentration artifact.
* **Failure of Euclidean Distance:**

$$d_{\text{Euc}}(\mathbf{x}_A, \mathbf{x}_B) = \sqrt{\sum_{k=1}^{20,000} (2x_{Bk} - x_{Bk})^2} = \sqrt{\sum_{k=1}^{20,000} x_{Bk}^2} = \Vert{}\mathbf{x}_B\Vert{}_2$$



Over 20,000 genes, this sum produces a very large Euclidean distance. The algorithm would assign the two patients to different clusters purely based on experimental dye concentration rather than their shared underlying biology.

---

### Question 4: The Chaining Effect in Single Linkage

> **Exam Question:** Explain the "chaining effect" in agglomerative clustering. Which linkage criterion causes it, and what structural pattern does it produce in the resulting dendrogram?

#### Analytical Solution:

* **Causal Linkage:** **Single Linkage** ($D(A, B) = \min d(x, y)$).
* **The Underlying Mechanism:**
Single linkage calculates dissimilarity using only the closest pair of points between two clusters. If a sparse path of intermediate points connects two well-separated, dense clusters, single linkage will merge the points sequentially along this "bridge" like dominoes.
* **Resulting Dendrogram Pattern:**
* Generates an **unbalanced, highly skewed, comb-like dendrogram**.
* Rather than joining distinct sub-branches of comparable size, single observations are absorbed into one growing central cluster one at a time.
* Masks compact, spherical clusters and provides poor cluster partitions when horizontal cuts are applied.



---

### Question 5: Variable Scaling Diagnostic Scenario

> **Exam Question:** An analyst clusters customers using two variables: $X_1$ = Age (ranging from $20$ to $60$ years) and $X_2$ = Salary (ranging from $\$30,000$ to $\$150,000$).
> 1. Compute the contribution to squared Euclidean distance between two customers differing by 10 years in age vs. two customers differing by $\$1,000$ in salary.
> 2. Explain why standardization is necessary here and describe its effect on the feature space.
> 
> 

#### Analytical Solution:

1. **Distance Contributions:**
* Age difference of $\Delta X_1 = 10$:

$$(\Delta X_1)^2 = 10^2 = \mathbf{100}$$


* Salary difference of $\Delta X_2 = \$1,000$:

$$(\Delta X_2)^2 = 1,000^2 = \mathbf{1,000,000}$$


* The $\$1,000$ salary difference contributes **10,000 times more** to the distance metric than the 10-year age difference, effectively reducing the analysis to a 1D clustering on salary alone.


2. **The Effect of Standardization:**
* Dividing each variable by its standard deviation $s_k$ rescales the axes:

$$x_{ik}' = \frac{x_{ik} - \bar{x}_k}{s_k}$$


* Transforms the feature space so that a 1-standard-deviation change in Age carries the exact same mathematical weight as a 1-standard-deviation change in Salary, ensuring balanced feature attribution.



---

## Final Review: Exam-Day Formulas Cheat Sheet

| Evaluation Metric / Linkage | Governing Formula / Decision Rule |
| --- | --- |
| **Residual Sum of Squares (RSS)** | $RSS = \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 = \mathbf{e}^T\mathbf{e}$ |
| **Mean Squared Error (MSE)** | $MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 = \frac{RSS}{n}$ |
| **Root Mean Squared Error (RMSE)** | $RMSE = \sqrt{MSE} = \sqrt{\frac{RSS}{n}}$ |
| **Residual Standard Error (RSE)** | $RSE = \sqrt{\frac{RSS}{n - p - 1}}$ |
| **Mean Absolute Error (MAE)** | $MAE = \frac{1}{n} \sum_{i=1}^{n} \vert y_i - \hat{y}_i \vert$ |
| **Coefficient of Determination (R²)** | $R^2 = 1 - \frac{RSS}{TSS} = \frac{ESS}{TSS}$ |
| **Adjusted R²** | $R^2_{adj} = 1 - \left( \frac{RSS / (n - p - 1)}{TSS / (n - 1)} \right)$ |
| **Mallows' $C_p$** | $C_p = \frac{1}{n}(RSS + 2p\hat{\sigma}^2)$ |
| **Akaike Information Criterion (AIC)** | $AIC = n \ln\left(\frac{RSS}{n}\right) + 2p$ |
| **Bayesian Information Criterion (BIC)** | $BIC = n \ln\left(\frac{RSS}{n}\right) + p \ln(n)$ |
| **Huber Loss (Threshold $\delta$)** | $L_\delta(e) = \frac{1}{2}e^2 \text{ if } \vert e \vert \le \delta \text{ else } \delta(\vert e \vert - \frac{1}{2}\delta)$ |
| **Complete Linkage** | $D(A, B) = \max_{x \in A, y \in B} d(x, y)$ |
| **Single Linkage** | $D(A, B) = \min_{x \in A, y \in B} d(x, y)$ |
| **Average Linkage** | $D(A, B) = \frac{1}{\vert A \vert \vert B \vert} \sum_{x \in A} \sum_{y \in B} d(x, y)$ |
| **Centroid Linkage** | $D(A, B) = \Vert \bar{x}_A - \bar{x}_B \Vert_2$ *(Can cause inversions!)* |
| **Correlation Distance** | $d_{Cor}(x, y) = 1 - r_{xy}$ *(Compares observation profile shapes)* |