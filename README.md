# Resume Matcher

A tool for finding the best matching resumes for a given Job Description

## Setup:

1. **Download the resume dataset**: \
    https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset

2. **Download the JD dataset**: \
    https://huggingface.co/datasets/jacob-hugging-face/job-descriptions/viewer/default/train?row=0

3. **Install required libraries**

    ```
    pip install -r requirements.txt
    ```

4. **Set up your configuration details in config.py (use the given ones as reference)**

     - **job_description_csv** should hold the path to the JD dataset CSV

     - **resume_data_dir** should hold the path to the data directory (archive/data/data/) of the resume dataset containing the resumes

     - **extracted_resumes** should specify the output path for storing the json file with extracted resume sections from the dataset

     - **top5_result** should specify the output path for the csv file storing top 5 matches for each JD

     - **result_dict** should specify the output path for the JSON file holding the complete matching results
     
     - **mapping_dict** should be the path to the mapping_dict.json file in the repo
     
     - **resume_headers** should be the path to the resume_header.json file in the repo

     - **jd_range_left** and **jd_range_right** specify the beginning and ending list indexes for the sublist of the JD list for which u wish to do matching


## Execution 

1. **Run the extraction script to extract sections from all resumes**

    ```
    python extract_resume_sections.py
    ```

2. **Run the main script for matching resumes to JDs**

    ```
    python main.py
    ```
3. **The top5 matches for each JD will be found in the file top5.csv. For complete matching results check out result_dict.json**