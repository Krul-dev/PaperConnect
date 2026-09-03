# Research Report: Bridging Missing Data Theory and Deep Learning Imputation

This curated collection of **11 key sources** addresses the critical gap between classical missing data theory (Rubin's framework, MNAR, inferential validity) and modern deep learning imputation architectures (GANs, VAEs, diffusion models).

---

## 📄 Core Literature Summary Table

| # | Title | Venue / Source | Date |
| :--- | :--- | :--- | :--- |
| 1 | [On the use of the not-at-random fully conditional specification (NARFCS) procedure in practice](https://doi.org/10.1002/sim.7643) | *Statistics in Medicine* | 2018 |
| 2 | [Tipping Point Analysis: Assessing the Potential Impact of Missing Data](https://jamaevidence.mhmedical.com/content.aspx?bookid=2742&sectionid=305449669) | *JAMA Guide to Statistics and Methods* | 2019 |
| 3 | [FragmGAN: Generative Adversarial Nets for Fragmentary Data Imputation and Prediction](https://doi.org/10.1080/24754269.2023.2185532) | *Statistical Theory and Related Fields* | 2023 |
| 4 | [Handling Incomplete Heterogeneous Data using VAEs](https://arxiv.org/abs/1807.03653) | *arXiv* | 2020 |
| 5 | [MIWAE: Deep Generative Modelling and Imputation of Incomplete Data Sets](https://proceedings.mlr.press/v97/mattei19a.html) | *ICML* | 2019 |
| 6 | [not-MIWAE: Deep Generative Modelling with Missing not at Random Data](https://arxiv.org/abs/2006.12871) | *ICLR* | 2021 |
| 7 | [Deep Generative Imputation Model for Missing Not At Random Data](https://arxiv.org/abs/2308.08158) | *arXiv* | 2023 |
| 8 | [Deep Generative Missingness Pattern-Set Mixture Models](https://proceedings.mlr.press/v130/ghalebikesabi21a/ghalebikesabi21a.pdf) | *AISTATS* | 2021 |
| 9 | [IVGAE: Handling Incomplete Heterogeneous Data with a Variational Graph Autoencoder](https://arxiv.org/abs/2511.22116) | *arXiv* | 2025 |
| 10 | [Beyond Accuracy: An Empirical Study of Uncertainty Estimation in Imputation](https://arxiv.org/abs/2511.21607) | *arXiv* | 2025 |
| 11 | [Flexible Imputation of Missing Data (Section 2.6: Imputation is not prediction)](https://stefvanbuuren.name/fimd/sec-true.html) | *CRC Press / Stef van Buuren* | 2018 |

---

## 🔍 Detailed Thematic Analysis

### Theme 1: MNAR Identification, Taxonomy, and Sensitivity Analysis

#### (1) Tompsett, D. M., Leacy, F., Moreno-Betancur, M., Heron, J., & White, I. R. (2018)
* **Title:** On the use of the not-at-random fully conditional specification (NARFCS) procedure in practice
* **Explanation:** This paper formalizes NARFCS to execute multivariable missing data imputation under MNAR by shifting imputation distributions using explicit sensitivity parameters, providing a crucial bridge from MAR defaults to structured sensitivity testing.

#### (2) Liu, Y., Zhou, K., & Sims, K. D. (2019)
* **Title:** Tipping Point Analysis: Assessing the Potential Impact of Missing Data
* **Explanation:** It provides an accessible, rigorous clinical framework for conducting tipping-point sensitivity analyses, explaining how to systematically shift assumptions about MNAR values to locate the boundary where statistical conclusions are overturned.

---

### Theme 2: Theoretical Validity of DL Imputation Under Different Mechanisms

#### (3) Fang, F., & Bao, S. (2023)
* **Title:** FragmGAN: Generative Adversarial Nets for Fragmentary Data Imputation and Prediction
* **Explanation:** This paper critiques the popular GAIN model, showing that its foundational "hint mechanism" implicitly assumes MCAR, and introduces FragmGAN to provide explicit theoretical guarantees of convergence under the more general MAR mechanism.

#### (4) Nazábal, A., Olmos, P. M., Ghahramani, Z., & Valera, I. (2020)
* **Title:** Handling Incomplete Heterogeneous Data using VAEs
* **Explanation:** It formally outlines the mathematical conditions under which Variational Autoencoders are valid for fitting mixed-type incomplete tables, explicitly grounding VAE reconstruction in the statistical assumptions of MAR.

---

### Theme 3: Deep Generative Models Designed for MNAR

#### (5) Mattei, P.-A., & Frellsen, J. (2019)
* **Title:** MIWAE: Deep Generative Modelling and Imputation of Incomplete Data Sets
* **Explanation:** Introduces the Importance-Weighted Variational Autoencoder (MIWAE) framework designed to maximize a tight lower bound of the observed log-likelihood, establishing a highly competitive generative baseline under MAR.

#### (6) Ipsen, N. B., Mattei, P.-A., & Frellsen, J. (2021)
* **Title:** not-MIWAE: Deep Generative Modelling with Missing not at Random Data
* **Explanation:** This seminal paper directly bridges deep learning and non-ignorable theory by coupling a VAE with a deep neural network that explicitly models the conditional distribution of the missingness pattern under MNAR.

#### (7) Chen, J., Xu, Y., Wang, P., & Yang, Y. (2023)
* **Title:** Deep Generative Imputation Model for Missing Not At Random Data
* **Explanation:** It proposes GNR, which treats the complete data and the missingness mask as two modalities on equal footing, using a "conjunction model" in latent space to preserve the confidence of the reconstructed mask under MNAR.

#### (8) Ghalebikesabi, S., Cornish, R., Holmes, C., & Kelly, L. J. (2021)
* **Title:** Deep Generative Missingness Pattern-Set Mixture Models
* **Explanation:** It combines VAEs with classical pattern-set mixture models (PSMVAE) to perform robust imputation under both MCAR and MNAR, preventing the catastrophic failures of MAR-assuming deep models when the missingness mechanism is misspecified.

#### (9) Anonymous / Preprint (2025)
* **Title:** IVGAE: Handling Incomplete Heterogeneous Data with a Variational Graph Autoencoder
* **Explanation:** It introduces a dual-decoder VAE (one for feature embeddings, one for missingness patterns) over a sample-feature bipartite graph, showing how embedding structural missingness priors can yield consistent improvements under MCAR, MAR, and MNAR.

---

### Theme 4: Tension Between Point Reconstruction (RMSE) and Inferential Validity

#### (10) Anonymous / Preprint (2025)
* **Title:** Beyond Accuracy: An Empirical Study of Uncertainty Estimation in Imputation
* **Explanation:** This extensive benchmark demonstrates that reconstruction accuracy (RMSE) and uncertainty calibration are frequently misaligned, proving that highly accurate deep generative models (like GAIN, TabCSDI) often produce miscalibrated uncertainty intervals that fail downstream statistical tests.

#### (11) Stef van Buuren (2018)
* **Title:** Flexible Imputation of Missing Data (Section 2.6: Imputation is not prediction)
* **Explanation:** In this foundational text, van Buuren mathematically demonstrates why optimizing for the lowest RMSE (i.e. treating imputation as a deterministic prediction task) suppresses natural variance, resulting in severely biased standard errors and invalid statistical inference.

---

## 📈 Key Synthesis Themes Across Literature

* **The RMSE Fallacy:** Across both classic statistical texts (van Buuren, 2018) and modern benchmarks (*Beyond Accuracy*, 2025), there is a consensus that optimizing purely for reconstruction error (RMSE) systematically underrepresents imputation uncertainty, leading to invalid downstream statistical inference.
* **Joint Modeling of the Mask:** Seminal advances in deep latent variable models under non-ignorable missingness (*not-MIWAE*, *GNR*, *IVGAE*) achieve robustness by explicitly modeling the joint distribution of the data and the missingness indicator matrix, rather than assuming ignorability.
* **Explicit Sensitivity Controls:** Since MNAR mechanisms cannot be verified using observed data alone, papers like NARFCS (Tompsett et al., 2018) and Tipping Point Guides (Liu et al., 2019) emphasize using adjustable "delta" sensitivity parameters to explore the robustness of conclusions.

---
*Research compiled and synthesized on September 3, 2026.*
