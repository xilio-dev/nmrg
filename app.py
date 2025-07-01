import tkinter as tk
from tkinter import ttk, scrolledtext
import os,datetime,platform
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import subprocess
import threading
import tkinter.font as tkFont
def update_status():
    log_text.config(state=tk.DISABLED)  # 禁止编辑文本框
    add_button.config(state=tk.NORMAL,text='下载')#恢复按钮状态为可用
def run_command():
    m3u8 = m3u8_entry.get('1.0',tk.END).strip()
    save_name = video_name_entry.get()
    save_dir = save_path_entry.get()
    full_path = os.path.join(save_dir, f"{save_name}.mp4")
    if not m3u8 or not save_dir  or not m3u8:
        messagebox.showwarning("输入错误", "请确保所有字段都已填写。")
        update_status()
        return
   # 检查路径是否已经存在
    if not save_dir.startswith('/'):
        messagebox.showwarning("警告", f"保存路径 必须以斜杠 {os.sep} 开头")
        update_status()
        return
    if os.path.exists(full_path):
        messagebox.showwarning("警告", f"'{full_path}' 视频名已存在")
        update_status()
        return
    log_text.config(state=tk.NORMAL)  # 允许编辑文本框
    log_text.delete(1.0, tk.END)  # 清空日志框
    command = ["N_m3u8DL-RE", m3u8, "--save-name", save_name, "--save-dir", save_dir]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 读取输出流
        for stdout_line in iter(process.stdout.readline, ""):
            log_text.insert(tk.END, stdout_line)
            # 自动滚动到最后一行
            log_text.see(tk.END)  
        process.stdout.close()
        process.wait()
        # 捕获任何错误输出
        stderr_output = process.stderr.read()
        if stderr_output:
            log_text.insert(tk.END, "\n错误信息:\n")
            log_text.insert(tk.END, stderr_output)
            log_text.see(tk.END)
        log_text.insert(tk.END, "运行结束。\n")
        #添加下载记录到表格
        record_table_entry()
    except Exception as e:
        log_text.insert(tk.END, f"发生错误: {e}\n")
    update_status()
def start_command_thread():
    #启动新的线程来运行命令
    #禁用下载按钮，避免重复点击
    add_button.config(state=tk.DISABLED,text='下载中...')
    thread = threading.Thread(target=run_command)
    thread.start()
#记录下载历史记录
def record_table_entry():
    MP4='.mp4'
    video_name = video_name_entry.get()+MP4
    save_path = save_path_entry.get()
    full_save_path = os.path.join(save_path, video_name)
    now = datetime.datetime.now()
    create_date_time = now.strftime('%Y-%m-%d %H:%M')
    if video_name and full_save_path:
        # 插入新记录到第一行
        table.insert("", 0, values=(1, video_name, full_save_path, create_date_time))
        # 更新所有行的序号
        update_sequence_numbers()
def clear_form():
  video_name_entry.delete(0, tk.END)
  save_path_entry.delete(0,tk.END)
  m3u8_entry.delete('1.0',tk.END)
def update_sequence_numbers():
    #更新序号
    for index, item in enumerate(table.get_children(), start=1):
        table.item(item, values=(index, *table.item(item, 'values')[1:]))
#打开文件夹选择窗口
def browse_directory():
    #打开文件选择对话框选择目录
    directory = filedialog.askdirectory()
    if directory:
        save_path_entry.delete(0, tk.END)
        save_path_entry.insert(0, directory)

# 创建主窗口
root = tk.Tk()
root.title("NMRG")

# 设置窗口为屏幕的 4/5
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)
x_position = (screen_width // 2) - (window_width // 2)
y_position = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# 配置行和列的权重
root.grid_rowconfigure(0, weight=2)  # 第一行占2/3
root.grid_rowconfigure(1, weight=1)  # 第二行占1/3

# 设置两列的权重为相等，以实现平均显示宽度
root.grid_columnconfigure(0, weight=1)  # 第一列权重1
root.grid_columnconfigure(1, weight=2)  # 第二列权重1

# 创建日志输入框（黑色背景）
log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="black", fg="green", state='normal',font=("Arial", 16),highlightthickness=0)
log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# 创建一个框架来包含用户名和密码输入框以及按钮
input_frame = ttk.Frame(root)
input_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

# 创建用户名和密码标签及输入框
video_name_label = tk.Label(input_frame, text="视频名称:")
video_name_label.grid(row=0, column=0, sticky="w", padx=5)

video_name_entry = tk.Entry(input_frame)
video_name_entry.grid(row=1, column=0, sticky="ew", padx=5)


save_path_label = tk.Label(input_frame, text="保存路径")
save_path_label.grid(row=2, column=0, sticky="w", padx=5)

save_path_entry = tk.Entry(input_frame)
save_path_entry.grid(row=3, column=0, sticky="ew", padx=5)

# 创建浏览目录按钮
download_button = tk.Button(input_frame, text="浏览", command=browse_directory)
download_button.grid(row=3, column=1, sticky="ew", padx=1)

m3u8_text_label = tk.Label(input_frame, text="m3u8文本")
m3u8_text_label.grid(row=4, column=0, sticky="w", padx=5)
m3u8_entry = scrolledtext.ScrolledText(input_frame,  wrap=tk.WORD, width=1, height=17,state='normal',font=("Arial", 16),highlightthickness=0)
m3u8_entry.grid(row=5, column=0, sticky="ew", padx=5)

add_button = tk.Button(input_frame, text="下载", command=start_command_thread)
add_button.grid(row=6, column=0, sticky="ew", padx=5, pady=(10, 0))

clear_button = tk.Button(input_frame, text="清空", command=clear_form)
clear_button.grid(row=6, column=1, sticky="ew", padx=5, pady=(10, 0))

# 将框架的列权重设置以保持横向可扩展性
input_frame.grid_columnconfigure(0, weight=1)  # 确保输入框和按钮可扩展

# 创建第二行的表格
frame = ttk.Frame(root)
frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
# 创建表格
columns = ("序号", "视频名称", "保存路径","创建时间")
table = ttk.Treeview(frame, columns=columns, show='headings', height=5)
table.heading("序号", text="序号")
table.heading("视频名称", text="视频名称")
table.heading("保存路径", text="保存路径")
table.heading("创建时间", text="创建时间")

# 创建滚动条
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
table.configure(yscroll=scrollbar.set)

# 放置表格和滚动条
table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 创建右键菜单
def delete_item():
    #删除选中的表格行
    selected_item = table.selection()
    for item in selected_item:
        table.delete(item)

def view_item():
    """查看选中的表格行的信息"""
    selected_item = table.selection()
    if selected_item:
        for item in selected_item:
            item_values = table.item(item, "values")
            if not os.path.exists(item_values[2]):
              messagebox.showwarning("警告", f"'{item_values[2]}' 视频不存在！")
              return
            if platform.system() == "Darwin":  # macOS
                subprocess.call(['open', item_values[2]])

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="浏览视频", command=view_item)
context_menu.add_command(label="删除历史记录", command=delete_item)

def show_context_menu(event):
    #弹出右键菜单
    try:
        table.selection_set(table.identify_row(event.y))
        context_menu.post(event.x_root, event.y_root)
    except Exception as e:
        pass  # 防止异常抛出

# 绑定双击事件和右键事件
table.bind("<Double-Button-1>", show_context_menu)
# 启动 Tkinter 主循环
root.mainloop()