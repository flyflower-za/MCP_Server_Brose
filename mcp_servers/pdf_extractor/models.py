"""
PDF提取器的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class PDFExtractRequest(BaseModel):
    """PDF提取请求"""
    url: str = Field(..., description="PDF文件的URL地址")
    include_metadata: bool = Field(default=True, description="是否包含元数据")
    return_task_id: bool = Field(default=False, description="是否返回任务ID以支持异步进度查询")


class PDFExtractResponse(BaseModel):
    """PDF提取响应"""
    success: bool
    url: str
    total_pages: Optional[int] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None


class BatchPDFExtractRequest(BaseModel):
    """批量PDF提取请求"""
    urls: list[str] = Field(..., description="PDF文件的URL地址列表")
    include_metadata: bool = Field(default=True, description="是否包含元数据")


class BatchPDFExtractResponse(BaseModel):
    """批量PDF提取响应"""
    results: list[PDFExtractResponse]
    total_success: int
    total_failed: int
