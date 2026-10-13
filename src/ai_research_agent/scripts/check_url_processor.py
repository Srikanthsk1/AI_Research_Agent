"""Small manual check for extracting and ranking URLs."""

from ai_research_agent.executor.result_processor import ResultProcessor


text = """
Title: LangGraph
URL: https://langchain.com/langgraph

Title: CrewAI
URL: https://crewai.com
"""

urls = ResultProcessor.extract_urls(text)

print(urls)
