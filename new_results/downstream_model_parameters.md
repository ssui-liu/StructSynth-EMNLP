# Downstream Model Parameter Settings

These are the parameter settings used by `scripts/evaluate_downstream_models.py` for the downstream evaluation tables.

## Random Forest

Classification tasks use `sklearn.ensemble.RandomForestClassifier`:

```python
RandomForestClassifier(
    n_estimators=200,
    random_state=random_state,
    n_jobs=-1,
)
```

Regression tasks use `sklearn.ensemble.RandomForestRegressor`:

```python
RandomForestRegressor(
    n_estimators=200,
    random_state=random_state,
    n_jobs=-1,
)
```

## Logistic Regression / Linear Baseline

Classification tasks use `sklearn.linear_model.LogisticRegression`:

```python
LogisticRegression(
    max_iter=1000,
    solver="lbfgs",
)
```

Regression tasks use `sklearn.linear_model.Ridge` instead of Logistic Regression:

```python
Ridge()
```

## MLP

Classification tasks use `sklearn.neural_network.MLPClassifier`:

```python
MLPClassifier(
    hidden_layer_sizes=(100,),
    max_iter=500,
    random_state=random_state,
)
```

Regression tasks use `sklearn.neural_network.MLPRegressor`:

```python
MLPRegressor(
    hidden_layer_sizes=(100,),
    max_iter=500,
    random_state=random_state,
)
```

## Shared Notes

- `random_state` defaults to `42` in the CLI unless `--random-state` is provided.
- Parameters not listed above use the corresponding scikit-learn defaults.
- Classification datasets in the current table: Adult, Anxiety, Churn.
- Regression datasets in the current table: Salary.
