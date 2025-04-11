import sys
import base64
import google.generativeai as gmai
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel,
    QFileDialog, QLineEdit, QTextEdit, QScrollBar, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from PIL import Image
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import webbrowser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    QMessageBox.critical(None, "Error", "API key not found. Please create a .env file with GEMINI_API_KEY.")
    sys.exit(1)

gmai.configure(api_key=api_key)

class MathSolverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.custom_responses = {
            "hi": "<b>Hey there! 👋 Ready to solve some math?</b>",
            "hello": "<b>Hello! Let's get solving 📂</b>",
            "hii": "<b>Hi! 😊 Please enter your math question.</b>",
            "thanks": "<b>You're welcome! Happy to help ✨</b>",
            "thank you": "<b>Anytime! 🙌</b>",
            "who made you": "<b>I was built by Krishna 🚀</b>",
            "who are you": "<b>I'm your friendly AI Math Solver 🤖💡</b>",
            "hey": "<b>Hey! 😊 How can I help you today?</b>",
            "good morning": "<b>Good morning! ☀️ Ready to solve some problems?</b>",
            "good night": "<b>Good night! 🌙 See you soon!</b>",
            "bye": "<b>Bye! 👋 Come back for more math help anytime!</b>",
            "i love you": "<b>❤️ Aww! I love solving math with you too!</b>",
            "help": "<b>Need help? Just ask your math problem or upload an image! 🆘</b>",
            "how are you": "<b>I'm great! Thanks for asking 😊</b>",
            "yo": "<b>Yo! Ready to do some math magic? 🧠</b>",
            "what's up": "<b>Not much! Just chilling and solving equations 😎</b>",
            "ok": "<b>Okay! Just drop in your next math challenge 📝</b>",
            "cool": "<b>Cool cool! Let's keep going 🔥</b>",
            "what can you do": "<b>I can solve math problems, explain steps, read from images, and more! 🧮</b>",
            "awesome": "<b>You're awesome too! Let's crack some numbers! 🤩</b>",
            "are you real": "<b>I'm real in the digital world 🌐💻</b>",
            "thank god": "<b>Haha, I'll take that as a compliment 😄</b>",
            "who's your creator": "<b>I was crafted by Krishna! 👨‍💻</b>",
            "you are cool": "<b>You're cooler! Let's keep solving 🔥</b>",
            "you're smart": "<b>Thanks! I'm trained to be clever at math 😄</b>",
            "solve this": "<b>Sure! Just send me the problem 🧮</b>",
            "love you": "<b>Back at ya! 💖 Let's conquer those numbers!</b>",
            "good evening": "<b>Good evening! 🌇 Let's dive into some math!</b>",
            "gm": "<b>GM! ☀️ Hit me with a math question!</b>",
            "gn": "<b>GN! 🌙 Dream of numbers!</b>"
        }
        self.dark_mode = False
        # Initialize button variables
        self.github_btn = None
        self.issue_btn = None
        self.solve_btn = None
        self.upload_btn = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MathSolver AI - Your Personal Math Assistant")
        self.setMinimumSize(800, 600)  # Minimum window size
        self.setGeometry(100, 100, 1000, 700)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.update_theme()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with logo and title
        header = QFrame(self)
        header_layout = QHBoxLayout(header)
        header.setStyleSheet("background: #3C8CE7; border-radius: 15px; padding: 15px;")
        
        # Logo and title container
        title_container = QFrame()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel("🧮")
        logo_label.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(logo_label)
        
        title_label = QLabel("MathSolver AI")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-left: 10px;")
        title_label.setMinimumWidth(200)  # Minimum width for title
        title_layout.addWidget(title_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch(1)

        # Control buttons container
        buttons_container = QFrame()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.clear_btn = QPushButton("🗑️ Clear Chat", self)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_chat)
        buttons_layout.addWidget(self.clear_btn)

        self.export_btn = QPushButton("📄 Export PDF", self)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.export_btn.clicked.connect(self.export_chat)
        buttons_layout.addWidget(self.export_btn)

        self.dark_toggle = QCheckBox("🌙 Dark Mode", self)
        self.dark_toggle.setStyleSheet("""
            QCheckBox {
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        self.dark_toggle.stateChanged.connect(self.toggle_dark_mode)
        buttons_layout.addWidget(self.dark_toggle)

        header_layout.addWidget(buttons_container)
        main_layout.addWidget(header)

        # Chat area with improved styling
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
                font-size: 14px;
                border: 2px solid #E0E0E0;
            }
        """)
        self.chat_area.setFont(QFont("Segoe UI", 12))
        main_layout.addWidget(self.chat_area, 8)

        # Input area with improved styling
        input_container = QFrame()
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Type your math problem here...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3C8CE7;
            }
        """)
        self.text_input.returnPressed.connect(self.solve_problem)
        input_layout.addWidget(self.text_input, 3)

        # Buttons container for input area
        input_buttons_container = QFrame()
        input_buttons_layout = QHBoxLayout(input_buttons_container)
        input_buttons_layout.setSpacing(10)
        input_buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.solve_btn = QPushButton("🚀 Solve", self)
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        self.solve_btn.clicked.connect(self.solve_problem)
        input_buttons_layout.addWidget(self.solve_btn)

        self.upload_btn = QPushButton("📸 Upload", self)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_image)
        input_buttons_layout.addWidget(self.upload_btn)

        input_layout.addWidget(input_buttons_container, 1)
        main_layout.addWidget(input_container, 1)

        # Footer with improved styling
        footer = QFrame(self)
        footer_layout = QHBoxLayout(footer)
        footer.setStyleSheet("""
            QFrame {
                background: #FF9800;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        # Left side - Developer info
        developer_info = QFrame()
        developer_layout = QVBoxLayout(developer_info)
        developer_layout.setContentsMargins(0, 0, 0, 0)
        
        developer_label = QLabel("👨‍💻 Developed by Krishna Singh")
        developer_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        developer_layout.addWidget(developer_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("color: white; font-size: 12px;")
        developer_layout.addWidget(version_label)
        
        footer_layout.addWidget(developer_info)
        footer_layout.addStretch(1)
        
        # Right side - Links
        links_container = QFrame()
        links_layout = QHBoxLayout(links_container)
        links_layout.setSpacing(10)
        
        # GitHub button
        self.github_btn = QPushButton("⭐ Star", self)
        self.github_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.github_btn.clicked.connect(lambda: webbrowser.open("https://github.com/Krishna-singh18/mathsolver-ai"))
        links_layout.addWidget(self.github_btn)
        
        # Report Issue button
        self.issue_btn = QPushButton("🐛 Issue", self)
        self.issue_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.issue_btn.clicked.connect(lambda: webbrowser.open("https://github.com/Krishna-singh18/mathsolver-ai/issues"))
        links_layout.addWidget(self.issue_btn)
        
        footer_layout.addWidget(links_container)
        main_layout.addWidget(footer)

        # Add welcome message
        self.add_chat_message("""
        <b>Welcome to MathSolver AI! 🎉</b><br><br>
        I can help you with:
        • Solving math problems step by step<br>
        • Reading math problems from images<br>
        • Explaining concepts in detail<br>
        • And much more!<br><br>
        Just type your problem or upload an image to get started! 🚀
        """, "AI")

    def update_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: #121212; color: white;")
            self.chat_area.setStyleSheet("background-color: #1E1E1E; color: white; border-radius: 10px; padding: 10px; font-size: 14px;")
        else:
            self.setStyleSheet("background: #F0F4F8;")
            if hasattr(self, 'chat_area'):
                self.chat_area.setStyleSheet("background-color: white; color: black; border-radius: 10px; padding: 10px; font-size: 14px;")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.update_theme()

    def add_chat_message(self, text, sender="AI"):
        if sender == "User":
            self.chat_area.append(f"<b>🧑‍💻 You:</b> {text}")
        else:
            self.chat_area.append(f"<b>🤖 AI:</b> {text}")
        self.chat_area.moveCursor(QTextCursor.End)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def clear_chat(self):
        self.chat_area.clear()

    def export_chat(self):
        try:
            chat_content = self.chat_area.toPlainText()
            if not chat_content.strip():
                QMessageBox.warning(self, "Warning", "No chat history to export!")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Chat History",
                "chat_history.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                y = height - 50
                c.setFont("Helvetica", 12)
                
                # Add title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 30, "MathSolver AI - Chat History")
                c.setFont("Helvetica", 12)
                y = height - 70
                
                for line in chat_content.split("\n"):
                    if y < 50:
                        c.showPage()
                        c.setFont("Helvetica", 12)
                        y = height - 50
                    c.drawString(50, y, line)
                    y -= 15
                
                c.save()
                QMessageBox.information(self, "Success", "Chat history exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export chat history: {str(e)}")

    def solve_problem(self):
        problem = self.text_input.text().strip()
        if problem:
            self.add_chat_message(problem, sender="User")
            self.text_input.clear()
            self.add_chat_message("Typing...", sender="AI")
            QTimer.singleShot(1000, lambda: self.solve_math_problem(problem))

    def solve_math_problem(self, problem):
        problem_lower = problem.lower().strip()
        for key in self.custom_responses:
            if key in problem_lower:
                self.chat_area.append(f"<b>🤖 AI:</b> {self.custom_responses[key]}")
                self.chat_area.moveCursor(QTextCursor.End)
                self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
                return

        if len(problem) < 5 or not any(char.isdigit() for char in problem):
            self.chat_area.append("<b>🤖 AI:</b> Please enter a valid math problem to solve.")
            self.chat_area.moveCursor(QTextCursor.End)
            self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
            return

        # Show loading message
        self.chat_area.append("<b>🤖 AI:</b> Generating step-by-step solution...")
        self.chat_area.moveCursor(QTextCursor.End)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
        
        # Disable buttons while processing
        self.solve_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.text_input.setEnabled(False)
        
        try:
            model = gmai.GenerativeModel("gemini-2.0-flash")
            prompt = f"Solve this math problem step-by-step. Clearly show final answer at the end without LaTeX or special formatting:\n{problem}"
            response = model.generate_content(prompt)
            result = response.text.strip() if response and hasattr(response, "text") else "Sorry, I couldn't solve this."
            html_result = self.markdown_to_html(result)
            self.chat_area.append(f"<b>🤖 AI:</b><br>{html_result}")
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg:
                self.chat_area.append("<b>❌ Error:</b> API key is invalid or not set. Please check your configuration.")
            elif "network" in error_msg.lower():
                self.chat_area.append("<b>❌ Error:</b> Network connection error. Please check your internet connection.")
            else:
                self.chat_area.append(f"<b>❌ Error:</b> {error_msg}")
        finally:
            # Re-enable buttons after processing
            self.solve_btn.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self.text_input.setEnabled(True)
            self.text_input.setFocus()
            
        self.chat_area.moveCursor(QTextCursor.End)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def upload_image(self):
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Upload Image", 
                "", 
                "Images (*.png *.jpg *.jpeg *.bmp *.gif)", 
                options=options
            )
            
            if file_path:
                # Show loading message
                self.chat_area.append("<b>📸 AI:</b> Processing image...")
                self.chat_area.moveCursor(QTextCursor.End)
                self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
                
                # Disable buttons while processing
                self.solve_btn.setEnabled(False)
                self.upload_btn.setEnabled(False)
                self.text_input.setEnabled(False)
                
                extracted_text = self.get_text_from_image(file_path)
                if extracted_text:
                    self.chat_area.append(f"<b>📸 Extracted Text:</b> {extracted_text}")
                    self.solve_math_problem(extracted_text)
                else:
                    self.chat_area.append("<b>⚠️ Unable to extract text from the image. Please try another image.</b>")
        except Exception as e:
            self.chat_area.append(f"<b>❌ Error:</b> {str(e)}")
        finally:
            # Re-enable buttons after processing
            self.solve_btn.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self.text_input.setEnabled(True)
            self.text_input.setFocus()
            
        self.chat_area.moveCursor(QTextCursor.End)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def get_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            model = gmai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content([image])
            if response and hasattr(response, "text"):
                extracted_text = response.text.strip()
                for line in extracted_text.split("\n"):
                    if any(char.isdigit() for char in line):
                        return line.strip()
        except Exception as e:
            return f"Error: {str(e)}"
        return None

    def markdown_to_html(self, text):
        text = re.sub(r"\\boxed\{(.*?)\}", r"\1", text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
        text = re.sub(r"\n", r"<br>", text)
        return text

    def resizeEvent(self, event):
        # Update button sizes based on window width
        window_width = self.width()
        
        # Adjust button text based on window width
        if window_width < 900:
            self.solve_btn.setText("🚀")
            self.upload_btn.setText("📸")
            self.github_btn.setText("⭐")
            self.issue_btn.setText("🐛")
        else:
            self.solve_btn.setText("🚀 Solve")
            self.upload_btn.setText("📸 Upload")
            self.github_btn.setText("⭐ Star")
            self.issue_btn.setText("🐛 Issue")
        
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MathSolverApp()
    window.show()
    sys.exit(app.exec_())
