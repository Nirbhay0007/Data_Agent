import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from langchain_core.messages import HumanMessage, AIMessage
from utils.database import DatabaseUtils
from utils.llm_pick import pick_llm
from models.schema import AgentSchema,JudgeSchema
from langgraph.graph import StateGraph,START,END



# ---------------------------------- AI AGENT CODE ------------------
def curate_question(state: AgentSchema) -> AgentSchema:
    llm = pick_llm("medium")
    
    prompt = f"""You are a question refiner. Your task is to rephrase the user's question into a clean, concise, single-sentence query for database search.
IMPORTANT: Return ONLY the refined question string. Do NOT include any greetings, explanations, SQL queries, or markdown formatting.

User Question: {state.user_question}"""

    response = llm.invoke(prompt).content.strip()
    # Remove surrounding quotes if the LLM wrapped them
    state.curated_ques = response.strip('"').strip("'")
    return state



def prompt_query_context(state : AgentSchema) -> AgentSchema:
          curated_question = state.curated_ques

          db_obj = DatabaseUtils({'host':os.environ['DB_HOST'],'port':os.environ['DB_PORT'],'user':os.environ['DB_USER'],'password':os.environ['DB_PASSWORD'],'database':os.environ['DB_NAME']})
          
          schema_info = db_obj.schema_details("public",5)
          



          # Constructing the prompt query for the agent to generate the SQL query
          prompt = f"""
          You are an SQL analyst agent. Your task is to convert the user's natural language 
          query into Postgres SQL query that can be executed on the database. You are provided 
          with the user's original query and the schema details of the database, including
          table names, column names, data types, and sample data for each table so that 
          you can understand the structure of the database and generate an accurate SQL query.
          Unless user explicitly asks for specific number of rows, always limit the output to 10 rows.
          Note - Just generate the SQL query without any explanation or additional text because
          this query will be executed directly on the database. So, the output should be SQL
          ready to be executed without any modifications.  
          
          User's Original Query: {curated_question}

          Database Schema Details:
          {schema_info}
            
          """  
          state.prompt_query_context = prompt
          return state



def clean_sql(query: str) -> str:
    query = query.strip()
    if query.startswith("```sql"):
        query = query[6:]
    elif query.startswith("```"):
        query = query[3:]
    if query.endswith("```"):
        query = query[:-3]
    return query.strip()
# Node for sequal query generation

def generate_sql(state:AgentSchema) -> AgentSchema:
    llm = pick_llm("high")
    generated_sql_query = llm.invoke(state.prompt_query_context).content
    state.generated_sql_query = clean_sql(generated_sql_query)
    return state


    

# Is safe node 
          
def is_safe_sql(state:AgentSchema) -> AgentSchema:

          sql_query = state.generated_sql_query
          llm = pick_llm("medium")
          llm_judge = llm.with_structured_output(JudgeSchema)

          prompt = f"""
                You are an SQL Judge for data security. Your task is to determine whether the SQL query is 
                safe or not. The SQL query should only be used for data retrieval and should not modify the 
                database in any way. Neither the SQL query nor the prompt should contain any SQL commands that can modify the
                database, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or any other commands that can change
                the structure or content of the database. If the SQL query is safe, respond with 'Yes' otherwise respond with 
                'No'. Additionally, provide comments explaining your decision.
                Here is the SQL query : {sql_query}"""


          response = llm_judge.invoke(prompt).model_dump()
          state.is_safe_sql = response['answer']
          state.comments = response['comments']

          return state



# Cancel SQL Query Node


def cancel_sql_query(state:AgentSchema) -> AgentSchema:

        comments = state.comments
        state.final_answer = f"The SQL query is unsafe to execute. Reason: {comments}"
        state.messages = state.messages + [AIMessage(content=f"The SQL query is unsafe to execute. Reason: {comments}")]
        return state




# Execute SQL Query Node

def  execute_sql(state:AgentSchema) -> AgentSchema:
          
          sql_query = state.generated_sql_query

          connection = {
            "host":os.environ['DB_HOST'],
            "port":os.environ['DB_PORT'],
            "user":os.environ['DB_USER'],
            "password":os.environ['DB_PASSWORD'],
            "database":os.environ['DB_NAME']
          }

          obj = DatabaseUtils(connection)

          execution_result = obj.execute_query(sql_query)  # execute the SQL query on the database
          
          result = execution_result
          state.sql_query_execution_result = result
          return state

# Representation node 
def represent_final_answer(state:AgentSchema)->AgentSchema:
    curated_question = state.curated_ques
    execution_result = state.sql_query_execution_result
    
    llm = pick_llm("low") 

    prompt = f"""
    You are an SQL analyst agent. Your task is to provide a final answer to the user based on the
    execution result of the SQL query and the user's original question. The final answer should be
    concise, clear, and directly address the user's query. Avoid including any SQL code or technical
    details in the final answer. The final answer should be in a user-friendly format that is easy to
    understand. If the execution result is empty or does not provide a clear answer to the user's question, explain this in the final answer. \n
    Here is the execution result: {execution_result} \n
    Here is the user's original question: {curated_question}
    """
    final_answer = llm.invoke(prompt)
    state.final_answer = final_answer.content
    state.messages = state.messages + [AIMessage(content=f"{final_answer.content}")]
    return state 


# ------------------------------------------- graph builder -------------------------------------------
sql_agent_graph = StateGraph(AgentSchema)

# Nodes
sql_agent_graph.add_node("curate_question", curate_question)
sql_agent_graph.add_node("prompt_query_context", prompt_query_context)
sql_agent_graph.add_node("generate_sql", generate_sql)
sql_agent_graph.add_node("is_safe_sql", is_safe_sql)
sql_agent_graph.add_node("cancel_sql_query", cancel_sql_query)
sql_agent_graph.add_node("execute_sql", execute_sql)
sql_agent_graph.add_node("represent_final_answer", represent_final_answer)

# Linear Edges
sql_agent_graph.add_edge(START, "curate_question")
sql_agent_graph.add_edge("curate_question", "prompt_query_context")
sql_agent_graph.add_edge("prompt_query_context", "generate_sql")
sql_agent_graph.add_edge("generate_sql", "is_safe_sql")

# Conditional Edge Function
def is_safe_sql_edge(state: AgentSchema) -> str:
    # Use state.is_safe_sql to match schema and node output
    is_safe = state.is_safe_sql

    if is_safe and is_safe.lower() == "yes":
        return "execute_sql"
    else:
        return "cancel_sql_query"  # Matches registered node name

sql_agent_graph.add_conditional_edges(
    "is_safe_sql",
    is_safe_sql_edge,
    {
        "execute_sql": "execute_sql",
        "cancel_sql_query": "cancel_sql_query"
    }
)

# Terminal / Continuation Edges
sql_agent_graph.add_edge("cancel_sql_query", END)
sql_agent_graph.add_edge("execute_sql", "represent_final_answer")
sql_agent_graph.add_edge("represent_final_answer", END)

# Compile the Graph
sql_analyst = sql_agent_graph.compile()


# if __name__ == "__main__":
    # Visualize from the compiled graph
    # from IPython.display import Image, display

    # img = Image(sql_analyst.get_graph().draw_mermaid_png())

    # with open("sql_analyst_graph.png", "wb") as f:
    #     f.write(img.data)
    
# if __name__ == "__main__":
#     input_schema = {
#         "user_question": "what are the different types of payments methods we have in our database ?"
#     }
    
#     result = sql_analyst.invoke(input_schema)
    
#     print("\n" + "="*50)
#     print("FINAL ANSWER:")
#     print("="*50)
#     print(result["final_answer"])

input_schema = {
        "user_question": "what are the different types of payments methods we have in our database ?"
}

# executing the grpah

sql_analyst_response = sql_analyst.invoke(input_schema)
print("===========================================================================================")
print("\n")
print("Messages: ")
print(sql_analyst_response['messages'])
print("===========================================================================================")
print("\n")
print("Generated SQL Query: ")
print(sql_analyst_response['generated_sql_query'])
print("===========================================================================================")
print("\n")
print("SQL Query Execution Result: ")
print(sql_analyst_response['sql_query_execution_result'])
print("===========================================================================================")
print("\n")
print("Prompt Query Context: ")
print(sql_analyst_response['prompt_query_context'])
print("\n")
print("Curated Question: ")
print(sql_analyst_response['curated_ques'])
print("===========================================================================================")
print("\n")
print("Final Answer: ")
print(sql_analyst_response['final_answer'])
