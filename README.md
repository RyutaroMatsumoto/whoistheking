# whoistheking
ranking calculation methods for our efootball league

## Bradley-Terry Model
### Overview

The Bradley–Terry model is a probabilistic model used to estimate the "ability" or "strength" parameters of competitors (teams or individuals) based on paired comparisons or game outcomes. In this model, each competitor \(i\) is assigned a positive parameter \(\beta_i\), and the probability that competitor \(i\) beats competitor \(j\) is given by:

\[
P(i \text{ beats } j) = \frac{\beta_i}{\beta_i + \beta_j}
\]

This formula implies that if \(\beta_i > \beta_j\), then competitor \(i\) has a greater than 50% chance of winning against competitor \(j\).

### 1. Model Definition

For each competitor \(i\), we assign a positive strength parameter \(\beta_i > 0\). The probability that competitor \(i\) wins against competitor \(j\) is defined as:

\[
P(i \text{ beats } j) = \frac{\beta_i}{\beta_i + \beta_j}
\]

### 2. Log-Likelihood Function

Suppose we have data on paired comparisons in the form of the number of contests and wins between competitors. Let:
- \(w_{ij}\) be the number of wins by competitor \(i\) against competitor \(j\),
- \(w_{ji}\) be the number of wins by competitor \(j\) against competitor \(i\),
- \(n_{ij} = w_{ij} + w_{ji}\) be the total number of contests between \(i\) and \(j\).

For each pair \((i, j)\), the likelihood of the observed results is given by:

\[
\left(\frac{\beta_i}{\beta_i + \beta_j}\right)^{w_{ij}} \left(\frac{\beta_j}{\beta_i + \beta_j}\right)^{w_{ji}}
\]

The overall likelihood \(L\) for all pairs is:

\[
L(\{\beta_i\}) = \prod_{i<j} \left(\frac{\beta_i}{\beta_i + \beta_j}\right)^{w_{ij}} \left(\frac{\beta_j}{\beta_i + \beta_j}\right)^{w_{ji}}
\]

Taking the natural logarithm yields the log-likelihood function:

\[
\ell(\{\beta_i\}) = \sum_{i<j} \left[ w_{ij} \ln \beta_i + w_{ji} \ln \beta_j - (w_{ij}+w_{ji}) \ln (\beta_i + \beta_j) \right]
\]

### 3. Maximum Likelihood Estimation

The goal is to estimate the parameters \(\{\beta_i\}\) by maximizing the log-likelihood function:

\[
\hat{\beta} = \underset{\{\beta_i > 0\}}{\operatorname{argmax}} \; \ell(\{\beta_i\})
\]

**3.1 Numerical Optimization Methods**

Since an analytical solution is often not available, numerical optimization methods are used. Representative methods include:

- **Newton–Raphson Method**
- **MM Algorithm (Majorization–Minimization)**

**3.2 MM Algorithm Update Rule**

Using the MM algorithm, the parameters are updated iteratively. The update rule for each competitor \(i\) is given by:

\[
\beta_i^{(\text{new})} = \frac{w_i}{\sum_{j \neq i} \frac{n_{ij}}{\beta_i^{(\text{old})} + \beta_j^{(\text{old})}}}
\]

where:
- \(w_i = \sum_{j \neq i} w_{ij}\) is the total number of wins for competitor \(i\),
- \(n_{ij} = w_{ij} + w_{ji}\) is the total number of contests between competitors \(i\) and \(j\).

This update is repeated until convergence, for example, until:

\[
\max_i \left|\beta_i^{(\text{new})} - \beta_i^{(\text{old})}\right| < \epsilon
\]

### 4. Identifiability and Normalization

The Bradley–Terry model has an identifiability issue because multiplying all \(\beta_i\) by a constant does not change the probabilities. To resolve this, a normalization constraint is imposed, such as:

- Fixing one of the parameters to 1 (e.g., \(\beta_1 = 1\)), or
- Constraining the sum of the parameters to 1 (i.e., \(\sum_i \beta_i = 1\)).

This ensures a unique solution.
