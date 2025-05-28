import logging
import json
import re
from typing import Optional, Dict, Any, List
from langchain_community.llms import Tongyi
from langchain.schema import SystemMessage, HumanMessage

class QWENDialogueAnalyzer:
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
        if not api_key:
            raise ValueError("DashScope API key is required.")
        if not model_name:
            raise ValueError("Qwen model name is required.")
        if not system_prompt:
            raise ValueError("System prompt is required.")

        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
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

            # 处理 JSON 响应
            response_text = response_text.strip()
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1).strip()
                logging.info("Extracted JSON block from markdown.")
            else:
                json_string = response_text
                first_brace = json_string.find('[')
                last_brace = json_string.rfind(']')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_string = json_string[first_brace:last_brace+1]
                    logging.info("Attempting to parse extracted array-like string.")
                else:
                    logging.warning("Could not reliably find JSON array structure in the response.")

            try:
                analysis_result = json.loads(json_string)
                if isinstance(analysis_result, list):
                    logging.info(f"Successfully parsed JSON array response from Qwen. Records found: {len(analysis_result)}")
                    return analysis_result
                else:
                    logging.error(f"Qwen response parsed but is not the expected list format. Type: {type(analysis_result)}")
                    return [{"error": "LLM response is not a JSON array", "raw_response": response_text}]

            except json.JSONDecodeError as json_err:
                logging.error(f"Failed to parse JSON response from Qwen: {json_err}")
                logging.error(f"Raw content causing error: {response_text}")
                return [{"error": f"Failed to parse JSON response: {json_err}", "raw_response": response_text}]

        except Exception as e:
            logging.error(f"An error occurred during Qwen API call or processing: {e}")
            import traceback
            traceback.print_exc()
            return [{"error": f"API call failed: {str(e)}", "raw_response": None}]
