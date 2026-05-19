# GIGP Framework

The Generalized Immanantal Gibbs Process (GIGP) unifies 8 point process classes into three independent multiplicative blocks:

**Block 1 — Intensity Λ:** controls where events tend to appear.
- Uniform → Poisson
- exp(GP) → Log-Gaussian Cox Process
- Heavy-tailed → Alpha-Stable

**Block 2 — Immanant Imm_β(K):** controls correlation structure between events.
- β = -1 → DPP (repulsion)
- β = 0 → Poisson (independence)
- β = +1 → Permanental (attraction)

**Block 3 — Gibbs Energy:** explicit hard constraints.
- w_S > 0 → Strauss (exclusion threshold)
- w_H > 0 → Hawkes (ordered dependence)

See paper for full mathematical derivation.
