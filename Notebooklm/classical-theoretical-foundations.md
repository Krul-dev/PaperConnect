# Classical Theoretical Foundations of Missing Data Inferences

This report compiles the pre-2018 classical statistical foundations that underwrite modern deep learning imputation architectures. When modern frameworks (such as *not-MIWAE*, *PSMVAE*, or *FragmGAN*) handle non-ignorable missingness (MNAR), they directly translate, scale, or parameterize these exact mathematical structures.

---

## 1. Selection Models vs. Pattern-Mixture Models

To model the joint distribution of the data matrix $Y$ and the missingness indicator mask $M$, classical statistics established two distinct factorizations. Modern deep learning models are fundamentally divided along these same two conceptual lines.

### Heckman, J. J. (1979)
* **Title:** *"Sample selection bias as a specification error"*
* **Theoretical Contribution:** Formalizes the classical **Selection Model** factorization:
  $$f(Y, M \mid X) = f(Y \mid X) P(M \mid Y, X)$$
  It demonstrates that when missingness is non-random, treating the observed data as a representative sample introduces a specification bias analogous to omitted variables.
* **Modern Bridge:** Direct theoretical ancestor to **not-MIWAE** (Ipsen et al., 2021) and **GNR** (Chen et al., 2023), which use deep neural networks to model the highly complex conditional distribution of the missingness mask $P(M \mid Y)$ rather than assuming ignorability.

### Little, R. J. (1993)
* **Title:** *"Pattern-mixture models for multivariate incomplete data"*
* **Theoretical Contribution:** Formalizes the **Pattern-Mixture Model** factorization:
  $$f(Y, M \mid X) = f(Y \mid M, X) P(M \mid X)$$
  This approach models distinct, pattern-specific distributions for the data conditioned on the observed missingness pattern, utilizing identifying restrictions to handle the unobserved strata.
* **Modern Bridge:** Directly underpins **PSMVAE** (Ghalebikesabi et al., 2021), which maps these classical pattern-specific mixture distributions into deep latent spaces using variational autoencoders.

### Diggle, P. J., & Kenward, M. G. (1994)
* **Title:** *"Informative drop-out in longitudinal data analysis"*
* **Theoretical Contribution:** Establishes the first fully parametric longitudinal selection model for continuous data with informative dropout.
* **Modern Bridge:** Serves as the mathematical benchmark for modern recurrent and bidirectional MNAR imputation networks (e.g., BRITS) that attempt to capture temporal decay and informative transitions.

---

## 2. The Taxonomy of MNAR

Before a deep learning model can be engineered to process non-randomly missing data, researchers must characterize *how* the missingness process behaves. The formal taxonomy of these mechanisms originates in these works.

### Little, R. J. (1995)
* **Title:** *"Modeling the drop-out mechanism in repeated-measures studies"*
* **Theoretical Contribution:** Systematically defines and contrasts covariate-dependent dropout (where missingness depends on observed baseline characteristics) and outcome-dependent dropout (self-masking MNAR).
* **Modern Bridge:** Establishes the classification system and testing criteria used to design synthetic missingness masks in modern deep learning benchmarks (such as the *Beyond Accuracy* 2025 study).

### Heckman, J. J. (1976)
* **Title:** *"The common structure of statistical models of truncation, sample selection and limited dependent variables and a simple estimator for such models"*
* **Theoretical Contribution:** Mathematically defines threshold-based truncation and self-censoring, establishing the limits of what can be recovered when data is systematically missing due to its own extreme values.
* **Modern Bridge:** Essential for understanding **sensor clipping and physical saturation** in environmental monitoring (e.g., air pollution monitors failing precisely when particulate concentrations exceed toxic thresholds).

---

## 3. Sensitivity Analysis & Tipping-Point Origins

Because MNAR mechanisms cannot be verified using observed data alone, classical statistics pioneered sensitivity analysis. Rather than searching for a single "perfect" imputation, this paradigm evaluates how robust conclusions are to variations in non-random assumptions.

### Scharfstein, D. O., Rotnitzky, A., & Robins, J. M. (1999)
* **Title:** *"Adjusting for nonignorable consecutive drop-out in semiparametric nonresponse models"*
* **Theoretical Contribution:** Introduces semiparametric sensitivity parameters to systematically perturb the probability of non-response, validating the use of non-identifiable offsets to map boundaries of statistical inference.
* **Modern Bridge:** Groundwork for the mathematical integration of structured sensitivity bounds into generative autoencoders and probabilistic predictors.

### Carpenter, J. R., Kenward, M. G., & White, I. R. (2007)
* **Title:** *"Sensitivity analysis after multiple imputation under missing at random: a weighting approach"*
* **Theoretical Contribution:** Introduces the formal **$\delta$-adjustment (offset) method** within multiple imputation frameworks, where imputed values are systematically shifted by a sensitivity parameter $\delta$.
* **Modern Bridge:** This direct mathematical formulation is what multivariable sensitivity frameworks—such as **NARFCS** (Tompsett et al., 2018)—generalize and scale for high-dimensional settings.

---

## 4. Ignorability & Its Consequences

To critically evaluate what modern deep learning models gain—and what they risk losing—one must return to the foundational theorems defining the boundaries of statistical ignorability.

### Rubin, D. B. (1976)
* **Title:** *"Inference and missing data"*
* **Theoretical Contribution:** The seminal mathematical formulation of Missing Completely at Random (MCAR), Missing at Random (MAR), and the exact conditions under which the missingness mechanism is "ignorable" for likelihood-based and Bayesian inferences.
* **Modern Bridge:** The ultimate yardstick of the field. Every modern deep learning paper makes implicit or explicit assumptions regarding Rubin's taxonomy (e.g., *FragmGAN* proving that GAIN's hint matrix restricts its validity to Rubin's MCAR condition).

### Little, R. J., & Rubin, D. B. (1987 / 2002)
* **Title:** *Statistical Analysis with Missing Data (Textbook)*
* **Theoretical Contribution:** The definitive textbook of the discipline. It mathematically demonstrates that applying MAR-assuming imputation methods (like standard expectation-maximization or basic multiple imputation) to MNAR data introduces systematic asymptotic bias and severely invalidates downstream hypothesis testing.
* **Modern Bridge:** Essential reading for the "Inference vs. Reconstruction" debate, proving why minimizing point-accuracy error (lowest RMSE) often comes at the cost of statistical validity.

### Dempster, A. P., Laird, N. M., & Rubin, D. B. (1977)
* **Title:** *"Maximum Likelihood from Incomplete Data via the EM Algorithm"*
* **Theoretical Contribution:** Formalizes the Expectation-Maximization (EM) algorithm for computing maximum likelihood estimates from incomplete data under MAR.
* **Modern Bridge:** The classic mathematical optimization engine that modern latent-variable deep architectures (such as VAEs, MIWAE, and diffusion models) seek to parallel and accelerate in high dimensions.
