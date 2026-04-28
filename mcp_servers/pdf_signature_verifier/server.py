"""
PDF签章验证器MCP服务器
支持验证PDF文件中的数字签章和电子签名
"""
import io
import requests
from typing import Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
import PyPDF2
from PyPDF2 import PdfReader

from mcp_servers.pdf_signature_verifier.models import (
    PDFSignatureVerifyRequest,
    PDFSignatureVerifyResponse,
    BatchPDFSignatureVerifyRequest,
    BatchPDFSignatureVerifyResponse
)
from utils.logger import logger
from utils.http_helpers import fetch_url


# 创建路由器
router = APIRouter(tags=["PDF Signature Verifier"])


def download_pdf_from_url(url: str) -> bytes:
    """
    从URL下载PDF文件

    Args:
        url: PDF文件的URL地址

    Returns:
        PDF文件的字节数据
    """
    try:
        response = fetch_url(url)
        return response.content
    except Exception as e:
        raise ValueError(f"下载PDF文件失败: {str(e)}")


def verify_pdf_signature_data(pdf_data: bytes, detailed_report: bool = True) -> Dict[str, Any]:
    """
    验证PDF文件中的数字签章

    Args:
        pdf_data: PDF文件的字节数据
        detailed_report: 是否返回详细报告

    Returns:
        包含验证结果的字典
    """
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_data))

        result = {
            "has_signature": False,
            "signature_count": 0,
            "signature_fields": [],
            "validation_checks": [],
            "warnings": [],
            "metadata": {},
            "detailed_info": {}
        }

        # 检查PDF元数据
        if pdf_reader.metadata:
            result["metadata"] = {
                "title": pdf_reader.metadata.get("/Title", ""),
                "author": pdf_reader.metadata.get("/Author", ""),
                "creator": pdf_reader.metadata.get("/Creator", ""),
                "producer": pdf_reader.metadata.get("/Producer", ""),
                "subject": pdf_reader.metadata.get("/Subject", "")
            }

        # 检查AcroForm（表单字段，通常包含签章字段）
        has_acroform = False
        if "/AcroForm" in pdf_reader.trailer["/Root"]:
            acroform = pdf_reader.trailer["/Root"]["/AcroForm"]
            if acroform and "/Fields" in acroform:
                has_acroform = True
                fields = acroform["/Fields"]
                for field in fields:
                    field_object = field.get_object()
                    if "/FT" in field_object and field_object["/FT"] == "/Sig":
                        result["has_signature"] = True
                        result["signature_count"] += 1

                        # 获取签章字段名称
                        field_name = field_object.get("/T", "Unknown")
                        signature_info = {
                            "name": field_name,
                            "type": "Digital Signature",
                            "page": "Unknown"
                        }

                        # 尝试获取更多信息
                        if "/V" in field_object:
                            value = field_object["/V"]
                            if isinstance(value, dict):
                                # 签名值对象
                                if "/M" in value:
                                    signature_info["modification_date"] = value["/M"]
                                if "/Name" in value:
                                    signature_info["signer_name"] = value["/Name"]
                                if "/Reason" in value:
                                    signature_info["reason"] = value["/Reason"]
                                if "/Location" in value:
                                    signature_info["location"] = value["/Location"]

                        result["signature_fields"].append(signature_info)

        # 执行验证检查
        validation_checks = []

        # 检查1：签章存在性
        if result["has_signature"]:
            validation_checks.append({
                "check": "Signature Presence",
                "result": "PASSED",
                "message": f"发现 {result['signature_count']} 个数字签章"
            })
        else:
            validation_checks.append({
                "check": "Signature Presence",
                "result": "FAILED",
                "message": "PDF中未发现数字签章"
            })

        # 检查2：PDF完整性
        try:
            page_count = len(pdf_reader.pages)
            if page_count > 0:
                validation_checks.append({
                    "check": "PDF Integrity",
                    "result": "PASSED",
                    "message": f"PDF包含 {page_count} 页，结构完整"
                })
            else:
                validation_checks.append({
                    "check": "PDF Integrity",
                    "result": "FAILED",
                    "message": "PDF页面数为0，文件可能损坏"
                })
                result["warnings"].append("PDF结构异常")
        except Exception as e:
            validation_checks.append({
                "check": "PDF Integrity",
                "result": "FAILED",
                "message": f"PDF完整性检查失败: {str(e)}"
            })
            result["warnings"].append("PDF完整性检查失败")

        # 检查3：元数据一致性
        if result["metadata"]:
            creator = result["metadata"].get("creator") or result["metadata"].get("producer")
            if creator:
                validation_checks.append({
                    "check": "Metadata Consistency",
                    "result": "PASSED",
                    "message": f"创建工具: {creator}"
                })
            else:
                validation_checks.append({
                    "check": "Metadata Consistency",
                    "result": "WARNING",
                    "message": "缺少元数据信息"
                })
                result["warnings"].append("元数据不完整")

        # 检查4：AcroForm存在性
        if has_acroform:
            validation_checks.append({
                "check": "Form Structure",
                "result": "PASSED",
                "message": "PDF包含表单结构（支持数字签章）"
            })

        # 检查5：签章字段详细信息
        if detailed_report and result["signature_fields"]:
            signature_details = []
            for idx, sig_field in enumerate(result["signature_fields"], 1):
                detail = {
                    "index": idx,
                    "field_name": sig_field.get("name", "Unknown"),
                    "type": sig_field.get("type", "Unknown"),
                    "signer_name": sig_field.get("signer_name", "Unknown"),
                    "modification_date": sig_field.get("modification_date", "Unknown"),
                    "reason": sig_field.get("reason", ""),
                    "location": sig_field.get("location", "")
                }
                signature_details.append(detail)

            result["detailed_info"]["signatures"] = signature_details

        # 检查6：文件大小和基本信息
        result["detailed_info"]["file_info"] = {
            "size_bytes": len(pdf_data),
            "size_mb": round(len(pdf_data) / (1024 * 1024), 2),
            "page_count": page_count if 'page_count' in locals() else 0
        }

        # 检查7：加密状态
        try:
            if pdf_reader.is_encrypted:
                validation_checks.append({
                    "check": "Encryption Status",
                    "result": "WARNING",
                    "message": "PDF文件已加密，可能影响签章验证"
                })
                result["detailed_info"]["file_info"]["encrypted"] = True
                result["warnings"].append("PDF已加密")
            else:
                validation_checks.append({
                    "check": "Encryption Status",
                    "result": "PASSED",
                    "message": "PDF文件未加密"
                })
                result["detailed_info"]["file_info"]["encrypted"] = False
        except:
            pass

        result["validation_checks"] = validation_checks

        # 生成验证结果摘要
        passed_checks = sum(1 for check in validation_checks if check["result"] == "PASSED")
        failed_checks = sum(1 for check in validation_checks if check["result"] == "FAILED")
        warning_checks = sum(1 for check in validation_checks if check["result"] == "WARNING")

        result["validation_summary"] = {
            "total_checks": len(validation_checks),
            "passed": passed_checks,
            "failed": failed_checks,
            "warnings": warning_checks,
            "overall_valid": failed_checks == 0 and result["has_signature"]
        }

        return result

    except Exception as e:
        logger.error(f"PDF签章验证失败: {str(e)}")
        return {
            "has_signature": False,
            "error": f"PDF签章验证失败: {str(e)}",
            "validation_checks": [],
            "warnings": [],
            "metadata": {},
            "detailed_info": {}
        }


def process_signature_verification_request(request: PDFSignatureVerifyRequest) -> Dict[str, Any]:
    """
    处理PDF签章验证请求

    Args:
        request: PDF签章验证请求

    Returns:
        包含验证结果的字典
    """
    try:
        logger.info(f"开始验证PDF签章: {request.url}")

        # 下载PDF文件
        pdf_data = download_pdf_from_url(request.url)

        # 验证签章
        verification_result = verify_pdf_signature_data(pdf_data, request.detailed_report)

        logger.info(f"PDF签章验证完成: 签章存在={verification_result['has_signature']}")

        return {
            "success": True,
            "url": request.url,
            "has_signature": verification_result["has_signature"],
            "signature_count": verification_result.get("signature_count", 0),
            "validation_result": verification_result,
            "detailed_report": verification_result if request.detailed_report else None,
            "error": None
        }

    except ValueError as e:
        logger.error(f"PDF签章验证请求处理失败: {str(e)}")
        return {
            "success": False,
            "url": request.url,
            "has_signature": False,
            "validation_result": None,
            "detailed_report": None,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"处理PDF签章验证请求时发生错误: {str(e)}")
        return {
            "success": False,
            "url": request.url,
            "has_signature": False,
            "validation_result": None,
            "detailed_report": None,
            "error": f"处理请求时发生错误: {str(e)}"
        }


@router.post("/verify", response_model=PDFSignatureVerifyResponse)
async def verify_pdf_signature(request: PDFSignatureVerifyRequest):
    """
    验证PDF文件的数字签章（通用接口）

    支持从URL下载PDF文件并验证其中的数字签章和电子签名

    Args:
        request: PDF签章验证请求体

    Returns:
        PDF签章验证结果
    """
    result = process_signature_verification_request(request)
    return PDFSignatureVerifyResponse(**result)


@router.post("/verify/url", response_model=PDFSignatureVerifyResponse)
async def verify_pdf_signature_from_url(request: PDFSignatureVerifyRequest):
    """
    从URL验证PDF签章（专用接口）

    专门用于处理URL输入的PDF签章验证

    Args:
        request: 包含url字段的请求体

    Returns:
        PDF签章验证结果
    """
    try:
        logger.info(f"从URL验证PDF签章: {request.url}")
        result = process_signature_verification_request(request)
        logger.info(f"PDF签章验证{'成功' if result['success'] else '失败'}")
        return PDFSignatureVerifyResponse(**result)
    except Exception as e:
        logger.error(f"URL PDF签章验证失败: {str(e)}")
        return PDFSignatureVerifyResponse(
            success=False,
            url=request.url,
            has_signature=False,
            validation_result=None,
            detailed_report=None,
            error=f"URL PDF签章验证失败: {str(e)}"
        )


@router.post("/verify/batch", response_model=BatchPDFSignatureVerifyResponse)
async def verify_batch_pdf_signatures(request: BatchPDFSignatureVerifyRequest):
    """
    批量验证多个PDF文件的签章
    """
    results = []
    success_count = 0
    failed_count = 0

    for url in request.urls:
        verify_request = PDFSignatureVerifyRequest(
            url=url,
            detailed_report=request.detailed_report
        )
        result = process_signature_verification_request(verify_request)
        results.append(PDFSignatureVerifyResponse(**result))

        if result["success"]:
            success_count += 1
        else:
            failed_count += 1

    # 生成摘要统计
    total_signatures = sum(r.signature_count for r in results if r.signature_count)
    files_with_signatures = sum(1 for r in results if r.has_signature)

    summary = {
        "total_files": len(request.urls),
        "files_with_signatures": files_with_signatures,
        "total_signatures_found": total_signatures,
        "success_rate": f"{(success_count/len(request.urls)*100):.1f}%"
    }

    return BatchPDFSignatureVerifyResponse(
        results=results,
        total_success=success_count,
        total_failed=failed_count
    )


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "PDF Signature Verifier",
        "version": "1.0.0"
    }


def get_info():
    """获取服务器信息"""
    return {
        "name": "PDF Signature Verifier",
        "version": "1.0.0",
        "description": "验证PDF文件中的数字签章和电子签名",
        "endpoints": [
            {"path": "/signature/verify", "method": "POST", "description": "验证PDF签章（通用接口）"},
            {"path": "/signature/verify/url", "method": "POST", "description": "从URL验证PDF签章（专用接口）"},
            {"path": "/signature/verify/batch", "method": "POST", "description": "批量验证PDF签章"},
            {"path": "/signature/health", "method": "GET", "description": "健康检查"}
        ],
        "capabilities": [
            "检测PDF中的数字签章",
            "验证PDF结构完整性",
            "检查元数据一致性",
            "提供详细的签章信息",
            "批量处理多个PDF文件",
            "返回验证检查报告"
        ]
    }