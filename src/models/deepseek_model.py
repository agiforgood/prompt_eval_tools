import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI
from .base_model import BaseDialogueAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DeepSeekDialogueAnalyzer(BaseDialogueAnalyzer):
    """使用 DeepSeek 模型分析对话内容的类"""

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
        初始化 DeepSeekDialogueAnalyzer。

        Args:
            api_key (str): DeepSeek API 密钥
            model_name (str): 要使用的 DeepSeek 模型名称
            system_prompt (str): 用于指导模型的系统提示
            base_url (Optional[str]): API 基础 URL
            temperature (float): 控制生成文本的随机性
            max_output_tokens (int): 生成响应的最大 token 数
        """
        super().__init__(model_name, system_prompt, temperature, max_output_tokens)
        
        if not api_key:
            raise ValueError("DeepSeek API key is required.")

        self.api_key = api_key
        self.base_url = base_url

        try:
            # 初始化 OpenAI 客户端，指向 DeepSeek API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logging.info(f"DeepSeek client initialized successfully for model: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to initialize DeepSeek client: {e}")
            raise ConnectionError(f"Failed to initialize DeepSeek client: {e}")

    def _analyze_dialogue(self, user_prompt_content: str) -> str:
        """
        使用 DeepSeek 模型分析提供的对话内容。

        Args:
            user_prompt_content (str): 包含对话内容的 JSON 字符串

        Returns:
            str: 模型的原始响应文本
        """
        # 准备系统提示
        final_system_prompt = self.system_prompt.replace("{{TRANSACTION}}", user_prompt_content)

        # 构建消息列表
        messages = [
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": "请根据系统提示中的信息进行分析并按要求格式输出。"}
        ]

        try:
            logging.info(f"Sending request to DeepSeek model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens
            )
            logging.info("Received response from DeepSeek.")
            
            # 返回原始响应文本
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"An error occurred during DeepSeek API call: {e}")
            raise  # 让基类的重试机制处理错误