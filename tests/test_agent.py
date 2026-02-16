import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.models.base_model import DeepEvalBaseLLM
from app.agent import get_agent_response
from langchain_groq import ChatGroq

class GroqJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        return self.model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        return self.model.invoke(prompt).content

    def get_model_name(self):
        return "Llama 3.3 (Groq)"
groq_judge = GroqJudge()


def test_return_policy_accuracy():
    """
    Test if the agent correctly retrieves the 30-day return window.
    """
    input_query = "How many days do I have to return my order?"
    actual_output = get_agent_response(input_query)
    retrieval_context = ["The return window is 30 days from the delivery date."]
    
    test_case = LLMTestCase(
        input=input_query,
        actual_output=actual_output,
        retrieval_context=retrieval_context
    )
    
    # Define Metrics
    # Faithfulness: Does the answer stick to the context?
    faithfulness = FaithfulnessMetric(
        threshold=0.7,
        model=groq_judge,
        include_reason=True
    )
    
    # Relevancy: Did it answer the specific question asked?
    relevancy = AnswerRelevancyMetric(
        threshold=0.7,
        model=groq_judge,
        include_reason=True
    )
    
    # 5. Assert (Pass/Fail)
    print(f"\n--- Agent Answer: {actual_output} ---")
    assert_test(test_case, [faithfulness, relevancy])