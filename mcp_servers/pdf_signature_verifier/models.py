"""
PDF签章验证器的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PDFSignatureVerifyRequest(BaseModel):
    """PDF签章验证请求"""
    url: str = Field(..., description="PDF文件的URL地址")
    detailed_report: bool = Field(default=True, description="是否返回详细报告")


class PDFSignatureVerifyResponse(BaseModel):
    """PDF签章验证响应"""
    success: bool
    url: str
    has_signature: Optional[bool] = None
    signature_count: Optional[int] = None
    validation_result: Optional[Dict[str, Any]] = None
    detailed_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BatchPDFSignatureVerifyRequest(BaseModel):
    """批量PDF签章验证请求"""
    urls: List[str] = Field(..., description="PDF文件的URL地址列表")
    detailed_report: bool = Field(default=True, description="是否返回详细报告")


class BatchPDFSignatureVerifyResponse(BaseModel):
    """批量PDF签章验证响应"""
    results: List[PDFSignatureVerifyResponse]
    total_success: int
    total_failed: int
    summary: Dict[str, Any]