# -*- coding: utf-8 -*-
"""Equations added in v11. Every equation is written from the project code (scripts/), not from the text:
15/30_v7_qc (spline), 12_v4 (covariates, futF), 32_v7_hp_cv (CV), 33b_v7_train10 / 50_v10_ensemble (models,
stocks, N), 52_v10_aggregate (uncertainty, TL, quadrants), 41_v8_fractions (MAOC/POC), 42_v8_drivers (SHAP, PDP,
breakpoints, logistic, path model), 19b_v6_huang_N_fix (fert+dep, Zamanian), 51_v10_bias_tests (LUCAS)."""

# ---------------------------------------------------------------- main text (Eq. 1 ..)
MAIN_INTRO = "Key equations. Horizon data were harmonized with the equal-area spline, and each layer value is the spline mean over the target layer:"
# items: ('eq', key, latex) or ('w', text)  -- 'w' = definition paragraph (not indented)
MAIN = [
('w', MAIN_INTRO),
('eq','m_spline', r"\min_{f}\ \frac{1}{n}\sum_{i=1}^{n}\left(y_i-\bar{f}_i\right)^{2}+\lambda\int_{x_0}^{x_n}\left[f'(z)\right]^{2}dz,\qquad \bar{y}_l=\frac{1}{b_l-a_l}\int_{a_l}^{b_l}f(z)\,dz"),
('w', "where y_i is the value observed in horizon i, f̄_i the mean of the spline f over that horizon, λ = 0.1, and ȳ_l the harmonized value for layer l = [a_l, b_l]. Expected SIC content (g kg⁻¹) follows the two-step (hurdle) model:"),
('eq','m_hurdle', r"\widehat{\mathrm{SIC}}_l(\mathbf{x})=\pi_l(\tilde{\mathbf{x}})\;s_l\,\exp\!\left[g_l(\tilde{\mathbf{x}})\right],\qquad \tilde{\mathbf{x}}=\left[\mathbf{x},\ \widehat{\mathrm{pH}}_l(\mathbf{x})\right]"),
('w', "where π_l is the classifier probability that SIC > 0.1 g kg⁻¹, g_l the regression of ln(SIC) fitted to carbonate-bearing samples, s_l Duan’s smearing factor, and **x** the covariate vector. Stocks (Mg C ha⁻¹) of layer l with thickness h_l (cm) are:"),
('eq','m_soc', r"\mathrm{SOC}_l=\left[P_{\mathrm{org},l}\,\rho_{\mathrm{org},l}+\left(1-P_{\mathrm{org},l}\right)\hat{c}_{\mathrm{min},l}\,\mathrm{BD}_l\right]\left(1-\frac{\mathrm{CF}_l}{100}\right)h_l\times0.1"),
('eq','m_sic', r"\mathrm{SIC}_l^{\mathrm{stock}}=\left(1-P_{\mathrm{org},l}\right)\widehat{\mathrm{SIC}}_l\,\mathrm{BD}_l\left(1-\frac{\mathrm{CF}_l}{100}\right)h_l\times0.1"),
('w', "where P_{org} is the PEATMAP-scaled organic-horizon probability, ρ_{org} the organic-horizon carbon density (kg C m⁻³), ĉ_{min} the predicted mineral-soil SOC (g kg⁻¹), BD the bulk density (g cm⁻³), and CF_l the coarse-fragment content (%), a single value per layer (median of harmonized WoSIS observations). Global totals (Pg C) sum over 10′ cells j of area A_j (ha) at latitude φ_j:"),
('eq','m_area', r"T=10^{-9}\sum_{j}S_j\,A_j,\qquad A_j=\left(\frac{111.32}{6}\right)^{2}\cos\varphi_j\times100"),
('w', "Equilibrium climate-driven change for fold-model m and GCM g, and its time-limited (first-order) realization by 2100, are:"),
('eq','m_eq', r"\Delta X^{(m,g)}=10^{-9}\sum_{j}A_j\left[X_j\!\left(\mathbf{F}^{\mathrm{fut}}_{g,j};M_m\right)-X_j\!\left(\mathbf{F}^{\mathrm{pres}}_{j};M_m\right)\right]"),
('eq','m_tl', r"\Delta X_{\mathrm{TL}}=\Delta X_{\mathrm{eq}}\left[1-\exp\!\left(-\frac{t}{\tau}\right)\right],\qquad \ln\tau\sim\mathcal{U}\!\left(\ln\tau_{\min},\ln\tau_{\max}\right)"),
('w', "with t = 85 years. Nitrogen-driven acidification and the resulting SIC change on cropland were computed as:"),
('eq','m_dph', r"\Delta\mathrm{pH}_j=-0.06\,N_{\mathrm{in},j}+0.11"),
('eq','m_dsicN', r"\Delta\mathrm{SIC}_{N,l,j}=f_{\mathrm{crop},j}\left[\mathrm{SIC}_{l,j}\!\left(\mathrm{pH}_j+\Delta\mathrm{pH}_j\right)-\mathrm{SIC}_{l,j}\!\left(\mathrm{pH}_j\right)\right]"),
('w', "where N_{in} is cumulative 2020–2050 fertilizer N per cropland hectare (Mg N ha⁻¹) and f_{crop} the cropland fraction. Mineral SOC was partitioned with the modeled MAOC fraction:"),
('eq','m_maoc', r"\mathrm{MAOC}_l=\mathrm{SOC}_{\mathrm{min},l}\,\hat{f}_{\mathrm{MAOC},l},\qquad \mathrm{POC}_l=\mathrm{SOC}_{\mathrm{min},l}\left(1-\hat{f}_{\mathrm{MAOC},l}\right),\qquad \hat{f}_{\mathrm{MAOC}}=\frac{1}{1+e^{-h(\mathbf{x})}}"),
('w', "where h is the XGBoost regression of logit(f_{MAOC}). Full equations and symbol definitions are given in the supplementary materials (eqs. S1 to S{NSM})."),
]

# ---------------------------------------------------------------- SM equations, inserted after v10 MM item index
SM_INSERT = {
1: [
('w', "In equation form, carbon concentrations (g kg⁻¹) of each harmonized layer are:"),
('eq','sic_def', r"\mathrm{SIC}=0.12\times\mathrm{TCEQ};\qquad \mathrm{SIC}=0\ \ \text{if TCEQ is missing and }\mathrm{pH}<6.5"),
('eq','tc_def', r"\mathrm{TC}=\mathrm{SOC}+\mathrm{SIC}"),
('w', "where TCEQ is the total calcium carbonate equivalent (g kg⁻¹) and the factor 0.12 is the mass fraction of C in CaCO₃. The zero assignment applies to profiles without carbonate measurements whose harmonized pH is below 6.5."),
],
5: [
('w', "For a profile with n contiguous horizons with boundaries x_0 < x_1 < … < x_n (cm) and observed values y_i, the spline f minimizes [@bishop99]:"),
('eq','spline', r"\min_{f}\ \frac{1}{n}\sum_{i=1}^{n}\left(y_i-\bar{f}_i\right)^{2}+\lambda\int_{x_0}^{x_n}\left[f'(z)\right]^{2}dz,\qquad \bar{f}_i=\frac{1}{x_i-x_{i-1}}\int_{x_{i-1}}^{x_i}f(z)\,dz"),
('w', "with λ = 0.1 and predictions constrained to [0, v_{max}] (v_{max} = 14 for pH, 1000 for TCEQ, 600 for organic C, 2.6 for BD, and 100 for coarse fragments). The value for target layer l = [a_l, b_l] (0–30, 30–100, 100–200 cm) is the spline mean, retained only if the profile spans the layer midpoint m_l = (a_l + b_l)/2:"),
('eq','spline_layer', r"\bar{y}_l=\frac{1}{b_l-a_l}\int_{a_l}^{b_l}f(z)\,dz,\qquad \text{retained if } x_0\le m_l\le x_n"),
('w', "Single-horizon profiles take ȳ_l = y_1 under the same coverage rule. Overlapping horizons were removed before fitting."),
],
7: [
('w', "Monthly Hargreaves potential evapotranspiration (mm) and the humidity index were computed from WorldClim monthly minimum and maximum temperature (T_{min}, T_{max}, °C) and precipitation P (mm) [@hargreaves85]:"),
('eq','pet', r"\mathrm{PET}=\sum_{k=1}^{12}0.0023\,R_{a,k}\left(\frac{T_{\min,k}+T_{\max,k}}{2}+17.8\right)\sqrt{T_{\max,k}-T_{\min,k}}\;d_k"),
('eq','ra', r"R_{a,k}=0.408\times\frac{24\cdot60}{\pi}G_{sc}\,d_{r}\left[\omega_s\sin\phi\sin\delta+\cos\phi\cos\delta\sin\omega_s\right]"),
('eq','ai', r"\mathrm{AI}=\ln\!\left(1+\frac{\sum_{k}P_k}{\max(\mathrm{PET},1)}\right)"),
('w', "where d_k is the number of days in month k; R_{a,k} is extraterrestrial radiation in equivalent evaporation (mm d⁻¹) at the mid-month day J_k, with solar constant G_{sc} = 0.082 MJ m⁻² min⁻¹, inverse relative Earth–Sun distance d_r = 1 + 0.033 cos(2πJ_k/365), solar declination δ = 0.409 sin(2πJ_k/365 − 1.39), sunset hour angle ω_s = arccos(−tan φ tan δ), and latitude φ. Terrain covariates were derived from elevation z on the 10′ grid:"),
('eq','terrain', r"\mathrm{slope}=\arctan\sqrt{\left(\frac{\partial z}{\partial x}\right)^{2}+\left(\frac{\partial z}{\partial y}\right)^{2}},\qquad \mathrm{TPI}=z-\frac{1}{25}\sum_{5\times5}z"),
],
10: [
('w', "Each XGBoost model is an additive ensemble of K regression trees f_k with learning rate η, fitted by minimizing a weighted, regularized objective [@chen16]:"),
('eq','xgb', r"\hat{y}_i=b_0+\eta\sum_{k=1}^{K}f_k(\mathbf{x}_i),\qquad \mathcal{L}=\sum_{i}w_i\,\ell\!\left(y_i,\hat{y}_i\right)+\sum_{k=1}^{K}\left(\gamma T_k+\frac{1}{2}\lambda_{\mathrm{r}}\left\Vert\boldsymbol{\omega}_k\right\Vert^{2}\right)"),
('eq','loss', r"\ell_{\mathrm{reg}}=\left(y_i-\hat{y}_i\right)^{2},\qquad \ell_{\mathrm{clf}}=-\left[y_i\ln p_i+\left(1-y_i\right)\ln\left(1-p_i\right)\right],\qquad p_i=\frac{1}{1+e^{-\hat{y}_i}}"),
('w', "where ℓ_{reg} is used for regressions and ℓ_{clf} for classifiers, b_0 is the base score, T_k and **ω**_k are the number of leaves and leaf weights of tree k, γ = 0 and λ_r = 1 (XGBoost defaults; not tuned), and w_i is the declustering weight (eq. S{decluster}). The tuned hyperparameters are K, η, maximum tree depth, row and column subsampling, and the minimum child weight (table S4). With predicted pH appended to the covariates (**x̃** = [**x**, pĤ_l(**x**)]), the SIC hurdle model combines a classifier π_l and a regression g_l of ln(SIC) fitted to samples with SIC > 0.1 g kg⁻¹:"),
('eq','hurdle', r"\pi_l(\tilde{\mathbf{x}})=\Pr\!\left(\mathrm{SIC}>0.1\mid\tilde{\mathbf{x}}\right),\qquad \widehat{\mathrm{SIC}}_l(\mathbf{x})=\pi_l(\tilde{\mathbf{x}})\;s_l\,\exp\!\left[g_l(\tilde{\mathbf{x}})\right]"),
('eq','smear', r"s_l=\frac{\sum_{i\in I_{l}}w_i\exp\!\left[\ln\mathrm{SIC}_i-g_l(\tilde{\mathbf{x}}_i)\right]}{\sum_{i\in I_{l}}w_i}"),
('w', "where I_l is the set of carbonate-bearing training samples, so that s_l · exp(g_l) estimates E[SIC | SIC > 0.1, **x̃**] [@duan83]. Mineral SOC, the organic-horizon probability, the organic-horizon carbon density, and bulk density are:"),
('eq','socmin', r"\hat{c}_{\mathrm{min},l}=\min\!\left\{\exp\!\left[g^{\mathrm{SOC}}_l(\mathbf{x})\right]-1,\ 120\right\}"),
('eq','porg', r"P_{\mathrm{org},1}=\min\!\left(\kappa\,\pi^{\mathrm{org}}_1,1\right),\quad P_{\mathrm{org},l}=\min\!\left[\min\!\left(\kappa\,\pi^{\mathrm{org}}_l,1\right),P_{\mathrm{org},l-1}\right],\quad \kappa=\frac{A_{\mathrm{peat}}}{\sum_j\pi^{\mathrm{org}}_{1,j}A_j}"),
('eq','rhoorg', r"\rho_{\mathrm{org},l}=\frac{1}{n_{\mathrm{org},l}}\sum_{i:\,\mathrm{SOC}_i>120}\mathrm{SOC}_i\,\mathrm{BD}_i"),
('eq','bd', r"\widehat{\mathrm{BD}}_l=\min\!\left\{\max\!\left[g^{\mathrm{BD}}_l\!\left(\mathbf{x},\ln\!\left(1+\hat{c}_{\mathrm{min},l}\right)\right),0.5\right],2.0\right\}"),
('w', "where g^{SOC}_l is the regression of ln(1 + SOC) for mineral samples (SOC ≤ 120 g kg⁻¹), π^{org}_l the classifier probability that SOC > 120 g kg⁻¹, layer 1 is 0–30 cm, A_{peat} = 4.23 Mkm² (PEATMAP) [@xu18], A_j the cell area (eq. S{area}), ρ_{org,l} in kg C m⁻³ (g kg⁻¹ × g cm⁻³), and g^{BD}_l the regression of BD (trained with observed ln(1 + SOC); applied with predicted mineral SOC)."),
],
11: [
('eq','decluster', r"w_i=\frac{1}{n_{c(i)}}"),
('w', "where c(i) is the 0.5° × 0.5° cell containing profile i and n_{c(i)} the number of profiles in that cell."),
],
13: [
('w', "Metrics are computed on out-of-fold predictions ŷ_i, that is, predictions for profile i from the model trained on the nine folds that do not contain i (n samples with observations y_i and mean ȳ):"),
('eq','r2', r"R^{2}=1-\frac{\sum_{i=1}^{n}\left(y_i-\hat{y}_i\right)^{2}}{\sum_{i=1}^{n}\left(y_i-\bar{y}\right)^{2}},\qquad \mathrm{RMSE}=\sqrt{\frac{1}{n}\sum_{i=1}^{n}\left(\hat{y}_i-y_i\right)^{2}},\qquad \mathrm{bias}=\frac{1}{n}\sum_{i=1}^{n}\left(\hat{y}_i-y_i\right)"),
('eq','clf', r"\mathrm{precision}=\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FP}},\qquad \mathrm{recall}=\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}},\qquad F_1=\frac{2\,\mathrm{precision}\cdot\mathrm{recall}}{\mathrm{precision}+\mathrm{recall}}"),
('eq','auc', r"\mathrm{AUC}=\frac{1}{n_{1}n_{0}}\sum_{i:\,y_i=1}\sum_{k:\,y_k=0}\left\{\mathbf{1}\left[\hat{\pi}_i>\hat{\pi}_k\right]+\frac{1}{2}\mathbf{1}\left[\hat{\pi}_i=\hat{\pi}_k\right]\right\}"),
('w', "R² in this form is the model-efficiency coefficient (it can be negative, as for the uncorrected LUCAS comparison). TP, FP, and FN are true-positive, false-positive, and false-negative counts at a probability threshold of 0.5; n_1 and n_0 are the numbers of positive (y = 1) and negative (y = 0) samples, π̂ the out-of-fold classifier probability, and **1**[·] the indicator function. For SIC, ŷ_i in the combined hurdle R² is the out-of-fold expected content of eq. S{hurdle} for all samples; the log-scale R² compares ln(1 + y_i) with ln(1 + ŷ_i). For SOC, R² and RMSE are computed after back-transformation (exp(·) − 1)."),
],
15: [
('w', "In full, SOC and SIC stocks of cell j and layer l (Mg C ha⁻¹) are:"),
('eq','socstock', r"\mathrm{SOC}_{l,j}=\left[P_{\mathrm{org},l,j}\,\rho_{\mathrm{org},l}+\left(1-P_{\mathrm{org},l,j}\right)\hat{c}_{\mathrm{min},l,j}\,\widehat{\mathrm{BD}}_{l,j}\right]\left(1-\frac{\widetilde{\mathrm{CF}}_l}{100}\right)h_l\times0.1"),
('eq','sicstock', r"\mathrm{SIC}^{\mathrm{stock}}_{l,j}=\left(1-P_{\mathrm{org},l,j}\right)\widehat{\mathrm{SIC}}_{l,j}\,\widehat{\mathrm{BD}}_{l,j}\left(1-\frac{\widetilde{\mathrm{CF}}_l}{100}\right)h_l\times0.1"),
('eq','area', r"T_l=10^{-9}\sum_{j\in\Omega}S_{l,j}\,A_j,\qquad A_j=\left(\frac{111.32}{6}\right)^{2}\cos\varphi_j\times100,\qquad T_{0\text{–}200}=\sum_{l=1}^{3}T_l"),
('w', "where h_l = 30, 70, and 100 cm; the factor 0.1 converts g kg⁻¹ × g cm⁻³ × cm to Mg C ha⁻¹ (and kg C m⁻³ × cm to Mg C ha⁻¹ for ρ_{org}); CF̃_l is the coarse-fragment content applied to layer l, taken as the median of the spline-harmonized WoSIS observations of that layer in the training profiles; S_{l,j} is either stock; A_j is the area (ha) of 10′ cell j at latitude φ_j (111.32 km per degree); Ω is the land mask, or the cells of one country or continent for national and continental totals; and T is in Pg C (10⁻⁹ converts Mg to Pg)."),
],
17: [
('w', "For fold-model m (m = 1, …, 10) and Monte Carlo draw d (d = 1, …, 300), layer totals (eq. S{area}) were perturbed as:"),
('eq','mc_soc', r"\mathrm{SOC}^{(m,d)}_l=\varepsilon_{\mathrm{BD}}\,\phi_{\mathrm{CF},l}\,\theta_l\,T^{(m)}_{\mathrm{SOC,min},l}+\varepsilon_{\mathrm{org},l}\,\theta_l\,T^{(m)}_{\mathrm{SOC,org},l},\qquad \mathrm{SIC}^{(m,d)}_l=\varepsilon_{\mathrm{BD}}\,\phi_{\mathrm{CF},l}\,\theta_l\,T^{(m)}_{\mathrm{SIC},l}"),
('eq','mc_cf', r"\phi_{\mathrm{CF},l}=\frac{1-\mathrm{CF}'_l/100}{1-\widetilde{\mathrm{CF}}_l/100},\qquad \mathrm{CF}'_l=\min\!\left(\widetilde{\mathrm{CF}}_l\,e^{u},60\right),\quad u\sim\mathcal{U}\!\left(\ln0.5,\ln2\right)"),
('w', "where CF′_l is the perturbed coarse-fragment content, u a log-uniform multiplicative factor, ε_{BD} ~ N(1, 0.05²) drawn once per draw for all layers, θ_1 = 1, θ_2 ~ N(1, 0.05²), θ_3 ~ N(1, 0.10²) (effective thickness of 30–100 and 100–200 cm), and ε_{org,l} ~ N(1, 0.20²) (organic C density). MAOC and POC are perturbed with the same factor as mineral SOC. For any quantity Z with N draws (N = 3000 for present stocks), we report:"),
('eq','stats', r"\bar{Z}=\frac{1}{N}\sum_{r=1}^{N}Z_r,\qquad \mathrm{SD}=\sqrt{\frac{1}{N-1}\sum_{r=1}^{N}\left(Z_r-\bar{Z}\right)^{2}},\qquad \mathrm{CI}_{90}=\left[Q_{0.05}(Z),\,Q_{0.95}(Z)\right]"),
('w', "where Q_p is the empirical p-quantile; values are reported as Z̄ (Q_{0.05}–Q_{0.95}; ±SD)."),
],
19: [
('w', "For fold-model M_m and GCM g, the equilibrium change in layer l is:"),
('eq','deq', r"\Delta X^{(m,g)}_l=10^{-9}\sum_{j}A_j\left[X_{l,j}\!\left(\mathbf{F}^{\mathrm{fut}}_{g,j};M_m\right)-X_{l,j}\!\left(\mathbf{F}^{\mathrm{pres}}_{j};M_m\right)\right],\qquad X\in\left\{\mathrm{SOC},\mathrm{SIC}^{\mathrm{stock}}\right\}"),
('w', "where **F**^{pres} and **F**^{fut}_g are the present (1970–2000) and 2081–2100 covariate vectors (climate, PET, and humidity index replaced; soil, terrain, and lithology fixed), and X is evaluated with eqs. S{socstock} and S{sicstock}, with pH, SIC, mineral SOC, P_{org}, and BD all re-predicted from **F**^{fut}_g."),
],
20: [
('eq','ensmean', r"\overline{\Delta X}_{l,j}=\frac{1}{60}\sum_{m=1}^{10}\sum_{g=1}^{6}\Delta X^{(m,g)}_{l,j},\qquad 10^{-9}\sum_{j}A_j\,\overline{\Delta X}_{l,j}=\frac{1}{60}\sum_{m=1}^{10}\sum_{g=1}^{6}\Delta X^{(m,g)}_l"),
('w', "The second identity follows from linearity and is why map integrals equal headline means; 90% CIs use the 60 member totals (eq. S{stats})."),
],
22: [
('eq','tl', r"\Delta X_{\mathrm{TL}}(t)=\Delta X_{\mathrm{eq}}\left[1-\exp\!\left(-\frac{t}{\tau}\right)\right]"),
('w', "Applied to the layer totals of each ensemble member (eq. S{deq}):"),
('eq','tl_sum', r"\Delta\mathrm{SOC}_{\mathrm{TL}}=\sum_{l=1}^{3}\Delta\mathrm{SOC}_{\mathrm{eq},l}\left[1-e^{-t/\tau_{\mathrm{SOC},l}}\right],\qquad \Delta\mathrm{SIC}_{\mathrm{TL}}=\left(\sum_{l=1}^{3}\Delta\mathrm{SIC}_{\mathrm{eq},l}\right)\left[1-e^{-t/\tau_{\mathrm{SIC}}}\right]"),
('eq','tau', r"\ln\tau\sim\mathcal{U}\!\left(\ln\tau_{\min},\ln\tau_{\max}\right),\qquad \overline{\Delta X}_{\mathrm{TL},j}=\overline{\Delta X}_{\mathrm{eq},j}\;\mathbb{E}_{\tau}\!\left[1-e^{-t/\tau}\right]"),
('w', "where ΔTC_{TL} = ΔSOC_{TL} + ΔSIC_{TL}; one τ_{SIC} is drawn for all SIC layers. For each fold-model × GCM member, 20 sets of τ were drawn (1200 values per scenario). Time-limited maps multiply the ensemble-mean equilibrium map by the expected realized fraction, estimated from 4000 τ draws. For MAOC and POC in the ensemble (table S10 and Fig. 7B), t = 85 years with ln τ_{MAOC} ~ U(ln 50, ln 400) and ln τ_{POC} ~ U(ln 5, ln 30); the fixed-τ sensitivity of fig. S7 uses t = 80 years."),
],
24: [
('eq','quad', r"Q_j=\begin{cases}\text{trade-off}, & \overline{\Delta\mathrm{SOC}}_j<0,\ \overline{\Delta\mathrm{SIC}}_j>0\\ \text{both gain}, & \overline{\Delta\mathrm{SOC}}_j>0,\ \overline{\Delta\mathrm{SIC}}_j>0\\ \text{both loss}, & \overline{\Delta\mathrm{SOC}}_j<0,\ \overline{\Delta\mathrm{SIC}}_j<0\\ \text{SOC gain, SIC loss}, & \text{otherwise}\end{cases}"),
('eq','quadarea', r"\mathrm{Area}(Q)=\sum_{j}A_j\,\mathbf{1}\!\left[Q_j=Q\right],\qquad \mathrm{shift}_j=\mathbf{1}\!\left[K^{2071\text{–}2099}_j\neq K^{1991\text{–}2020}_j\right]"),
('w', "where the overbars denote ensemble-mean 0–200 cm changes (eq. S{ensmean}) and K is the Köppen–Geiger class."),
],
26: [
('w', "In equation form, with r_{c,y,j} the IMAGE fertilizer application rate (kg N ha⁻¹ yr⁻¹) and a_{c,y,j} the area fraction of crop group c in year y and 0.5° cell j:"),
('eq','nin', r"N_{\mathrm{in},j}=10^{-3}\sum_{y=2020}^{2050}\frac{\sum_{c}r_{c,y,j}\,a_{c,y,j}}{\sum_{c}a_{c,y,j}},\qquad f_{\mathrm{crop},j}=\frac{1}{31}\sum_{y=2020}^{2050}\sum_{c}a_{c,y,j}"),
('eq','dph', r"\Delta\mathrm{pH}_j=\begin{cases}-0.06\,N_{\mathrm{in},j}+0.11, & f_{\mathrm{crop},j}>0.001\\ 0, & \text{otherwise}\end{cases}"),
('eq','dsicN', r"\Delta\mathrm{SIC}_{N,l,j}=f_{\mathrm{crop},j}\left[\mathrm{SIC}^{\mathrm{stock}}_{l,j}\!\left(\widehat{\mathrm{pH}}_{l,j}+\Delta\mathrm{pH}_j\right)-\mathrm{SIC}^{\mathrm{stock}}_{l,j}\!\left(\widehat{\mathrm{pH}}_{l,j}\right)\right]"),
('eq','lossonly', r"L_l=10^{-9}\sum_{j}A_j\min\!\left(\Delta\mathrm{SIC}_{N,l,j},0\right),\qquad \mathrm{Net}_l=10^{-9}\sum_{j}A_j\,\Delta\mathrm{SIC}_{N,l,j}"),
('w', "where c ∈ {C3 annual, C3 perennial, C4 annual, C4 perennial, C3 N-fixing}, fields are mapped from 0.5° to the 10′ grid by replication, and SIC^{stock} is eq. S{sicstock} with P_{org} and BD fixed at their present-day values and SIC re-evaluated through eq. S{hurdle} with the shifted pH covariate. For SSP2-4.5, N_{in} and f_{crop} are the means of the SSP1-2.6 and SSP3-7.0 fields. The intercept implies ΔpH > 0 for N_{in} < 0.11/0.06 ≈ 1.83 Mg N ha⁻¹."),
],
27: [
('eq','nfd', r"N^{\mathrm{FD}}_{\mathrm{in},j}=N_{\mathrm{in},j}+10^{-3}D_j"),
('eq','zam', r"C_{\mathrm{pot},j}=10^{-3}\kappa_{Z}\left(F_j+0.5\,D_j\right)"),
('eq','zam2', r"L^{Z}_{1,j}=\min\!\left(C_{\mathrm{pot},j},\mathrm{SIC}^{\mathrm{stock}}_{1,j}\right),\qquad L^{Z}_{2,j}=\min\!\left[\max\!\left(C_{\mathrm{pot},j}-L^{Z}_{1,j},0\right),\mathrm{SIC}^{\mathrm{stock}}_{2,j}\right]"),
('eq','nscale', r"k_{N}=\frac{L_{\mathrm{Huang},0\text{–}30}}{\left|L_{\mathrm{IMAGE},0\text{–}30}\right|}"),
('w', "where D_j is cumulative 2020–2050 NHx + NOy deposition (kg N ha⁻¹; with ΔpH applied where f_{crop} > 0.01 in this sensitivity run), F_j the cumulative grid-mean fertilizer input Σ_y Σ_c r_{c,y,j} a_{c,y,j} (kg N ha⁻¹), κ_Z = 0.21 (0.055–0.32) kg C per kg N [@zamanian18], L^{Z}_1 and L^{Z}_2 the stoichiometric losses capped by the available SIC stock in 0–30 and 30–100 cm, and k_N the ratio of the topsoil loss of Huang *et al.* (10, 14, or 23 Pg) to our loss-only IMAGE topsoil loss (eq. S{lossonly}) reported in table S9."),
],
30: [
('eq','fm_logit', r"y_i=\ln\frac{f_{\mathrm{MAOC},i}}{1-\min\left(f_{\mathrm{MAOC},i},0.995\right)},\qquad f_{\mathrm{MAOC}}=\frac{\mathrm{MAOC}}{\mathrm{MAOC}+\mathrm{POC}}"),
('eq','fm_hat', r"\hat{f}_{\mathrm{MAOC}}(\mathbf{x})=\frac{1}{1+\exp\!\left[-h\!\left(\mathbf{x},z_{\mathrm{mid}},m\right)\right]}"),
('eq','partition', r"\mathrm{MAOC}_{l,j}=\mathrm{SOC}_{\mathrm{min},l,j}\,\hat{f}_{\mathrm{MAOC},l,j},\qquad \mathrm{POC}_{l,j}=\mathrm{SOC}_{\mathrm{min},l,j}\left(1-\hat{f}_{\mathrm{MAOC},l,j}\right)"),
('eq','dmaoc', r"\Delta\mathrm{MAOC}^{(m,g)}=10^{-9}\sum_{j}A_j\left[\mathrm{SOC}^{\mathrm{fut}}_{\mathrm{min},j}\hat{f}^{\mathrm{fut}}_{\mathrm{MAOC},j}-\mathrm{SOC}^{\mathrm{pres}}_{\mathrm{min},j}\hat{f}^{\mathrm{pres}}_{\mathrm{MAOC},j}\right]"),
('w', "where h is the XGBoost regression of y on covariates, depth midpoint z_{mid}, and method indicator m (0, particle size; 1, density); maps use z_{mid} = 15 cm (0–30 cm) or 65 cm (30–100 cm) and m = 0; SOC_{min,l,j} = (1 − P_{org})ĉ_{min} BD (1 − CF̃_l/100) h_l × 0.1 is the mineral term of eq. S{socstock}; and ΔPOC is defined analogously with (1 − f̂_{MAOC}). In the projection ensemble, fold-model m is paired with bootstrap refit m of the fraction model."),
],
32: [
('w', "SHAP values decompose each prediction additively on the model’s output scale (pH units; log-odds for classifiers; ln SIC; ln(1 + SOC); logit f_{MAOC}) [@lundberg17;@lundberg20]:"),
('eq','shap', r"F(\mathbf{x}_i)=\phi_0+\sum_{k=1}^{p}\phi_{k}(\mathbf{x}_i),\qquad \phi_k=\sum_{S\subseteq K_{-k}}\frac{s!\,\left(p-s-1\right)!}{p!}\left[v\left(S\cup\{k\}\right)-v\left(S\right)\right],\qquad s=\left\vert S\right\vert"),
('eq','shapgroup', r"\Phi_{G,i}=\sum_{k\in G}\phi_k(\mathbf{x}_i),\qquad I_G=100\times\frac{\frac{1}{N}\sum_{i=1}^{N}\left|\Phi_{G,i}\right|}{\sum_{G'}\frac{1}{N}\sum_{i=1}^{N}\left|\Phi_{G',i}\right|},\qquad I_k=100\times\frac{\sum_i\left|\phi_k(\mathbf{x}_i)\right|}{\sum_{k'}\sum_i\left|\phi_{k'}(\mathbf{x}_i)\right|}"),
('eq','dominant', r"D_j=\underset{G\in\{\text{climate, soil, topography, parent material}\}}{\arg\max}\left|\Phi_{G,j}\right|"),
('w', "where φ_0 is the expected model output, K the set of p covariates (K_{-k}, K without covariate k), s the size of coalition S, v(S) the TreeSHAP conditional expectation of the output given covariates in S, N = 30,000 sampled cells, I_G the group importance (table S11), I_k the covariate importance (fig. S3), and D_j the dominant group computed from approximate SHAP values for all cells. Partial dependence of covariate k and the breakpoint of its two-segment fit are:"),
('eq','pdp', r"\bar{F}_k(v)=\frac{1}{N_{\mathrm{p}}}\sum_{i=1}^{N_{\mathrm{p}}}\psi\!\left[F\!\left(v,\mathbf{x}_{i,-k}\right)\right]"),
('eq','brk', r"v_{\mathrm{b}}=\underset{v_q,\ 5\le q\le Q-4}{\arg\min}\left[\min_{\alpha_1,\beta_1}\sum_{r\le q}\left(\bar{F}_k(v_r)-\alpha_1-\beta_1v_r\right)^{2}+\min_{\alpha_2,\beta_2}\sum_{r\ge q}\left(\bar{F}_k(v_r)-\alpha_2-\beta_2v_r\right)^{2}\right]"),
('w', "where N_p = 3000 random land cells, v takes Q = 40 values at the 2nd to 98th percentiles of covariate k, ψ maps the output to the reported scale (probability; exp(·) for SIC amount; exp(·) − 1 for SOC; inverse logit for f_{MAOC}), and the two segments are fitted independently by least squares. The observed pH–SIC relation is:"),
('eq','logistic', r"\Pr\!\left(\mathrm{SIC}>0.1\mid\mathrm{pH}\right)=\frac{1}{1+\exp\!\left[-k\left(\mathrm{pH}-\mathrm{pH}_{50}\right)\right]}"),
('eq','logistic_fit', r"\left(k,\mathrm{pH}_{50}\right)=\arg\min\sum_{i}\left(\mathbf{1}\!\left[\mathrm{SIC}_i>0.1\right]-\Pr\!\left(\mathrm{SIC}>0.1\mid\mathrm{pH}_i\right)\right)^{2}"),
('w', "fitted by nonlinear least squares to the presence indicator of individual topsoil observations. The path model uses z-scored variables, z_V = (V − mean(V))/SD(V):"),
('eq','path_ph', r"z_{\mathrm{pH}}=\beta_1z_{\mathrm{AI}}+\beta_2z_{\mathrm{MAT}}+\beta_3z_{\mathrm{clay}}+\beta_4z_{\mathrm{carb}}+e_1"),
('eq','path_sic', r"z_{\mathrm{SIC}}=\gamma_{\mathrm{pH}}z_{\mathrm{pH}}+\gamma_1z_{\mathrm{AI}}+\gamma_2z_{\mathrm{MAT}}+\gamma_3z_{\mathrm{clay}}+\gamma_4z_{\mathrm{carb}}+e_2"),
('eq','path_soc', r"z_{\mathrm{SOC}}=\delta_{\mathrm{pH}}z_{\mathrm{pH}}+\delta_1z_{\mathrm{AI}}+\delta_2z_{\mathrm{MAT}}+\delta_3z_{\mathrm{clay}}+e_3"),
('eq','pathfx', r"\mathrm{indirect}_{\mathrm{AI}\rightarrow\mathrm{SIC}}=\beta_1\gamma_{\mathrm{pH}},\qquad \mathrm{total}_{\mathrm{AI}\rightarrow\mathrm{SIC}}=\beta_1\gamma_{\mathrm{pH}}+\gamma_1"),
('w', "where V is pH, ln(1 + SIC), ln(1 + SOC), AI = ln(1 + P/PET), MAT (mean annual temperature, bio1), clay, or carb (the GLiM carbonate-rock indicator), z_{SIC} and z_{SOC} denote the z-scores of ln(1 + SIC) and ln(1 + SOC), e_1 to e_3 are residuals, and the coefficients are ordinary least-squares estimates (table S11)."),
],
34: [
('eq','lucas', r"r(\beta)=\frac{1-\beta^{20}}{1-\beta^{30}},\qquad \hat{S}_{0\text{–}20,i}=r(\beta)\,\hat{S}_{0\text{–}30,i},\qquad \mathrm{bias}=\frac{1}{n}\sum_{i=1}^{n}\left(\hat{S}_{0\text{–}20,i}-S^{\mathrm{obs}}_{0\text{–}20,i}\right)"),
('w', "where 1 − β^{d} is the cumulative fraction of the SOC stock above depth d (cm) in the depth model of Jobbágy and Jackson, β = 0.978 [r(β) ≈ 0.74], and Ŝ_{0–30} is the predicted 0–30 cm stock of the LUCAS location’s 10′ cell."),
],
}

# References in the v10 SM text to old equation numbers -> new keys
# old v10 number -> replacement template (applied to 'eq. Sn' in MM and ST text; Huang's 'eqs. S1 and S2' untouched)
SM_TEXT_REFS = {'1':'eq. S{hurdle}', '2':'eqs. S{socstock} and S{sicstock}', '3':'eq. S{tl}', '4':'eq. S{dph}', '5':'eq. S{dsicN}'}
# Minimal accuracy fixes of v10 SM text to match the code (reported to the user)
SM_TEXT_FIXES = [
 ("to binned WoSIS topsoil observations (n = 91,273)", "to the presence indicator of individual WoSIS topsoil observations (n = 91,273; binned means are shown in fig. S6)"),
 ("Group importance is the sum of mean |SHAP| values within a group as a percentage of the total (table S11).", "Group importance is the mean absolute value of the summed SHAP values within a group, expressed as a percentage of the total over groups (eq. S{shapgroup}; table S11)."),
]
