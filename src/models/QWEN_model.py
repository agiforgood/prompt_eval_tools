import logging
from typing import Optional, Dict, Any, List
from langchain_community.llms import Tongyi
from langchain.schema import SystemMessage, HumanMessage
from .base_model import BaseDialogueAnalyzer
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import ProxyError, ConnectionError, Timeout

class QWENDialogueAnalyzer(BaseDialogueAnalyzer):
    """使用 Qwen 模型分析对话内容的类"""

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
        初始化 QWENDialogueAnalyzer。

        Args:
            api_key (str): DashScope API 密钥
            model_name (str): 要使用的 Qwen 模型名称
            system_prompt (str): 用于指导模型的系统提示
            base_url (Optional[str]): API 基础 URL
            temperature (float): 控制生成文本的随机性
            max_output_tokens (int): 生成响应的最大 token 数
        """
        super().__init__(model_name, system_prompt, temperature, max_output_tokens)
        
        if not api_key:
            raise ValueError("DashScope API key is required.")

        self.api_key = api_key
        self.base_url = base_url

        try:
            # 初始化 LangChain 的 Tongyi
            self.llm = Tongyi(
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens,
                api_key=self.api_key,
                base_url=self.base_url
            )
            logging.info(f"Qwen client initialized successfully for model: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to initialize Qwen client: {e}")
            raise ConnectionError(f"Failed to initialize Qwen client: {e}")

    @retry(
        stop=stop_after_attempt(3),  # 最多重试3次
        wait=wait_exponential(multiplier=1, min=4, max=10),  # 指数退避重试
        retry=retry_if_exception_type((ProxyError, ConnectionError, Timeout)),  # 只对特定错误重试
        reraise=True  # 重试失败后抛出异常
    )
    def analyze_dialogue(self, user_prompt_content: str) -> List[Dict[str, Any]]:
        """
        使用 Qwen 模型分析提供的对话内容。

        Args:
            user_prompt_content (str): 包含对话内容的 JSON 字符串

        Returns:
            List[Dict[str, Any]]: 分析结果的列表，每个字典代表一条记录。如果出错则返回包含错误信息的字典列表。
        """
        # 准备系统提示
        final_system_prompt = self.system_prompt.replace("{{TRANSACTION}}", user_prompt_content)

        # 构建提示
        prompt = f"{final_system_prompt}\n\n请根据系统提示中的信息进行分析并按要求格式输出。"

        try:
            logging.info(f"Sending request to Qwen model: {self.model_name}")
            response = self.llm.invoke(prompt)

            # 提取响应内容
            response_text = str(response)
            logging.info("Received response from Qwen.")
            
            # 使用基类的方法处理响应
            return self._process_response(response_text)

        except (ProxyError, ConnectionError, Timeout) as e:
            logging.error(f"Network error occurred: {str(e)}")
            raise  # 让重试机制处理这些错误

        except Exception as e:
            logging.error(f"An error occurred during Qwen API call or processing: {e}")
            import traceback
            traceback.print_exc()
            return [{"error": f"API call failed: {str(e)}", "raw_response": None}]

    def _analyze_dialogue(self, user_prompt_content: str) -> str:
        """
        使用 Qwen 模型分析提供的对话内容。

        Args:
            user_prompt_content (str): 包含对话内容的 JSON 字符串

        Returns:
            str: 模型的原始响应文本
        """
        # 准备系统提示
        final_system_prompt = self.system_prompt.replace("{{TRANSACTION}}", user_prompt_content)

        # 构建提示
        prompt = f"{final_system_prompt}\n\n请根据系统提示中的信息进行分析并按要求格式输出。"

        try:
            logging.info(f"Sending request to Qwen model: {self.model_name}")
            response = self.llm.invoke(prompt)
            logging.info("Received response from Qwen.")
            
            # 返回原始响应文本
            return str(response)

        except Exception as e:
            logging.error(f"An error occurred during Qwen API call: {e}")
            raise  # 让基类的重试机制处理错误
