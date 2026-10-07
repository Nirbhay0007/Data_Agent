
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from langchain_core.messages import HumanMessage
from utils.database import DatabaseUtils
from utils.llm_pick import pick_llm
from models.schema import AgentSchema


# ---------------------------------- AI AGENT CODE ------------------
def curate_question(state : AgentSchema) -> AgentSchema:
          user_question = state.user_question  # because it is pydantic model object

          llm = pick_llm(level="low") 

          response = llm.invoke(f"Cureate the following  question   :  {user_question}")
          state.curated_ques = response.content
          state.messages  = state.messages+ [HumanMessage(content=f"{response.content}")] 
          return state



def prompt_querry_context(state : AgentSchema) -> AgentSchema:
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
          
          
          state.prompt_querry_context = prompt

          llm = pick_llm("medium")

          response = llm.invoke(prompt)
          state.generated_sql_querry = response.content 
          return state


# Is safe node 
          
def is_safe_sql(state:AgentSchema) -> AgentSchema:

          sql_query = state.generated_sql_querry