import logging
from typing import Optional, Dict, Any, List
from anthropic import Anthropic
from .base_model import BaseDialogueAnalyzer

class ClaudeDialogueAnalyzer(BaseDialogueAnalyzer):
    """使用 Claude 模型分析对话内容的类"""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        system_prompt: str,
        base_url: Optional[str] = None,
        temperature: float = 0,
        max_output_tokens: int = 8192
    ):
        """
        初始化 ClaudeDialogueAnalyzer。

        Args:
            api_key (str): Anthropic API 密钥
            model_name (str): 要使用的 Claude 模型名称
            system_prompt (str): 用于指导模型的系统提示
            base_url (Optional[str]): API 基础 URL
            temperature (float): 控制生成文本的随机性
            max_output_tokens (int): 生成响应的最大 token 数
        """
        super().__init__(model_name, system_prompt, temperature, max_output_tokens)
        
        if not api_key:
            raise ValueError("Anthropic API key is required.")

        self.api_key = api_key
        self.base_url = base_url

        try:
            # 初始化 Anthropic 客户端
            self.client = Anthropic(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logging.info(f"Claude client initialized successfully for model: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to initialize Claude client: {e}")
            raise ConnectionError(f"Failed to initialize Claude client: {e}")

    def _analyze_dialogue(self, user_prompt_content: str) -> str:
        """
        使用 Claude 模型分析提供的对话内容。

        Args:
            user_prompt_content (str): 包含对话内容的 JSON 字符串

        Returns:
            str: 模型的原始响应文本
        """
        # 准备系统提示
        final_system_prompt = self.system_prompt.replace("{{TRANSACTION}}", user_prompt_content)

        try:
            logging.info(f"Sending request to Claude model: {self.model_name}")
            
            # 调用 Claude API
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_output_tokens,
                temperature=self.temperature,
                system=final_system_prompt,
                messages=[
                    {"role": "user", "content": "请根据系统提示中的信息进行分析并按要求格式输出。"}
                ]
            )
            
            logging.info("Received response from Claude.")
            
            # 返回原始响应文本
            return response.content[0].text

        except Exception as e:
            logging.error(f"An error occurred during Claude API call: {e}")
            raise  # 让基类的重试机制处理错误



