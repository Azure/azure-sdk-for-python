# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class SearchSpace:
    # Hyperparameter search constants
    CHOICE = "choice"
    UNIFORM = "uniform"
    LOGUNIFORM = "loguniform"
    QUNIFORM = "quniform"
    QLOGUNIFORM = "qloguniform"
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    QNORMAL = "qnormal"
    QLOGNORMAL = "qlognormal"
    RANDINT = "randint"

    UNIFORM_LOGUNIFORM = [UNIFORM, LOGUNIFORM]
    QUNIFORM_QLOGUNIFORM = [QUNIFORM, QLOGUNIFORM]
    NORMAL_LOGNORMAL = [NORMAL, LOGNORMAL]
    QNORMAL_QLOGNORMAL = [QNORMAL, QLOGNORMAL]
