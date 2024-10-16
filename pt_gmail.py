import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pt_config
import pt_logger
import pt_db

logger = pt_logger.logger


def send(subject, message_body):
    """
    發送 Gmail 郵件的通用函數

    :param subject: 郵件的主題
    :param message_body: 郵件的內容（HTML格式）
    """
    # 定義郵件的發送者和接收者
    mail_from = pt_config.GMAIL_AUTH_USER  # 發送者的電子郵件地址
    mail_to = pt_config.GMAIL_MAIL_TO        # 接收者的電子郵件地址
    
    # Gmail SMTP 設定
    smtp_user = pt_config.GMAIL_AUTH_USER      # 用來發送郵件的Gmail帳號
    smtp_password = pt_config.GMAIL_AUTH_PASS   # 使用應用程式密碼（或你的Gmail帳號密碼）

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # 構建郵件內容
    mail_options = MIMEMultipart()
    mail_options['From'] = mail_from
    mail_options['To'] = mail_to
    mail_options['Subject'] = subject
    mail_options.attach(MIMEText(message_body, 'html'))

    try:
        # 發送郵件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 啟用 TLS 加密
            server.login(smtp_user, smtp_password)  # 登錄 Gmail 帳號
            server.sendmail(mail_from, mail_to, mail_options.as_string())  # 發送郵件
            logger.info(f"Email sent successfully to {mail_to} with subject: {subject}")
            return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
