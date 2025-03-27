def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r') as f:
            data = f.read().strip()
        if data:
            converted_data = ",".join(data.split())
        else:
            converted_data = ""
        with open(output_file, 'w') as f:
            f.write(converted_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])