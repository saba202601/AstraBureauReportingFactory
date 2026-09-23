# Astra Bureau Reporting Factory

Streamlit prototype for Neurology Insurance AGI-OS.

## Flow
Line of Business → Premium/Loss/Type → Bureau → Reporting Module → Upload Source → Upload Layout → Canonical Mapping → Validation → Output.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Production design
Connect the UI to SQL Server canonical metadata, source staging, effective-dated bureau layouts, mapping/synonym/picklist tables, deterministic transformation rules, validation, reconciliation, acknowledgements, and audit history.

The application must never invent missing bureau codes or regulatory requirements. Use current licensed bureau layouts and controlled exception policies.
