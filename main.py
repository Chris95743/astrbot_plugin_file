from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api import AstrBotConfig
from astrbot.api.star import Context, Star, register
import os
import shutil

# 创建配置对象
# 注册插件的装饰器
@register("文件操作", "Chris", "一个简单的文件发送、删除、移动、复制和查看文件夹内容插件", "1.0.0")
class FileSenderPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.base_path = config.get('FileBasePath', '/default/path')  # 配置文件中的基础路径

    # 根据路径发送文件
    async def send_file(self, event: AstrMessageEvent, file_path: str):
        full_file_path = os.path.join(self.base_path, file_path)

        # 检查文件是否存在
        if not os.path.exists(full_file_path):
            yield event.plain_result(f"文件 {file_path} 不存在，请检查路径。")
            return

        # 检查文件是否为文件而非文件夹
        if os.path.isdir(full_file_path):
            yield event.plain_result(f"指定的路径是一个目录，而不是文件：{file_path}")
            return

        # 获取文件名（不带路径）
        file_name = os.path.basename(file_path)

        # 发送文件
        yield event.plain_result(f"开始发送文件 {file_name}...")
        yield event.chain_result([File(name=file_name, file=full_file_path)])
        yield event.plain_result(f"文件 {file_name} 已发送。")

    # 根据路径删除文件
    async def delete_file(self, event: AstrMessageEvent, file_path: str):
        full_file_path = os.path.join(self.base_path, file_path)

        # 检查文件是否存在
        if not os.path.exists(full_file_path):
            yield event.plain_result(f"文件 {file_path} 不存在，请检查路径。")
            return

        # 检查文件是否为文件而非文件夹
        if os.path.isdir(full_file_path):
            yield event.plain_result(f"指定的路径是一个目录，而不是文件：{file_path}")
            return

        try:
            # 删除文件
            os.remove(full_file_path)
            yield event.plain_result(f"文件 {file_path} 已成功删除。")
        except Exception as e:
            yield event.plain_result(f"删除文件时发生错误: {str(e)}")

    # 根据路径删除目录
    async def delete_directory(self, event: AstrMessageEvent, dir_path: str):
        full_dir_path = os.path.join(self.base_path, dir_path)

        # 检查目录是否存在
        if not os.path.exists(full_dir_path):
            yield event.plain_result(f"目录 {dir_path} 不存在，请检查路径。")
            return

        # 检查是否是目录
        if not os.path.isdir(full_dir_path):
            yield event.plain_result(f"指定路径 {dir_path} 不是一个目录。")
            return

        try:
            # 删除目录及其中所有内容
            shutil.rmtree(full_dir_path)
            yield event.plain_result(f"目录 {dir_path} 已成功删除。")
        except Exception as e:
            yield event.plain_result(f"删除目录时发生错误: {str(e)}")

    # 查看目录内容
    async def list_files(self, event: AstrMessageEvent, dir_path: str):
        full_dir_path = os.path.join(self.base_path, dir_path)

        # 检查目录是否存在
        if not os.path.exists(full_dir_path):
            yield event.plain_result(f"目录 {dir_path} 不存在，请检查路径。")
            return

        # 检查是否是目录
        if not os.path.isdir(full_dir_path):
            yield event.plain_result(f"指定路径 {dir_path} 不是一个目录。")
            return

        # 获取目录内容
        try:
            files = os.listdir(full_dir_path)
            if not files:
                yield event.plain_result(f"目录 {dir_path} 是空的。")
                return

            # 格式化文件和文件夹输出
            result = ""
            for file in files:
                full_path = os.path.join(full_dir_path, file)
                if os.path.isdir(full_path):
                    result += f"/{file}\n"  # 文件夹前加 '/'
                else:
                    result += f"{file}\n"  # 文件不加 '/'

            yield event.plain_result(f"目录 {dir_path} 的内容：\n{result}")
        except Exception as e:
            yield event.plain_result(f"读取目录时发生错误: {str(e)}")

    # 移动文件或目录
    async def move(self, event: AstrMessageEvent, source_path: str, destination_path: str):
        source_full_path = os.path.join(self.base_path, source_path)
        destination_full_path = os.path.join(self.base_path, destination_path)

        # 检查源文件/目录是否存在
        if not os.path.exists(source_full_path):
            yield event.plain_result(f"源路径 {source_path} 不存在，请检查路径。")
            return

        try:
            # 移动文件或目录
            shutil.move(source_full_path, destination_full_path)
            yield event.plain_result(f"文件/目录 {source_path} 已成功移动到 {destination_path}。")
        except Exception as e:
            yield event.plain_result(f"移动文件/目录时发生错误: {str(e)}")

    # 复制文件或目录
    async def copy(self, event: AstrMessageEvent, source_path: str, destination_path: str):
        source_full_path = os.path.join(self.base_path, source_path)
        destination_full_path = os.path.join(self.base_path, destination_path)

        # 检查源文件/目录是否存在
        if not os.path.exists(source_full_path):
            yield event.plain_result(f"源路径 {source_path} 不存在，请检查路径。")
            return

        try:
            # 复制文件或目录
            if os.path.isdir(source_full_path):
                shutil.copytree(source_full_path, destination_full_path)
            else:
                shutil.copy2(source_full_path, destination_full_path)
            yield event.plain_result(f"文件/目录 {source_path} 已成功复制到 {destination_path}。")
        except Exception as e:
            yield event.plain_result(f"复制文件/目录时发生错误: {str(e)}")

    # 解析命令并发送文件
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("发送")
    async def send_file_command(self, event: AstrMessageEvent):
        '''发送指定文件'''
        messages = event.get_messages()

        if not messages:
            yield event.plain_result("请输入文件路径，格式为 /path/file")
            return

        # 处理消息中的 At 对象
        message_text = ""
        for message in messages:
            if isinstance(message, At):
                continue  # 跳过 At 类型的消息
            message_text = message.text
            break  # 获取第一个非 At 消息

        parts = message_text.split()

        # 检查命令格式是否正确
        if len(parts) < 2:
            yield event.plain_result("请输入正确的文件路径，格式为 /path/file")
            return

        file_path = parts[1]

        # 调用文件发送方法
        async for result in self.send_file(event, file_path):
            yield result

    # 解析命令并删除文件
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("删除")
    async def delete_file_command(self, event: AstrMessageEvent):
        '''删除指定文件'''
        messages = event.get_messages()

        if not messages:
            yield event.plain_result("请输入文件路径，格式为 删除 路径")
            return

        # 处理消息中的 At 对象
        message_text = ""
        for message in messages:
            if isinstance(message, At):
                continue  # 跳过 At 类型的消息
            message_text = message.text
            break  # 获取第一个非 At 消息

        parts = message_text.split()

        # 检查命令格式是否正确
        if len(parts) < 2:
            yield event.plain_result("请输入正确的文件路径，格式为 /path/file")
            return

        file_path = parts[1]

        # 调用文件删除方法
        async for result in self.delete_file(event, file_path):
            yield result

    # 解析命令并删除目录
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("删除目录")
    async def delete_directory_command(self, event: AstrMessageEvent):
        '''删除指定目录'''
        messages = event.get_messages()

        if not messages:
            yield event.plain_result("请输入目录路径，格式为 删除目录 路径")
            return

        # 处理消息中的 At 对象
        message_text = ""
        for message in messages:
            if isinstance(message, At):
                continue  # 跳过 At 类型的消息
            message_text = message.text
            break  # 获取第一个非 At 消息

        parts = message_text.split()

        # 检查命令格式是否正确
        if len(parts) < 2:
            yield event.plain_result("请输入正确的目录路径，格式为 删除目录 /path")
            return

        dir_path = parts[1]

        # 调用删除目录方法
        async for result in self.delete_directory(event, dir_path):
            yield result

    # 解析命令并查看目录内容
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("查看")
    async def list_file_command(self, event: AstrMessageEvent):
        '''查看指定目录的文件和子目录'''
        messages = event.get_messages()

        if not messages:
            yield event.plain_result("请输入目录路径，格式为 查看 路径")
            return

        # 处理消息中的 At 对象
        message_text = ""
        for message in messages:
            if isinstance(message, At):
                continue  # 跳过 At 类型的消息
            message_text = message.text
            break  # 获取第一个非 At 消息

        parts = message_text.split()

        # 检查命令格式是否正确
        if len(parts) < 2:
            yield event.plain_result("请输入正确的目录路径，格式为 /path/file")
            return

        dir_path = parts[1]

        # 调用查看目录内容方法
        async for result in self.list_files(event, dir_path):
            yield result

    # 显示帮助信息
    @filter.command("文件帮助")
    async def show_help(self, event: AstrMessageEvent):
        '''显示帮助信息'''
        help_text = """指令说明：    
/发送 路径 - 发送指定路径的文件（绝对路径） 
/删除 路径 - 删除指定路径的文件（绝对路径） 
/删除目录 路径 - 删除指定路径的目录（绝对路径） 
/查看 路径 - 查看指定目录的文件和子目录（绝对路径） 
/移动 源路径 目标路径 - 移动指定路径的文件或目录
/复制 源路径 目标路径 - 复制指定路径的文件或目录
/文件帮助 - 显示本帮助信息（除此命令外，其余命令均默认开启管理员权限。）"""
        yield event.plain_result(help_text)
