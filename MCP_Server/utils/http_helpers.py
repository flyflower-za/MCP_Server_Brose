"""
HTTP辅助函数
"""
import requests
from typing import Optional, Dict, Any
from utils.logger import logger


def fetch_url(
    url: str,
    timeout: int = 30,
    verify_ssl: bool = False,
    headers: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    通用URL获取函数

    Args:
        url: 目标URL
        timeout: 超时时间
        verify_ssl: 是否验证SSL证书
        headers: 自定义请求头

    Returns:
        Response对象

    Raises:
        requests.RequestException: 请求失败
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    if headers:
        default_headers.update(headers)

    try:
        logger.info(f"Fetching URL: {url}")
        response = requests.get(
            url,
            headers=default_headers,
            timeout=timeout,
            verify=verify_ssl
        )
        response.raise_for_status()
        return response

    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching URL: {url}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        raise


def download_content(url: str, **kwargs) -> bytes:
    """
    下载URL内容

    Args:
        url: 目标URL
        **kwargs: 传递给fetch_url的参数

    Returns:
        下载的内容字节
    """
    response = fetch_url(url, **kwargs)
    return response.content
