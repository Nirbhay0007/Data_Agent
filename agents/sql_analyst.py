
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from utils.llm_pick import pick_llm
from models.schema import AgentSchema


# ---------------------------------- AI AGENT CODE ------------------
def curate_question(state : AgentSchema) -> AgentSchema:
          user_question = state.user_question  # because it is pydantic model object

          llm = pick_llm(level="low") 

          response = llm.invoke(f"Cureate the following  question   :  {user_question}")
          state.curated_ques = response.content
          return state



def prompt_querry_context(state : AgentSchema) -> AgentSchema:
          curated_question = state.curated_ques

          llm = pick_llm(level="medium")
          
          