import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from .features import make_features, make_labels

MODELS_DIR = os.getenv("MODELS_DIR", "./models")

def model_path(symbol: str) -> str:
    return os.path.join(MODELS_DIR, f"model_{symbol.upper()}.joblib")

def train_symbol(symbol: str, df: pd.DataFrame) -> dict:
    y = make_labels(df)
    X = make_features(df).loc[y.index]
    if len(X) < 100:
        return {"symbol": symbol, "status": "not_enough_data", "n": len(X)}

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=200, multi_class='auto'))
    ])
    pipe.fit(X, y)

    yhat = pipe.predict(X)
    report = classification_report(y, yhat, output_dict=True)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(pipe, model_path(symbol))

    return {"symbol": symbol, "status": "ok", "n": len(X), "report": report}

def predict_symbol(symbol: str, df: pd.DataFrame):
    path = model_path(symbol)
    if not os.path.exists(path):
        return ("HOLD", None)
    pipe = joblib.load(path)
    X = make_features(df).tail(1)
    if X.empty:
        return ("HOLD", None)
    p = None
    if hasattr(pipe, "predict_proba"):
        pr = pipe.predict_proba(X)[0]
        classes = list(pipe.classes_)
        if 1 in classes:
            p = float(pr[classes.index(1)])
    pred = int(pipe.predict(X)[0])
    signal = "BUY" if pred == 1 else ("SELL" if pred == -1 else "HOLD")
    return (signal, p)
