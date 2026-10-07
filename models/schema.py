from typing import Annotated,Optional, Literal, List
from pydantic import BaseModel,Field
from operator import add



class AgentSchema(BaseModel):
    user_question: str = Field(..., description="The original question asked by the user")
    messages: List = Field(default_factory=list, description="Conversation history")
    curated_ques: Optional[str] = Field(default=None, description="Curated user question")
    prompt_query_context: Optional[str] = Field(default=None, description="Detailed prompt with SQL DB context")
    is_safe_sql: Optional[Literal["Yes", "No"]] = Field(default=None, description="Indicates whether the generated SQL query is safe")
    comments: Optional[str] = Field(default=None, description="Judge comments on the query")
    generated_sql_query: Optional[str] = Field(default=None, description="Generated SQL query")
    sql_query_execution_result: Optional[str] = Field(default=None, description="Result of executing the SQL query")
    final_answer: Optional[str] = Field(default=None, description="Final user-facing answer")

          
class JudgeSchema(BaseModel):
    answer : Literal["Yes","No"] = Field(..., description="Indicates whether the generated SQL query is safe to execute or not")
    comments : str = Field(..., description="Additional comments or feedback from the judge regarding the SQL querry")
