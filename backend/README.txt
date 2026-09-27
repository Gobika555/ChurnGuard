ChurnGuard corrected backend
=============================

This backend is designed for the existing ChurnGuard frontend.

Important prediction fix:
- Reads the uploaded CSV directly.
- Removes UTF-8 BOM/leading/trailing spaces from headers.
- Validates the 20 raw Telco customer columns.
- Converts numeric fields safely.
- One-hot encodes categorical fields.
- Aligns exactly to the trained model's 30 feature names.
- Returns Low/Medium/High risk.
- Saves successful predictions to the logged-in user's history.

Run from the ChurnGuard project root:

    python -m pip install -r backend\requirements.txt
    python backend\main.py

Then open:

    http://127.0.0.1:5000

Self-test prediction without starting Flask:

    python backend\predict.py

The backend does not overwrite data/churnguard.db or models/churn_model.pkl.
