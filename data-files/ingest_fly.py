from ingestion.pipeline import run_pipeline

result = run_pipeline(
    xlsx_paths=["/app/data-files/main.xlsx", "/app/data-files/extra.xlsx"],
    docx_path="/app/data-files/dictionary.docx",
    reset=False,
)
print(f"Ingestion done: {result}")
