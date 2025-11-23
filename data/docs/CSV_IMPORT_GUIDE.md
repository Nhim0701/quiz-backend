# CSV to YAML Import Guide

This guide explains how to import quiz questions from CSV format into your database.

## ✅ Successfully Imported

Your CSV file has been successfully imported!

**Results:**
- ✅ **50 questions** imported to database
- 📁 Category: `aws`
- 📦 Question Set: `AWS DVA-C02 Dump 1`
- 🔢 Question IDs: `1000-1049`

## CSV Format Requirements

Your CSV file should have this structure:

```csv
No,Content,A,B,C,D,Answered
2,"Question text here...",Option A text,Option B text,Option C text,Option D text,"# Answer\n- **Correct option:** A\n- **Reason:** Explanation..."
```

### Column Descriptions

| Column | Description | Example |
|--------|-------------|---------|
| `No` | Question number (not used as ID) | `2` |
| `Content` | Question text (can include newlines) | `"What is AWS?"` |
| `A`, `B`, `C`, `D` | Answer options | `"Amazon Web Services"` |
| `Answered` | Contains correct answer and explanation | `"# Answer\n- **Correct option:** A\n- **Reason:**..."` |

### Answered Field Format

The `Answered` field should contain:

```markdown
# Answer
- **Correct option:** A
- **Reason:** Explanation of why this is correct...

# Example / Analogy
- Additional context...

# Common Mistakes / Traps
- Things to watch out for...

# Memory Tip
- Tips to remember...
```

**Important:** The script automatically extracts:
- ✅ Correct answer letter (A, B, C, or D)
- ✅ Full explanation (attached to correct answer only)

## Import Commands

### Basic Import (Default Settings)

```bash
cd quiz/
poetry run python data/csv_to_yaml_import.py "My aws - Sheet3 (1).csv"
```

This uses default settings:
- Start ID: `1000`
- Category: `aws`
- Question Set: `AWS DVA-C02 Dump 1`

### Custom Import Settings

```bash
# Specify custom starting ID
poetry run python data/csv_to_yaml_import.py "questions.csv" --start-id 2000

# Specify custom category
poetry run python data/csv_to_yaml_import.py "questions.csv" --category jlpt

# Specify custom question set
poetry run python data/csv_to_yaml_import.py "questions.csv" --question-set "JLPT N2 Set 1"

# Combine multiple options
poetry run python data/csv_to_yaml_import.py "questions.csv" \
  --start-id 3000 \
  --category "google-cloud" \
  --question-set "GCP Professional Architect Dump 1"
```

### Update Existing Questions

```bash
# Overwrite existing questions with same IDs
poetry run python data/csv_to_yaml_import.py "questions.csv" --update
```

### Save to YAML File (Don't Import Yet)

```bash
# Convert to YAML file for review before importing
poetry run python data/csv_to_yaml_import.py "questions.csv" \
  --save-yaml data/20251121/aws_questions.yaml

# Then import the YAML file separately
poetry run python data/import_questions.py data/20251121/aws_questions.yaml
```

## Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `csv_file` | Path to CSV file (required) | - | `"My questions.csv"` |
| `--start-id` | Starting question ID | `1000` | `--start-id 2000` |
| `--category` | Question category | `aws` | `--category jlpt` |
| `--question-set` | Question set/dump name | `AWS DVA-C02 Dump 1` | `--question-set "Set 2"` |
| `--save-yaml` | Save to YAML instead of importing | - | `--save-yaml output.yaml` |
| `--update` | Update existing questions | `false` | `--update` |

## What Happens During Import

1. **CSV Parsing**: Reads your CSV file
2. **Content Cleaning**: Removes JSON markers and formats text
3. **Answer Extraction**: Finds correct answer from "Answered" field
4. **Explanation Parsing**: Extracts full explanation for correct answer
5. **Database Import**: Inserts questions and answers into database
6. **Summary Report**: Shows imported/skipped counts

## Example Output

```
📂 Reading CSV: My aws - Sheet3 (1).csv
   Category: aws
   Question Set: AWS DVA-C02 Dump 1
   Starting ID: 1000

⚠️  Warning: Question 1014 - couldn't parse correct answer, defaulting to 'A'

✅ Parsed 50 questions from CSV

🚀 Importing to database...
➕ Adding question ID 1000
➕ Adding question ID 1001
...

============================================================
✅ Import completed!
   Imported: 50 questions
   Skipped:  0 questions
============================================================
```

## Organizing Your Imports

### Recommended ID Ranges

Keep your question IDs organized by category:

| Category | ID Range | Example |
|----------|----------|---------|
| AWS | 1000-1999 | AWS DVA-C02 questions |
| JLPT | 2000-2999 | Japanese language questions |
| Google Cloud | 3000-3999 | GCP certification questions |
| Other | 4000+ | Other topics |

### Example: Multiple CSV Files

```bash
# Import AWS Dump 1
poetry run python data/csv_to_yaml_import.py "aws_dump1.csv" \
  --start-id 1000 --question-set "AWS DVA-C02 Dump 1"

# Import AWS Dump 2
poetry run python data/csv_to_yaml_import.py "aws_dump2.csv" \
  --start-id 1100 --question-set "AWS DVA-C02 Dump 2"

# Import JLPT N2
poetry run python data/csv_to_yaml_import.py "jlpt_n2.csv" \
  --start-id 2000 --category jlpt --question-set "JLPT N2 Set 1"

# Import Google Cloud
poetry run python data/csv_to_yaml_import.py "gcp_questions.csv" \
  --start-id 3000 --category "google-cloud" \
  --question-set "GCP Professional Cloud Architect"
```

## Troubleshooting

### Warning: "couldn't parse correct answer"

**Issue**: Script couldn't find correct answer in "Answered" field

**Solution**:
- Check that "Answered" field contains `**Correct option:** A` (or B, C, D)
- Script will default to option 'A' if not found
- You can manually fix in database later or re-import with `--update`

### Questions Already Exist

**Issue**: Questions with same IDs already in database

**Solution**:
```bash
# Skip existing (default)
poetry run python data/csv_to_yaml_import.py "questions.csv"

# Or overwrite existing
poetry run python data/csv_to_yaml_import.py "questions.csv" --update
```

### CSV Encoding Issues

**Issue**: Special characters not displaying correctly

**Solution**:
- Ensure CSV is saved as UTF-8 encoding
- In Excel: Save As → CSV UTF-8
- The script uses `encoding='utf-8'` by default

## Verify Your Import

After importing, verify in the database:

```bash
poetry run python -c "
from app.db.session import SessionLocal
from app.models.questions import Question

db = SessionLocal()
count = db.query(Question).filter(
    Question.category == 'aws',
    Question.question_set == 'AWS DVA-C02 Dump 1'
).count()
print(f'Total questions: {count}')
db.close()
"
```

Or check in the application:
1. Log in to quiz app
2. Go to Profile page
3. Select "AWS" category
4. Choose "AWS DVA-C02 Dump 1" set
5. Start quiz!

## Related Files

- **Import Script**: [data/csv_to_yaml_import.py](csv_to_yaml_import.py)
- **YAML Import Script**: [data/import_questions.py](import_questions.py)
- **General Guide**: [data/README.md](README.md)
- **YAML Template**: [data/questions_template.yaml](questions_template.yaml)
