import argparse
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('QtAgg')

def command_line_arguments():
  parser = argparse.ArgumentParser(
    description="Parse the raw data output from the Instek GDS-1054B "
                "oscilloscope and generate a structured CSV file for easy "
                "analysis and visualization.")

  # Add the arguments
  parser.add_argument("input_file", type=str,
    help="file with raw data from instek oszilloscope")
  parser.add_argument("output_file", type=str,
    help="csv file to create from the input_file")

  # Parse the arguments
  args = parser.parse_args()
  
  return args.input_file, args.output_file


    
def main():

  input_file, output_file = command_line_arguments()
  # Open the binary file in read-binary mode
  with open(input_file, 'rb') as file:
    data = file.read()
    print(data)

    pattern = b'Vertical Scale,'
    start_index = data.find(pattern)
    
    if start_index == -1:
      try:
        print(f"Pattern '{pattern.decode('utf-8')}' not found.")
      except UnicodeDecodeError:
        print("Pattern not found and could not be decoded.")
      return
        

    start_index += len(pattern)
    
    # Find the next semicolon after the pattern
    end_index = data.find(b';', start_index)
    
    if end_index == -1:
      try:
        print(f"Semicolon not found after: {pattern.decode('utf-8')}.")
      except UnicodeDecodeError:
        print("Semicolon not found and could not be decoded.")
      return

 
    # Extract bytes between the pattern and the next semicolon
    try:
      vertical_scale_str = data[start_index:end_index].decode('utf-8')
    except UnicodeDecodeError:
      print("vertical scale string could not be decoded")
      return
 
    # Convert the extracted string to a floating-point number
    try:
      vertical_scale = float(vertical_scale_str)
      print("Floating-point number found:", vertical_scale)
    except ValueError:
      print("Failed to convert the extracted bytes to a float.")
      return

    pattern = b'Waveform Data;\x0a#'
    start_index = data.find(pattern)
    
    if start_index == -1:
      try:
        print(f"Pattern '{pattern.decode('utf-8')}' not found.")
      except UnicodeDecodeError:
        print("Pattern not found and could not be decoded.")
      return

    start_index += len(pattern)
    length_numdigits_str = chr(data[start_index])

    try:
      length_numdigits = int(length_numdigits_str)
      print(f"Number of digits for length: {length_numdigits}")
    except ValueError:
      print("Failed to convert number of digits for length")
      return

    start_index += 1

    try:
      length_str = data[start_index:start_index+length_numdigits].decode('utf-8')
    except UnicodeDecodeError:
      print("data length string could not be decoded")
      return

    try:
      length = int(length_str)
      print(f"Length of Data: {length}")
    except ValueError:
      print("Failed to read the data length!")
      return
    
    start_index += length_numdigits

    double_list = [int.from_bytes(data[i:i+2], byteorder='big', signed=True)
      * vertical_scale/25 for i in range(start_index, start_index+length, 2)]

    print(double_list)

    with open(output_file, "w", newline="") as file:
      writer = csv.writer(file)
      for item in double_list:
        writer.writerow([item])

    y_series = pd.Series(double_list)

    # Plot the data
    y_series.plot(title="One-Dimensional Plot", xlabel="X (Consecutive)", ylabel="Y (Values)")
    plt.show() 

if __name__ == "__main__":
  main()

