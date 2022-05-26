# coding: utf-8
import lightgbm as lgb
import pandas as pd

if lgb.compat.MATPLOTLIB_INSTALLED:
    import matplotlib.pyplot as plt
else:
    raise ImportError("You need to install matplotlib for plot_example.py.")

print("Loading data...")
# load or create your dataset
df_train = pd.read_csv("../regression/regression.train", header=None, sep="\t")
df_test = pd.read_csv("../regression/regression.test", header=None, sep="\t")

y_train = df_train[0]
y_test = df_test[0]
X_train = df_train.drop(0, axis=1)
X_test = df_test.drop(0, axis=1)

# create dataset for lightgbm
lgb_train = lgb.Dataset(X_train, y_train)
lgb_test = lgb.Dataset(X_test, y_test, reference=lgb_train)

# specify your configurations as a dict
params = {"num_leaves": 5, "metric": ("l1", "l2"), "verbose": 0}

evals_result = {}  # to record eval results for plotting

print("Starting training...")
# train
gbm = lgb.train(
    params,
    lgb_train,
    num_boost_round=100,
    valid_sets=[lgb_train, lgb_test],
    feature_name=["f" + str(i + 1) for i in range(X_train.shape[-1])],
    categorical_feature=[21],
    evals_result=evals_result,
    verbose_eval=10,
)

print("Plotting metrics recorded during training...")
ax = lgb.plot_metric(evals_result, metric="l1")
plt.show()

print("Plotting feature importances...")
ax = lgb.plot_importance(gbm, max_num_features=10)
plt.show()

print("Plotting split value histogram...")
ax = lgb.plot_split_value_histogram(gbm, feature="f26", bins="auto")
plt.show()

print("Plotting 54th tree...")  # one tree use categorical feature to split
ax = lgb.plot_tree(gbm, tree_index=53, figsize=(15, 15), show_info=["split_gain"])
plt.show()

print("Plotting 54th tree with graphviz...")
graph = lgb.create_tree_digraph(gbm, tree_index=53, name="Tree54")
graph.render(view=True)
