# main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from tag_store import tag_store  # 导入标签存储服务

# 初始化 FastAPI 应用
app = FastAPI(
    title="网易云音乐用户标签服务",
    description="用于管理网易云音乐中的用户画像标签的服务",
    version="1.0.0"
)

# 配置跨域资源共享（CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发阶段使用）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头
)


# 统一 API 响应的数据结构
class ApiResponse(BaseModel):
    status: str  # 响应状态，如 "成功" 或 "错误"
    message: str  # 响应信息
    data: Optional[Dict[str, Any]] = None  # 实际返回的数据内容


# 添加标签请求的数据结构
class TagAddRequest(BaseModel):
    tags: List[str]  # 要添加的标签列表


@app.get("/ping")
async def ping():
    """
    健康检查接口，用于确认服务是否正在运行
    """
    return {"status": "成功", "message": "用户标签服务正在运行"}


@app.get("/users/{user_id}/tags", response_model=ApiResponse)
async def get_user_tags(user_id: str):
    """
    获取指定用户的所有标签

    参数：
        user_id：用户ID

    返回：
        用户标签列表或空标签信息
    """
    tags = tag_store.get_user_tags(user_id)

    if not tags and user_id not in tag_store._user_tags:
        # 用户不存在
        return ApiResponse(
            status="成功",
            message="用户不存在",
            data={"user_id": user_id, "tags": []}
        )

    # 用户存在（有标签或没有标签）
    return ApiResponse(
        status="成功",
        message="成功获取标签" if tags else "用户没有标签",
        data={"user_id": user_id, "tags": list(tags)}
    )


@app.post("/users/{user_id}/tags", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def add_user_tags(user_id: str, request: TagAddRequest):
    """
    为指定用户添加一个或多个标签，或创建一个没有标签的用户

    参数：
        user_id：用户ID
        request：请求体，包含要添加的标签列表

    返回：
        添加成功后的用户标签信息
    """
    # 允许创建没有标签的用户
    if not request.tags:
        # 创建没有标签的用户
        tag_store.create_user(user_id)

        return ApiResponse(
            status="成功",
            message="用户创建成功",
            data={"user_id": user_id, "tags": []}
        )

    # 为用户添加每个标签
    for tag in request.tags:
        tag_store.add_tag(user_id, tag)

    # 获取更新后的标签
    updated_tags = tag_store.get_user_tags(user_id)

    return ApiResponse(
        status="成功",
        message="标签添加成功",
        data={"user_id": user_id, "tags": list(updated_tags)}
    )


@app.post("/users/{user_id}", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_id: str):
    """
    创建一个没有标签的用户

    参数：
        user_id：要创建的用户ID

    返回：
        用户创建成功的确认信息
    """
    result = tag_store.create_user(user_id)

    message = "用户创建成功" if result else "用户已存在"

    return ApiResponse(
        status="成功",
        message=message,
        data={"user_id": user_id, "tags": []}
    )


@app.delete("/users/{user_id}/tags/{tag}", response_model=ApiResponse)
async def remove_user_tag(user_id: str, tag: str):
    """
    删除指定用户的某个标签

    参数：
        user_id：用户ID
        tag：要删除的标签名称

    返回：
        删除结果信息
    """
    result = tag_store.remove_tag(user_id, tag)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 '{user_id}' 没有标签 '{tag}'"
        )

    return ApiResponse(
        status="成功",
        message=f"成功删除标签 '{tag}'",
        data={"user_id": user_id, "removed_tag": tag}
    )


@app.get("/tags/{tag}/users", response_model=ApiResponse)
async def get_users_with_tag(tag: str):
    """
    获取所有拥有某个标签的用户

    参数：
        tag：标签名称

    返回：
        拥有该标签的用户ID列表
    """
    users = tag_store.get_users_with_tag(tag)

    return ApiResponse(
        status="成功",
        message=f"成功获取拥有标签 '{tag}' 的用户",
        data={"tag": tag, "users": list(users)}
    )


@app.get("/tags", response_model=ApiResponse)
async def get_all_tags():
    """
    获取系统中所有存在的标签

    返回：
        标签列表
    """
    tags = tag_store.get_all_tags()

    return ApiResponse(
        status="成功",
        message="成功获取所有标签",
        data={"tags": tags}
    )


@app.get("/users", response_model=ApiResponse)
async def get_all_users():
    """
    获取系统中所有用户

    返回：
        用户ID列表
    """
    users = tag_store.get_all_users()

    return ApiResponse(
        status="成功",
        message="成功获取所有用户",
        data={"users": users}
    )


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    可用于未来从数据库等持久化系统加载数据
    """
    print("网易云音乐用户标签服务已启动")


# 自定义HTTP异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return ApiResponse(
        status="错误",
        message=exc.detail
    )


if __name__ == "__main__":
    # 启动本地开发服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)