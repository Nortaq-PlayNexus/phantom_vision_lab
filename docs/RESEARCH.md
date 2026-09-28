# PHANTOM VISION LAB - Research Documentation

## 1. What Is Established Scientifically

### Predictive Processing / Predictive Coding
- The brain (and computational analogues) generate predictions about incoming sensory data
- Prediction errors drive updates to internal models (Rao & Ballard, 1999; Friston, 2005)
- Altering the balance between prediction and error processing changes perception

### Visual Perception of Structured Patterns
- Humans and computational systems are sensitive to symmetry, regularity, and geometric structure (Palmer, 1999)
- Grid lattices and repeating patterns activate orientation-selective systems in V1
- Fractal patterns with specific fractal dimensions (1.3-1.5) are particularly salient (Taylor et al., 2011)

### Feature Visualization / Activation Perturbation
- Deep neural networks can be interrogated by visualizing activations (Yosinski et al., 2015)
- Activation perturbation studies show that noise injection changes network behavior (Goodfellow et al., 2015)
- Feature visualization reveals that networks develop internal representations of geometric patterns

### Hallucination in AI/Vision-Language Models
- Current vision-language models produce confident but incorrect interpretations (Gao et al., 2022)
- These "hallucinations" are systematic and related to training biases
- Structural perturbations can alter the types of misinterpretations produced

## 2. What Is Plausible But Unproven

- **Cross-modal associations in vision**: Visual patterns may trigger non-visual semantic associations in multimodal models (Radford et al., 2021). The strength of this effect under perturbation is unmeasured.
- **Recursive attention effects**: Iterative self-referential processing may alter representation stability in transformers (Vaswani et al., 2017). No empirical test of this in perception tasks exists.
- **Pattern amplification**: Boosting repeating structures may disproportionately affect transformer attention patterns, since they are inherently pattern-sensitive.
- **Novelty-driven reinterpretation**: Increasing attention to unusual features may cause models to generate novel but ungrounded interpretations.

## 3. What Is Speculative

- Whether computational perturbation analogues to sensory gain modulation actually produce emergent geometric/symbolic interpretations in AI systems
- Whether specific parameter combinations correspond to qualitatively different "altered states" of processing
- Whether the perception divergence score captures anything analogous to subjective experience differences
- Whether code-like interpretation emergence under perturbation indicates any deep structural property of neural networks

## 4. What This Experiment Can Actually Measure

- Changes in geometric pattern detection scores between baseline and altered configurations
- Changes in confidence, uncertainty, and novelty metrics
- Emergence of code-like structures (grid patterns, sequential arrangements) in edge/structure analysis
- Semantic concept shifts in model descriptions
- Embedding distance between baseline and altered representations
- Reproducibility of these effects across seeds

## 5. What It Cannot Establish

- Whether the AI is "experiencing" anything at all (no consciousness test possible)
- Whether observed effects are specific to the type of perturbation (vs. any perturbation)
- Whether results generalize across different model architectures
- Whether the effects have any correspondence to biological psychedelic perception
- Causal mechanisms (correlation only)

## 6. Technical Design Implications

### Determinism
- All generators use seeded random number generators
- Experiment IDs and parameter sets are recorded
- Full replay is possible from metadata alone

### Modularity
- VisionModelProvider interface allows swapping analysis backends
- AlteredStateEngine parameters are configurable and saveable
- StimulusGenerator supports 15+ pattern types with deterministic seeds

### Anti-Priming
- Vision analysis describes what it sees independently
- Code-like structure detection happens as a separate post-hoc classification
- No language in analysis prompts suggests looking for specific patterns

## 7. Full Bibliography

- Ballard, D. H., & Rao, R. P. (1995). Predictive coding in the visual cortex. *Current Opinion in Neurobiology*, 5(1), 79-84.
- Friston, K. (2005). A theory of cortical responses. *Philosophical Transactions of the Royal Society B*, 360(1456), 815-846.
- Palmer, S. E. (1999). *Vision Science: Photons to Phenomenology*. MIT Press.
- Taylor, R. P., et al. (2011). Human attraction to fractal visual patterns. *Perception*, 40(3), 312-323.
- Yosinski, J., et al. (2015). Understanding neural networks through visualization. *ICML Workshop*.
- Goodfellow, I., et al. (2015). Explaining and harnessing adversarial examples. *ICLR*.
- Gao, C., et al. (2022). Why can GPT learn in-context? *NeurIPS*.
- Vaswani, A., et al. (2017). Attention is all you need. *NeurIPS*.
- Radford, A., et al. (2021). Learning transferable visual models from natural language supervision. *ICML*.
- Clauset, A., Shalizi, C. R., & Newman, M. E. (2009). Power-law distributions in empirical data. *SIAM Review*, 51(4), 661-703.

---

## Disclaimer

This is a computational simulation. It does not reproduce a biological psychedelic state and does not establish subjective consciousness. All measurements are derived from mathematical image analysis algorithms, not from neural network internal states. This software simulates computational changes in AI perception. It does not claim that the AI is literally having any experience.
