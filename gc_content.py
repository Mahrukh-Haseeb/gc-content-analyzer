"""
GC Content Analysis Backend Module
Author: [Your Name]
Provides functions for reading DNA sequences and calculating GC content.
"""

import argparse
import csv
import matplotlib.pyplot as plt

def read_sequences(file_path):
    sequences = []
    header = None
    current_seq = ""

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                if current_seq:
                    sequences.append((header, current_seq))
                    current_seq = ""
                header = line[1:]
            else:
                current_seq += line.upper()
        if current_seq:
            sequences.append((header, current_seq))

    return sequences


def gc_content(sequence):
    gc_count = sequence.count('G') + sequence.count('C')
    return (gc_count / len(sequence)) * 100 if len(sequence) > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="GC Content Analysis Tool")
    parser.add_argument("input", help="Input FASTA/sequence file")
    parser.add_argument("-o", "--output", help="Optional: Save results to CSV file")
    args = parser.parse_args()

    try:
        sequences = read_sequences(args.input)
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
        return
    except Exception as e:
        print(f"Error while reading file: {e}")
        return

    if not sequences:
        print("No valid sequences found.")
        return

    results = []
    valid_bases = set("ATGC")

    for i, (header, seq) in enumerate(sequences, start=1):
        if not set(seq).issubset(valid_bases):
            print(f"Warning: Sequence {header or f'Sequence {i}'} contains invalid characters.")
        gc = gc_content(seq)
        name = header if header else f"Sequence {i}"
        results.append((name, len(seq), gc))
        print(f"{name}: Length={len(seq)}, GC%={gc:.2f}")

    if args.output:
        try:
            with open(args.output, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Sequence Name", "Length", "GC%"])
                for name, length, gc in results:
                    writer.writerow([name, length, f"{gc:.2f}"])
            print(f"\nResults saved to {args.output}")
        except Exception as e:
            print(f"Error writing CSV: {e}")

    if results:
        gc_values = [gc for _, _, gc in results]
        names = [name for name, _, _ in results]

        print("\nSummary Statistics:")
        print(f"Minimum GC%: {min(gc_values):.2f}")
        print(f"Maximum GC%: {max(gc_values):.2f}")
        print(f"Average GC%: {sum(gc_values)/len(gc_values):.2f}")

        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.hist(gc_values, bins=10, color="skyblue", edgecolor="black")
        plt.xlabel("GC%")
        plt.ylabel("Frequency")
        plt.title("GC Content Distribution")

        plt.subplot(1, 2, 2)
        plt.bar(names, gc_values, color="lightgreen", edgecolor="black")
        plt.xlabel("Sequences")
        plt.ylabel("GC%")
        plt.title("GC% per Sequence")
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
