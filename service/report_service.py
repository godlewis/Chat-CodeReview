import pandas as pd
from datetime import datetime
import os
from service.chat_review import ChatReview
from service.get_commit_content import get_commit_content
import gitlab

class CodeReviewReport:
    def __init__(self):
        self.chat_review = ChatReview()
        # 创建存放报告的目录
        self.report_dir = "reports"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def generate_report(self, project_id, branch):
        """
        生成代码评审报告
        
        Args:
            project_id: GitLab项目ID
            branch: 分支名称
        """
        try:
            # 获取所有提交
            commits = get_commit_content(project_id, branch)
            
            # 准备报告数据
            report_data = []
            
            for commit in commits:
                # 获取提交的代码变更
                diffs = commit.diff()
                
                # 计算代码行数变更
                added_lines = 0
                removed_lines = 0
                for diff in diffs:
                    if diff.get('diff'):
                        for line in diff['diff'].split('\n'):
                            if line.startswith('+') and not line.startswith('+++'):
                                added_lines += 1
                            elif line.startswith('-') and not line.startswith('---'):
                                removed_lines += 1
                
                # 进行代码评审
                review_result = self.chat_review.review_code(commit.diff())
                
                # 解析评审结果，假设返回格式为 {"score": 85, "comments": "详细评审意见..."}
                score = review_result.get('score', 0)
                review_comments = review_result.get('comments', '')
                
                # 添加到报告数据
                report_data.append({
                    '提交人': commit.author_name,
                    '提交人邮箱': commit.author_email,
                    '提交时间': commit.committed_date,
                    '提交ID': commit.id,
                    '新增代码行数': added_lines,
                    '删除代码行数': removed_lines,
                    '代码质量评分': score,
                    '评审报告': review_comments
                })
            
            # 创建DataFrame
            df = pd.DataFrame(report_data)
            
            # 生成报告文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"code_review_report_{branch}_{timestamp}.xlsx"
            filepath = os.path.join(self.report_dir, filename)
            
            # 保存为Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            return True, filepath
            
        except Exception as e:
            return False, f"生成报告失败: {str(e)}" 