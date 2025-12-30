from fastapi import APIRouter

from app.api.endpoints import wx_public, test_api, sogou_wx_public, system, ai_assistant

api_router = APIRouter()
api_router.include_router(wx_public.router, prefix="/wx/public", tags=["微信公众号"])
api_router.include_router(test_api.router, prefix="/test", tags=["引入库测试接口"])
api_router.include_router(sogou_wx_public.router, prefix="/sogou/wx/public", tags=["搜狗微信公众号"])
api_router.include_router(system.router, prefix="/wx/public/system", tags=["系统工具"])
api_router.include_router(ai_assistant.router, prefix="/wx/public/ai", tags=["AI助手"])
