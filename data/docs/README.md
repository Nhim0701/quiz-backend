# Question Import Guide

This guide explains the best way to import questions and answers into your quiz database.

## Quick Start

### 1. Create Your Question YAML File

Use the template at `data/questions_template.yaml` as a reference:

```yaml
- id: 1001  # Must be unique
  content: "What is Amazon S3?"
  category: aws
  question_set: "AWS DVA-C02 Dump 1"  # Optional
  image_url: null  # Optional
  answers:
    - content: "Object Storage Service"
      is_correct: true
      explanation: "S3 is for object storage"  # Optional
    - content: "Relational Database"
      is_correct: false
```

### 2. Run the Import Script

```bash
cd quiz/
poetry run python data/import_questions.py data/your_questions.yaml
```

## Field Reference

### Question Fields

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `id` | ✅ Yes | Integer | Unique question ID (cannot be changed later) | `1001` |
| `content` | ✅ Yes | Text | The question text | `"What is AWS?"` |
| `category` | ✅ Yes | String | Question category | `"aws"`, `"jlpt"`, `"geography"` |
| `question_set` | ❌ No | String | Group questions into sets/dumps | `"AWS DVA-C02 Dump 1"` |
| `image_url` | ❌ No | URL | URL to question image | `"https://example.com/image.png"` |
| `answers` | ✅ Yes | Array | List of answers (at least 1 required) | See below |

### Answer Fields

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `content` | ✅ Yes | Text | The answer text | `"Amazon S3"` |
| `is_correct` | ✅ Yes | Boolean | Is this the correct answer? | `true` or `false` |
| `explanation` | ❌ No | Text | Explanation why this is correct/incorrect | `"S3 is object storage"` |
| `image_url` | ❌ No | URL | URL to answer image | `"https://example.com/answer.png"` |

## Import Modes

### Default Mode (Skip Existing)
Skips questions that already exist in the database:

```bash
poetry run python data/import_questions.py data/your_questions.yaml
```

### Update Mode (Overwrite Existing)
Updates existing questions with new data:

```bash
poetry run python data/import_questions.py data/your_questions.yaml --update
```

⚠️ **Warning**: Update mode will delete old answers and replace them with new ones!

## Best Practices

### 1. **Organize by Date Folders**
Keep your imports organized by date:

```
data/
├── 20251121/
│   ├── aws_questions.yaml
│   └── jlpt_questions.yaml
├── 20251122/
│   └── more_questions.yaml
└── questions_template.yaml
```

### 2. **Use Sequential Question IDs**
Organize IDs by category:

- **1000-1999**: AWS questions
- **2000-2999**: JLPT questions
- **3000-3999**: Google Cloud questions
- **4000-4999**: Other categories

### 3. **Group with question_set**
Use `question_set` to organize questions into practice sets:

```yaml
- id: 1001
  content: "..."
  category: aws
  question_set: "AWS DVA-C02 Dump 1"  # All questions in same dump
```

### 4. **Multi-Select Questions**
Mark multiple answers as correct for multi-select questions:

```yaml
- id: 1005
  content: "Which are AWS compute services? (Select TWO)"
  category: aws
  answers:
    - content: "EC2"
      is_correct: true
    - content: "Lambda"
      is_correct: true
    - content: "S3"
      is_correct: false
```

### 5. **Add Explanations**
Help users learn by adding explanations:

```yaml
answers:
  - content: "Amazon S3"
    is_correct: true
    explanation: "S3 (Simple Storage Service) is AWS's object storage solution"
  - content: "Amazon EBS"
    is_correct: false
    explanation: "EBS is block storage for EC2, not object storage"
```

## Example Import Workflow

### Step 1: Create Question File

Create `data/20251121/aws_dump1.yaml`:

```yaml
- id: 1001
  content: "What is the maximum size of an S3 object?"
  category: aws
  question_set: "AWS DVA-C02 Dump 1"
  answers:
    - content: "5 TB"
      is_correct: true
      explanation: "S3 supports objects up to 5 TB in size"
    - content: "5 GB"
      is_correct: false
    - content: "500 GB"
      is_correct: false

- id: 1002
  content: "Which AWS service provides serverless compute?"
  category: aws
  question_set: "AWS DVA-C02 Dump 1"
  answers:
    - content: "AWS Lambda"
      is_correct: true
    - content: "Amazon EC2"
      is_correct: false
    - content: "Amazon ECS"
      is_correct: false
```

### Step 2: Import Questions

```bash
cd quiz/
poetry run python data/import_questions.py data/20251121/aws_dump1.yaml
```

### Step 3: Verify Import

Check the output:
```
📂 Loading questions from: data/20251121/aws_dump1.yaml
✅ Import completed!
   Imported: 2 questions
   Skipped:  0 questions
```

### Step 4: Test in Application

1. Log in to the quiz app
2. Select "AWS" category
3. Choose "AWS DVA-C02 Dump 1" set
4. Start taking the quiz!

## Common Issues

### Issue: "Question ID already exists"

**Solution**: Use `--update` flag to overwrite, or use a different ID

```bash
poetry run python data/import_questions.py data/questions.yaml --update
```

### Issue: "No questions found in YAML file"

**Solution**: Check YAML syntax with a validator (https://www.yamllint.com/)

### Issue: "Question has no answers"

**Solution**: Add at least one answer to the `answers` array

## Alternative Import Methods

### Method 1: Python Script (Current - Recommended ✅)
- ✅ Easy to use
- ✅ Good error handling
- ✅ Can skip or update existing questions
- ✅ Validates data before import

### Method 2: Direct Database Insert (Not Recommended)
- ❌ No validation
- ❌ Risk of data corruption
- ❌ Must handle relationships manually
- ❌ No rollback on errors

### Method 3: API Endpoint (Future Enhancement)
- 📋 Todo: Create POST `/api/v1/questions/import` endpoint
- Would allow web-based imports
- Good for non-technical users

## Support

For issues or questions about importing data:
1. Check the template: `data/questions_template.yaml`
2. Review this README
3. Check import logs for specific error messages

## Script Location

- **Import script**: `data/import_questions.py`
- **Template**: `data/questions_template.yaml`
- **Example data**: `data/20251102/questions.yaml`
