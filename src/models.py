from __future__ import annotations

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import model_feature_lists
from .config import RANDOM_STATE


def _preprocessor(scale: bool, include_demographics: bool = True):
    numeric, categorical = model_feature_lists(include_demographics=include_demographics)

    num_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    num_pipe = Pipeline(num_steps)

    transformers = [("num", num_pipe, numeric)]
    if categorical:
        cat_pipe = Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ])
        transformers.append(("cat", cat_pipe, categorical))

    return ColumnTransformer(transformers)


def candidate_models(include_demographics: bool = True):
    return {
        "logistic_regression": Pipeline([
            ("prep", _preprocessor(scale=True, include_demographics=include_demographics)),
            ("model", LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                solver="liblinear",
                random_state=RANDOM_STATE,
            )),
        ]),
        "random_forest": Pipeline([
            ("prep", _preprocessor(scale=False, include_demographics=include_demographics)),
            ("model", RandomForestClassifier(
                n_estimators=500,
                max_depth=10,
                min_samples_leaf=10,
                max_features="sqrt",
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=RANDOM_STATE,
            )),
        ]),
        # HistGradientBoosting requires dense input; with our few categorical columns the
        # one-hot output is converted to dense by the ColumnTransformer configuration below.
    }


def gradient_boosting_model(include_demographics: bool = False):
    # For a fully reproducible sklearn challenger without sparse-matrix complications,
    # use engineered numeric features only.
    numeric, _ = model_feature_lists(include_demographics=False)
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
        ]), numeric)
    ])
    return Pipeline([
        ("prep", prep),
        ("model", HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=250,
            max_leaf_nodes=31,
            l2_regularization=1.0,
            random_state=RANDOM_STATE,
        )),
    ])


def save_model(model, path):
    joblib.dump(model, path)
