"""
Agent Orchestrator — the brain of FoodMemory.

Takes a user message, classifies intent, calls the right tools
(MCP, memory engine, LLM), and returns a contextual response.

Will be implemented in Phase 5.
"""


class AgentOrchestrator:
    def __init__(self):
        pass

    async def process(self, user_id: str, message: str) -> dict:
        """Process a user message and return a response."""
        # TODO: Phase 5
        # 1. Send message to LLM for intent classification
        # 2. Based on intent, call MCP / memory engine
        # 3. Build context-rich prompt with memory
        # 4. Get LLM response
        # 5. Return structured response
        return {
            "reply": "Orchestrator not yet implemented",
            "intent": "unknown",
        }
