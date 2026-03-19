import base64
import requests

from src.config import APIConfig
from src.logger_config import logger

def pdf2markdown(file_bytes):
    try:
        logger.info("使用PaddleOCR-VL解析PDF")

        headers = {
            "Authorization": f"token {APIConfig.PADDLE_OCR_TOKEN}",
            "Content-Type": "application/json"
        }

        # For PDF documents, set `fileType` to 0; for images, set `fileType` to 1
        payload = {
            "file": base64.b64encode(file_bytes).decode("ascii"),
            "fileType": 0,
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": True,
        }

        response = requests.post(APIConfig.PADDLE_OCR_API_URL, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"pdf_to_markdown,请求失败, status_code={response.status_code}")
            return None

        result = response.json()["result"]

        markdown = ''
        for i, res in enumerate(result["layoutParsingResults"]):
            markdown += res["markdown"]["text"]
            for img_path, img in res["markdown"]["images"].items():
                markdown = markdown.replace(img_path, img)
        return markdown
    except Exception as e:
        logger.error(f"pdf_to_markdown,请求失败, {e}")
    return None
