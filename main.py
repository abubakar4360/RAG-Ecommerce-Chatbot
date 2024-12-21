from sentence_transformers import SentenceTransformer
import faiss
import os
import yaml
import warnings
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain_core._api.deprecation import LangChainDeprecationWarning
from utils.load_data import load_sql_data, format_data_for_chunks
from utils.vector_db import store_data_in_vector_db, query_vector_db
from utils.code_exec import extract_python_code, execute_code_and_generate_plot
from utils.query_exec import execute_sql_query, extract_sql_query, format_sql_result_to_table

# Ignore LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Set up your OpenAI API key
os.environ['OPENAI_API_KEY'] = config['openai_api_key']

db_path = config['db_path']
faiss_index_path = config['faiss_index_path']
plot_keywords = config['plot_keywords']
sql_keywords = config['sql_keywords']
prompt_file_path = config['prompt_file_path']
model_name = config['model_name']
llm_model_name = config['llm_model_name']


with open('prompt.txt', 'r') as f:
    system = f.read()
queries = [
    'SELECT product_id, product_name, description, price, category, brand, stock_quantity, rating, release_date, supplier FROM products',
    'SELECT review_id, product_id, rating, comment FROM reviews'
]

model = SentenceTransformer(model_name)

# Load SQL data
data = load_sql_data(db_path, queries)
formatted_data = format_data_for_chunks(data)

# Store in vector database
index = store_data_in_vector_db(model, formatted_data)

# Save the index
faiss.write_index(index, faiss_index_path)
print(f"Stored {len(formatted_data)} entries in the vector database.")

# Set up LangChain's conversation chain with memory
memory = ConversationBufferWindowMemory(k=3)
llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=os.getenv('OPENAI_API_KEY'))
conversation = ConversationChain(llm=llm, memory=memory)

# Interactive loop with conversation memory
while True:
    user_prompt = input('Enter your query: ')

    if user_prompt.lower() == 'exit':
        break
    else:
        retrieved_data = query_vector_db(user_prompt, model, index, formatted_data)
        context = "\n".join(retrieved_data)
        final_prompt = f"System: {system}\n\nContext: {context}\n\nUser query: {user_prompt}"
        response = conversation.run(input=final_prompt)

        sql_query = extract_sql_query(response)

        if any(keyword in user_prompt.lower() for keyword in plot_keywords):
            try:
                code = extract_python_code(response)
                image_path = execute_code_and_generate_plot(code)
                continue
            except Exception as e:
                print(f"Error processing plot request: {e}")

        elif sql_query:
            try:
                sql_result = execute_sql_query(sql_query)
                table = format_sql_result_to_table(sql_result)
                print("Generated Table:\n", table)
            except Exception as e:
                print(f"Error processing SQL request: {e}")

        else:
            print("Answer:", response)
