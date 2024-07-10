# import streamlit as st
# import json

# # Streamlit app title
# st.title('Input to Dictionary/JSON App')

# # Input fields
# key = st.text_input('Enter the key:', '')
# value = st.text_input('Enter the value:', '')

# # Button to add the key-value pair to the dictionary
# if st.button('Add to Dictionary'):
#     # Initialize the dictionary if it doesn't exist
#     if 'data_dict' not in st.session_state:
#         st.session_state.data_dict = {}
    
#     # Add the key-value pair
#     st.session_state.data_dict[key] = value
    
#     # Display the current dictionary
#     st.write('Current Dictionary:', st.session_state.data_dict)
    
#     # Optionally, convert the dictionary to a JSON string and display it
#     json_str = json.dumps(st.session_state.data_dict)
#     st.write('JSON String:', json_str)

import streamlit as st
import json

# Streamlit app title
st.title('Elasticsearch Query Builder')

# Input fields for the query parameters
title = st.text_input('Enter title:', '')
content = st.text_input('Enter content:', '')
status = st.text_input('Enter status:', '')
publish_date = st.date_input('Enter publish date (gte):')

# Button to build the query
if st.button('Build Query'):
    # Construct the query dictionary
    query_dict = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"title": title}},
                    {"match": {"content": content}}
                ],
                "filter": [
                    {"term": {"status": status}},
                    {"range": {"publish_date": {"gte": str(publish_date)}}}
                ]
            }
        }
    }
    
    # Display the query dictionary
    st.write('Query Dictionary:', query_dict)
    
    # Convert the dictionary to a JSON string and display it
    json_str = json.dumps(query_dict, indent=2)
    st.write('JSON Query:', json_str)