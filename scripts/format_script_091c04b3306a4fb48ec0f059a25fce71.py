def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r') as f_in:
            lines = f_in.readlines()
        truncated_lines = lines[:10]
        with open(output_file, 'w') as f_out:
            f_out.writelines(truncated_lines)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])