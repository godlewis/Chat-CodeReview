from flask import Blueprint, jsonify, request
from service.gitlab_service import GitLabService
from datetime import datetime

gitlab_bp = Blueprint('gitlab', __name__)
gitlab_service = GitLabService()

@gitlab_bp.route('/projects', methods=['GET'])
def get_projects():
    """
    获取所有GitLab项目信息
    """
    success, result = gitlab_service.get_all_projects()
    
    if not success:
        return jsonify({
            'success': False,
            'message': result
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    }) 

@gitlab_bp.route('/projects/<int:project_id>/developers', methods=['GET'])
def get_project_developers(project_id):
    """
    获取项目的开发者成员信息
    
    Args:
        project_id: 项目ID
    """
    success, result = gitlab_service.get_project_developers(project_id)
    
    if not success:
        return jsonify({
            'success': False,
            'message': result
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    }) 

@gitlab_bp.route('/developers/<string:username>/projects', methods=['GET'])
def get_developer_projects(username):
    """
    获取开发者参与的所有项目及其提交历史
    
    Args:
        username: 开发者的用户名
    """
    success, result = gitlab_service.get_developer_projects(username)
    
    if not success:
        return jsonify({
            'success': False,
            'message': result
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    })

@gitlab_bp.route('/developers', methods=['GET'])
def get_developers():
    """
    获取所有开发者列表，支持时间范围筛选
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        return jsonify({
            'success': False,
            'message': '日期格式错误，请使用 YYYY-MM-DD 格式'
        }), 400
    
    success, result = gitlab_service.get_developers_with_commits(start_date, end_date)
    
    if not success:
        return jsonify({
            'success': False,
            'message': result
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    })

@gitlab_bp.route('/developers/<string:username>/commits', methods=['GET'])
def get_developer_commits(username):
    """
    获取指定开发者的提交记录
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except ValueError:
        return jsonify({
            'success': False,
            'message': '日期格式错误，请使用 YYYY-MM-DD 格式'
        }), 400
    
    success, result = gitlab_service.get_developer_commits(username, start_date, end_date)
    
    if not success:
        return jsonify({
            'success': False,
            'message': result
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    })

@gitlab_bp.route('/commits/<string:commit_id>', methods=['GET'])
def get_commit_details(commit_id):
    """
    获取提交详情
    """
    success, result = gitlab_service.get_commit_details(commit_id)
    
    if not success:
        return jsonify({
            'success': False,
            'message': result
        }), 500
    
    return jsonify({
        'success': True,
        'data': result
    })