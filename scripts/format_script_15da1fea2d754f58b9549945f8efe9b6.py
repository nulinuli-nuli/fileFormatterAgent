def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r') as f_in:
            lines = f_in.readlines()

        converted_lines = []
        for line in lines:
            line = line.strip()
            if line.isdigit():
                converted_lines.append(str(int(line) + 1) + '\n')
            else:
                converted_lines.append('N/A\n')

        with open(output_file, 'w') as f_out:
            f_out.writelines(converted_lines)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])