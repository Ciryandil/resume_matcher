import os
from pdfminer.high_level import extract_text
import json
from parsers import extract_sections
from config import CONFIG_DICT


data_dir = CONFIG_DICT['resume_data_dir']
resume_headers = json.load(open(CONFIG_DICT['resume_headers']))

# Iteratively reading and extracting the respective sections of each resume into the sections_dir dict
sections_dir = {}
for dir in os.listdir(data_dir):
  dir_path = os.path.join(data_dir, dir)
  for resume in os.listdir(dir_path):
    resume_path = os.path.join(dir_path, resume)
    resume_text = extract_text(resume_path)
    sections_found = extract_sections(resume_text, resume_headers)
    sections_dir[resume] = sections_found

# Save the extracted resumes as json for further use
resumes_json = json.dumps(sections_dir)
with open(CONFIG_DICT['extracted_resumes'], 'w') as f:
  f.write(resumes_json)

