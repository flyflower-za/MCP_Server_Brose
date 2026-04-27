"""
二维码识别器的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class QRCodeReadRequest(BaseModel):
    """二维码识别请求（通用）"""
    image_url: Optional[str] = Field(None, description="图片URL地址")
    image_base64: Optional[str] = Field(None, description="Base64编码的图片数据")
    text_input: Optional[str] = Field(None, description="文本形式的二维码（用于特殊格式）")

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/qrcode.png",
                "image_base64": None,
                "text_input": None
            }
        }


class QRCodeURLRequest(BaseModel):
    """二维码识别请求（URL专用）"""
    url: str = Field(..., description="图片URL地址")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/qrcode.png"
            }
        }


class QRCodeBase64Request(BaseModel):
    """二维码识别请求（Base64专用）"""
    base64_data: str = Field(..., description="Base64编码的图片数据")

    class Config:
        json_schema_extra = {
            "example": {
                "base64_data": "iVBORw0KGgoAAAANSUhEUgAA..."
            }
        }


class QRCodeReadResponse(BaseModel):
    """二维码识别响应"""
    success: bool
    qr_data: Optional[str] = None
    format: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


class BatchQRCodeReadRequest(BaseModel):
    """批量二维码识别请求"""
    requests: List[QRCodeReadRequest] = Field(..., description="二维码识别请求列表")


class BatchQRCodeReadResponse(BaseModel):
    """批量二维码识别响应"""
    results: List[QRCodeReadResponse]
    total_success: int
    total_failed: int
