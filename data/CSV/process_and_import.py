#!/usr/bin/env python3
"""
Process AWS DVA-C02 exam data and import to database.
This script:
1. Reads Data.csv
2. Cleans and splits data into 25 day files (20 questions each)
3. Imports to database with questions and answers (including explanations)
"""

import sys
import os
import csv
import re
from pathlib import Path


def clean_text(text):
    """Remove unnecessary characters and clean text."""
    if not text:
        return ""

    text = text.strip()

    # Remove newlines within text (keep single spaces)
    text = ' '.join(text.split())

    return text


def parse_correct_answers(correct_field):
    """Parse the Correct field to extract answer letters."""
    if not correct_field:
        return []

    correct_field = correct_field.strip()

    # Try to parse as JSON
    answers = []
    try:
        # Extract voted_answers from JSON structure
        matches = re.findall(r'"voted_answers"\s*:\s*"([A-E]+)"', correct_field)
        if matches:
            # Get the most voted answer (first one)
            answer_str = matches[0]
            # Split into individual letters (e.g., "AB" -> ["A", "B"])
            answers = list(answer_str)
    except Exception as e:
        print(f"Error parsing correct answers: {correct_field}, Error: {e}")

    # If JSON parsing failed, try simple parsing
    if not answers and correct_field:
        # Simple format like "A", "B", "AB", etc.
        valid_options = ['A', 'B', 'C', 'D', 'E']
        for char in correct_field:
            if char in valid_options:
                answers.append(char)

    return answers


def split_csv_to_days(input_file, output_dir, questions_per_day=20, total_days=25):
    """Split CSV file into day files."""

    os.makedirs(output_dir, exist_ok=True)

    print(f"Reading {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_questions = len(rows)
    total_questions_needed = questions_per_day * total_days

    print(f"Total questions in file: {total_questions}")
    print(f"Questions needed for {total_days} days: {total_questions_needed}")
    print(f"Questions per day: {questions_per_day}")

    # Use only the first total_questions_needed questions
    rows = rows[:total_questions_needed]

    # Split into days
    for day in range(1, total_days + 1):
        start_idx = (day - 1) * questions_per_day
        end_idx = start_idx + questions_per_day
        day_rows = rows[start_idx:end_idx]

        if not day_rows:
            break

        output_file = os.path.join(output_dir, f'DVA-C02_Day_{day}.csv')

        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['ID', 'Question', 'Answer_A', 'Answer_B', 'Answer_C', 'Answer_D', 'Answer_E', 'Correct_Answers', 'Explanation']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in day_rows:
                # Clean the data
                question_id = row['ID'].strip()
                question_text = clean_text(row['Question'])

                answer_a = clean_text(row['Chose_A'])
                answer_b = clean_text(row['Chose_B'])
                answer_c = clean_text(row['Chose_C'])
                answer_d = clean_text(row['Chose_D'])
                answer_e = clean_text(row.get('Chose_E', ''))

                correct_answers = parse_correct_answers(row.get('Answered', row.get('Correct', '')))
                explanation = clean_text(row.get('Explain', ''))

                writer.writerow({
                    'ID': question_id,
                    'Question': question_text,
                    'Answer_A': answer_a,
                    'Answer_B': answer_b,
                    'Answer_C': answer_c,
                    'Answer_D': answer_d,
                    'Answer_E': answer_e,
                    'Correct_Answers': ','.join(correct_answers),
                    'Explanation': explanation
                })

        print(f"Created {output_file} with {len(day_rows)} questions")

    print(f"\nSuccessfully split {len(rows)} questions into {total_days} day files!")
    return True


def import_csv_to_database(csv_file, question_set_name, db_session, Question, Answer):
    """Import a single CSV file to database."""

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        questions_imported = 0

        for row in reader:
            question_id = int(row['ID'])

            # Check if question already exists
            existing_question = db_session.query(Question).filter(Question.id == question_id).first()

            if existing_question:
                print(f"  Question ID {question_id} already exists, skipping...")
                continue

            # Create question
            question = Question(
                id=question_id,
                content=row['Question'],
                category="AWS Certified Developer - Associate DVA-C02",
                question_set=question_set_name
            )

            db_session.add(question)
            db_session.flush()

            # Get correct answers
            correct_answers_str = row['Correct_Answers']
            correct_answers = correct_answers_str.split(',') if correct_answers_str else []

            explanation = row.get('Explanation', '')

            # Create answers (A, B, C, D, E)
            answer_options = {
                'A': row['Answer_A'],
                'B': row['Answer_B'],
                'C': row['Answer_C'],
                'D': row['Answer_D'],
                'E': row.get('Answer_E', '')
            }

            for option_letter, option_text in answer_options.items():
                if option_text:  # Only create if answer text exists
                    is_correct = option_letter in correct_answers

                    # Add explanation only to correct answers
                    answer_explanation = explanation if is_correct else None

                    answer = Answer(
                        question_id=question.id,
                        content=option_text,
                        is_correct=is_correct,
                        explanation=answer_explanation
                    )
                    db_session.add(answer)

            questions_imported += 1

            # Commit every 10 questions
            if questions_imported % 10 == 0:
                db_session.commit()
                print(f"  Imported {questions_imported} questions...")

        # Final commit
        db_session.commit()
        print(f"  ✓ Successfully imported {questions_imported} questions from {csv_file.name}")
        return questions_imported


def import_all_to_database(split_days_dir='split_days'):
    """Import all day CSV files to database."""

    # Import database modules here
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Add parent directory to path for app imports
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from app.models.questions import Question
    from app.models.answers import Answer

    # Load environment variables
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found in environment variables")
        print("Please create a .env file with DATABASE_URL")
        return False

    script_dir = Path(__file__).parent
    days_dir = script_dir / split_days_dir

    if not days_dir.exists():
        print(f"Directory {days_dir} does not exist!")
        return False

    # Get all CSV files sorted by day number
    csv_files = sorted(days_dir.glob('DVA-C02_Day_*.csv'),
                      key=lambda x: int(x.stem.split('_')[-1]))

    if not csv_files:
        print(f"No CSV files found in {days_dir}")
        return False

    print(f"\n{'='*60}")
    print(f"IMPORTING TO DATABASE")
    print(f"{'='*60}")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    print(f"Found {len(csv_files)} day files to import\n")

    # Create database engine and session
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    total_imported = 0

    try:
        for csv_file in csv_files:
            day_name = csv_file.stem  # e.g., "DVA-C02_Day_1"

            print(f"\n{day_name}:")
            count = import_csv_to_database(csv_file, day_name, db, Question, Answer)
            total_imported += count

        print(f"\n{'='*60}")
        print(f"IMPORT COMPLETE")
        print(f"Total questions imported: {total_imported}")
        print(f"{'='*60}\n")
        return True

    except Exception as e:
        db.rollback()
        print(f"\nERROR during import: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Process and import DVA-C02 exam data')
    parser.add_argument('--split-only', action='store_true', help='Only split CSV, do not import')
    parser.add_argument('--import-only', action='store_true', help='Only import (CSV already split)')
    parser.add_argument('--days', type=int, default=25, help='Number of days to split into (default: 25)')
    parser.add_argument('--questions-per-day', type=int, default=20, help='Questions per day (default: 20)')

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    input_file = script_dir / 'Data.csv'
    output_dir = script_dir / 'split_days'

    # Step 1: Split CSV
    if not args.import_only:
        print(f"\n{'='*60}")
        print("STEP 1: SPLITTING CSV INTO DAY FILES")
        print(f"{'='*60}\n")

        if not input_file.exists():
            print(f"ERROR: {input_file} not found!")
            return 1

        success = split_csv_to_days(
            input_file,
            output_dir,
            questions_per_day=args.questions_per_day,
            total_days=args.days
        )

        if not success:
            return 1

    # Step 2: Import to database
    if not args.split_only:
        print(f"\n{'='*60}")
        print("STEP 2: IMPORTING TO DATABASE")
        print(f"{'='*60}\n")

        success = import_all_to_database('split_days')

        if not success:
            return 1

    print("\n✓ All operations completed successfully!\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
