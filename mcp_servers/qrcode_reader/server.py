"""
二维码识别器MCP服务器
支持从图片URL或Base64数据中识别二维码内容
"""
import io
import base64
from typing import Dict, Any, Optional

import requests
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException
from PIL import Image

from mcp_servers.qrcode_reader.models import (
    QRCodeReadRequest,
    QRCodeReadResponse,
    BatchQRCodeReadRequest,
    BatchQRCodeReadResponse
)
from utils.logger import logger
from utils.http_helpers import fetch_url


# 创建路由器
router = APIRouter(tags=["QR Code Reader"])


def decode_base64_image(base64_data: str) -> Image.Image:
    """
    解码Base64图片数据

    Args:
        base64_data: Base64编码的图片数据

    Returns:
        PIL Image对象
    """
    try:
        # 移除可能的data URL前缀
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]

        # 解码Base64
        image_data = base64.b64decode(base64_data)

        # 创建PIL Image对象
        image = Image.open(io.BytesIO(image_data))

        return image
    except Exception as e:
        raise ValueError(f"Base64图片解码失败: {str(e)}")


def download_image_from_url(url: str) -> Image.Image:
    """
    从URL下载图片

    Args:
        url: 图片URL地址

    Returns:
        PIL Image对象
    """
    try:
        response = fetch_url(url)
        image = Image.open(io.BytesIO(response.content))
        return image
    except Exception as e:
        raise ValueError(f"下载图片失败: {str(e)}")


def read_qrcode_from_image(image: Image.Image) -> Dict[str, Any]:
    """
    从图片中识别二维码

    Args:
        image: PIL Image对象

    Returns:
        包含识别结果的字典
    """
    try:
        # 转换为RGB模式（如果需要）
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 转换为OpenCV格式（numpy array）
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 创建QRCode检测器
        detector = cv2.QRCodeDetector()

        # 检测并解码二维码
        data, bbox, _ = detector.detectAndDecode(opencv_image)

        if not data:
            return {
                "success": False,
                "qr_data": None,
                "format": None,
                "error": "未检测到二维码"
            }

        # 转换bbox格式
        bbox_list = None
        if bbox is not None:
            bbox_list = bbox.tolist()

        metadata = {
            "type": "QR_CODE",
            "bbox": bbox_list,
            "detected": True
        }

        return {
            "success": True,
            "qr_data": data,
            "format": "QR_CODE",
            "error": None,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"二维码识别失败: {str(e)}")
        return {
            "success": False,
            "qr_data": None,
            "format": None,
            "error": f"二维码识别失败: {str(e)}",
            "metadata": None
        }


def process_qrcode_request(request: QRCodeReadRequest) -> Dict[str, Any]:
    """
    处理二维码识别请求

    Args:
        request: 二维码识别请求

    Returns:
        包含识别结果的字典
    """
    try:
        image = None

        # 优先级1: 从图片URL获取
        if request.image_url:
            logger.info(f"从URL识别二维码: {request.image_url}")
            image = download_image_from_url(request.image_url)

        # 优先级2: 从Base64数据获取
        elif request.image_base64:
            logger.info("从Base64数据识别二维码")
            image = decode_base64_image(request.image_base64)

        # 优先级3: 文本输入（特殊格式）
        elif request.text_input:
            logger.info("处理文本形式的二维码")
            # 这里可以处理特殊的文本格式，比如markdown中的二维码描述
            # 目前直接返回文本内容
            return {
                "success": True,
                "qr_data": request.text_input,
                "format": "text",
                "error": None,
                "metadata": {"source": "text_input"}
            }

        else:
            return {
                "success": False,
                "qr_data": None,
                "format": None,
                "error": "必须提供image_url、image_base64或text_input之一",
                "metadata": None
            }

        # 识别二维码
        if image:
            result = read_qrcode_from_image(image)
            logger.info(f"二维码识别{'成功' if result['success'] else '失败'}")
            return result

    except ValueError as e:
        logger.error(f"请求处理失败: {str(e)}")
        return {
            "success": False,
            "qr_data": None,
            "format": None,
            "error": str(e),
            "metadata": None
        }
    except Exception as e:
        logger.error(f"处理二维码识别请求时发生错误: {str(e)}")
        return {
            "success": False,
            "qr_data": None,
            "format": None,
            "error": f"处理请求时发生错误: {str(e)}",
            "metadata": None
        }


@router.post("/read", response_model=QRCodeReadResponse)
async def read_qrcode(request: QRCodeReadRequest):
    """
    识别单个二维码

    支持三种输入方式：
    1. 图片URL (image_url)
    2. Base64编码的图片数据 (image_base64)
    3. 文本形式 (text_input) - 用于特殊格式的二维码描述
    """
    result = process_qrcode_request(request)
    return QRCodeReadResponse(**result)


@router.post("/read/batch", response_model=BatchQRCodeReadResponse)
async def read_batch_qrcodes(request: BatchQRCodeReadRequest):
    """
    批量识别多个二维码
    """
    results = []
    success_count = 0
    failed_count = 0

    for req in request.requests:
        result = process_qrcode_request(req)
        results.append(QRCodeReadResponse(**result))

        if result["success"]:
            success_count += 1
        else:
            failed_count += 1

    return BatchQRCodeReadResponse(
        results=results,
        total_success=success_count,
        total_failed=failed_count
    )


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "QR Code Reader",
        "version": "1.0.0"
    }


def get_info():
    """获取服务器信息"""
    return {
        "name": "QR Code Reader",
        "version": "1.0.0",
        "description": "从图片URL或Base64数据中识别二维码内容",
        "endpoints": [
            {"path": "/qrcode/read", "method": "POST", "description": "识别单个二维码"},
            {"path": "/qrcode/read/batch", "method": "POST", "description": "批量识别二维码"},
            {"path": "/qrcode/health", "method": "GET", "description": "健康检查"}
        ],
        "capabilities": [
            "支持图片URL输入",
            "支持Base64图片数据输入",
            "支持文本形式输入",
            "批量处理",
            "返回二维码位置信息"
        ]
    }
