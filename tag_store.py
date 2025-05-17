# tag_store.py
import json
import os
import threading
from typing import Dict, Set, List, Optional


class UserTagStore:
    """
    用户标签存储服务。

    提供用户标签的增删改查功能，支持数据持久化。
    """

    def __init__(self, storage_file="user_tags.json"):
        """
        初始化标签存储服务

        参数:
            storage_file: 数据持久化的JSON文件路径
        """
        # 获取当前目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 如果storage_file是相对路径，则转换为绝对路径
        if not os.path.isabs(storage_file):
            self._storage_file = os.path.join(current_dir, storage_file)
        else:
            self._storage_file = storage_file

        print(f"存储文件路径: {self._storage_file}")

        self._user_tags: Dict[str, Set[str]] = {}  # 用户ID -> 标签集合
        self._tag_users: Dict[str, Set[str]] = {}  # 标签 -> 用户ID集合
        self._lock = threading.RLock()  # 可重入锁，确保线程安全

        # 加载现有数据
        self._load_data()

        # 立即保存以确保文件被创建
        self._save_data()

    def _load_data(self) -> None:
        """从存储文件加载数据（如果文件存在）"""
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 将列表转换回集合
                    self._user_tags = {k: set(v) for k, v in data.get("user_tags", {}).items()}
                    self._tag_users = {k: set(v) for k, v in data.get("tag_users", {}).items()}
                print(f"从 {self._storage_file} 加载数据成功")
            except Exception as e:
                print(f"加载数据错误: {e}")
                import traceback
                traceback.print_exc()
                # 如果加载失败，初始化为空结构
                self._user_tags = {}
                self._tag_users = {}
        else:
            print(f"存储文件尚不存在: {self._storage_file}")

    def _save_data(self) -> None:
        """将数据保存到存储文件"""
        try:
            # 创建目录（如果不存在）
            directory = os.path.dirname(self._storage_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"已创建目录: {directory}")

            # 将集合转换为列表以便序列化为JSON
            data = {
                "user_tags": {k: list(v) for k, v in self._user_tags.items()},
                "tag_users": {k: list(v) for k, v in self._tag_users.items()}
            }

            # 使用临时文件确保原子写入
            temp_file = f"{self._storage_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 重命名替换原文件（大多数文件系统上是原子操作）
            os.replace(temp_file, self._storage_file)
            print(f"数据已保存到 {self._storage_file}")

        except Exception as e:
            print(f"保存数据错误: {e}")
            import traceback
            traceback.print_exc()

    def add_tag(self, user_id: str, tag: str = None) -> None:
        """
        为用户添加标签。如果tag为None，则只创建用户。

        参数:
            user_id: 用户ID
            tag: 要添加的标签，如果为None则只创建用户
        """
        with self._lock:
            print(f"为用户 '{user_id}' 添加标签 '{tag}'")

            # 如果用户不存在，创建用户条目
            if user_id not in self._user_tags:
                self._user_tags[user_id] = set()

            # 如果提供了标签，则添加标签
            if tag is not None:
                self._user_tags[user_id].add(tag)

                # 更新反向索引
                if tag not in self._tag_users:
                    self._tag_users[tag] = set()
                self._tag_users[tag].add(user_id)

            # 持久化更改
            self._save_data()

    def remove_tag(self, user_id: str, tag: str) -> bool:
        """
        删除用户的标签

        参数:
            user_id: 用户ID
            tag: 要删除的标签

        返回:
            如果标签被成功删除返回True，如果用户或标签不存在返回False
        """
        with self._lock:
            print(f"从用户 '{user_id}' 删除标签 '{tag}'")

            if user_id not in self._user_tags or tag not in self._user_tags[user_id]:
                print(f"用户 '{user_id}' 没有标签 '{tag}'")
                return False

            # 从用户移除标签
            self._user_tags[user_id].remove(tag)

            # 如果用户没有标签了，保留用户条目
            # 注意：我们不再删除没有标签的用户

            # 更新反向索引
            if tag in self._tag_users:
                self._tag_users[tag].discard(user_id)
                if not self._tag_users[tag]:
                    del self._tag_users[tag]

            # 持久化更改
            self._save_data()

            return True

    def get_user_tags(self, user_id: str) -> Set[str]:
        """
        获取用户的所有标签

        参数:
            user_id: 用户ID

        返回:
            用户的标签集合（如果用户不存在则返回空集合）
        """
        with self._lock:
            tags = self._user_tags.get(user_id, set()).copy()
            print(f"获取用户 '{user_id}' 的 {len(tags)} 个标签")
            return tags

    def get_users_with_tag(self, tag: str) -> Set[str]:
        """
        获取拥有特定标签的所有用户

        参数:
            tag: 要查找的标签

        返回:
            拥有该标签的用户ID集合（如果标签不存在则返回空集合）
        """
        with self._lock:
            users = self._tag_users.get(tag, set()).copy()
            print(f"找到 {len(users)} 个拥有标签 '{tag}' 的用户")
            return users

    def has_tag(self, user_id: str, tag: str) -> bool:
        """
        检查用户是否拥有特定标签

        参数:
            user_id: 用户ID
            tag: 要检查的标签

        返回:
            如果用户拥有该标签则返回True，否则返回False
        """
        with self._lock:
            result = user_id in self._user_tags and tag in self._user_tags[user_id]
            print(f"用户 '{user_id}' 拥有标签 '{tag}': {result}")
            return result

    def get_all_users(self) -> List[str]:
        """
        获取所有用户ID

        返回:
            所有用户ID的列表
        """
        with self._lock:
            users = list(self._user_tags.keys())
            print(f"获取到 {len(users)} 个用户")
            return users

    def get_all_tags(self) -> List[str]:
        """
        获取所有标签

        返回:
            所有标签的列表
        """
        with self._lock:
            tags = list(self._tag_users.keys())
            print(f"获取到 {len(tags)} 个标签")
            return tags

    def create_user(self, user_id: str) -> bool:
        """
        创建一个没有标签的用户

        参数:
            user_id: 用户ID

        返回:
            如果用户成功创建返回True，如果用户已存在返回False
        """
        with self._lock:
            if user_id in self._user_tags:
                print(f"用户 '{user_id}' 已存在")
                return False

            # 创建空标签集合的用户
            self._user_tags[user_id] = set()

            # 持久化更改
            self._save_data()
            print(f"创建了没有标签的用户 '{user_id}'")
            return True

    def clear(self) -> None:
        """
        清除所有数据并删除存储文件
        """
        with self._lock:
            print("正在清除所有数据")
            self._user_tags.clear()
            self._tag_users.clear()

            if os.path.exists(self._storage_file):
                try:
                    os.remove(self._storage_file)
                    print(f"已删除存储文件: {self._storage_file}")
                except Exception as e:
                    print(f"删除存储文件错误: {e}")
                    import traceback
                    traceback.print_exc()

            # 创建空文件
            self._save_data()


# 创建单例实例
tag_store = UserTagStore("user_tags.json")