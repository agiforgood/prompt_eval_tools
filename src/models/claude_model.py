import logging
from typing import Optional, Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain.schema import SystemMessage, HumanMessage
from .base_model import BaseDialogueAnalyzer

class ClaudeDialogueAnalyzer(BaseDialogueAnalyzer):
    """使用 Claude 模型分析对话内容的类"""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        system_prompt: str,
        base_url: Optional[str] = "https://api.oaipro.com/",
        temperature: float = 0,
        max_output_tokens: int = 8192
    ):
        """
        初始化 ClaudeDialogueAnalyzer。

        Args:
            api_key (str): Anthropic API 密钥
            model_name (str): 要使用的 Claude 模型名称
            system_prompt (str): 用于指导模型的系统提示
            base_url (str): API 基础 URL
            temperature (float): 控制生成文本的随机性
            max_output_tokens (int): 生成响应的最大 token 数
        """
        super().__init__(model_name, system_prompt, temperature, max_output_tokens)
        
        if not api_key:
            raise ValueError("Anthropic API key is required.")

        self.api_key = api_key
        self.base_url = base_url

        try:
            # 初始化 LangChain 的 ChatAnthropic
            self.llm = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens,
                base_url=self.base_url
            )
            logging.info(f"Claude client initialized successfully for model: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to initialize Claude client: {e}")
            raise ConnectionError(f"Failed to initialize Claude client: {e}")

    def analyze_dialogue(self, user_prompt_content: str) -> List[Dict[str, Any]]:
        """
        使用 Claude 模型分析提供的对话内容。

        Args:
            user_prompt_content (str): 包含对话内容的 JSON 字符串

        Returns:
            List[Dict[str, Any]]: 分析结果的列表，每个字典代表一条记录。如果出错则返回包含错误信息的字典列表。
        """
        # 准备系统提示
        final_system_prompt = self.system_prompt.replace("{{TRANSACTION}}", user_prompt_content)

        # 构建 LangChain 消息列表
        user_message = "请根据系统提示中的信息进行分析并按要求格式输出。"
        messages = [
            SystemMessage(content=final_system_prompt),
            HumanMessage(content=user_message)
        ]

        try:
            logging.info(f"Sending request to Claude model: {self.model_name}")
            response = self.llm.invoke(messages)

            # 提取响应内容
            response_text = ""
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                logging.warning(f"Warning: Unexpected response type from Claude invoke: {type(response)}")
                response_text = str(response)

            logging.info("Received response from Claude.")
            
            # 使用基类的方法处理响应
            return self._process_response(response_text)

        except Exception as e:
            logging.error(f"An error occurred during Claude API call or processing: {e}")
            import traceback
            traceback.print_exc()
            return [{"error": f"API call failed: {str(e)}", "raw_response": None}]



