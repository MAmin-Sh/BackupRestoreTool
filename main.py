import os
import re
import sys
import datetime
import subprocess
import threading
import psycopg2

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def register_custom_font(font_filename):
    font_path = resource_path(font_filename)
    if not os.path.exists(font_path):
        return "Segoe UI"

    if os.name == "nt":
        import ctypes
        AddFontResourceEx = ctypes.windll.gdi32.AddFontResourceExW
        font_added = AddFontResourceEx(font_path, 0x10, 0)
        if font_added > 0:
            ctypes.windll.user32.SendMessageTimeoutW(
                0xFFFF, 0x001D, 0, 0, 0x0002, 1000, None
            )

    try:
        available_fonts = tkfont.families()
        for f in available_fonts:
            if "vazir" in f.lower():
                return f
    except Exception:
        pass

    return "Vazirmatn"


FONT_FILE_NAME = "LMU-Vazir.ttf"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

LOG_FILE_TXT = os.path.join(os.path.dirname(__file__), "project_actions.txt")

TRANSLATIONS = {
    "fa": {
        "title": "سامانه مدیریت و پشتیبان‌گیری دیتابیس PostgreSQL",
        "header": "مدیریت و پشتیبان‌گیری PostgreSQL",
        "conn_title": "تنظیمات اتصال به سرور",
        "host": "میزبان (Host)",
        "port": "پورت",
        "user": "نام کاربری",
        "pass": "رمز عبور",
        "test_conn": "تست اتصال",
        "db_title": "مدیریت پایگاه داده target",
        "db_name": "نام دیتابیس",
        "db_select_placeholder": "انتخاب کنید...",
        "btn_refresh": "🔄 بروزرسانی",
        "btn_create_db": "➕ ایجاد دیتابیس",
        "btn_drop_db": "🗑️ حذف دیتابیس",
        "pg_version_lbl": "نسخه PostgreSQL سیستم",
        "btn_scan": "🔍 اسکن",
        "backup_file_lbl": "مسیر فایل پشتیبان",
        "btn_select_file": "انتخاب فایل",
        "file_placeholder": "مسیر فایل ذخیره یا بازیابی...",
        "btn_backup": "📥 تهیه پشتیبان (Backup)",
        "btn_restore": "📤 بازگردانی (Restore)",
        "status_ready": "v2.1.0",
        "terminal_title": "System Terminal Console (CMD)",
        "cmd_placeholder": "Type CMD command and press Enter...",
        "searching": "در حال جستجو...",
        "no_version_found": "هیچ نسخه‌ای یافت نشد",
        "add_custom_path": "➕ افزودن مسیر سفارشی...",
        "msg_success": "موفقیت",
        "msg_error": "خطا",
        "conn_success": "اتصال با موفقیت برقرار شد!",
        "conn_error": "برقراری ارتباط امکان‌پذیر نیست:\n",
        "db_fetched": "تعداد {count} دیتابیس دریافت شد.",
        "db_fetch_error": "دریافت لیست دیتابیس‌ها ناموفق بود:\n",
        "db_name_req": "لطفاً نام دیتابیس را وارد یا انتخاب کنید!",
        "backup_in_progress": "در حال تهیه نسخه پشتیبان...",
        "backup_success": "بکاپ با موفقیت انجام شد!\n",
        "backup_failed": "بکاپ شکست خورد!\n",
        "pg_dump_missing": "ابزار pg_dump پیدا نشد:\n",
        "restore_in_progress": "در حال بازیابی اطلاعات...",
        "restore_success": "بازگردانی با موفقیت انجام شد!",
        "restore_failed": "بازگردانی شکست خورد!\n",
        "drop_confirm_title": "تایید حذف",
        "drop_confirm_msg": "آیا از حذف دیتابیس '{dbname}' مطمئن هستید؟ این عملیات غیرقابل بازگشت است!",
        "drop_success": "دیتابیس {dbname} با موفقیت حذف شد!",
        "drop_failed": "حذف دیتابیس شکست خورد!\n",
        "create_success": "دیتابیس {dbname} ساخته شد!",
        "create_failed": "ساخت دیتابیس شکست خورد!\n",
        "custom_path_title": "انتخاب پوشه bin نسخه PostgreSQL",
        "custom_path_success": "مسیر سفارشی اضافه شد.",
        "custom_path_error": "فایل pg_dump در این پوشه یافت نشد!"
    },
    "en": {
        "title": "PostgreSQL Management & Backup Suite",
        "header": "PostgreSQL Backup & Management Tool",
        "conn_title": "Server Connection Settings",
        "host": "Host Address",
        "port": "Port",
        "user": "Username",
        "pass": "Password",
        "test_conn": "Test Connection",
        "db_title": "Target Database Management",
        "db_name": "Database Name",
        "db_select_placeholder": "Select Database...",
        "btn_refresh": "🔄 Refresh",
        "btn_create_db": "➕ Create DB",
        "btn_drop_db": "🗑️ Drop DB",
        "pg_version_lbl": "PostgreSQL Version",
        "btn_scan": "🔍 Scan",
        "backup_file_lbl": "Backup File Path",
        "btn_select_file": "Browse...",
        "file_placeholder": "Select file path for backup or restore...",
        "btn_backup": "📥 Take Backup",
        "btn_restore": "📤 Restore Data",
        "status_ready": "v2.1.0",
        "terminal_title": "System Terminal Console (CMD)",
        "cmd_placeholder": "Type CMD command and press Enter...",
        "searching": "Searching...",
        "no_version_found": "No versions found",
        "add_custom_path": "➕ Add Custom Path...",
        "msg_success": "Success",
        "msg_error": "Error",
        "conn_success": "Connection established successfully!",
        "conn_error": "Connection failed:\n",
        "db_fetched": "{count} databases retrieved.",
        "db_fetch_error": "Failed to retrieve databases:\n",
        "db_name_req": "Please enter or select a database name!",
        "backup_in_progress": "Creating backup...",
        "backup_success": "Backup completed successfully!\n",
        "backup_failed": "Backup failed!\n",
        "pg_dump_missing": "pg_dump tool not found:\n",
        "restore_in_progress": "Restoring data...",
        "restore_success": "Restore completed successfully!",
        "restore_failed": "Restore failed!\n",
        "drop_confirm_title": "Confirm Drop",
        "drop_confirm_msg": "Are you sure you want to drop database '{dbname}'? This action is irreversible!",
        "drop_success": "Database {dbname} dropped successfully!",
        "drop_failed": "Failed to drop database!\n",
        "create_success": "Database {dbname} created successfully!",
        "create_failed": "Failed to create database!\n",
        "custom_path_title": "Select PostgreSQL bin Directory",
        "custom_path_success": "Custom path added successfully.",
        "custom_path_error": "pg_dump file not found in this directory!"
    }
}


class BackupRestoreApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "fa"
        self.geometry("880x880")
        self.resizable(True, True)

        self.font_family = register_custom_font(FONT_FILE_NAME)
        self.f_header = ctk.CTkFont(family=self.font_family, size=16, weight="bold")
        self.f_card_title = ctk.CTkFont(family=self.font_family, size=12, weight="bold")
        self.f_label = ctk.CTkFont(family=self.font_family, size=10, weight="bold")
        self.f_input = ctk.CTkFont(family=self.font_family, size=11)
        self.f_button = ctk.CTkFont(family=self.font_family, size=11, weight="bold")
        self.f_status = ctk.CTkFont(family=self.font_family, size=10)
        self.f_console = ctk.CTkFont(family="Consolas", size=10)

        self.detected_pg_paths = {}
        self.terminal_cwd = os.path.abspath(os.path.dirname(__file__))

        self.init_ui()
        self.update_ui_language()
        self.detect_installed_pg_versions()

        self.log_to_terminal("Microsoft Windows [Version 10.0.19045.3803]")
        self.log_to_terminal("(c) Microsoft Corporation. All rights reserved.\n")
        self.log_to_terminal("[SYSTEM] Application initialized successfully.")

    def t(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def change_language(self, choice):
        self.current_lang = "fa" if choice == "فارسی" else "en"
        self.update_ui_language()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        self.header_frame.grid(row=0, column=0, padx=16, pady=(10, 4), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.lang_combo = ctk.CTkOptionMenu(
            self.header_frame, values=["فارسی", "English"], font=self.f_input,
            dropdown_font=self.f_input, width=100, height=30,
            command=self.change_language, fg_color="#334155", button_color="#475569"
        )
        self.header_title = ctk.CTkLabel(
            self.header_frame, text="", font=self.f_header, text_color="#F8FAFC"
        )

        # 2. Connection Settings Card
        self.conn_card = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        self.conn_card.grid(row=1, column=0, padx=16, pady=4, sticky="ew")

        self.conn_card_title = ctk.CTkLabel(self.conn_card, text="", font=self.f_card_title, text_color="#38BDF8")

        self.host_input, self.lbl_host = self._create_field(self.conn_card, "localhost")
        self.port_input, self.lbl_port = self._create_field(self.conn_card, "5432")
        self.user_input, self.lbl_user = self._create_field(self.conn_card, "postgres")
        self.password_input, self.lbl_pass = self._create_field(self.conn_card, "", is_pass=True)

        self.test_btn = ctk.CTkButton(
            self.conn_card, text="", font=self.f_button, height=32,
            fg_color="#059669", hover_color="#047857", command=self.test_connection
        )

        # 3. Database Target Card
        self.db_card = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        self.db_card.grid(row=2, column=0, padx=16, pady=4, sticky="ew")

        self.db_card_title = ctk.CTkLabel(self.db_card, text="", font=self.f_card_title, text_color="#38BDF8")
        self.lbl_db = ctk.CTkLabel(self.db_card, text="", font=self.f_label, text_color="#94A3B8")

        self.db_input = ctk.CTkComboBox(
            self.db_card, font=self.f_input, dropdown_font=self.f_input, height=32,
            values=[self.t("db_select_placeholder")]
        )
        self.fetch_db_btn = ctk.CTkButton(
            self.db_card, text="", font=self.f_button, height=32,
            fg_color="#334155", hover_color="#475569", command=self.fetch_databases
        )
        self.create_btn = ctk.CTkButton(
            self.db_card, text="", font=self.f_button, height=32,
            fg_color="#2563EB", hover_color="#1D4ED8", command=self.create_db
        )
        self.drop_btn = ctk.CTkButton(
            self.db_card, text="", font=self.f_button, height=32,
            fg_color="#DC2626", hover_color="#B91C1C", command=self.drop_db
        )

        # 4. System & File Config Card
        self.paths_card = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        self.paths_card.grid(row=3, column=0, padx=16, pady=4, sticky="ew")

        self.lbl_ver = ctk.CTkLabel(self.paths_card, text="", font=self.f_label, text_color="#94A3B8")
        self.pg_version_combo = ctk.CTkComboBox(
            self.paths_card, font=self.f_input, dropdown_font=self.f_input, height=32,
            values=[self.t("searching")], command=self._on_version_selected
        )
        self.scan_btn = ctk.CTkButton(
            self.paths_card, text="", font=self.f_button, height=32, width=80,
            fg_color="#334155", hover_color="#475569", command=self.detect_installed_pg_versions
        )

        self.lbl_file = ctk.CTkLabel(self.paths_card, text="", font=self.f_label, text_color="#94A3B8")
        self.backup_file_input = ctk.CTkEntry(self.paths_card, font=self.f_input, height=32)
        self.file_btn = ctk.CTkButton(
            self.paths_card, text="", font=self.f_button, height=32, width=80,
            fg_color="#334155", hover_color="#475569", command=self.select_backup_file
        )

        # 5. Actions Card
        self.action_card = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E293B")
        self.action_card.grid(row=4, column=0, padx=16, pady=4, sticky="ew")
        self.action_card.grid_columnconfigure((0, 1), weight=1, uniform="actions")

        self.backup_btn = ctk.CTkButton(
            self.action_card, text="", font=self.f_button, height=36,
            fg_color="#0D9488", hover_color="#0F766E",
            command=lambda: self._run_async(self.run_backup)
        )
        self.restore_btn = ctk.CTkButton(
            self.action_card, text="", font=self.f_button, height=36,
            fg_color="#D97706", hover_color="#B45309",
            command=lambda: self._run_async(self.run_restore)
        )

        # 6. Status & Progress
        self.status_label = ctk.CTkLabel(self, text="", font=self.f_status, text_color="#64748B")
        self.status_label.grid(row=5, column=0, padx=16, pady=(1, 0))

        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate", height=3)
        self.progress_bar.grid(row=6, column=0, padx=16, pady=(1, 4), sticky="ew")
        self.progress_bar.stop()

        # 7. Terminal CMD Console Card
        self.terminal_card = ctk.CTkFrame(self, corner_radius=10, fg_color="#0F172A")
        self.terminal_card.grid(row=7, column=0, padx=16, pady=(2, 10), sticky="nsew")
        self.terminal_card.grid_columnconfigure(0, weight=1)
        self.terminal_card.grid_rowconfigure(1, weight=1)

        self.terminal_title_lbl = ctk.CTkLabel(
            self.terminal_card, text="", font=self.f_card_title, text_color="#38BDF8"
        )
        self.terminal_title_lbl.grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")

        # جعبه متنی ترمینال
        self.terminal_box = ctk.CTkTextbox(
            self.terminal_card, font=self.f_console, fg_color="#000000", text_color="#22C55E",
            corner_radius=6, wrap="word", activate_scrollbars=True
        )
        self.terminal_box.grid(row=1, column=0, padx=8, pady=(0, 6), sticky="nsew")

        # ورودی دستورات CMD
        self.cmd_input = ctk.CTkEntry(
            self.terminal_card, font=self.f_console, fg_color="#020617", text_color="#F8FAFC",
            height=30, placeholder_text=""
        )
        self.cmd_input.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="ew")
        self.cmd_input.bind("<Return>", self.execute_cmd_command)

        # میانبر کیبورد برای اسکرول
        self.cmd_input.bind("<Prior>", lambda e: self.terminal_box.yview_scroll(-1, "pages"))
        self.cmd_input.bind("<Next>", lambda e: self.terminal_box.yview_scroll(1, "pages"))

    def _create_field(self, parent, default_val, is_pass=False):
        lbl = ctk.CTkLabel(parent, text="", font=self.f_label, text_color="#94A3B8")
        entry = ctk.CTkEntry(parent, font=self.f_input, height=32, show="*" if is_pass else "")
        entry.insert(0, default_val)
        return entry, lbl

    def update_ui_language(self):
        is_fa = self.current_lang == "fa"
        anchor_align = "e" if is_fa else "w"

        self.title(self.t("title"))
        self.header_title.configure(text=self.t("header"))

        self.lang_combo.grid(row=0, column=0 if is_fa else 1, padx=12, pady=6)
        self.header_title.grid(row=0, column=1 if is_fa else 0, padx=12, pady=6, sticky="w" if not is_fa else "e")

        for i in range(4):
            self.conn_card.grid_columnconfigure(i, weight=1, uniform="conn")

        self.conn_card_title.configure(text=self.t("conn_title"), anchor=anchor_align)
        self.conn_card_title.grid(row=0, column=0, columnspan=4, padx=12, pady=(6, 2), sticky="ew")

        fields = [
            (self.lbl_host, self.host_input, "host"),
            (self.lbl_port, self.port_input, "port"),
            (self.lbl_user, self.user_input, "user"),
            (self.lbl_pass, self.password_input, "pass"),
        ]

        ordered_fields = [fields[1], fields[0], fields[3], fields[2]] if is_fa else fields

        ordered_fields[0][0].configure(text=self.t(ordered_fields[0][2]), anchor=anchor_align)
        ordered_fields[0][0].grid(row=1, column=0, padx=(12, 4), pady=(1, 1), sticky="ew")
        ordered_fields[0][1].grid(row=2, column=0, padx=(12, 6), pady=(0, 6), sticky="ew")

        ordered_fields[1][0].configure(text=self.t(ordered_fields[1][2]), anchor=anchor_align)
        ordered_fields[1][0].grid(row=1, column=1, padx=4, pady=(1, 1), sticky="ew")
        ordered_fields[1][1].grid(row=2, column=1, padx=4, pady=(0, 6), sticky="ew")

        ordered_fields[2][0].configure(text=self.t(ordered_fields[2][2]), anchor=anchor_align)
        ordered_fields[2][0].grid(row=3, column=0, padx=(12, 4), pady=(1, 1), sticky="ew")
        ordered_fields[2][1].grid(row=4, column=0, padx=(12, 6), pady=(0, 8), sticky="ew")

        ordered_fields[3][0].configure(text=self.t(ordered_fields[3][2]), anchor=anchor_align)
        ordered_fields[3][0].grid(row=3, column=1, padx=4, pady=(1, 1), sticky="ew")
        ordered_fields[3][1].grid(row=4, column=1, padx=4, pady=(0, 8), sticky="ew")

        self.test_btn.configure(text=self.t("test_conn"))
        self.test_btn.grid(row=4, column=2 if is_fa else 3, padx=12, pady=(0, 8), sticky="ew")

        for i in range(4):
            self.db_card.grid_columnconfigure(i, weight=1, uniform="db")

        self.db_card_title.configure(text=self.t("db_title"), anchor=anchor_align)
        self.db_card_title.grid(row=0, column=0, columnspan=4, padx=12, pady=(6, 2), sticky="ew")

        self.lbl_db.configure(text=self.t("db_name"), anchor=anchor_align)
        self.lbl_db.grid(row=1, column=0 if not is_fa else 3, padx=12, pady=(1, 1), sticky="ew")

        if is_fa:
            self.db_input.grid(row=2, column=3, padx=(6, 12), pady=(0, 8), sticky="ew")
            self.fetch_db_btn.grid(row=2, column=2, padx=4, pady=(0, 8), sticky="ew")
            self.create_btn.grid(row=2, column=1, padx=4, pady=(0, 8), sticky="ew")
            self.drop_btn.grid(row=2, column=0, padx=(12, 4), pady=(0, 8), sticky="ew")
        else:
            self.db_input.grid(row=2, column=0, padx=(12, 4), pady=(0, 8), sticky="ew")
            self.fetch_db_btn.grid(row=2, column=1, padx=4, pady=(0, 8), sticky="ew")
            self.create_btn.grid(row=2, column=2, padx=4, pady=(0, 8), sticky="ew")
            self.drop_btn.grid(row=2, column=3, padx=(4, 12), pady=(0, 8), sticky="ew")

        self.fetch_db_btn.configure(text=self.t("btn_refresh"))
        self.create_btn.configure(text=self.t("btn_create_db"))
        self.drop_btn.configure(text=self.t("btn_drop_db"))

        self.paths_card.grid_columnconfigure(0, weight=1)
        self.paths_card.grid_columnconfigure(1, weight=0)

        self.lbl_ver.configure(text=self.t("pg_version_lbl"), anchor=anchor_align)
        self.lbl_ver.grid(row=0, column=0, columnspan=2, padx=12, pady=(6, 1), sticky="ew")

        if is_fa:
            self.pg_version_combo.grid(row=1, column=0, padx=(6, 12), pady=(0, 4), sticky="ew")
            self.scan_btn.grid(row=1, column=1, padx=(12, 4), pady=(0, 4), sticky="ew")
        else:
            self.pg_version_combo.grid(row=1, column=0, padx=(12, 4), pady=(0, 4), sticky="ew")
            self.scan_btn.grid(row=1, column=1, padx=(4, 12), pady=(0, 4), sticky="ew")

        self.scan_btn.configure(text=self.t("btn_scan"))

        self.lbl_file.configure(text=self.t("backup_file_lbl"), anchor=anchor_align)
        self.lbl_file.grid(row=2, column=0, columnspan=2, padx=12, pady=(1, 1), sticky="ew")
        self.backup_file_input.configure(placeholder_text=self.t("file_placeholder"))

        if is_fa:
            self.backup_file_input.grid(row=3, column=0, padx=(6, 12), pady=(0, 8), sticky="ew")
            self.file_btn.grid(row=3, column=1, padx=(12, 4), pady=(0, 8), sticky="ew")
        else:
            self.backup_file_input.grid(row=3, column=0, padx=(12, 4), pady=(0, 8), sticky="ew")
            self.file_btn.grid(row=3, column=1, padx=(4, 12), pady=(0, 8), sticky="ew")

        self.file_btn.configure(text=self.t("btn_select_file"))

        self.backup_btn.configure(text=self.t("btn_backup"))
        self.restore_btn.configure(text=self.t("btn_restore"))

        if is_fa:
            self.backup_btn.grid(row=0, column=1, padx=(4, 12), pady=6, sticky="ew")
            self.restore_btn.grid(row=0, column=0, padx=(12, 4), pady=6, sticky="ew")
        else:
            self.backup_btn.grid(row=0, column=0, padx=(12, 4), pady=6, sticky="ew")
            self.restore_btn.grid(row=0, column=1, padx=(4, 12), pady=6, sticky="ew")

        self.status_label.configure(text=self.t("status_ready"))

        self.terminal_title_lbl.configure(text=self.t("terminal_title"), anchor=anchor_align)
        self.cmd_input.configure(placeholder_text=self.t("cmd_placeholder"))

    def log_to_terminal(self, text):
        def _append():
            self.terminal_box.configure(state="normal")
            self.terminal_box.insert("end", text + "\n")
            self.terminal_box.see("end")
            self.terminal_box.configure(state="disabled")

        self.after(0, _append)
        write_log(text)

    def execute_cmd_command(self, event=None):
        command = self.cmd_input.get().strip()
        if not command:
            return

        self.cmd_input.delete(0, "end")
        self.log_to_terminal(f"\n{self.terminal_cwd}> {command}")

        if command.lower() in ["cls", "clear"]:
            self.terminal_box.configure(state="normal")
            self.terminal_box.delete("1.0", "end")
            self.terminal_box.configure(state="disabled")
            return

        cd_match = re.match(r'^\s*cd\s+(.*)$', command, re.IGNORECASE)
        if cd_match:
            target = cd_match.group(1).strip().strip('"')
            if not target or target == ".":
                pass
            else:
                new_dir = target if os.path.isabs(target) else os.path.join(self.terminal_cwd, target)
                new_dir = os.path.normpath(new_dir)
                if os.path.isdir(new_dir):
                    self.terminal_cwd = new_dir
                    self.log_to_terminal(f"[INFO] Current directory changed to: {self.terminal_cwd}")
                else:
                    self.log_to_terminal(f"[ERROR] The system cannot find the path specified: {new_dir}")
            return

        def _run_cmd():
            try:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True,
                    timeout=30, cwd=self.terminal_cwd
                )
                if result.stdout:
                    self.log_to_terminal(result.stdout.strip())
                if result.stderr:
                    self.log_to_terminal(f"[ERROR] {result.stderr.strip()}")
            except Exception as e:
                self.log_to_terminal(f"[EXCEPTION] {e}")

        threading.Thread(target=_run_cmd, daemon=True).start()

    def detect_installed_pg_versions(self):
        self.detected_pg_paths.clear()

        common_subdirs = [
            r"Program Files\PostgreSQL",
            r"Program Files (x86)\PostgreSQL",
            r"PostgreSQL",
            r"PostgreSQL\bin"
        ]

        if os.name == "nt":
            import string
            from ctypes import windll

            available_drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    available_drives.append(f"{letter}:\\")
                bitmask >>= 1

            for drive in available_drives:
                for subdir in common_subdirs:
                    target_dir = os.path.join(drive, subdir)
                    if not os.path.exists(target_dir):
                        continue

                    pg_dump_name = "pg_dump.exe"
                    if os.path.isfile(os.path.join(target_dir, pg_dump_name)):
                        display_name = f"PostgreSQL Custom ({target_dir})"
                        self.detected_pg_paths[display_name] = target_dir
                        continue

                    try:
                        for item in os.listdir(target_dir):
                            bin_path = os.path.join(target_dir, item, "bin")
                            if os.path.isfile(os.path.join(bin_path, pg_dump_name)):
                                display_name = f"PostgreSQL v.{item} ({drive[0]})"
                                self.detected_pg_paths[display_name] = bin_path
                    except Exception as e:
                        print(f"Error reading directory {target_dir}: {e}")
        else:
            base_dir = "/usr/lib/postgresql"
            if os.path.exists(base_dir):
                try:
                    for item in os.listdir(base_dir):
                        bin_path = os.path.join(base_dir, item, "bin")
                        if os.path.isfile(os.path.join(bin_path, "pg_dump")):
                            self.detected_pg_paths[f"PostgreSQL v{item}"] = bin_path
                except Exception as e:
                    print(f"Error scanning PG versions: {e}")

        if self.detected_pg_paths:
            version_names = list(self.detected_pg_paths.keys())
            version_names.append(self.t("add_custom_path"))
            self.pg_version_combo.configure(values=version_names)
            self.pg_version_combo.set(version_names[0])
            self.log_to_terminal(f"[INFO] Detected {len(self.detected_pg_paths)} PostgreSQL installation(s).")
            self._cd_terminal_to(self.detected_pg_paths[version_names[0]])
        else:
            self.pg_version_combo.configure(values=[self.t("no_version_found")])
            self.pg_version_combo.set(self.t("no_version_found"))
            self.log_to_terminal("[WARNING] No PostgreSQL installation detected automatically.")

    def _cd_terminal_to(self, path):
        if path and os.path.isdir(path) and os.path.normpath(path) != os.path.normpath(self.terminal_cwd):
            self.terminal_cwd = os.path.normpath(path)
            self.log_to_terminal(f"\n{self.terminal_cwd}> cd \"{self.terminal_cwd}\"")
            self.log_to_terminal(f"[INFO] Terminal directory switched to: {self.terminal_cwd}")

    def _on_version_selected(self, choice):
        if choice in [self.t("add_custom_path"), self.t("no_version_found")]:
            folder = filedialog.askdirectory(title=self.t("custom_path_title"))
            if folder:
                pg_dump_name = "pg_dump.exe" if os.name == "nt" else "pg_dump"
                if os.path.isfile(os.path.join(folder, pg_dump_name)):
                    custom_label = f"Custom: {folder}"
                    self.detected_pg_paths[custom_label] = folder

                    current_values = list(self.detected_pg_paths.keys())
                    if self.t("add_custom_path") not in current_values:
                        current_values.append(self.t("add_custom_path"))

                    self.pg_version_combo.configure(values=current_values)
                    self.pg_version_combo.set(custom_label)
                    self.log_to_terminal(f"[INFO] Added custom bin path: {folder}")
                    messagebox.showinfo(self.t("msg_success"), self.t("custom_path_success"))
                    self._cd_terminal_to(folder)
                else:
                    self.log_to_terminal(f"[ERROR] Invalid bin path selected: {folder}")
                    messagebox.showerror(self.t("msg_error"), self.t("custom_path_error"))
                    self.detect_installed_pg_versions()
            else:
                self.detect_installed_pg_versions()
        elif choice in self.detected_pg_paths:
            self._cd_terminal_to(self.detected_pg_paths[choice])

    def get_selected_bin_path(self):
        selected = self.pg_version_combo.get()
        if selected in self.detected_pg_paths:
            return self.detected_pg_paths[selected]

        for i in range(11, 25):
            path = fr"C:\Program Files\PostgreSQL\{i}\bin"
            pg_dump_exe = os.path.join(path, "pg_dump.exe" if os.name == "nt" else "pg_dump")
            if os.path.isfile(pg_dump_exe):
                return path
        return ""

    def _conn_args(self):
        args = []
        host = self.host_input.get().strip()
        if host: args += ["-h", host]
        port = self.port_input.get().strip()
        if port: args += ["-p", port]
        user = self.user_input.get().strip()
        if user: args += ["-U", user]
        return args

    def _start_loading(self, message):
        self.status_label.configure(text=message, text_color="#38BDF8")
        self.progress_bar.start()

    def _stop_loading(self, message=None, is_error=False):
        if message is None:
            message = self.t("status_ready")
        self.progress_bar.stop()
        color = "#EF4444" if is_error else "#64748B"
        self.status_label.configure(text=message, text_color=color)

    def _run_async(self, target_func):
        threading.Thread(target=target_func, daemon=True).start()

    def fetch_databases(self):
        self.log_to_terminal("[ACTION] Fetching database list from server...")
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.user_input.get().strip(),
                password=self.password_input.get(),
                host=self.host_input.get().strip() or "localhost",
                port=self.port_input.get().strip() or "5432",
                connect_timeout=3
            )
            cur = conn.cursor()
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
            db_list = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()

            if db_list:
                self.db_input.configure(values=db_list)
                current = self.db_input.get().strip()
                if not current or current not in db_list:
                    self.db_input.set(db_list[0])
                self.log_to_terminal(f"[SUCCESS] Retrieved {len(db_list)} databases.")
                messagebox.showinfo(self.t("msg_success"), self.t("db_fetched").format(count=len(db_list)))
        except Exception as e:
            self.log_to_terminal(f"[ERROR] Failed to fetch databases: {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('db_fetch_error')}{e}")

    def test_connection(self):
        self.log_to_terminal("[ACTION] Testing database connection...")
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.user_input.get().strip(),
                password=self.password_input.get(),
                host=self.host_input.get().strip() or "localhost",
                port=self.port_input.get().strip() or "5432",
                connect_timeout=3
            )
            conn.close()
            self.log_to_terminal("[SUCCESS] Database connection successful.")
            messagebox.showinfo(self.t("msg_success"), self.t("conn_success"))
            self.fetch_databases()
        except Exception as e:
            self.log_to_terminal(f"[ERROR] Connection failed: {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('conn_error')}{e}")

    def select_backup_file(self):
        path = filedialog.asksaveasfilename(title=self.t("btn_select_file"), filetypes=[("All Files", "*.*")])
        if path:
            self.backup_file_input.delete(0, "end")
            self.backup_file_input.insert(0, path)
            self.log_to_terminal(f"[INFO] Backup path set to: {path}")

    def run_backup(self):
        dbname = self.db_input.get().strip()
        if not dbname or dbname == self.t("db_select_placeholder"):
            self.log_to_terminal("[WARNING] Backup aborted: No target database specified.")
            messagebox.showerror(self.t("msg_error"), self.t("db_name_req"))
            return

        self._start_loading(self.t("backup_in_progress"))
        self.log_to_terminal(f"[ACTION] Starting backup process for database: {dbname}")

        bin_path = self.get_selected_bin_path()
        pg_dump_exe = os.path.join(bin_path, "pg_dump.exe" if os.name == "nt" else "pg_dump")

        if not os.path.isfile(pg_dump_exe):
            self._stop_loading(self.t("pg_dump_missing"), is_error=True)
            self.log_to_terminal(f"[ERROR] pg_dump not found at path: {pg_dump_exe}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('pg_dump_missing')}{pg_dump_exe}")
            return

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password_input.get()

        project_root = os.path.dirname(os.path.abspath(__file__))
        backup_folder = os.path.join(project_root, "backup")
        os.makedirs(backup_folder, exist_ok=True)
        default_backup_file = os.path.join(
            backup_folder, f"{dbname}_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.dump"
        )

        path = filedialog.asksaveasfilename(
            title=self.t("btn_backup"),
            initialfile=os.path.basename(default_backup_file),
            initialdir=backup_folder,
            filetypes=[("All Files", "*.*")]
        )
        if not path:
            path = default_backup_file

        self.backup_file_input.delete(0, "end")
        self.backup_file_input.insert(0, path)

        try:
            cmd = [pg_dump_exe] + self._conn_args() + ["-F", "c", "-f", path, dbname]
            self.log_to_terminal(f"[EXEC] {' '.join(cmd)}")
            subprocess.run(cmd, check=True, env=env)
            self._stop_loading()
            self.log_to_terminal(f"[SUCCESS] Backup saved successfully to: {path}")
            messagebox.showinfo(self.t("msg_success"), f"{self.t('backup_success')}{path}")
        except subprocess.CalledProcessError as e:
            self._stop_loading(self.t("msg_error"), is_error=True)
            self.log_to_terminal(f"[ERROR] Backup process failed: {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('backup_failed')}{e}")

    def run_restore(self):
        dbname = self.db_input.get().strip()
        if not dbname or dbname == self.t("db_select_placeholder"):
            self.log_to_terminal("[WARNING] Restore aborted: No target database specified.")
            messagebox.showerror(self.t("msg_error"), self.t("db_name_req"))
            return

        backup_file = filedialog.askopenfilename(title=self.t("btn_restore"), filetypes=[("All Files", "*.*")])
        if not backup_file:
            return

        self._start_loading(self.t("restore_in_progress"))
        self.log_to_terminal(f"[ACTION] Restoring database '{dbname}' from: {backup_file}")

        bin_path = self.get_selected_bin_path()
        pg_restore_exe = os.path.join(bin_path, "pg_restore.exe" if os.name == "nt" else "pg_restore")
        psql_exe = os.path.join(bin_path, "psql.exe" if os.name == "nt" else "psql")
        missing = [exe for exe in (pg_restore_exe, psql_exe) if not os.path.isfile(exe)]

        if missing:
            self._stop_loading(self.t("msg_error"), is_error=True)
            self.log_to_terminal(f"[ERROR] Missing PostgreSQL tools: {missing}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('pg_dump_missing')}\n" + "\n".join(missing))
            return

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password_input.get()

        temp_sql = os.path.join(os.path.dirname(__file__), f"{dbname}_temp_restore.sql")
        processed_sql = os.path.join(os.path.dirname(__file__), f"{dbname}_processed.sql")

        try:
            self.log_to_terminal("[EXEC] Extracting SQL statements from dump...")
            subprocess.run([pg_restore_exe] + self._conn_args() + ["-f", temp_sql, backup_file],
                           check=True, env=env)
        except subprocess.CalledProcessError as e:
            self._stop_loading(self.t("msg_error"), is_error=True)
            self.log_to_terminal(f"[ERROR] Restore failed on SQL extraction: {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('restore_failed')}{e}")
            return

        with open(temp_sql, "r", encoding="utf-8") as f_in, open(processed_sql, "w", encoding="utf-8") as f_out:
            for line in f_in:
                create_match = re.match(r'CREATE TABLE (\S+)', line, re.IGNORECASE)
                if create_match:
                    table_name = create_match.group(1)
                    f_out.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                    continue

                insert_match = re.match(r'(INSERT INTO .+?)\s+VALUES\s*(\(.*\));', line, re.IGNORECASE)
                if insert_match:
                    f_out.write(f"{insert_match.group(1)} VALUES {insert_match.group(2)} ON CONFLICT DO NOTHING;\n")
                else:
                    f_out.write(line)

        try:
            self.log_to_terminal(f"[EXEC] Executing safe restore query into database '{dbname}'...")
            subprocess.run([psql_exe] + self._conn_args() + ["-d", dbname, "-f", processed_sql],
                           check=True, env=env)
            self._stop_loading()
            self.log_to_terminal(f"[SUCCESS] Restore completed successfully for '{dbname}'.")
            messagebox.showinfo(self.t("msg_success"), self.t("restore_success"))
        except subprocess.CalledProcessError as e:
            self._stop_loading(self.t("msg_error"), is_error=True)
            self.log_to_terminal(f"[ERROR] Restore execution failed: {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('restore_failed')}{e}")
        finally:
            if os.path.exists(temp_sql): os.remove(temp_sql)
            if os.path.exists(processed_sql): os.remove(processed_sql)

    def drop_db(self):
        dbname = self.db_input.get().strip()
        if not dbname or dbname == self.t("db_select_placeholder"):
            self.log_to_terminal("[WARNING] Drop DB aborted: No database selected.")
            messagebox.showerror(self.t("msg_error"), self.t("db_name_req"))
            return

        if not messagebox.askyesno(self.t("drop_confirm_title"), self.t("drop_confirm_msg").format(dbname=dbname)):
            return

        self.log_to_terminal(f"[ACTION] Dropping database '{dbname}'...")
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.user_input.get().strip(),
                password=self.password_input.get(),
                host=self.host_input.get().strip() or "localhost",
                port=self.port_input.get().strip() or "5432"
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f'DROP DATABASE IF EXISTS "{dbname}";')
            cur.close()
            conn.close()
            self.log_to_terminal(f"[SUCCESS] Database '{dbname}' dropped.")
            messagebox.showinfo(self.t("msg_success"), self.t("drop_success").format(dbname=dbname))
            self.fetch_databases()
        except Exception as e:
            self.log_to_terminal(f"[ERROR] Failed to drop database '{dbname}': {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('drop_failed')}{e}")

    def create_db(self):
        dbname = self.db_input.get().strip()
        if not dbname or dbname == self.t("db_select_placeholder"):
            self.log_to_terminal("[WARNING] Create DB aborted: No database name supplied.")
            messagebox.showerror(self.t("msg_error"), self.t("db_name_req"))
            return

        self.log_to_terminal(f"[ACTION] Creating database '{dbname}'...")
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.user_input.get().strip(),
                password=self.password_input.get(),
                host=self.host_input.get().strip() or "localhost",
                port=self.port_input.get().strip() or "5432"
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f'CREATE DATABASE "{dbname}";')
            cur.close()
            conn.close()
            self.log_to_terminal(f"[SUCCESS] Database '{dbname}' created.")
            messagebox.showinfo(self.t("msg_success"), self.t("create_success").format(dbname=dbname))
            self.fetch_databases()
        except Exception as e:
            self.log_to_terminal(f"[ERROR] Failed to create database '{dbname}': {e}")
            messagebox.showerror(self.t("msg_error"), f"{self.t('create_failed')}{e}")


def write_log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE_TXT, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception as e:
        print(f"Error writing log file: {e}")


if __name__ == "__main__":
    app = BackupRestoreApp()
    app.mainloop()