"""
에이전트 프롬프트 템플릿

각 에이전트의 시스템 프롬프트를 정의합니다.
"""

from multi_agent.prompts.agent_prompts import (
    SEARCH_AGENT_PROMPT,
    MARKET_AGENT_PROMPT,
    ANALYSIS_AGENT_PROMPT,
    POSITION_AGENT_PROMPT,
    REPORT_AGENT_PROMPT,
    EXPORT_AGENT_PROMPT,
    AGENT_PROMPTS,
    get_agent_prompt
)

from multi_agent.prompts.supervisor_prompt import (
    SUPERVISOR_PROMPT,
    RESULT_COMBINATION_PROMPT,
    get_supervisor_prompt,
    get_result_combination_prompt
)

__all__ = [
    'SEARCH_AGENT_PROMPT',
    'MARKET_AGENT_PROMPT',
    'ANALYSIS_AGENT_PROMPT',
    'POSITION_AGENT_PROMPT',
    'REPORT_AGENT_PROMPT',
    'EXPORT_AGENT_PROMPT',
    'AGENT_PROMPTS',
    'get_agent_prompt',
    'SUPERVISOR_PROMPT',
    'RESULT_COMBINATION_PROMPT',
    'get_supervisor_prompt',
    'get_result_combination_prompt'
]
