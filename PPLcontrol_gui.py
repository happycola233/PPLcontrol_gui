import tkinter as tk  # 导入 tkinter 库，用于创建 GUI 应用程序
from tkinter import ttk, simpledialog  # 从 tkinter 导入 ttk、simpledialog，用于增强 GUI 功能
import subprocess  # 导入 subprocess 库，用于运行外部命令
import os  # 导入 os 库，用于与操作系统交互
import sys  # 导入 sys 库，用于访问解释器的变量
import ctypes, win32print, win32gui, win32con, win32api # 用于高DPI适配

def get_resource_path(relative_path):
    """获取资源的绝对路径，支持 PyInstaller 打包后的环境"""
    try:
        # PyInstaller 创建临时文件夹，并将路径存储于 _MEIPASS 中
        base_path = sys._MEIPASS
    except AttributeError:
        # 如果没有 _MEIPASS，使用当前目录的绝对路径
        base_path = os.path.abspath(".")

    # 返回完整的文件路径
    return os.path.join(base_path, relative_path).replace("/","\\")

def run_command(command):
    """运行命令并将输出显示在文本框中"""
    output_text.config(state=tk.NORMAL)  # 将文本框设置为可写入状态
    output_text.insert(tk.END, f"> {command}\n")  # 在文本框中显示执行的命令
    
    try:
        # 执行命令并获取输出，捕获所有输出（包括错误）
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = result.stdout.strip()  # 去掉输出中的多余空白
    except subprocess.CalledProcessError as e:
        # 如果命令失败，捕获错误输出
        output = e.stdout.strip()
    
    # 将输出结果插入到文本框中
    output_text.insert(tk.END, output + "\n")
    # 在输出结果后添加分隔线
    output_text.insert(tk.END, "-"*60 + "\n")
    
    # 自动滚动到最后一行，以便查看最新输出
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)  # 将文本框设置为只读状态

def list_processes():
    """列出受保护的进程"""
    run_command(f"{pplcontrol_exe} list")  # 执行命令以列出受保护进程

def get_protection_level():
    """获取指定进程的保护级别"""
    pid = simpledialog.askstring("输入", "请输入进程PID:")  # 弹出对话框请求用户输入进程 PID
    if pid:
        run_command(f"{pplcontrol_exe} get {pid}")  # 根据用户输入的 PID 获取保护级别

def set_protection_level():
    """设置指定进程的保护级别"""
    pid = simpledialog.askstring("输入", "请输入进程PID:")  # 弹出对话框请求用户输入进程 PID
    if pid:
        pp_type = pp_type_var.get()  # 获取用户选择的保护类型
        signer_type = signer_type_var.get()  # 获取用户选择的签名类型
        run_command(f"{pplcontrol_exe} set {pid} {pp_type} {signer_type}")  # 设置保护级别和签名类型

def protect_process():
    """保护指定的进程"""
    pid = simpledialog.askstring("输入", "请输入进程PID:")  # 弹出对话框请求用户输入进程 PID
    if pid:
        pp_type = pp_type_var.get()  # 获取用户选择的保护类型
        signer_type = signer_type_var.get()  # 获取用户选择的签名类型
        run_command(f"{pplcontrol_exe} protect {pid} {pp_type} {signer_type}")  # 执行命令保护进程

def unprotect_process():
    """取消保护指定的进程"""
    pid = simpledialog.askstring("输入", "请输入进程PID:")  # 弹出对话框请求用户输入进程 PID
    if pid:
        run_command(f"{pplcontrol_exe} unprotect {pid}")  # 执行命令取消保护进程

def install_driver():
    """安装驱动程序"""
    run_command(f'sc.exe create RTCore64 type= kernel start= auto binPath= "{driver_sys}" DisplayName= "Micro - Star MSI Afterburner"')  # 创建驱动服务
    run_command("net start RTCore64")  # 启动驱动服务

def uninstall_driver():
    """卸载驱动程序"""
    run_command("net stop RTCore64")  # 停止驱动服务
    run_command("sc.exe delete RTCore64")  # 删除驱动服务

def run_tasklist():
    """运行 tasklist 命令"""
    run_command("tasklist")  # 执行命令以列出所有进程

def clear_output():
    """清除输出框内容"""
    output_text.config(state=tk.NORMAL)  # 将文本框设置为可写入状态
    output_text.delete(1.0, tk.END)  # 删除文本框中的所有内容
    output_text.config(state=tk.DISABLED)  # 将文本框设置为只读状态

def copy_selection():
    """复制选中内容到剪贴板"""
    root.clipboard_clear()  # 清空剪贴板内容
    text = output_text.get(tk.SEL_FIRST, tk.SEL_LAST)  # 获取选中的文本
    root.clipboard_append(text)  # 将选中的文本添加到剪贴板

def copy_all():
    """复制所有内容到剪贴板"""
    root.clipboard_clear()  # 清空剪贴板内容
    text = output_text.get(1.0, tk.END)  # 获取文本框中的所有内容
    root.clipboard_append(text)  # 将所有内容添加到剪贴板

def show_context_menu(event):
    """显示右键菜单"""
    context_menu.post(event.x_root, event.y_root)  # 在鼠标右键点击的位置显示上下文菜单

# 获取资源路径
pplcontrol_exe = get_resource_path("res\\PPLcontrol.exe")  # 获取 PPLcontrol.exe 的绝对路径
driver_sys = get_resource_path("res\\RTCore64.sys")  # 获取 RTCore64.sys 的绝对路径

# 创建主窗口
root = tk.Tk()  # 创建主窗口
root.title("PPLcontrol GUI")  # 设置窗口标题
root.geometry("1200x800")  # 设置窗口大小

#----------高DPI适配start---------

#获得当前的缩放因子
ScaleFactor=round(win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPHORZRES) / win32api.GetSystemMetrics (0), 2)

#调用api设置成由应用程序缩放
try:  # 系统版本 >= win 8.1
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:  # 系统版本 <= win 8.0
    ctypes.windll.user32.SetProcessDPIAware()

#设置缩放因子
root.tk.call('tk', 'scaling', ScaleFactor/0.75)

#----------高DPI适配end---------

# 创建标题
title_label = ttk.Label(root, text="PPLcontrol GUI", font=("Arial", 16))  # 创建标题标签，使用 Arial 字体，大小为 16
title_label.pack(pady=10)  # 将标题放置在窗口的顶部，并设置上下填充（pady）为 10 像素

# 创建按钮框架
button_frame = ttk.Frame(root)  # 创建按钮框架，用于放置按钮
button_frame.pack(pady=10)  # 将按钮框架放置在标题下方，并设置上下填充为 10 像素

# 配置按钮框架使其内容居中
button_frame.grid_columnconfigure(0, weight=1)  # 设置第一列的权重为 1，使得内容居中
button_frame.grid_columnconfigure(1, weight=1)  # 设置第二列的权重为 1
button_frame.grid_columnconfigure(2, weight=1)  # 设置第三列的权重为 1

# 第一行按钮
ttk.Button(button_frame, text="安装驱动", command=install_driver, width=20).grid(row=0, column=0, padx=5, pady=5)  # 创建“安装驱动”按钮，宽度为 20
ttk.Button(button_frame, text="卸载驱动", command=uninstall_driver, width=20).grid(row=0, column=1, padx=5, pady=5)  # 创建“卸载驱动”按钮，宽度为 20
ttk.Button(button_frame, text="tasklist命令", command=run_tasklist, width=20).grid(row=0, column=2, padx=5, pady=5)  # 创建“tasklist命令”按钮，宽度为 20

# 第二行按钮
ttk.Button(button_frame, text="列出受保护进程", command=list_processes, width=20).grid(row=1, column=0, padx=5, pady=5)  # 创建“列出受保护进程”按钮，宽度为 20
ttk.Button(button_frame, text="获取进程保护级别", command=get_protection_level, width=20).grid(row=1, column=1, padx=5, pady=5)  # 创建“获取进程保护级别”按钮，宽度为 20
ttk.Button(button_frame, text="设置进程保护级别", command=set_protection_level, width=20).grid(row=1, column=2, padx=5, pady=5)  # 创建“设置进程保护级别”按钮，宽度为 20

# 第三行按钮
ttk.Button(button_frame, text="保护进程", command=protect_process, width=20).grid(row=2, column=0, padx=5, pady=5)  # 创建“保护进程”按钮，宽度为 20
ttk.Button(button_frame, text="取消保护进程", command=unprotect_process, width=20).grid(row=2, column=1, padx=5, pady=5)  # 创建“取消保护进程”按钮，宽度为 20

# 创建下拉菜单框架
dropdown_frame = ttk.Frame(root)  # 创建下拉菜单框架，用于放置下拉菜单
dropdown_frame.pack(pady=10)  # 将下拉菜单框架放置在按钮框架下方，并设置上下填充为 10 像素

# 配置下拉菜单框架使其内容居中
dropdown_frame.grid_columnconfigure(0, weight=1)  # 设置第一列的权重为 1，使得内容居中
dropdown_frame.grid_columnconfigure(1, weight=1)  # 设置第二列的权重为 1

# 保护类型
ttk.Label(dropdown_frame, text="保护类型:").grid(row=0, column=0, padx=5, pady=5, sticky="e")  # 创建“保护类型”标签，并设置其位置和对齐方式
pp_type_var = tk.StringVar(value="PPL")  # 创建一个 StringVar 变量，用于存储下拉菜单的选择值，默认值为 "PPL"
ttk.Combobox(dropdown_frame, textvariable=pp_type_var, values=["PP", "PPL"]).grid(row=0, column=1, padx=5, pady=5, sticky="w")  # 创建下拉菜单，允许选择保护类型

# 签名类型
ttk.Label(dropdown_frame, text="签名类型:").grid(row=1, column=0, padx=5, pady=5, sticky="e")  # 创建“签名类型”标签，并设置其位置和对齐方式
signer_type_var = tk.StringVar(value="WinTcb")  # 创建一个 StringVar 变量，用于存储下拉菜单的选择值，默认值为 "WinTcb"
ttk.Combobox(dropdown_frame, textvariable=signer_type_var, values=["Authenticode", "CodeGen", "Antimalware", "Lsa", "Windows", "WinTcb", "WinSystem"]).grid(row=1, column=1, padx=5, pady=5, sticky="w")  # 创建下拉菜单，允许选择签名类型

# 创建输出框
output_frame = ttk.Frame(root)  # 创建输出框框架，用于放置文本框和滚动条
output_frame.pack(fill="both", expand=True, padx=10, pady=10)  # 将输出框框架放置在窗口底部，并设置填充和扩展属性

output_text = tk.Text(output_frame, wrap="word", state=tk.DISABLED)  # 创建文本框，用于显示命令的输出，设置为只读状态
output_text.pack(fill="both", expand=True, side="left")  # 将文本框放置在框架中，并设置填充和扩展属性

output_scrollbar = ttk.Scrollbar(output_frame, command=output_text.yview)  # 创建滚动条，用于文本框的垂直滚动
output_scrollbar.pack(side="right", fill="y")  # 将滚动条放置在文本框的右侧

output_text.config(yscrollcommand=output_scrollbar.set)  # 将滚动条与文本框关联

# 创建右键菜单
context_menu = tk.Menu(root, tearoff=0)  # 创建上下文菜单（右键菜单），tearoff=0 表示菜单不带分离线
context_menu.add_command(label="清屏", command=clear_output)  # 添加“清屏”选项，并关联 clear_output 函数
context_menu.add_command(label="复制选中内容", command=copy_selection)  # 添加“复制选中内容”选项，并关联 copy_selection 函数
context_menu.add_command(label="复制全部内容", command=copy_all)  # 添加“复制全部内容”选项，并关联 copy_all 函数

# 绑定右键菜单
output_text.bind("<Button-3>", show_context_menu)  # 绑定鼠标右键点击事件，以显示右键菜单

# 启动主循环
root.mainloop()  # 启动 Tkinter 主事件循环，等待用户输入
