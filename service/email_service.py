import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
from dotenv import load_dotenv
import ssl  # 添加 ssl 模块

# 加载环境变量
load_dotenv()

class EmailService:
    def __init__(self):
        # 从环境变量获取SMTP配置
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # 测试收件人
        self.test_receiver = "godlewis@qq.com"
        
        # 创建 SSL 上下文
        self.context = ssl.create_default_context()
    
    def send_test_email(self):
        """
        发送测试邮件
        """
        try:
            # 创建邮件内容
            message = MIMEText('这是一封测试邮件，用于验证邮件服务是否正常工作。', 'plain', 'utf-8')
            message['From'] = Header(self.smtp_user)
            message['To'] = Header(self.test_receiver)
            message['Subject'] = Header('GitLab代码审查系统测试邮件', 'utf-8')
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=self.context) as server:
                server.login(self.smtp_user, self.smtp_password)
                try:
                    server.sendmail(self.smtp_user, self.test_receiver, message.as_string())
                    return True, "邮件发送成功"
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 250:  # 250 表示成功
                        return True, "邮件发送成功"
                    raise e
            
        except Exception as e:
            if isinstance(e, smtplib.SMTPResponseException) and e.smtp_code == 250:
                return True, "邮件发送成功"
            return False, f"邮件发送失败: {str(e)}"
    
    def send_email(self, to_addr, subject, content):
        """
        发送自定义邮件
        
        Args:
            to_addr (str): 收件人邮箱
            subject (str): 邮件主题
            content (str): 邮件内容
        """
        try:
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = Header(self.smtp_user)
            message['To'] = Header(to_addr)
            message['Subject'] = Header(subject, 'utf-8')
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=self.context) as server:
                server.login(self.smtp_user, self.smtp_password)
                try:
                    server.sendmail(self.smtp_user, to_addr, message.as_string())
                    return True, "邮件发送成功"
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 250:  # 250 表示成功
                        return True, "邮件发送成功"
                    raise e
            
        except Exception as e:
            if isinstance(e, smtplib.SMTPResponseException) and e.smtp_code == 250:
                return True, "邮件发送成功"
            return False, f"邮件发送失败: {str(e)}"

# 测试代码
if __name__ == "__main__":
    email_service = EmailService()
    
    print("开始发送测试邮件...")
    
    # 测试发送预设的测试邮件
    success, message = email_service.send_test_email()
    print(f"测试邮件结果: {message}")
    
    # 测试发送自定义邮件
    success, message = email_service.send_email(
        to_addr="godlewis@qq.com",
        subject="自定义测试邮件",
        content="这是一封通过自定义方法发送的测试邮件。\n\n祝好！"
    )
    print(f"自定义邮件结果: {message}") 