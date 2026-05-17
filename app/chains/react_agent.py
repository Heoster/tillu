import time
import re
import json
import traceback
from typing import Any, Dict, List, Optional

from app.config import settings
from app.chains.base import BaseChain, ChainType
from app.tools.registry import ToolRegistry
from app.providers.llm_router import TilluLLM
from app.utils.logging import get_logger

logger = get_logger("react_agent_chain")


class ReActAgentChain(BaseChain):
    """
    Autonomous ReAct Tool Agent
    Uses LLM to reason and dynamically execute tools (productivity, search, weather, crypto, notion, youtube, memory)
    """
    
    chain_type = ChainType.REACT_AGENT
    description = "Fully autonomous multi-step reasoning and dynamic tool execution agent"
    
    def __init__(self):
        super().__init__()
        # Use TilluLLM for unified, failover-safe routing
        self.llm = TilluLLM(task="analysis", temperature=0.1)
        
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        query = input_data.get("text", "")
        user_id = (context or {}).get("user_id") or settings.single_user_id
        
        # Get tool list
        tools = ToolRegistry.get_all_tools()
        tools_description = "\n".join([
            f"- {tool.metadata.name}: {tool.metadata.description}. Parameters schema: {json.dumps(tool.metadata.parameters)}"
            for tool in tools
        ])
        tool_names = ", ".join([tool.metadata.name for tool in tools])
        
        scratchpad = ""
        max_iterations = 3
        current_iteration = 0
        executed_actions = []
        
        logger.info(f"Starting ReAct Agent loop for query: {query[:100]}... (Tools: {len(tools)})")
        
        system_prompt = f"""You are TILLU, an extremely smart, capable, and helpful AI assistant that operates as a premium, professional agent.
You have access to a suite of real-world tools listed below. Your task is to reason step-by-step and execute the correct tools to get accurate, real-world data and take actions for the user.

AVAILABLE TOOLS:
{tools_description}

FORMAT INSTRUCTIONS:
To solve the task, you MUST use the following format for each step:
Thought: Describe your reasoning about the query and what action to take next.
Action: the name of the tool to use (must be one of: {tool_names})
Action Input: the parameters for the tool in JSON format (e.g., {{"param1": "val1"}})

Once you have gathered enough information to fully answer the query, or if no tools are needed, use this format:
Thought: I have all the information I need / No tools are needed.
Final Answer: The final, polished response for the user in Hindi/Hinglish (matching their language/style). Keep it friendly, premium, and professional.

IMPORTANT RULES:
- If a tool requires `user_id`, use: "{user_id}"
- Never make up tool names. Only use registered tools.
- Output exactly one Thought + Action + Action Input, or Thought + Final Answer block in each turn.
- Stop immediately after writing 'Final Answer: ...'
"""

        while current_iteration < max_iterations:
            current_iteration += 1
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Task: {query}\n\nScratchpad:\n{scratchpad}\n\nContinue the reasoning process."}
            ]
            
            try:
                # Call LLM
                response = await self.llm.ainvoke(messages)
                output = response.content
                logger.info(f"ReAct Iteration {current_iteration} LLM response:\n{output}")
                
                # Check for Final Answer
                if "Final Answer:" in output:
                    final_ans = output.split("Final Answer:")[-1].strip()
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    return {
                        "response": {
                            "type": "text",
                            "content": final_ans,
                            "structured_data": {
                                "iterations": current_iteration,
                                "tools_called": executed_actions
                            }
                        },
                        "personality_mode": "analytical",
                        "chain": self.chain_type.value,
                        "model": response.response_metadata.get("model", "unknown"),
                        "latency_ms": elapsed_ms,
                        "tokens_used": 0,
                        "sources": []
                    }
                
                # Parse action & action input
                action_match = re.search(r"Action:\s*([a-zA-Z0-9_-]+)", output)
                action_input_match = re.search(r"Action\s*Input:\s*(\{.*?\})", output, re.DOTALL)
                
                if action_match and action_input_match:
                    tool_name = action_match.group(1).strip()
                    tool_input_str = action_input_match.group(1).strip()
                    
                    try:
                        tool_input = json.loads(tool_input_str)
                    except Exception as je:
                        logger.warning(f"Failed to parse JSON parameters: {tool_input_str} - {je}")
                        scratchpad += f"\n{output}\nObservation: Error parsing tool parameters JSON. Ensure valid JSON key/value pairs."
                        continue
                    
                    # Fetch tool
                    tool = ToolRegistry.get(tool_name)
                    if tool:
                        # Auto-inject user_id if needed
                        if tool.metadata.requires_auth and "user_id" not in tool_input:
                            tool_input["user_id"] = user_id
                            
                        logger.info(f"Executing tool {tool_name} with params {tool_input}")
                        executed_actions.append(tool_name)
                        
                        try:
                            tool_result = await tool.execute(**tool_input)
                            logger.info(f"Tool {tool_name} result: {tool_result}")
                            
                            # Append to scratchpad
                            scratchpad += f"\n{output}\nObservation: {json.dumps(tool_result)}"
                        except Exception as te:
                            logger.error(f"Tool {tool_name} execution error: {te}")
                            scratchpad += f"\n{output}\nObservation: Tool returned an error: {str(te)}"
                    else:
                        scratchpad += f"\n{output}\nObservation: Tool '{tool_name}' is not registered. Try a different tool."
                else:
                    # If LLM didn't match the format exactly, append instructions and try again
                    scratchpad += f"\n{output}\nObservation: Format incorrect. You must write exactly one 'Thought:' and either an 'Action:' / 'Action Input:' pair or a 'Final Answer:'."
                    
            except Exception as e:
                logger.error(f"ReAct iteration failed: {e}\n{traceback.format_exc()}")
                break
                
        # Final fallback - execute direct query using conversation rules
        try:
            logger.warning("ReAct loop limit reached or error. Running fallback direct call.")
            messages = [
                {"role": "system", "content": f"You are TILLU, an AI presence. Provide a friendly, premium direct response in Hindi/Hinglish to the user's query.\nContext gathered: {scratchpad}"},
                {"role": "user", "content": query}
            ]
            response = await self.llm.ainvoke(messages)
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "response": {
                    "type": "text",
                    "content": response.content,
                    "structured_data": {"fallback": True, "iterations": current_iteration}
                },
                "personality_mode": "neutral",
                "chain": self.chain_type.value,
                "model": response.response_metadata.get("model", "fallback"),
                "latency_ms": elapsed_ms,
                "tokens_used": 0,
                "sources": []
            }
        except Exception as fe:
            logger.error(f"ReAct fallback failed: {fe}")
            return {
                "response": {
                    "type": "text",
                    "content": "Mujhe maaf kijiye, abhi is request ko process karne mein thodi problem aa rahi hai. Kripya thodi der baad fir se try karein.",
                    "structured_data": {"error": str(fe)}
                },
                "personality_mode": "neutral",
                "chain": self.chain_type.value,
                "model": "error",
                "latency_ms": int((time.time() - start_time) * 1000),
                "tokens_used": 0,
                "sources": []
            }
