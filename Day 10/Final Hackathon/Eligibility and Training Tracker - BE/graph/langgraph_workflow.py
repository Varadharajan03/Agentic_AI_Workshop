from langgraph.graph import StateGraph, END, START
from agents import jd_parser, eligibility_mapper, gap_analyzer, training_rag_agent
from typing import List, Optional, Dict
from pydantic import BaseModel
from langchain_core.documents import Document

class TrackerState(BaseModel):
    file_path: Optional[str] = None
    jd_criteria: Optional[Dict] = None
    eligibility_results: Optional[List[Dict]] = None
    gap_analysis: Optional[List[Dict]] = None
    training_plan_docs: Optional[List[Document]] = None
    training_recommendations: Optional[List[Dict]] = None
    notification_summary: Optional[List[Dict]] = None  # will be updated separately

graph = StateGraph(state_schema=TrackerState)

graph.add_node("JDParser", jd_parser.run)
graph.add_node("EligibilityMapper", eligibility_mapper.run)
graph.add_node("GapAnalyzer", gap_analyzer.run)
graph.add_node("TrainingRecommender", training_rag_agent.run)

# ✅ New workflow ends after training
graph.add_edge(START, "JDParser")
graph.add_edge("JDParser", "EligibilityMapper")
graph.add_edge("EligibilityMapper", "GapAnalyzer")
graph.add_edge("GapAnalyzer", "TrainingRecommender")
graph.add_edge("TrainingRecommender", END)  # ends here

workflow = graph.compile()
