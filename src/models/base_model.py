import logging
import json
import re
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

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
        # 首先尝试从 <formal> 标签中提取
        formal_match = re.search(r'<formal>\s*([\s\S]*?)\s*</formal>', response_text, re.DOTALL)
        if formal_match:
            json_string = formal_match.group(1).strip()
            logging.info("Extracted JSON from <formal> tags.")
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

    @abstractmethod
    def analyze_dialogue(self, user_prompt_content: str) -> List[Dict[str, Any]]:
        """
        分析对话内容。

        Args:
            user_prompt_content (str): 用户提示内容

        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        pass 