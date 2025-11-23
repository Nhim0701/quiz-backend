# Question Data Import Guide

This document describes how to import quiz questions from CSV files into the database.

## Overview

The import process consists of two main scripts:

1. **`split_csv.py`** - Splits a large CSV file into smaller daily files
2. **`csv_to_yaml_import.py`** - Imports CSV data directly to the database

## CSV File Format

The CSV file should have the following columns:

| Column | Description | Required |
|--------|-------------|----------|
| `No` | Question number | Optional |
| `Content` | Question text | Required |
| `A` | Option A text | Required |
| `B` | Option B text | Required |
| `C` | Option C text | Optional |
| `D` | Option D text | Optional |
| `Answered` | Correct answer and explanation | Required |

### Answered Field Format

The `Answered` column should contain the correct answer in one of these formats:

**Single correct answer:**
```
# Answer
- **Correct option:** A
- **Reason:** Explanation text here...
```

**Multiple correct answers:**
```
# Answer
- **Correct options:** B and D
- **Reason:** Explanation text here...
```

## Directory Structure

```
quiz/data/
├── CSV/                          # CSV files directory
│   ├── Question_data1.csv        # Original large CSV
│   ├── DVA-C02 Day1.csv          # Split files
│   ├── DVA-C02 Day2.csv
│   └── ...
├── split_csv.py                  # CSV splitter script
├── csv_to_yaml_import.py         # Import script
└── docs/
    └── IMPORT_QUESTIONS.md       # This file
```

## Step-by-Step Import Process

### Step 1: Prepare Your CSV File

Place your CSV file in the `quiz/data/CSV/` directory.

### Step 2: Split CSV into Daily Files (Optional)

If you have a large CSV file and want to split it into smaller daily practice sets:

```bash
cd quiz/

# Split into 20 questions per file
poetry run python data/split_csv.py data/CSV/Question_data1.csv \
    --per-file 20 \
    --prefix "DVA-C02 Day"
```

**Options:**
- `--per-file` - Number of questions per file (default: 20)
- `--prefix` - Filename prefix (default: "DVA-C02 Day")
- `--output-dir` - Output directory (default: same as input)

**Output:**
```
DVA-C02 Day1.csv  (questions 1-20)
DVA-C02 Day2.csv  (questions 21-40)
DVA-C02 Day3.csv  (questions 41-60)
...
```

### Step 3: Import to Database

#### Import a Single File

```bash
cd quiz/

poetry run python data/csv_to_yaml_import.py "data/CSV/DVA-C02 Day1.csv" \
    --start-id 1 \
    --category "aws" \
    --question-set "DVA-C02 Day1"
```

**Options:**
- `--start-id` - Starting question ID (default: 1000)
- `--category` - Question category (default: "aws")
- `--question-set` - Question set name (default: "AWS DVA-C02 Dump 1")
- `--update` - Update existing questions instead of skipping
- `--save-yaml` - Save as YAML file instead of importing

#### Import All Split Files

Use a loop to import all daily files:

```bash
cd quiz/

for day in $(seq 1 15); do
  start_id=$((1 + (day - 1) * 20))
  poetry run python data/csv_to_yaml_import.py \
    "data/CSV/DVA-C02 Day${day}.csv" \
    --start-id $start_id \
    --category "aws" \
    --question-set "DVA-C02 Day${day}"
done
```

### Step 4: Verify Import

Check the database to verify the import:

```bash
# Count total questions
PGPASSWORD=animepass psql -U animeuser -h localhost -d quiz_db \
    -c "SELECT COUNT(*) as total FROM questions;"

# Count by question_set
PGPASSWORD=animepass psql -U animeuser -h localhost -d quiz_db \
    -c "SELECT question_set, COUNT(*) FROM questions GROUP BY question_set ORDER BY question_set;"

# Count answers
PGPASSWORD=animepass psql -U animeuser -h localhost -d quiz_db \
    -c "SELECT COUNT(*) as total_answers FROM answers;"
```

## Database Reset (If Needed)

To reset the database and start fresh:

```bash
cd quiz/

# Drop and recreate database
PGPASSWORD=animepass psql -U animeuser -h localhost -d postgres \
    -c "DROP DATABASE IF EXISTS quiz_db;"
PGPASSWORD=animepass psql -U animeuser -h localhost -d postgres \
    -c "CREATE DATABASE quiz_db;"

# Apply migrations
poetry run alembic upgrade head
```

## Current Data Summary

After importing `Question_data1.csv`:

| Question Set | Count |
|--------------|-------|
| DVA-C02 Day1 | 19 |
| DVA-C02 Day2 | 20 |
| DVA-C02 Day3 | 20 |
| DVA-C02 Day4 | 20 |
| DVA-C02 Day5 | 20 |
| DVA-C02 Day6 | 20 |
| DVA-C02 Day7 | 20 |
| DVA-C02 Day8 | 20 |
| DVA-C02 Day9 | 20 |
| DVA-C02 Day10 | 20 |
| DVA-C02 Day11 | 20 |
| DVA-C02 Day12 | 20 |
| DVA-C02 Day13 | 20 |
| DVA-C02 Day14 | 20 |
| DVA-C02 Day15 | 20 |
| **Total** | **299** |

> Note: Question 1 in Day1 was skipped because it had no answer options.

## Troubleshooting

### Warning: Question has no answers
This occurs when the CSV row has empty A/B/C/D columns. Check the source CSV for missing data.

### Warning: Couldn't parse correct answer
The `Answered` column format doesn't match expected patterns. Ensure it contains `**Correct option:** X` or `**Correct options:** X and Y`.

### Question ID conflicts
Use `--start-id` to specify unique starting IDs for each import batch, or use `--update` to overwrite existing questions.

## API Endpoints

After import, questions are available via:

- `GET /api/v1/questions/categories` - List all categories
- `GET /api/v1/questions/by-category/{category}` - Get questions by category
- `GET /api/v1/questions/by-set/{question_set}` - Get questions by set (if implemented)
