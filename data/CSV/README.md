# AWS DVA-C02 Exam Data Processing

This directory contains scripts to process and import AWS DVA-C02 practice exam questions into the database.

## Files

- `data.csv` - Original CSV file with all exam questions
- `split_exam_data.py` - Script to clean and split the data into daily question sets
- `import_to_database.py` - Script to import the processed data into the database
- `split_days/` - Directory containing the split CSV files (one per day)

## Data Structure

### Original CSV Format
- **ID**: Question ID
- **Title**: Category (AWS Certified Developer - Associate DVA-C02)
- **Question**: The question text
- **Chose A, B, C, D**: Answer options
- **Correct**: Correct answer(s) in JSON format

### Processed CSV Format
- **ID**: Question ID
- **Category**: Question category
- **Question**: The question text
- **Answer_A, B, C, D**: Clean answer options
- **Correct_Answers**: Comma-separated correct answer letters (e.g., "A" or "A,B")

## Usage

### Step 1: Split the CSV into daily files

```bash
cd quiz-backend/data/CSV
python3 split_exam_data.py
```

This will:
- Read `data.csv`
- Clean up unnecessary characters (quotes, brackets, etc.)
- Split into 20 questions per day
- Create files like `DVA-C02_Day_1.csv`, `DVA-C02_Day_2.csv`, etc. in the `split_days/` directory

### Step 2: Import to Database

Import all day files at once:
```bash
cd quiz-backend/data/CSV
python3 import_to_database.py --all
```

Or import a single file:
```bash
python3 import_to_database.py --file split_days/DVA-C02_Day_1.csv --set-name "DVA-C02_Day_1"
```

## Database Schema

### Questions Table
- `id` (Integer, Primary Key) - Question ID from CSV
- `content` (Text) - The question text
- `category` (String) - Question category
- `question_set` (String) - Set name (e.g., "DVA-C02_Day_1")
- `image_url` (Text, nullable) - Optional image URL
- `created_at`, `updated_at`, `deleted_at` - Timestamps

### Answers Table
- `id` (Integer, Primary Key, Auto-increment)
- `question_id` (Integer, Foreign Key) - References questions.id
- `content` (Text) - Answer text
- `is_correct` (Boolean) - Whether this is a correct answer
- `image_url` (Text, nullable) - Optional image URL
- `explanation` (Text, nullable) - Optional explanation
- `created_at`, `updated_at`, `deleted_at` - Timestamps

## Features

- **Automatic Duplicate Detection**: The import script checks for existing questions and skips them
- **Batch Processing**: Commits every 10 questions for better performance
- **Error Handling**: Rolls back on errors to maintain data integrity
- **Progress Tracking**: Shows progress during import

## Notes

- Total questions in original file: 535
- Questions per day: 20
- Total days created: 27 (last day has 15 questions)
- Each question can have multiple correct answers (stored as separate Answer records with is_correct=True)
