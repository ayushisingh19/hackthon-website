import math


CLASSES = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]


def _order(cls: str) -> int:
    return CLASSES.index(cls)


def cm_coarse(inf_cls: str, exp_cls: str) -> float:
        d = _order(inf_cls) - _order(exp_cls)
        if d <= 0:
            return 1.0
        if d == 1:
         return 0.6
        return 0.0


def fit_score(fit_error: float, kappa: float = 2.0) -> float:
    return 1.0 / (1.0 + kappa * max(0.0, fit_error))


def complexity_multiplier(inf_cls: str, exp_cls: str, fit_error: float, kappa: float = 2.0) -> float:
    return cm_coarse(inf_cls, exp_cls) * fit_score(fit_error, kappa)


def const_multiplier(C: float, alpha: float = 1.0, lam: float = 2.0) -> float:
    if C <= alpha:
     return 1.0
    return 1.0 / (1.0 + lam * (C / alpha - 1.0))


def memory_multiplier(peak_mem_mb: float, mem_limit_mb: float, baseline_mb: float = 0.0) -> float:
    effective = max(0.0, peak_mem_mb - baseline_mb)
    ratio = effective / float(mem_limit_mb)
    ratio = min(1.0, max(0.0, ratio))
    return 1.0 - ratio


def final_score(
corr: bool,
inf_cls: str,
exp_cls: str,
fit_error: float,
C: float,
alpha: float,
peak_mem_mb: float,
mem_limit_mb: float,
baseline_mb: float = 0.0,
) -> float:
    if not corr:
        return 0.0
    CM = complexity_multiplier(inf_cls, exp_cls, fit_error)
    CONST = const_multiplier(C, alpha)
    MEM = memory_multiplier(peak_mem_mb, mem_limit_mb, baseline_mb)
    return 100.0 * 1.0 * CM * CONST * MEM