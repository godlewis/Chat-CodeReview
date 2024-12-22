import os
import gitlab
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class GitLabService:
    def __init__(self):
        self.gitlab_url = os.getenv('GITLAB_SERVER_URL')
        self.private_token = os.getenv('GITLAB_PRIVATE_TOKEN')
        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.private_token)
    
    def get_all_projects(self):
        """
        获取所有项目信息
        """
        try:
            # 获取所有项目
            projects = self.gl.projects.list(all=True)
            
            projects_info = []
            for project in projects:
                # 获取项目分支
                branches = [branch.name for branch in project.branches.list()]
                
                # 获取项目标签
                tags = [tag.name for tag in project.tags.list()]
                
                # 收集项目信息
                project_info = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'web_url': project.web_url,
                    'git_http_url': project.http_url_to_repo,
                    'git_ssh_url': project.ssh_url_to_repo,
                    'default_branch': project.default_branch,
                    'branches': branches,
                    'tags': tags,
                    'created_at': project.created_at,
                    'last_activity_at': project.last_activity_at,
                    'visibility': project.visibility,
                    'namespace': project.namespace['name']
                }
                projects_info.append(project_info)
            
            return True, projects_info
            
        except Exception as e:
            return False, f"获取项目信息失败: {str(e)}" 
    
    def get_project_developers(self, project_id):
        """
        获取项目中具有开发者权限的成员信息
        
        Args:
            project_id: 项目ID
        """
        try:
            # 获取项目实例
            project = self.gl.projects.get(project_id)
            
            # 获取所有成员
            members = project.members.list(all=True)
            
            # 筛选具有开发者权限的成员
            # GitLab 访问级别：
            # 10 = Guest
            # 20 = Reporter
            # 30 = Developer
            # 40 = Maintainer
            # 50 = Owner
            developers = []
            for member in members:
                if member.access_level >= 30:  # Developer及以上权限
                    developer_info = {
                        'id': member.id,
                        'username': member.username,
                        'name': member.name,
                        'email': member.email,
                        'access_level': member.access_level,
                        'access_level_name': self._get_access_level_name(member.access_level),
                        'avatar_url': member.avatar_url,
                        'web_url': member.web_url,
                        'state': member.state
                    }
                    developers.append(developer_info)
            
            return True, developers
            
        except Exception as e:
            return False, f"获取项目成员信息失败: {str(e)}"
        
    def _get_access_level_name(self, access_level):
        """
        将访问级别数字转换为对应的名称
        """
        access_levels = {
            10: '访客',
            20: '报告者',
            30: '开发者',
            40: '维护者',
            50: '所有者'
        }
        return access_levels.get(access_level, '未知')
    
    def get_developer_projects(self, username):
        """
        获取开发者参与的所有项目及其首次提交时间
        
        Args:
            username: 开发者的用户名
        """
        try:
            # 获取所有项目
            projects = self.gl.projects.list(all=True)
            
            developer_projects = []
            for project in projects:
                try:
                    # 获取该用户在此项目的提交记录
                    commits = project.commits.list(all=True, query_parameters={'author': username})
                    
                    if commits:
                        # 按时间排序找出最早的提交
                        commits_sorted = sorted(commits, key=lambda x: x.created_at)
                        first_commit = commits_sorted[0]
                        last_commit = commits_sorted[-1]
                        
                        # 统计提交次数
                        commit_count = len(commits)
                        
                        project_info = {
                            'id': project.id,
                            'name': project.name,
                            'namespace': project.namespace['name'],
                            'description': project.description,
                            'web_url': project.web_url,
                            'first_commit_at': first_commit.created_at,
                            'last_commit_at': last_commit.created_at,
                            'commit_count': commit_count,
                            'default_branch': project.default_branch,
                            'visibility': project.visibility
                        }
                        developer_projects.append(project_info)
                except Exception as e:
                    # 如果获取某个项目的提交历史失败，继续处理下一个项目
                    print(f"获取项目 {project.name} 的提交历史失败: {str(e)}")
                    continue
            
            # 按首次提交时间排序
            developer_projects.sort(key=lambda x: x['first_commit_at'])
            
            return True, developer_projects
            
        except Exception as e:
            return False, f"获取开发者项目历史失败: {str(e)}"
    
    def get_developers_with_commits(self, start_date=None, end_date=None):
        """
        获取在指定时间范围内有提交记录的开发者列表
        
        Args:
            start_date: 开始日期 (datetime对象)
            end_date: 结束日期 (datetime对象)
        """
        try:
            # 获取所有项目
            projects = self.gl.projects.list(all=True)
            
            # 使用字典来去重和统计
            developers = {}
            
            for project in projects:
                try:
                    # 构建查询参数
                    params = {}
                    if start_date:
                        params['since'] = start_date.isoformat()
                    if end_date:
                        params['until'] = end_date.isoformat()
                    
                    # 获取项目成员（开发者及以上权限）
                    members = project.members.list(all=True)
                    for member in members:
                        if member.access_level >= 30:  # Developer及以上权限
                            if member.username not in developers:
                                developers[member.username] = {
                                    'username': member.username,
                                    'name': member.name,
                                    'email': member.email,
                                    'access_level': member.access_level,
                                    'access_level_name': self._get_access_level_name(member.access_level),
                                    'avatar_url': member.avatar_url,
                                    'commit_count': 0,
                                    'projects_count': 1
                                }
                            else:
                                developers[member.username]['projects_count'] += 1
                    
                    # 获取提交记录并统计
                    commits = project.commits.list(all=True, query_parameters=params)
                    for commit in commits:
                        username = commit.author_name.lower().replace(' ', '_')
                        if username in developers:
                            developers[username]['commit_count'] += 1
                
                except Exception as e:
                    print(f"处理项目 {project.name} 时出错: {str(e)}")
                    continue
            
            # 转换为列表并按提交数量排序
            developers_list = list(developers.values())
            developers_list.sort(key=lambda x: x['commit_count'], reverse=True)
            
            return True, developers_list
            
        except Exception as e:
            return False, f"获取开发者列表失败: {str(e)}"
    
    def get_developer_commits(self, username, start_date=None, end_date=None):
        """
        获取指定开发者的提交记录
        
        Args:
            username: 开发者用户名
            start_date: 开始日期 (datetime对象)
            end_date: 结束日期 (datetime对象)
        """
        try:
            # 获取所有项目
            projects = self.gl.projects.list(all=True)
            
            commits_data = []
            for project in projects:
                try:
                    # 构建查询参数
                    params = {'author': username}
                    if start_date:
                        params['since'] = start_date.isoformat()
                    if end_date:
                        params['until'] = end_date.isoformat()
                    
                    # 获取提交记录
                    commits = project.commits.list(all=True, query_parameters=params)
                    
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
                        
                        # 使用现有的代码评审功能
                        review_result = self.chat_review.review_code(diffs)
                        score = review_result.get('score', 60)  # 默认分数为60
                        
                        commit_info = {
                            'id': commit.id,
                            'author_name': commit.author_name,
                            'project_name': f"{project.namespace['name']}/{project.name}",
                            'project_id': project.id,
                            'committed_date': commit.committed_date,
                            'title': commit.title,
                            'message': commit.message,
                            'added_lines': added_lines,
                            'removed_lines': removed_lines,
                            'score': score,
                            'review_comments': review_result.get('comments', '')
                        }
                        commits_data.append(commit_info)
                
                except Exception as e:
                    print(f"获取项目 {project.name} 的提交记录失败: {str(e)}")
                    continue
            
            # 按时间排序
            commits_data.sort(key=lambda x: x['committed_date'], reverse=True)
            
            return True, commits_data
            
        except Exception as e:
            return False, f"获取提交记录失败: {str(e)}"
    
    def get_commit_details(self, commit_id):
        """
        获取提交详情
        
        Args:
            commit_id: 提交ID
        """
        try:
            # 遍历所有项目查找提交
            projects = self.gl.projects.list(all=True)
            
            for project in projects:
                try:
                    commit = project.commits.get(commit_id)
                    
                    # 获取提交的代码变更
                    diffs = commit.diff()
                    
                    # 计算代码行数变更
                    added_lines = 0
                    removed_lines = 0
                    changes = []
                    
                    for diff in diffs:
                        if diff.get('diff'):
                            file_added_lines = 0
                            file_removed_lines = 0
                            for line in diff['diff'].split('\n'):
                                if line.startswith('+') and not line.startswith('+++'):
                                    added_lines += 1
                                    file_added_lines += 1
                                elif line.startswith('-') and not line.startswith('---'):
                                    removed_lines += 1
                                    file_removed_lines += 1
                            
                            changes.append({
                                'file': diff['new_path'],
                                'diff': diff['diff'],
                                'added_lines': file_added_lines,
                                'removed_lines': file_removed_lines
                            })
                    
                    # 使用现有的代码评审功能
                    review_result = self.chat_review.review_code(diffs)
                    
                    commit_details = {
                        'id': commit.id,
                        'author_name': commit.author_name,
                        'author_email': commit.author_email,
                        'project_name': f"{project.namespace['name']}/{project.name}",
                        'committed_date': commit.committed_date,
                        'title': commit.title,
                        'message': commit.message,
                        'added_lines': added_lines,
                        'removed_lines': removed_lines,
                        'score': review_result.get('score', 60),
                        'review_comments': review_result.get('comments', ''),
                        'changes': changes
                    }
                    
                    return True, commit_details
                    
                except Exception:
                    continue
            
            return False, "找不到指定的提交"
            
        except Exception as e:
            return False, f"获取提交详情失败: {str(e)}"