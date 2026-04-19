"""
PDF提取器MCP服务器
"""
import io
from typing import Dict, Any

import requests
from fastapi import APIRouter, HTTPException
from PyPDF2 import PdfReader

from mcp_servers.pdf_extractor.models import (
    PDFExtractRequest,
    PDFExtractResponse,
    BatchPDFExtractRequest,
    BatchPDFExtractResponse
)
from utils.logger import logger
from utils.http_helpers import fetch_url


# 创建路由器
router = APIRouter(tags=["PDF Extractor"])


def extract_pdf_from_url(url: str, include_metadata: bool = True) -> Dict[str, Any]:
    """
    从URL下载PDF并提取文本内容

    Args:
        url: PDF文件的URL地址
        include_metadata: 是否包含元数据

    Returns:
        包含提取结果的字典
    """
    try:
        logger.info(f"开始提取PDF: {url}")

        # 发送HTTP请求获取PDF内容
        response = fetch_url(url)

        # 检查内容类型是否为PDF
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower():
            logger.warning(f"Content-Type不是PDF: {content_type}")

        # 从内存中读取PDF
        pdf_file = io.BytesIO(response.content)

        # 创建PDF阅读器
        pdf_reader = PdfReader(pdf_file)

        # 提取文本内容
        text_content = []
        total_pages = len(pdf_reader.pages)

        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append(f"--- 第 {page_num} 页 ---\n{page_text}")
            except Exception as e:
                logger.error(f"提取第{page_num}页失败: {str(e)}")
                text_content.append(f"--- 第 {page_num} 页 (提取失败: {str(e)}) ---")

        # 获取PDF元数据
        metadata = None
        if include_metadata:
            pdf_metadata = pdf_reader.metadata
            metadata = {
                "title": pdf_metadata.get('/Title', '') if pdf_metadata else '',
                "author": pdf_metadata.get('/Author', '') if pdf_metadata else '',
                "creator": pdf_metadata.get('/Creator', '') if pdf_metadata else '',
                "producer": pdf_metadata.get('/Producer', '') if pdf_metadata else '',
            }

        result = {
            "success": True,
            "url": url,
            "total_pages": total_pages,
            "content": "\n\n".join(text_content),
            "metadata": metadata,
            "error": None
        }

        logger.info(f"PDF提取成功: {url}, 页数: {total_pages}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"下载PDF失败: {url}, 错误: {str(e)}")
        return {
            "success": False,
            "url": url,
            "total_pages": None,
            "content": None,
            "metadata": None,
            "error": f"下载PDF失败: {str(e)}"
        }
    except Exception as e:
        logger.error(f"解析PDF失败: {url}, 错误: {str(e)}")
        return {
            "success": False,
            "url": url,
            "total_pages": None,
            "content": None,
            "metadata": None,
            "error": f"解析PDF失败: {str(e)}"
        }


@router.post("/extract", response_model=PDFExtractResponse)
async def extract_pdf(request: PDFExtractRequest):
    """
    从URL提取单个PDF文件的文本内容

    类似于n8n/dify工作流中的文档提取器功能
    """
    result = extract_pdf_from_url(request.url, request.include_metadata)
    return PDFExtractResponse(**result)


@router.post("/extract/batch", response_model=BatchPDFExtractResponse)
async def extract_batch_pdfs(request: BatchPDFExtractRequest):
    """
    批量从多个URL提取PDF文件的文本内容
    """
    results = []
    success_count = 0
    failed_count = 0

    for url in request.urls:
        result = extract_pdf_from_url(url, request.include_metadata)
        results.append(PDFExtractResponse(**result))

        if result["success"]:
            success_count += 1
        else:
            failed_count += 1

    return BatchPDFExtractResponse(
        results=results,
        total_success=success_count,
        total_failed=failed_count
    )


def get_info():
    """获取服务器信息"""
    return {
        "name": "PDF Extractor",
        "version": "1.0.0",
        "description": "从URL提取PDF文本内容",
        "endpoints": [
            {"path": "/pdf/extract", "method": "POST", "description": "提取单个PDF"},
            {"path": "/pdf/extract/batch", "method": "POST", "description": "批量提取PDF"}
        ]
    }
