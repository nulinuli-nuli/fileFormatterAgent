def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r') as f_in:
            lines = f_in.readlines()
        modified_lines = [line.strip() + ',' if not line.strip().endswith(',') else line.strip() for line in lines]
        with open(output_file, 'w') as f_out:
            f_out.write('\n'.join(modified_lines))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])