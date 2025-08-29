import math

CLASSES = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]

def order_of(cls: str) -> int:
    return CLASSES.index(cls)

def cm_coarse(inf_cls: str, exp_cls: str) -> float:
    if not inf_cls or not exp_cls:
        return 0.0
    d = order_of(inf_cls) - order_of(exp_cls)
    if d <= 0:
        return 1.0
    elif d == 1:
        return 0.6
    else:
        return 0.0

def fit_score(fit_error: float, kappa: float = 2.0) -> float:
    if fit_error is None:
        return 0.0
    return 1.0 / (1.0 + kappa * max(0.0, fit_error))

def complexity_multiplier(inf_cls: str, exp_cls: str, fit_error: float, kappa: float = 2.0) -> float:
    return cm_coarse(inf_cls, exp_cls) * fit_score(fit_error, kappa)

def const_mult(C: float, alpha: float = 1.0, method: str = "inverse", lam: float = 2.0, mu: float = 2.0) -> float:
    if C is None or C <= 0:
        return 0.0
    r = C / alpha if alpha > 0 else float('inf')
    if method == "hard":
        return max(0.0, min(1.0, alpha / C))
    elif method == "exp":
        x = max(0.0, r - 1.0)
        return math.exp(-mu * x)
    else:  # inverse (recommended)
        if r <= 1.0:
            return 1.0
        denom = 1.0 + lam * (r - 1.0)
        return max(0.0, min(1.0, 1.0 / denom))

def memory_mult(peak_mem: float, baseline_mem: float, mem_limit: float) -> float:
    # EffectiveMem = Peak - Baseline (language overhead removed)
    if mem_limit is None or mem_limit <= 0:
        return 0.0
    if peak_mem is None:
        return 0.0
    base = baseline_mem or 0.0
    eff = max(0.0, peak_mem - base)
    ratio = min(1.0, eff / mem_limit)
    return 1.0 - ratio  # linear drop to 0 at limit
