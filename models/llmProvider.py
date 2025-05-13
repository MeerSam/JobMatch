from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def get_llm(self):
        """Return a LangChain LLM object"""
        pass