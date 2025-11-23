#!/usr/bin/env python3
"""
Convert CSV quiz data to YAML and import to database.

CSV Format:
No,Content,A,B,C,D,Answered
2,"Question text...",Option A,Option B,Option C,Option D,"# Answer\n- **Correct option:** A\n- **Reason:**..."

Usage:
    cd quiz/
    poetry run python data/csv_to_yaml_import.py "My aws - Sheet3 (1).csv" --start-id 1000
"""
import os
import sys
import csv
import yaml
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.questions import Question
from app.models.answers import Answer


def parse_answered_field(answered_text):
    """
    Parse the 'Answered' field to extract the correct option letter(s).

    Supports both single and multiple correct answers:
    - "**Correct option:** A" -> ['A']
    - "**Correct options:** B and D" -> ['B', 'D']
    - "**Correct options:** A, B, and C" -> ['A', 'B', 'C']

    Returns:
        List of correct option letters (e.g., ['A'] or ['B', 'D'])
    """
    if not answered_text:
        return []

    # First try to match multiple options pattern: "Correct options: B and D" or "Correct options: A, B, and C"
    multi_match = re.search(r'\*\*Correct options?:\*\*\s*([A-D][^*\n]*)', answered_text, re.IGNORECASE)
    if not multi_match:
        multi_match = re.search(r'Correct options?:\s*([A-D][^\n]*)', answered_text, re.IGNORECASE)

    if multi_match:
        options_text = multi_match.group(1)
        # Extract all capital letters A-D from the matched text
        options = re.findall(r'[A-D]', options_text.upper())
        if options:
            return list(set(options))  # Remove duplicates

    return []


def extract_explanation(answered_text):
    """
    Extract the explanation/reason from the Answered field.

    Returns the full explanation including reason, examples, tips, etc.
    """
    if not answered_text:
        return None

    # Remove the "# Answer" header and correct option line (both singular and plural)
    explanation = re.sub(r'^#\s*Answer\s*\n', '', answered_text)
    explanation = re.sub(r'-\s*\*\*Correct options?:\*\*\s*[A-D][^\n]*\n', '', explanation)

    return explanation.strip() if explanation.strip() else None


def clean_content(text):
    """
    Clean question content by removing JSON array markers and extra quotes.

    Example: '["Question text..."]' -> 'Question text...'
    """
    if not text:
        return text

    # Remove JSON array markers and quotes
    text = re.sub(r'^\["', '', text)
    text = re.sub(r'"\]$', '', text)
    text = re.sub(r'\\n', '\n', text)  # Convert \n to actual newlines

    return text.strip()


def csv_to_yaml(csv_file_path, start_id=1000, category="aws", question_set="AWS DVA-C02 Dump 1"):
    """
    Convert CSV file to YAML format suitable for import.

    Args:
        csv_file_path: Path to CSV file
        start_id: Starting ID for questions
        category: Question category
        question_set: Question set/dump name

    Returns:
        List of question dictionaries
    """
    questions = []

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader):
            question_id = start_id + idx

            # Parse question content
            content = clean_content(row.get('Content', ''))
            if not content:
                print(f"⚠️  Warning: Skipping row {idx+1} - empty content")
                continue

            # Parse correct answer(s) - now returns a list
            correct_options = parse_answered_field(row.get('Answered', ''))
            if not correct_options:
                print(f"⚠️  Warning: Question {question_id} - couldn't parse correct answer, defaulting to 'A'")
                correct_options = ['A']

            # Extract explanation
            explanation = extract_explanation(row.get('Answered', ''))

            # Build answers list
            answers = []
            explanation_added = False
            for option_letter in ['A', 'B', 'C', 'D']:
                option_text = (row.get(option_letter) or '').strip()
                if option_text:
                    is_correct = option_letter in correct_options
                    # Only add explanation to the first correct answer
                    add_explanation = is_correct and not explanation_added
                    if add_explanation:
                        explanation_added = True
                    answers.append({
                        'content': option_text,
                        'is_correct': is_correct,
                        'explanation': explanation if add_explanation else None
                    })

            if not answers:
                print(f"⚠️  Warning: Question {question_id} has no answers")
                continue

            # Build question dict
            question = {
                'id': question_id,
                'content': content,
                'category': category,
                'question_set': question_set,
                'answers': answers
            }

            questions.append(question)

    return questions


def import_to_database(questions, skip_existing=True):
    """Import questions directly to database."""
    db = SessionLocal()

    try:
        imported_count = 0
        skipped_count = 0

        for q_data in questions:
            question_id = q_data['id']

            # Check if exists
            existing = db.query(Question).filter(Question.id == question_id).first()

            if existing and skip_existing:
                print(f"⏭️  Skipping existing question ID {question_id}")
                skipped_count += 1
                continue
            elif existing:
                print(f"🔄 Updating question ID {question_id}")
                existing.content = q_data['content']
                existing.category = q_data['category']
                existing.question_set = q_data['question_set']
                existing.updated_at = datetime.now()
                question = existing

                # Delete old answers
                db.query(Answer).filter(Answer.question_id == question_id).delete()
            else:
                print(f"➕ Adding question ID {question_id}")
                question = Question(
                    id=question_id,
                    content=q_data['content'],
                    category=q_data['category'],
                    question_set=q_data['question_set'],
                    created_at=datetime.now()
                )
                db.add(question)

            db.flush()

            # Add answers
            for a_data in q_data['answers']:
                answer = Answer(
                    question_id=question.id,
                    content=a_data['content'],
                    is_correct=a_data['is_correct'],
                    explanation=a_data.get('explanation'),
                    created_at=datetime.now()
                )
                db.add(answer)

            imported_count += 1

        db.commit()

        print("\n" + "="*60)
        print(f"✅ Import completed!")
        print(f"   Imported: {imported_count} questions")
        print(f"   Skipped:  {skipped_count} questions")
        print("="*60)

        return True

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def save_yaml_file(questions, output_path):
    """Save questions to YAML file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(questions, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"📝 YAML file saved: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Convert CSV quiz data to YAML and import to database')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--start-id', type=int, default=1000, help='Starting question ID (default: 1000)')
    parser.add_argument('--category', default='aws', help='Question category (default: aws)')
    parser.add_argument('--question-set', default='AWS DVA-C02 Dump 1', help='Question set name')
    parser.add_argument('--save-yaml', help='Save to YAML file instead of importing directly')
    parser.add_argument('--update', action='store_true', help='Update existing questions')

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"❌ Error: File not found: {args.csv_file}")
        sys.exit(1)

    print(f"📂 Reading CSV: {args.csv_file}")
    print(f"   Category: {args.category}")
    print(f"   Question Set: {args.question_set}")
    print(f"   Starting ID: {args.start_id}")
    print()

    # Convert CSV to questions
    questions = csv_to_yaml(
        args.csv_file,
        start_id=args.start_id,
        category=args.category,
        question_set=args.question_set
    )

    if not questions:
        print("❌ No valid questions found in CSV")
        sys.exit(1)

    print(f"\n✅ Parsed {len(questions)} questions from CSV")

    # Save to YAML or import directly
    if args.save_yaml:
        save_yaml_file(questions, args.save_yaml)
        print(f"\n💡 To import: poetry run python data/import_questions.py {args.save_yaml}")
    else:
        print("\n🚀 Importing to database...")
        success = import_to_database(questions, skip_existing=not args.update)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
