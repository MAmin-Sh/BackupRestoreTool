import os
import sys
import re
import subprocess
import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QFileDialog, QMessageBox
)
import psycopg2

LOG_FILE_TXT = os.path.join(os.path.dirname(__file__), "project_actions.txt")


def write_log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE_TXT, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


class BackupRestoreTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ابزار حرفه‌ای پشتیبان‌گیری و بازگردانی PostgreSQL")
        self.setFixedSize(750, 480)
        self.setLayoutDirection(Qt.RightToLeft)
        self.font = QFont("B Nazanin", 10)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)

        # Labels
        labels_text = [
            "میزبان (Host):",
            "پورت (اختیاری):",
            "نام دیتابیس:",
            "کاربر:",
            "رمز عبور:",
            "فایل پشتیبان:",
            "مسیر فایل‌های اجرایی PostgreSQL:"
        ]
        self.labels = []
        for i, text in enumerate(labels_text):
            lbl = QLabel(text)
            lbl.setFont(self.font)
            lbl.setAlignment(Qt.AlignRight)
            self.labels.append(lbl)
            layout.addWidget(lbl, i, 0)

        # Inputs
        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit()
        self.db_input = QLineEdit()
        self.user_input = QLineEdit("postgres")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.backup_file_input = QLineEdit()
        self.bin_path_input = QLineEdit()

        inputs = [
            self.host_input, self.port_input, self.db_input, self.user_input,
            self.password_input, self.backup_file_input, self.bin_path_input
        ]
        for i, inp in enumerate(inputs):
            inp.setFont(self.font)
            layout.addWidget(inp, i, 1)

        # Buttons
        bin_btn = QPushButton("انتخاب مسیر فایل‌های اجرایی")
        bin_btn.setFont(self.font)
        bin_btn.clicked.connect(self.select_bin_path)
        layout.addWidget(bin_btn, 6, 2)

        file_btn = QPushButton("انتخاب فایل پشتیبان")
        file_btn.setFont(self.font)
        file_btn.clicked.connect(self.select_backup_file)
        layout.addWidget(file_btn, 5, 2)

        backup_btn = QPushButton("تهیه پشتیبان حرفه‌ای")
        backup_btn.setFont(self.font)
        backup_btn.clicked.connect(self.run_backup)

        restore_btn = QPushButton("بازگردانی امن")
        restore_btn.setFont(self.font)
        restore_btn.clicked.connect(self.run_restore)

        drop_btn = QPushButton("پاک کردن دیتابیس")
        drop_btn.setFont(self.font)
        drop_btn.clicked.connect(self.drop_db)

        create_btn = QPushButton("ساخت دیتابیس جدید")
        create_btn.setFont(self.font)
        create_btn.clicked.connect(self.create_db)
        layout.addWidget(create_btn, 2, 2)
        layout.addWidget(drop_btn, 1, 2)

        exit_btn = QPushButton("خروج")
        exit_btn.setFont(self.font)
        exit_btn.clicked.connect(self.close)

        layout.addWidget(backup_btn, 8, 0)
        layout.addWidget(restore_btn, 8, 1)
        layout.addWidget(drop_btn, 8, 2)
        layout.addWidget(exit_btn, 9, 1)

        self.setLayout(layout)

    def select_backup_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "انتخاب فایل پشتیبان", "", "Backup Files (*.dump)"
        )
        if path:
            self.backup_file_input.setText(path)

    def select_bin_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, "انتخاب مسیر فایل‌های اجرایی PostgreSQL"
        )
        if folder:
            self.bin_path_input.setText(folder)

    def _conn_args(self):
        args = []
        host = self.host_input.text().strip()
        if host: args += ["-h", host]
        port = self.port_input.text().strip()
        if port: args += ["-p", port]
        user = self.user_input.text().strip()
        if user: args += ["-U", user]
        return args

    def run_backup(self):
        dbname = self.db_input.text().strip()
        if not dbname:
            QMessageBox.critical(self, "خطا", "لطفاً نام دیتابیس را وارد کنید!")
            return

        bin_path = self.bin_path_input.text().strip()
        if not bin_path:
            bin_path = r"C:\Program Files\PostgreSQL\15\bin"

        pg_dump_exe = os.path.join(bin_path, "pg_dump.exe" if os.name == "nt" else "pg_dump")
        if not os.path.isfile(pg_dump_exe):
            QMessageBox.critical(self, "خطا", f"ابزار pg_dump پیدا نشد:\n{pg_dump_exe}")
            write_log(f"Backup failed: pg_dump not found at {pg_dump_exe}")
            return

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password_input.text()

        project_root = os.path.dirname(os.path.abspath(__file__))
        backup_folder = os.path.join(project_root, "backup")
        os.makedirs(backup_folder, exist_ok=True)
        default_backup_file = os.path.join(
            backup_folder, f"{dbname}_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.dump"
        )
        path, _ = QFileDialog.getSaveFileName(
            self, "انتخاب فایل پشتیبان", default_backup_file, "Backup Files (*.dump)"
        )
        if not path:
            path = default_backup_file
        self.backup_file_input.setText(path)

        try:
            subprocess.run([pg_dump_exe] + self._conn_args() + ["-F", "c", "-f", path, dbname],
                           check=True, env=env)
            QMessageBox.information(self, "موفقیت", f"بکاپ با موفقیت انجام شد!\n{path}")
            write_log(f"Backup of {dbname} done successfully: {path}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "خطا", f"بکاپ شکست خورد!\n{e}")
            write_log(f"Backup of {dbname} failed: {e}")

    def run_restore(self):
        dbname = self.db_input.text().strip()
        if not dbname:
            QMessageBox.critical(self, "خطا", "لطفاً نام دیتابیس را وارد کنید!")
            return

        backup_file, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل پشتیبان برای بازگردانی", "", "Backup Files (*.dump)"
        )
        if not backup_file:
            return

        bin_path = self.bin_path_input.text().strip()
        if not bin_path:
            bin_path = r"C:\Program Files\PostgreSQL\15\bin"

        pg_restore_exe = os.path.join(bin_path, "pg_restore.exe" if os.name == "nt" else "pg_restore")
        psql_exe = os.path.join(bin_path, "psql.exe" if os.name == "nt" else "psql")
        missing = [exe for exe in (pg_restore_exe, psql_exe) if not os.path.isfile(exe)]
        if missing:
            QMessageBox.critical(self, "خطا", "ابزارهای PostgreSQL پیدا نشد:\n" + "\n".join(missing))
            write_log(f"Restore failed: PostgreSQL tools missing {missing}")
            return

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password_input.text()

        temp_sql = os.path.join(os.path.dirname(__file__), f"{dbname}_temp_restore.sql")
        processed_sql = os.path.join(os.path.dirname(__file__), f"{dbname}_processed.sql")
        try:
            subprocess.run([pg_restore_exe] + self._conn_args() + ["-f", temp_sql, backup_file],
                           check=True, env=env)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "خطا", f"تبدیل بکاپ به SQL شکست خورد!\n{e}")
            write_log(f"Restore failed converting to SQL: {e}")
            return

        with open(temp_sql, "r", encoding="utf-8") as f_in, open(processed_sql, "w", encoding="utf-8") as f_out:
            for line in f_in:
                # CREATE TABLE
                create_match = re.match(r'CREATE TABLE (\S+)', line, re.IGNORECASE)
                if create_match:
                    table_name = create_match.group(1)
                    f_out.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                    continue

                # INSERT INTO
                insert_match = re.match(r'(INSERT INTO .+?)\s+VALUES\s*(\(.*\));', line, re.IGNORECASE)
                if insert_match:
                    f_out.write(f"{insert_match.group(1)} VALUES {insert_match.group(2)} ON CONFLICT DO NOTHING;\n")
                else:
                    f_out.write(line)

        try:
            subprocess.run([psql_exe] + self._conn_args() + ["-d", dbname, "-f", processed_sql],
                           check=True, env=env)
            QMessageBox.information(self, "موفقیت", "بازگردانی امن با موفقیت انجام شد!")
            write_log(f"Restore of {dbname} done successfully from {backup_file}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "خطا", f"بازگردانی شکست خورد!\n{e}")
            write_log(f"Restore of {dbname} failed: {e}")
        finally:
            if os.path.exists(temp_sql): os.remove(temp_sql)
            if os.path.exists(processed_sql): os.remove(processed_sql)


    def drop_db(self):
        dbname = self.db_input.text().strip()
        if not dbname:
            QMessageBox.critical(self, "خطا", "لطفاً نام دیتابیس را وارد کنید!")
            return
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.user_input.text(),
                password=self.password_input.text(),
                host=self.host_input.text() or "localhost",
                port=self.port_input.text() or "5432"
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"DROP DATABASE IF EXISTS {dbname};")
            cur.close()
            conn.close()
            QMessageBox.information(self, "موفقیت", f"Database {dbname} دراپ شد!")
            write_log(f"Database {dbname} dropped ✅")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"دراپ دیتابیس شکست خورد!\n{e}")
            print(f"Error dropping DB {dbname}: {e}")

    def create_db(self):
        dbname = self.db_input.text().strip()
        if not dbname:
            QMessageBox.critical(self, "خطا", "لطفاً نام دیتابیس را وارد کنید!")
            return
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.user_input.text(),
                password=self.password_input.text(),
                host=self.host_input.text() or "localhost",
                port=self.port_input.text() or "5432"
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE {dbname};")
            cur.close()
            conn.close()
            QMessageBox.information(self, "موفقیت", f"Database {dbname} ساخته شد!")
            print(f"Database {dbname} created ✅")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ساخت دیتابیس شکست خورد!\n{e}")
            write_log(f"Error creating DB {dbname}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupRestoreTool()
    window.show()
    sys.exit(app.exec_())
