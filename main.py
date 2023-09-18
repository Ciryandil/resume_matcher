import os
from pdfminer.high_level import extract_text
import json
from parsers import parse_section
from encoders import encode, find_max_similarity
import pandas as pd
from tqdm import tqdm 
from config import CONFIG_DICT
import numpy as np

parsed_resumes = {}
parsed_jds = {}



job_descs = pd.read_csv(CONFIG_DICT['job_description_csv'])
extracted_resumes = json.load(open(CONFIG_DICT['extracted_resumes']))
# The mapping dictionary stores the mapping from each important resume section title to the corresponding resume section titles
mapping_dict = json.load(open(CONFIG_DICT['mapping_dict']))

# Parsing job description sections
print("Parsing JDs...")
for i in tqdm(range(job_descs.shape[0])):
    job_description = json.loads(job_descs['model_response'][i])

    for jd_key in list(job_description.keys()):
        if not i in parsed_jds.keys():
            parsed_jds[i] = {}
        if isinstance(job_description[jd_key], list):
            parsed_jds[i][jd_key] = job_description[jd_key]
        else:
            parsed_jds[i][jd_key] = parse_section(job_description[jd_key], jd_key)

# Parsing resume sections
print("Parsing resumes...")
for resume_i in tqdm(list(extracted_resumes.keys())):
    resume = extracted_resumes[resume_i]

    for r_key in list(resume.keys()):
        if not resume_i in parsed_resumes.keys():
            parsed_resumes[resume_i] = {}
        parsed_resumes[resume_i][r_key] = parse_section(resume[r_key], r_key)

# Encoding the parsed job descriptions and resumes
print("Encoding JDs...")
encoded_jds = encode(parsed_jds)
print("Encoding resumes...")
encoded_resumes = encode(parsed_resumes)

print("Matching resumes to JDs...")
# Calculating similarity between first jd_lim JDs and all resumes
result_dict = {}
# If a portion of the resumes have already been examined and matches stored, we add on to them
if os.path.exists(CONFIG_DICT['result_dict']):
    result_dict = json.load(open(CONFIG_DICT['result_dict']))

for jd_key in tqdm(list(encoded_jds.keys())[CONFIG_DICT['jd_range_left']:CONFIG_DICT['jd_range_right']]):
    for resume_i in list(encoded_resumes.keys()):
        # Initializing sim_arr to store the maximum similarity for each section of the JD
        sim_arr = []
        for key in list(encoded_jds[jd_key].keys()):
            # If the section is not part of our mapping dictionary, or has no text content, we skip it
            if len(encoded_jds[jd_key][key]) == 0:
                continue
            if key not in list(mapping_dict.keys()):
                continue
            # Obtain the best corresponding resume sections and create a list of all their parsed parts
            corr_keys = mapping_dict[key]
            resume_encoding_corr = None
            for r_key in corr_keys:
                if r_key in list(encoded_resumes[resume_i].keys()):
                    if resume_encoding_corr is None and encoded_resumes[resume_i][r_key].shape[0] != 0:
                        resume_encoding_corr = encoded_resumes[resume_i][r_key]
                    else:
                        if encoded_resumes[resume_i][r_key].shape[0] == 0:
                            continue
                        resume_encoding_corr = np.concatenate((resume_encoding_corr, encoded_resumes[resume_i][r_key]))
            # If the list is empty, then we score that resume 0 on that particular JD section
            if resume_encoding_corr is None or resume_encoding_corr.shape[0] == 0:
                sim_arr.append(0)
            else:
                sim_arr.append(find_max_similarity(encoded_jds[jd_key][key], resume_encoding_corr))

        # We store the mean of the cosine similarity scores across all JD sections as our final score
        if not jd_key in result_dict:
            result_dict[jd_key] = {}
            result_dict[jd_key][resume_i] = sum(sim_arr) / len(sim_arr)
        else:
            result_dict[jd_key][resume_i] = sum(sim_arr) / len(sim_arr)

# Sort the results in order of decreasing similarity score
for jd in result_dict.keys():
    result_dict[jd] = dict(sorted(result_dict[jd].items(), key=lambda item: item[1], reverse=True))

top5_matches = {}
# Find the top5 matches for each JD
for jd in result_dict.keys():
    if not jd in top5_matches.keys():
        top5_matches[jd] = []
    resume_list = list(result_dict[jd].keys())
    top5_matches[jd] = resume_list[:5]

print("Saving results...")
# Save the results of top 5 matches as csv
result_df = pd.DataFrame.from_dict(top5_matches)
result_df = result_df.transpose()
result_df.to_csv(CONFIG_DICT['top5_result'], index=True, header=True)

# Save the complete results as a json for later examination/reuse
json_result = json.dumps(result_dict)
with open(CONFIG_DICT['result_dict'], 'w') as f:
    f.write(json_result)

print("Finished!")
