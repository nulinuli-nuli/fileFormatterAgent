def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()
        
        truncated_lines = lines[:40]

        with open(output_file, 'w') as outfile:
            outfile.writelines(truncated_lines)
    
    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.")
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])