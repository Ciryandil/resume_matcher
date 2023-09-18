import os
import re
from pdfminer.high_level import extract_text

def find_sections(text):
  # Define the regular expression pattern: sequence of one or two words beginning with \n and ending with an option : and \n
  pattern = r'\n([A-Za-z]+\s?[A-Za-z]+(?=:?\n))'

  # Find all matching substrings and their indices and lengths
  matches = [(match.group(0), match.start(), len(match.group(0))) for match in re.finditer(pattern, text)]
  all_matches = []
  # Print the matches, their start indices, and lengths
  for match, start_idx, length in matches:
      all_matches.append(match[1:])

  return all_matches

def extract_sections(text, resume_headers):
  
  # Initialize dictionaries to store header information and sections.
  headers_dict= {}
  sections_dict = {}

  # Iterate through a predefined list of 'resume_headers'.
  for header in resume_headers:

    # Define three possible header formats with different delimiters.
    header_1 = '\n' + header + '\n'
    header_2 = '\n' + header + ':'
    header_3 = '\n' + header + ':\n'

    # Check if any of the header formats are found in the 'text'.
    if text.find(header_1) != -1:
      # If found, store header information in 'headers_dict'.
      headers_dict[header] = {'length': len(header_1), 'index': text.find(header_1)}
    elif text.find(header_2) != -1:
      headers_dict[header] = {'length': len(header_2), 'index': text.find(header_2)}
    elif text.find(header_3) != -1:
      headers_dict[header] = {'length': len(header_3), 'index': text.find(header_3)}

  # Sort the 'headers_dict' based on the 'index' values.
  sorted_headers_dict = dict(sorted(headers_dict.items(), key=lambda item: item[1]['index']))

  # Extract the list of sorted headers.
  headers = list(sorted_headers_dict.keys())
  
  # Iterate through the sorted headers to extract sections of text between them.
  for i in range(len(headers)):
    header = headers[i]
    if i < len(headers) - 1:
      next_header = headers[i+1]

      # Store the section of text between the current header and the next header.
      sections_dict[header] = text[sorted_headers_dict[header]['index']+sorted_headers_dict[header]['length']:
                                   sorted_headers_dict[next_header]['index']]
    else:
      # For the last header, store the text from the header to the end.
      sections_dict[header] = text[sorted_headers_dict[header]['index']+sorted_headers_dict[header]['length']:]

  # Return the 'sections_dict' containing extracted sections.
  return sections_dict

def parse_section(section_text, section_key):
  section_items = None

  # Check if the 'section_text' contains neither periods nor commas.
  if section_text.find('.') == -1 and section_text.find(',') == -1:
    # Split the 'section_text' into items using newline characters.
    section_items = section_text.split('\n')

  # Check if there are no periods but there are commas or semicolons, or if 'Skill' is in 'section_key'.
  elif (section_text.find('.') == -1 and (section_text.find(',') != -1 or section_text.find(';') != -1)) or 'Skill' in section_key:
    # Split the 'section_text' using commas or semicolons as delimiters.
    section_items = re.split(r'[,;]', section_text)
  
  # Check if the 'section_text' contains periods.
  elif section_text.find('.') != -1:
    # Split the 'section_text' into items using periods as delimiters.
    section_items = section_text.split('.')
  else:
    # If none of the above conditions are met, treat the entire 'section_text' as a single item.
    section_items = [section_text]

  # Clean up each item in 'section_items' by removing excess whitespace and newline characters.
  section_items = [re.sub('\n+', ' ', item.strip()) for item in section_items if item.strip() != '' and item.strip() != '\n' and item.strip() != '\t']

  # Return the cleaned 'section_items'.
  return section_items

