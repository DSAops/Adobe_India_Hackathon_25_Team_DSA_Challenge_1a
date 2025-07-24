import os
import json
import sys

def compare_json(json1, json2):
    """
    Recursively compares two JSON objects (dictionaries or lists) and returns a similarity score.
    """
    if type(json1) != type(json2):
        return 0.0

    if isinstance(json1, dict):
        all_keys = set(json1.keys()) | set(json2.keys())
        if not all_keys:
            return 1.0
        
        score = 0
        for key in all_keys:
            if key in json1 and key in json2:
                score += compare_json(json1[key], json2[key])
        return score / len(all_keys)

    if isinstance(json1, list):
        if not json1 and not json2:
            return 1.0
        # This is a simplification. A more complex list comparison might be needed
        # depending on whether the order of elements matters.
        # This simple version just checks for common elements.
        common_elements = 0
        # Create copies to avoid modifying original lists during comparison
        list2_copy = list(json2)
        for item1 in json1:
            for item2 in list2_copy:
                if compare_json(item1, item2) > 0.99: # using a threshold for float comparison
                    common_elements += 1
                    list2_copy.remove(item2)
                    break
        
        max_len = max(len(json1), len(json2))
        if max_len == 0:
            return 1.0
        return common_elements / max_len

    # For primitive types
    return 1.0 if json1 == json2 else 0.0

def compare_json_files(file1, file2):
    """Compares two JSON files and returns a similarity score."""
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading or parsing JSON files: {e}", file=sys.stderr)
        return 0.0

    return compare_json(data1, data2)

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    actual_dir = os.path.join(script_dir, 'actual')
    output_dir = os.path.join(script_dir, 'output')

    if not os.path.isdir(actual_dir):
        print(f"Error: Directory '{actual_dir}' not found.", file=sys.stderr)
        return
    if not os.path.isdir(output_dir):
        print(f"Error: Directory '{output_dir}' not found.", file=sys.stderr)
        return

    try:
        output_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.json')])
    except FileNotFoundError:
        print(f"Error: Could not list files in '{output_dir}'.", file=sys.stderr)
        return
        
    if not output_files:
        print(f"No JSON files found in the '{output_dir}' directory.")
        return

    total_accuracy = 0
    num_files_compared = 0

    print("--- Accuracy Test Results ---")
    for filename in output_files:
        output_file_path = os.path.join(output_dir, filename)
        actual_file_path = os.path.join(actual_dir, filename)

        if os.path.exists(actual_file_path):
            accuracy = compare_json_files(actual_file_path, output_file_path)
            total_accuracy += accuracy
            num_files_compared += 1
            print(f"  - Accuracy for {filename}: {accuracy:.2%}")
        else:
            print(f"  - Warning: No corresponding actual file for {filename}")

    if num_files_compared > 0:
        overall_accuracy = total_accuracy / num_files_compared
        print(f"\nOverall Model Accuracy: {overall_accuracy:.2%}")
    else:
        print("\nNo files were compared.")
    print("-----------------------------")


if __name__ == "__main__":
    main()