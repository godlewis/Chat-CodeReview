from flask import Blueprint, request, jsonify, send_file
from service.report_service import CodeReviewReport
from service.email_service import EmailService
import os

review_bp = Blueprint('review', __name__)
report_service = CodeReviewReport()
email_service = EmailService()

@review_bp.route('/generate_report', methods=['POST'])
def generate_report():
    """
    生成代码评审报告的API接口
    
    请求体格式：
    {
        "project_id": "项目ID",
        "branch": "分支名称",
        "notify_email": "通知邮箱（可选）"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        required_fields = ['username', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'缺少必要字段: {", ".join(missing_fields)}'
            }), 400
        
        project_id = data.get('project_id')
        branch = data.get('branch')
        notify_email = data.get('notify_email')
        
        if not project_id or not branch:
            return jsonify({
                'success': False,
                'message': '缺少必要参数：project_id 或 branch'
            }), 400
        
        # 生成报告
        success, result = report_service.generate_report(project_id, branch)
        
        if not success:
            return jsonify({
                'success': False,
                'message': result
            }), 500
        
        # 如果提供了通知邮箱，发送邮件通知
        if notify_email:
            email_service.send_email(
                to_addr=notify_email,
                subject=f"代码评审报告 - {branch}分支",
                content=f"您的代码评审报告已生成，请查看附件。\n\n分支：{branch}\n报告文件：{os.path.basename(result)}"
            )
        
        # 返回报告文件
        return send_file(
            result,
            as_attachment=True,
            download_name=os.path.basename(result),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成报告失败: {str(e)}'
        }), 500 