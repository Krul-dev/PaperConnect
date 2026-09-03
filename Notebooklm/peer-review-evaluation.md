# Peer Review Evaluation: Missing Data Inferences in Multivariate Air Pollution Time Series

**Subject:** Critical Methodological Evaluation of the Combined Literature Library (SIMA Personal + Curated Candidates)  
**Target Focus:** Narrative Review on Imputation for Multivariate Time Series in Air Pollution (*From Rubin to SAITS*)  
**Reviewer Stance:** Senior Academic Peer Reviewer in Statistics & Missing Data Methodology  

---

## Executive Summary

The evaluated collection (104 total works) traces an ambitious trajectory spanning classical inferential statistics (Dempster, Laird, & Rubin, 1977; Rubin, 1976; van Buuren, 2011) to cutting-edge deep generative and self-attention models (BRITS, SAITS, CSDI). 

However, when examined through the lens of rigorous statistical theory and environmental health applications, the library reveals profound structural imbalances:
1. **Architectural saturation vs. theoretical deficit:** Deep learning models are heavily represented but treated almost exclusively as deterministic curve-fitting point predictors.
2. **Neglect of non-ignorable missingness (MNAR):** Self-masking sensor saturation and systemic instrument failure mechanisms are ignored in favor of synthetic uniform MCAR benchmarking.
3. **Complete omission of causal inference:** Not a single paper bridges missing data mechanics with causal Directed Acyclic Graphs (m-DAGs) or confounding/collider bias.
4. **Neglect of downstream inferential validity:** The tension between signal reconstruction (minimizing RMSE) and valid parameter estimation (preserving standard errors and hypothesis tests) is unaddressed.

---

## 1. Modern Algorithmic Approaches

### Coverage Status: Saturated in Architecture, Deficient in Theory

The collection provides extensive coverage of modern deep learning and generative architectures developed between 2019 and 2026 (over 35 papers), including:
* **Generative Adversarial Frameworks:** Generative Adversarial Imputation Networks (GAIN), Wasserstein GAIN with Variational Autoencoders (WGAIN-VAE), Federated conditional GANs (Fed-cGAN), USGAN, and ImpuGAN.
* **Recurrent & Bidirectional Models:** Bidirectional Recurrent Imputation for Time Series (BRITS), Im-BiLSTM, and Recurrent Neural Network Denoising Autoencoders (RNN-DAE).
* **Self-Attention & Transformers:** Self-Attention-based Imputation for Time Series (SAITS), Contribution and Attention Networks (ContrAttNet), and Vision/Wavelet Transformers (X-WaveVT).
* **Diffusion & Score-Based Models:** Conditional Score-based Diffusion Models (CSDI) and boundary-enhanced long-term dependency diffusion models.

### Critical Methodological Holes:
* **Point Reconstruction vs. Distributional Sampling:** Current deep learning literature overwhelmingly evaluates models using root mean square error (RMSE) or mean absolute error (MAE). There is virtually no theoretical exploration of whether deep generative models draw authentic samples from the underlying conditional distribution $\mathbb{P}(X_{\text{mis}} \mid X_{\text{obs}})$ or collapse into mode-seeking point approximations.
* **Absence of Neural/Gaussian Process Hybrids:** While pure neural networks dominate the corpus, Gaussian Process (GP) state-space formulations and Deep Neural Processes—which explicitly output calibrated epistemic and aleatoric uncertainty bounds for spatiotemporal interpolation—are completely omitted.

---

## 2. Missingness Mechanisms: The MNAR Blind Spot

### Coverage Status: Severely Deficient

The library relies on Rubin’s (1976) seminal definitions, Little’s (1993) pattern-mixture modeling, and broad high-level taxonomies (Emmanuel et al., 2021). Beyond these, modern theoretical and empirical treatments of **Missing Not At Random (MNAR)** are absent.

### Critical Methodological Holes:
* **The Reality of Sensor Saturation and Clipping:** In ambient air quality monitoring, electrochemical and optical sensors frequently fail, saturate, or produce corrupted readings during extreme pollution episodes (e.g., severe wildfire smoke, toxic industrial plumes, or filter clogging from high $\text{PM}_{10}$ loading). This is an archetypal self-masking MNAR mechanism:
  11\mathbb{P}(M_{it} = 1 \mid Y_{it}) \neq \mathbb{P}(M_{it} = 1)11
  Despite this physical reality, nearly every modern time-series paper in the collection tests algorithms by randomly dropping observations (uniform MCAR) or assuming ignorability (MAR).
* **Identification Under Non-Ignorable Missingness:** The collection contains no coverage of modern econometric and statistical breakthroughs regarding non-parametric identification under MNAR, such as:
  * **Shadow Variables / Negative Controls:** Using auxiliary variables related to the complete data but conditionally independent of the missingness indicator.
  * **Instrumental Variables for Non-Response:** Formulations that allow identification of outcome distributions without untestable parametric assumptions.
* **Sensitivity & Tipping-Point Analysis:** When MNAR cannot be ruled out, standard statistical guidelines mandate sensitivity analysis (e.g., tipping-point modeling or pattern-mixture sensitivity bounds). The library lacks any framework demonstrating how to report uncertainty when missingness is suspected to be non-ignorable.

---

## 3. Causal Inference Intersections

### Coverage Status: Complete Void (0% Representation)

There is not a single paper in the library connecting missing data mechanisms to causal inference. For a review focused on air pollution—where imputed concentrations directly inform public health epidemiology, environmental policy, and clean-air regulations—this is a fatal omission.

### Critical Methodological Holes:
* **Missing Data Causal DAGs (m-DAGs):** The foundational framework developed by Mohan and Pearl (2014, 2021)—formalizing missingness mechanisms as graphical models to determine whether causal queries are non-parametrically recoverable—is absent.
* **Collider Stratification and M-Bias:** In atmospheric monitoring, missingness indicators often act as colliders. For example, severe weather conditions (e.g., high humidity, precipitation, freezing temperatures) simultaneously drive pollutant accumulation and trigger telemetric power outages. Applying listwise deletion or unadjusted imputation creates spurious associations between unconfounded variables, inducing severe collider stratification bias.
* **Doubly Robust & Targeted Estimation:** Methods that combine propensity score weighting for missingness with outcome regression models (such as Augmented Inverse Probability Weighting [AIPW] and Targeted Maximum Likelihood Estimation [TMLE]) are entirely unrepresented.

---

## 4. Application-Specific Challenges

### Coverage Status: Strong Temporal Focus, Neglected Spatial Physics

The library provides robust coverage of uniform, high-frequency multivariate time series from fixed monitoring stations, but overlooks several critical nuances of environmental observation.

### Critical Methodological Holes:
* **Continuous Space-Time Physics vs. Discrete Matrix Factorization:** Air pollutants disperse across continuous space governed by physical advection-diffusion processes, wind fields, and atmospheric boundary layer dynamics. In the current collection, spatial correlation is modeled almost exclusively via discrete matrix factorization (e.g., Hankel matrices or graph adjacency) rather than continuous geostatistical processes (e.g., Matérn spatiotemporal covariance kernels, INLA, or spatiotemporal Kriging).
* **Long Consecutive Gaps (Burst Missingness):** Multiple authors note that while deep attention and recurrent models excel on isolated missing hours, their performance degrades catastrophically during multi-day sensor outages. Dedicated methodologies for handling long temporal bursts remain under-developed.
* **Multi-Rate Sampling Heterogeneity:** Gaseous criteria pollutants (, NO_2, SO_2, O_3$) are continuously logged hourly, whereas particulate speciation (elemental carbon, sulfates, nitrates) is sampled on 1-in-3 or 1-in-6 day filter cycles. The collection treats all series as synchronously sampled matrices, neglecting multi-rate temporal alignment.

---

## 5. Critical Methodological Debates Missing from the Review

To present a mature, peer-reviewed critique of the transition from Rubin to SAITS, the review must center on three core controversies:

### Debate A: The Reconstruction Fallacy vs. Inferential Validity
* **The Conflict:** Modern machine learning papers celebrate deep learning models (SAITS, BRITS) for reducing point-prediction errors (RMSE) by 5–15% compared to MICE or MissForest. 
* **The Flaw:** When environmental epidemiologists use a single deterministic SAITS imputation to estimate exposure-response relationships (e.g., relative risk of mortality per 0\,\mu\text{g/m}^3$ increase in $\text{PM}_{2.5}$), the variance of the imputed points is treated as zero. This ignores imputation uncertainty, deflating standard errors, narrowing confidence intervals, and driving spurious statistical significance.
* **The Resolution:** Tracing how score-based diffusion models (CSDI) and Bayesian multiple imputation can bridge this divide by generating proper posterior draws rather than deterministic point estimates.

### Debate B: Information Leakage in Bidirectional Imputation
* **The Conflict:** Top-performing models (BRITS, BiLSTM, SAITS) rely on bidirectional recurrence and global self-attention across the full temporal window (looking both forward and backward in time).
* **The Flaw:** While mathematically optimal for historical gap-filling, bidirectional modeling cannot be deployed in real-time air quality alerting, early warning systems, or online industrial control. The literature rarely acknowledges the fundamental operational boundary between retrospective reconstruction and causal (autoregressive) online filtering.

### Debate C: Extreme Value and Regulatory Exceedance Imputation
* **The Conflict:** Air quality regulatory standards (e.g., US EPA National Ambient Air Quality Standards, EU Air Quality Directives) are determined by high-percentile exceedances (e.g., 24-hour 98th percentile $\text{PM}_{2.5}$).
* **The Flaw:** Standard $ and $ loss functions penalize mean deviations, biasing neural network predictions toward the conditional mean and consistently under-predicting toxic peak concentrations. Extreme Value Theory (EVT) under missingness is unaddressed.

---

## Summary Matrix of Literature Gaps

| Domain / Concept | Representation in Library | Methodological Risk | Recommended Addition |
| :--- | :--- | :--- | :--- |
| **Deep Learning Imputation** | Saturated (Over 35 papers) | Evaluated purely as point-reconstruction (RMSE); lacks distributional sampling guarantees. | Formulate generative models as conditional density samplers; incorporate CSDI. |
| **MNAR Mechanisms** | Neglected (Rubin 1976, Little 1993 only) | Real-world sensor saturation and clipping during high-pollution events are ignored. | Shadow variable identification (Miao et al., 2016); tipping-point sensitivity analysis. |
| **Causal Inference** | Completely Absent (0 papers) | Missingness as colliders induces severe M-bias and spurious environmental associations. | Missingness DAGs (Mohan & Pearl, 2021); Doubly robust estimation (AIPW/TMLE). |
| **Inferential Propagation** | Marginalized in ML literature | Single imputation under deep learning leads to deflated standard errors in downstream epidemiology. | Rubin's pooling rules; conformal prediction intervals for deep time-series imputation. |
| **Regulatory Peaks** | Unrepresented | Conditional mean optimization suppresses extreme toxic peak exceedances. | Extreme Value Theory (EVT) and quantile-calibrated loss functions. |

---
*Report compiled from senior peer-review analysis of SIMA PERSONAL and curated candidates.*