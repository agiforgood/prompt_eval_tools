import logging
import json
import re
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import ProxyError, ConnectionError, Timeout

class BaseDialogueAnalyzer(ABC):
    """所有对话分析器的基础类"""

    def __init__(
        self,
        model_name: str,
        system_prompt: str,
        temperature: float = 0,
        max_output_tokens: int = 8192
    ):
        """
        初始化基础对话分析器。

        Args:
            model_name (str): 模型名称
            system_prompt (str): 系统提示词
            temperature (float): 温度参数
            max_output_tokens (int): 最大输出 token 数
        """
        if not model_name:
            raise ValueError("Model name is required.")
        if not system_prompt:
            raise ValueError("System prompt is required.")

        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        # 创建 logs 目录（如果不存在）
        self.logs_dir = "logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def _save_raw_output(self, response_text: str) -> None:
        """
        保存 AI 的原始输出到文件。

        Args:
            response_text (str): AI 的原始输出文本
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.logs_dir, f"{self.model_name}_raw_output_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response_text)
            logging.info(f"Raw output saved to {filename}")
        except Exception as e:
            logging.error(f"Failed to save raw output: {e}")

    def _extract_json_from_response(self, response_text: str) -> str:
        """
        从响应文本中提取 JSON 数据。

        Args:
            response_text (str): AI 的原始响应文本

        Returns:
            str: 提取的 JSON 字符串
        """
        # 首先尝试从 <schema> 标签中提取
        schema_match = re.search(r'<schema>\s*([\s\S]*?)\s*</schema>', response_text, re.DOTALL)
        if schema_match:
            json_string = schema_match.group(1).strip()
            logging.info("Extracted JSON from <schema> tags.")
            return json_string

        # 如果没有找到 <formal> 标签，尝试从 markdown 代码块中提取
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group(1).strip()
            logging.info("Extracted JSON block from markdown.")
            return json_string

        # 如果都没有找到，尝试直接提取数组结构
        json_string = response_text.strip()
        first_brace = json_string.find('[')
        last_brace = json_string.rfind(']')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_string = json_string[first_brace:last_brace+1]
            logging.info("Attempting to parse extracted array-like string.")
            return json_string

        logging.warning("Could not reliably find JSON array structure in the response.")
        return json_string

    def _process_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        处理 AI 响应并返回解析后的结果。

        Args:
            response_text (str): AI 的原始响应文本

        Returns:
            List[Dict[str, Any]]: 解析后的结果列表
        """
        # 保存原始输出
        self._save_raw_output(response_text)

        # 提取 JSON
        json_string = self._extract_json_from_response(response_text)

        try:
            analysis_result = json.loads(json_string)
            if isinstance(analysis_result, list):
                logging.info(f"Successfully parsed JSON array response. Records found: {len(analysis_result)}")
                return analysis_result
            else:
                logging.error(f"Response parsed but is not the expected list format. Type: {type(analysis_result)}")
                return [{"error": "LLM response is not a JSON array", "raw_response": response_text}]

        except json.JSONDecodeError as json_err:
            logging.error(f"Failed to parse JSON response: {json_err}")
            logging.error(f"Raw content causing error: {response_text}")
            return [{"error": f"Failed to parse JSON response: {json_err}", "raw_response": response_text}]

    @retry(
        stop=stop_after_attempt(3),  # 最多重试3次
        wait=wait_exponential(multiplier=1, min=4, max=10),  # 指数退避重试
        retry=retry_if_exception_type((ProxyError, ConnectionError, Timeout)),  # 只对特定错误重试
        reraise=True  # 重试失败后抛出异常
    )
    def analyze_dialogue(self, user_prompt_content: str) -> List[Dict[str, Any]]:
        """
        分析对话内容。这是一个抽象方法，需要被子类实现。

        Args:
            user_prompt_content (str): 用户提示内容

        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        try:
            # 调用子类实现的 _analyze_dialogue 方法
            response_text = self._analyze_dialogue(user_prompt_content)
            return self._process_response(response_text)
        except (ProxyError, ConnectionError, Timeout) as e:
            logging.error(f"Network error occurred: {str(e)}")
            raise  # 让重试机制处理这些错误
        except Exception as e:
            logging.error(f"An error occurred during API call or processing: {str(e)}")
            return [{"error": f"API call failed: {str(e)}", "raw_response": str(e)}]

    @abstractmethod
    def _analyze_dialogue(self, user_prompt_content: str) -> str:
        """
        实际执行对话分析的方法。需要被子类实现。

        Args:
            user_prompt_content (str): 用户提示内容

        Returns:
            str: 模型的原始响应文本
        """
        pass 