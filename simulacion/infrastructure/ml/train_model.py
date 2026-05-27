import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score
from pathlib import Path


def entrenar(X_train: np.ndarray, y_train: np.ndarray):
    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='reg:squarederror',
    )
    model.fit(X_train, y_train)

    scores = cross_val_score(
        model, X_train, y_train,
        cv=5, scoring='neg_root_mean_squared_error',
    )
    rmse_cv = -scores.mean()
    print(f'RMSE validación cruzada: {rmse_cv:.3f}')
    assert rmse_cv < 5.0, f'RMSE {rmse_cv:.2f} no cumple el criterio de aceptación (< 5)'

    out = Path(__file__).parent / 'xgboost_model.pkl'
    joblib.dump(model, out)
    return model, rmse_cv
