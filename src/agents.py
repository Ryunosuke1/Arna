from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination, ExternalTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dataclasses import dataclass
import yaml
from typing import List, Dict, Optional
import requests
import json
import asyncio

from tools import (
    CodeStructureTools, WebTools, MathTools,
    QuestionTool, QuestionManager, Question
)
from chat_ui import ChatUI

class SharedData:
    def __init__(self):
        self.planning: bool = False
        self.coding: bool = False
        self.team: Optional[RoundRobinGroupChat] = None
        self.text_termination: Optional[TextMentionTermination] = None
        self.external_termination: Optional[ExternalTermination] = None
        self.base_url: str = ""
        self.api_key: str = ""
        self.model_name: str = "deepseek-r1"
        self.question_manager = QuestionManager()
        self.chat_ui: Optional[ChatUI] = None

@dataclass
class CodingAssistant:
    api_key: str
    base_url: str = ""
    model_name: str = "deepseek-r1"
    name: str = "coding assistant"
    desc: str = "A coding assistant that can generate python code structure based on the specification."
    max_tokens: int = 4096
    context_length: int = 8192

    def get_model_info(self) -> dict:
        """モデル情報を取得"""
        return {
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "unknown"
        }

class CodingAssistants:
    def __init__(self, planning_agents: list[CodingAssistant], coding_agent: CodingAssistant, api_key: str, base_url: str, shared_data: SharedData):
        self.api_key = api_key
        self.base_url = base_url
        self.coding_agent_config = coding_agent
        self.planning_agents = [
            AssistantAgent(
                name=agent.name,
                model_client=OpenAIChatCompletionClient(
                    api_key=agent.api_key,
                    base_url=agent.base_url,
                    model=agent.model_name,
                    model_info=agent.get_model_info()
                )
            ) for agent in planning_agents
        ]
        self.coding_assistants = AssistantAgent(
            name="coding agent",
            model_client=OpenAIChatCompletionClient(
                api_key=coding_agent.api_key,
                base_url=coding_agent.base_url,
                model=coding_agent.model_name,
                model_info=coding_agent.get_model_info()
            )
        )
        self.shared_data = shared_data

        # ツールの初期化
        self.code_tools = CodeStructureTools()
        self.web_tools = WebTools()
        self.math_tools = MathTools()
        self.question_tool = QuestionTool()

    async def plan(self, specification: str):
        """
        AIエージェントと協力してPythonコードの構造を計画する
        
        Args:
            specification: コードの仕様
        """
        system_message = """
        You have access to the following tools to help with code planning and implementation:

        1. Code Structure Tools:
        - create_project(name, description): Create a new project structure
        - add_function(name, description, parent_path?): Add a function definition
        - add_parameter(function_path, name, description): Add a parameter to a function
        - add_return(function_path, description): Add return value description
        - add_logic(function_path, description): Add function logic description
        - show_structure(): Display current code structure
        - show_summary(): Display project summary
        - save_yaml(file_path): Save structure to YAML
        - load_yaml(file_path): Load structure from YAML
        - generate_code(output_path): Generate Python code

        2. Web Tools:
        - search(query, limit=5): Perform web search
        - scrape(url): Extract content from webpage

        3. Math Tools:
        - evaluate(expression): Calculate mathematical expression
        - solve_equation(equation): Solve mathematical equation
        - integrate(expression): Perform integration
        - differentiate(expression): Perform differentiation

        4. Question Tools:
        - ask_question(agent_name: str, category: str, content: str): Ask a question to the user
        Available categories:
        - LIBRARY: Questions about library selection and usage
        - ALGORITHM: Questions about algorithm implementation
        - UI: Questions about UI design and implementation
        - ARCHITECTURE: Questions about code architecture
        - OTHERS: Other questions

        Follow this process:
        1. Understand the specification by asking detailed questions about:
           - Required libraries and their versions
           - Algorithm choices and implementations
           - UI requirements and design
           - Code architecture and patterns
        2. Wait for user's answers to your questions
        3. Create project structure with clear name and description
        4. Design functions with proper documentation
        5. Add parameters and return types
        6. Describe logic for each function
        7. Review and verify the structure
        8. Generate final code
        
        The YAML structure should follow:
        name: <name>
        description: <description>
        code_structure:
          - function:
              name: <name>
              description: <description>
              parameters:
                - name: <name>
                  description: <description>
              returns:
                description: <description>
              logic:
                description: <description>
              code_structure:
                - nested functions/classes
        """

        if self.shared_data.team is None or self.shared_data.planning:
            critic_agent = AssistantAgent(
                "critic",
                model_client=OpenAIChatCompletionClient(
                    api_key=self.coding_agent_config.api_key,
                    base_url=self.coding_agent_config.base_url,
                    model=self.coding_agent_config.model_name,
                    model_info=self.coding_agent_config.get_model_info()
                ),
                system_message="Provide constructive feedback. Respond with 'APPROVE' when your feedbacks are addressed"
            )
            
            user_message = f"Make a plan to generate python code based on the specification with the user. specification: {specification}"
            agents = self.planning_agents + [self.coding_assistants, critic_agent]
            
            self.shared_data.text_termination = TextMentionTermination("APPROVE")
            self.shared_data.external_termination = ExternalTermination()
            self.shared_data.team = RoundRobinGroupChat(
                agents,
                termination_condition=self.shared_data.text_termination | self.shared_data.external_termination
            )
            self.shared_data.planning = True

        async for message in self.run(system_message=system_message, user_message=user_message):
            yield message
            if isinstance(message, TaskResult):
                self.shared_data.planning = False
                last_message = message.messages[-1]
                try:
                    yaml_data = yaml.safe_load(last_message["content"])
                    # 生成された構造をツールに設定
                    await self.code_tools.create_project(
                        yaml_data["name"],
                        yaml_data["description"]
                    )
                    if "code_structure" in yaml_data:
                        await self._process_code_structure(yaml_data["code_structure"])
                except Exception as e:
                    print(f"Error processing YAML: {str(e)}")
                break
            elif not self.shared_data.planning:
                self.shared_data.external_termination.set()
                break

    async def run(self, system_message: str, user_message: str):
        """チームチャットを実行"""
        async for message in self.shared_data.team.run_stream(task=f"{system_message}\n{user_message}"):
            # メッセージがTaskResultの場合は処理をスキップ
            if isinstance(message, TaskResult):
                yield message
                continue

            # エージェントからの質問を処理
            if (
                isinstance(message, dict) 
                and "role" in message 
                and message["role"] == "assistant"
                and "content" in message
            ):
                content = message["content"]
                if "ask_question" in content.lower():
                    try:
                        agent_name = message.get("name", "Agent")
                        # カテゴリと質問内容を抽出
                        category = "OTHERS"  # デフォルトカテゴリ
                        for cat in self.question_tool.categories:
                            if cat.lower() in content.lower():
                                category = cat
                                break
                        
                        await self.question_tool.ask_question(
                            agent_name,
                            category,
                            content
                        )
                        
                        # 次の質問をUIに表示
                        if self.shared_data.chat_ui:
                            question = await self.shared_data.question_manager.get_next_question()
                            if question:
                                await self.shared_data.chat_ui.add_question(question)
                        continue
                    except Exception as e:
                        print(f"Error processing question: {str(e)}")
                        if self.shared_data.chat_ui:
                            await self.shared_data.chat_ui.add_user_message(
                                f"Error processing question: {str(e)}"
                            )

                # 通常のメッセージを表示
                if self.shared_data.chat_ui:
                    formatted_content = f"{message.get('name', 'Agent')}: {content}"
                    await self.shared_data.chat_ui.add_user_message(formatted_content)

            yield message

    async def _process_code_structure(self, structure: List[Dict]):
        """コード構造を再帰的に処理"""
        for item in structure:
            if isinstance(item, dict):
                if "function" in item:
                    func = item["function"]
                    await self.code_tools.add_function(
                        func["name"],
                        func["description"],
                        ""  # トップレベル
                    )
                    # パラメータの処理
                    if "parameters" in func:
                        for param in func["parameters"]:
                            await self.code_tools.add_parameter(
                                func["name"],
                                param["name"],
                                param["description"]
                            )
                    # 戻り値の処理
                    if "returns" in func:
                        await self.code_tools.add_return(
                            func["name"],
                            func["returns"]["description"]
                        )
                    # ロジックの処理
                    if "logic" in func:
                        await self.code_tools.add_logic(
                            func["name"],
                            func["logic"]["description"]
                        )
                    # ネストされた構造の処理
                    if "code_structure" in func:
                        await self._process_code_structure(func["code_structure"])
