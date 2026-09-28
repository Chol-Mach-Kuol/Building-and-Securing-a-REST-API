"""
search.py - DSA comparison: Linear Search vs Dictionary Lookup
Author: Alier Akuang

Task: find a transaction by its id.
  1. Linear search      - check every record in the list until the id matches.   O(n)
  2. Dictionary lookup  - store {id: transaction} and jump straight to the key.  O(1) average

Extra (for the reflection):
  3. Binary search      - on a list sorted by id, halve the search range each step. O(log n)

The comparison uses the REAL transactions from Chol's parser (dsa/parse_xml.py).
It measures:
  * exactly 20 records (the minimum the assignment asks for)
  * bigger sizes up to the full dataset, to show how each method grows
  * the average case (every id looked up once) and the worst case (an id that does not exist)

Run from the repository root:
    python dsa/search.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dsa.parse_xml import parse_sms_xml

XML_PATH = os.path.join(os.path.dirname(__file__), '..', 'modified_sms_v2.xml')
RESULTS_PATH = os.path.join(os.path.dirname(__file__), 'search_results.txt')

SIZES = [20, 100, 500, 1000]   # the full dataset size is added automatically
REPEATS = 200                  # how many times each full round of lookups is repeated


# --------------------------------------------------------------------------- #
# 1. Linear search - O(n)                                                      #
# --------------------------------------------------------------------------- #
def linear_search(transactions, target_id):
    """Check each transaction one by one. Returns the transaction or None."""
    for t in transactions:
        if t['id'] == target_id:
            return t
    return None


# --------------------------------------------------------------------------- #
# 2. Dictionary lookup - O(1) average                                          #
# --------------------------------------------------------------------------- #
def build_lookup_dict(transactions):
    """Build the dictionary once: {id: transaction}. Costs O(n) time and memory."""
    return {t['id']: t for t in transactions}


def dict_lookup(lookup, target_id):
    """Python hashes the id and jumps straight to its slot."""
    return lookup.get(target_id)


# --------------------------------------------------------------------------- #
# 3. Binary search - O(log n)  (alternative suggested in the reflection)       #
# --------------------------------------------------------------------------- #
def binary_search(sorted_transactions, target_id):
    """Search a list sorted by id by halving the range each step."""
    low, high = 0, len(sorted_transactions) - 1
    while low <= high:
        middle = (low + high) // 2
        middle_id = sorted_transactions[middle]['id']
        if middle_id == target_id:
            return sorted_transactions[middle]
        if middle_id < target_id:
            low = middle + 1
        else:
            high = middle - 1
    return None


# --------------------------------------------------------------------------- #
# Timing helpers                                                               #
# --------------------------------------------------------------------------- #
def average_time_per_lookup(search_function, target_ids, repeats=REPEATS):
    """Look up every target id, repeat many times, return the average seconds per lookup."""
    start = time.perf_counter()
    for _ in range(repeats):
        for target_id in target_ids:
            search_function(target_id)
    elapsed = time.perf_counter() - start
    return elapsed / (repeats * len(target_ids))


def compare(transactions, size):
    """Run all three methods on the first `size` records and return the timings."""
    subset = transactions[:size]
    lookup = build_lookup_dict(subset)
    sorted_subset = sorted(subset, key=lambda t: t['id'])
    target_ids = [t['id'] for t in subset]            # every id once = average case
    missing_id = max(target_ids) + 1_000_000          # does not exist = worst case

    # Correctness check: all three methods must return the same transaction.
    for target_id in target_ids + [missing_id]:
        expected = linear_search(subset, target_id)
        assert dict_lookup(lookup, target_id) is expected
        assert binary_search(sorted_subset, target_id) is expected

    return {
        'size': size,
        'linear': average_time_per_lookup(lambda i: linear_search(subset, i), target_ids),
        'dict': average_time_per_lookup(lambda i: dict_lookup(lookup, i), target_ids),
        'binary': average_time_per_lookup(lambda i: binary_search(sorted_subset, i), target_ids),
        'linear_worst': average_time_per_lookup(lambda i: linear_search(subset, i), [missing_id]),
        'dict_worst': average_time_per_lookup(lambda i: dict_lookup(lookup, i), [missing_id]),
    }


def micro(seconds):
    """Format seconds as microseconds, e.g. 0.000018 -> '18.211 us'."""
    return f"{seconds * 1_000_000:8.3f} us"


def main():
    transactions = parse_sms_xml(XML_PATH)
    total = len(transactions)
    print("Running the comparison - this takes about 15-30 seconds...\n")
    sizes = [s for s in SIZES if s < total] + [total]

    lines = []
    lines.append("DSA COMPARISON - Linear Search vs Dictionary Lookup (+ Binary Search)")
    lines.append("=" * 78)
    lines.append(f"Dataset      : {total} real transactions from modified_sms_v2.xml")
    lines.append(f"Method       : every id in each subset looked up once, repeated {REPEATS} times;")
    lines.append("               times are the AVERAGE per single lookup (us = microseconds)")
    lines.append("")
    lines.append(f"{'Records':>8} | {'Linear search':>13} | {'Dict lookup':>13} | "
                 f"{'Binary search':>13} | {'Dict speed-up':>13}")
    lines.append("-" * 78)

    results = [compare(transactions, size) for size in sizes]
    for r in results:
        lines.append(f"{r['size']:>8} | {micro(r['linear']):>13} | {micro(r['dict']):>13} | "
                     f"{micro(r['binary']):>13} | {r['linear'] / r['dict']:>12.1f}x")

    lines.append("")
    lines.append("Worst case - searching for an id that does NOT exist:")
    for r in results:
        lines.append(f"  {r['size']:>5} records: linear {micro(r['linear_worst'])} "
                     f"(checks all {r['size']})  vs  dict {micro(r['dict_worst'])}")

    first, last = results[0], results[-1]
    lines.append("")
    lines.append("--- Reflection ---")
    lines.append(f"* With the required 20 records, dictionary lookup was "
                 f"{first['linear'] / first['dict']:.1f}x faster.")
    lines.append(f"* With all {last['size']} records, it was {last['linear'] / last['dict']:.1f}x faster.")
    lines.append("* Linear search is O(n): it checks records one by one, so its time grows")
    lines.append("  as the dataset grows (on average it checks half the records).")
    lines.append("* Dictionary lookup is O(1) on average: Python hashes the id and jumps")
    lines.append("  straight to the record, so its time stays about the same at every size.")
    lines.append("* Trade-off: the dictionary uses extra memory and takes O(n) to build once,")
    lines.append("  and it only helps with exact-id lookups, not ranges (e.g. between two dates).")
    lines.append("")
    lines.append("Other structures that could improve searching:")
    lines.append("* Binary search on a list sorted by id - O(log n); measured above. Slower than")
    lines.append("  a dictionary but keeps data ordered, so it also supports range queries.")
    lines.append("* Balanced binary search tree (AVL / red-black) - O(log n) search, insert and")
    lines.append("  delete while staying sorted.")
    lines.append("* B-tree index (used by databases like MySQL/PostgreSQL) - O(log n), efficient")
    lines.append("  for sorted and range queries on large data stored on disk.")
    lines.append("")
    lines.append("All three methods returned the same transaction for every lookup (verified).")

    report = "\n".join(lines)
    print(report)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as file:
        file.write(report + "\n")
    print(f"\nResults saved to {os.path.relpath(RESULTS_PATH)}")


if __name__ == '__main__':
    main()