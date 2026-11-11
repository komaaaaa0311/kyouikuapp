import csv
import json
from pathlib import Path

# Googleスプレッドシートから「問題データ」シートをCSVでダウンロードし、
# このファイルと同じフォルダに questions.csv という名前で保存してください。

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "questions.csv"
JSON_FILE = BASE_DIR / "questions.json"

required_columns = {
    "id", "grade", "subject", "unit", "difficulty",
    "question", "choices", "answer", "explanation"
}

questions = []
with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    if not required_columns.issubset(set(reader.fieldnames or [])):
        raise ValueError("CSVの列名が正しくありません。元のシートの列名を残してください。")

    for line_number, row in enumerate(reader, start=2):
        choices = [item.strip() for item in row["choices"].split(" / ")]
        if len(choices) != 4:
            raise ValueError(f"{line_number}行目: 選択肢は「 / 」区切りで4つ必要です。")

        answer = int(row["answer"])
        if answer not in (0, 1, 2, 3):
            raise ValueError(f"{line_number}行目: answerは0〜3で指定してください。")

        questions.append({
            "id": row["id"].strip(),
            "grade": row["grade"].strip(),
            "subject": row["subject"].strip(),
            "unit": row["unit"].strip(),
            "difficulty": row["difficulty"].strip(),
            "question": row["question"].strip(),
            "choices": choices,
            "answer": answer,
            "explanation": row["explanation"].strip(),
        })

ids = [q["id"] for q in questions]
if len(ids) != len(set(ids)):
    raise ValueError("idが重複しています。各問題のidを別々にしてください。")

with JSON_FILE.open("w", encoding="utf-8") as file:
    json.dump(questions, file, ensure_ascii=False, indent=2)

print(f"{len(questions)}問を {JSON_FILE.name} に変換しました。")
