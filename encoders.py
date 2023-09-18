import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

def find_max_similarity(list1, list2):
    # Convert the lists of vectors to PyTorch tensors
    list1 = torch.tensor(list1)
    list2 = torch.tensor(list2)

    # Calculate cosine similarity between all pairs of vectors
    similarity_matrix = F.cosine_similarity(list1.unsqueeze(1), list2.unsqueeze(0), dim=2)

    # Find the index at which each job description vector had maximum similarity
    max_similarity_values = torch.max(similarity_matrix, dim=1).values

    # Find the average max similarity value for all job description vectors
    res = torch.mean(max_similarity_values, dim=0)

    return res.detach().numpy()

def encode(parsed_dict):
    # Initialize a SentenceTransformer model using the 'sentence-transformers/sentence-t5-base' model.
    model = SentenceTransformer('sentence-transformers/sentence-t5-base')
    
    # Initialize an empty dictionary to store encoded data.
    encoded_dict = {}

    # Iterate through the keys (entries) in the 'parsed_dict'.
    for pd_key in tqdm(parsed_dict.keys()):
        entry = parsed_dict[pd_key]
        for section in entry.keys():
            # Check if the 'entry' is not already a key in the 'encoded_dict'.
            if not pd_key in encoded_dict.keys():
                # If not, create an empty dictionary for the 'entry'.
                encoded_dict[pd_key] = {}
            
            # Use the SentenceTransformer model to encode the text in 'parsed_dict[entry][section]'.
            encoded_dict[pd_key][section] = np.array(model.encode(parsed_dict[pd_key][section]))
    
    # Return the 'encoded_dict' containing the encoded representations of the parsed text.
    return encoded_dict


