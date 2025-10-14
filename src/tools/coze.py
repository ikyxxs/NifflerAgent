import json
import tempfile

import requests
from streamlit.runtime.uploaded_file_manager import UploadedFile

from src.config import APIConfig


def upload_file_to_coze(file: UploadedFile):
    """上传文件到COZE"""

    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file.flush()
        tmp_file_path = tmp_file.name

        url = "https://api.coze.cn/v1/files/upload"
        headers = {
            "Authorization": f'Bearer {APIConfig.COZE_TOKEN}'
        }

        files = {
            "file": (
                file.name,  # 上传后的文件名（可自定义）
                open(tmp_file_path, "rb"),  # 以二进制模式打开文件
                file.type  # 文件的 MIME 类型
            )
        }

        try:
            response = requests.post(url=url, headers=headers, files=files)

            print("COZE上传文件:", response.json())
            return response.json()['data']['id']
        except Exception as e:
            print(f"上传文件到COZE,请求失败: {str(e)}")
        finally:
            # 确保文件被关闭
            if 'files' in locals() and files['file'][1].closed is False:
                files['file'][1].close()


def pdf2markdown(file_id: str):
    """将pdf转换为markdown"""

    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": f'Bearer {APIConfig.COZE_TOKEN}'
    }
    data = {
        "workflow_id": "7551781385305751561",
        "parameters": {
            "pdf": json.dumps({
                "file_id": file_id
            })           
        }
    }

    try:
        response = requests.post(url=url, headers=headers, json=data)
        print("PDF转Markdown:", response.json())
        return json.loads(response.json()['data'])['markdown']
    except Exception as e:
        print(f"PDF转Markdown,请求失败: {str(e)}")


def markdown2pdf(markdown: str):
    """将markdown转换为pdf"""

    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": f'Bearer {APIConfig.COZE_TOKEN}'
    }
    data = {
        "workflow_id": "7549518115056484415",
        "parameters": {
            "markdown": markdown
        }
    }

    try:
        response = requests.post(url=url, headers=headers, json=data)
        print("Markdown转PDF:", response.json())
        return json.loads(response.json()['data'])['pdf']
    except Exception as e:
        print(f"Markdown转PDF,请求失败: {str(e)}")


# if __name__ == "__main__":
#     print(pdf2markdown("7555864394627088411"))
