#!/usr/bin/env python3
"""
Split a large CSV file into smaller files with a specified number of questions per file.

Usage:
    cd quiz/
    poetry run python data/split_csv.py data/CSV/Question_data1.csv --per-file 20 --prefix "DVA-C02 Day"
"""
import os
import csv
import argparse


def split_csv(input_file, questions_per_file=20, output_dir=None, prefix="DVA-C02 Day"):
    """
    Split CSV file into multiple smaller files.

    Args:
        input_file: Path to input CSV file
        questions_per_file: Number of questions per output file
        output_dir: Output directory (defaults to same directory as input)
        prefix: Prefix for output filenames
    """
    if output_dir is None:
        output_dir = os.path.dirname(input_file)

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Read all rows
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    total_questions = len(rows)
    total_files = (total_questions + questions_per_file - 1) // questions_per_file

    print(f"Input file: {input_file}")
    print(f"Total questions: {total_questions}")
    print(f"Questions per file: {questions_per_file}")
    print(f"Will create {total_files} files")
    print()

    created_files = []

    for file_num in range(total_files):
        start_idx = file_num * questions_per_file
        end_idx = min(start_idx + questions_per_file, total_questions)
        chunk = rows[start_idx:end_idx]

        # Create output filename
        output_filename = f"{prefix}{file_num + 1}.csv"
        output_path = os.path.join(output_dir, output_filename)

        # Write chunk to file
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(chunk)

        print(f"Created: {output_filename} (questions {start_idx + 1}-{end_idx})")
        created_files.append(output_path)

    print()
    print(f"Successfully created {len(created_files)} files!")

    return created_files


def main():
    parser = argparse.ArgumentParser(description='Split CSV file into smaller files')
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('--per-file', type=int, default=20, help='Questions per file (default: 20)')
    parser.add_argument('--output-dir', help='Output directory (default: same as input)')
    parser.add_argument('--prefix', default='DVA-C02 Day', help='Filename prefix (default: "DVA-C02 Day")')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        return 1

    split_csv(
        args.input_file,
        questions_per_file=args.per_file,
        output_dir=args.output_dir,
        prefix=args.prefix
    )

    return 0


if __name__ == "__main__":
    exit(main())
