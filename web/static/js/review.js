$(document).ready(function() {
    // 初始化日期选择器
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        language: 'zh-CN',
        autoclose: true
    });

    // 设置默认日期范围（最近30天）
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    $('#startDate').datepicker('setDate', startDate);
    $('#endDate').datepicker('setDate', endDate);

    // 加载初始数据
    loadData();

    // 查询按钮点击事件
    $('#searchBtn').click(function() {
        loadData();
    });

    // 加载数据函数
    function loadData() {
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();

        // 显示加载动画
        showLoading();

        // 获取开发者列表
        $.ajax({
            url: '/api/gitlab/developers',
            method: 'GET',
            data: {
                start_date: startDate,
                end_date: endDate
            },
            success: function(response) {
                if (response.success) {
                    updateReviewersList(response.data);
                } else {
                    showAlert('danger', '加载开发者列表失败');
                }
            },
            error: function() {
                showAlert('danger', '加载开发者列表失败');
            },
            complete: function() {
                hideLoading();
            }
        });
    }

    // 更新开发者列表
    function updateReviewersList(developers) {
        const $list = $('#reviewersList');
        $list.empty();

        developers.forEach(dev => {
            const $item = $(`
                <div class="list-group-item list-group-item-action reviewer-item" data-username="${dev.username}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${dev.name}</h6>
                            <small class="text-muted">${dev.email}</small>
                        </div>
                        <button class="btn btn-sm btn-primary generate-report-btn">
                            生成报告
                        </button>
                    </div>
                </div>
            `);

            $list.append($item);
        });

        // 绑定点击事件
        $('.reviewer-item').click(function(e) {
            if (!$(e.target).hasClass('generate-report-btn')) {
                const username = $(this).data('username');
                $('.reviewer-item').removeClass('active');
                $(this).addClass('active');
                loadReviewList(username);
            }
        });

        // 绑定生成报告按钮事件
        $('.generate-report-btn').click(function(e) {
            e.stopPropagation();
            const $item = $(this).closest('.reviewer-item');
            const username = $item.data('username');
            const name = $item.find('h6').text();
            const email = $item.find('small').text();
            showReportModal(username, name, email);
        });
    }

    // 加载评审列表
    function loadReviewList(username) {
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();

        $.ajax({
            url: `/api/gitlab/developers/${username}/commits`,
            method: 'GET',
            data: {
                start_date: startDate,
                end_date: endDate
            },
            success: function(response) {
                if (response.success) {
                    updateReviewList(response.data);
                } else {
                    showAlert('danger', '加载评审列表失败');
                }
            },
            error: function() {
                showAlert('danger', '加载评审列表失败');
            }
        });
    }

    // 更新评审列表
    function updateReviewList(commits) {
        const $list = $('#reviewList');
        $list.empty();

        commits.forEach(commit => {
            const $row = $(`
                <tr>
                    <td>${commit.author_name}</td>
                    <td>${commit.project_name}</td>
                    <td>${formatDate(commit.committed_date)}</td>
                    <td>${commit.added_lines}</td>
                    <td>${commit.removed_lines}</td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar ${getScoreClass(commit.score)}" 
                                 role="progressbar" 
                                 style="width: ${commit.score}%"
                                 aria-valuenow="${commit.score}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${commit.score}
                            </div>
                        </div>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="showCommitDetails('${commit.id}')">
                            查看详情
                        </button>
                    </td>
                </tr>
            `);

            $list.append($row);
        });
    }

    // 显示报告生成模态框
    function showReportModal(username, name, email) {
        const $modal = $('#reportModal');
        const $info = $modal.find('.developer-info');
        $info.html(`
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">${name}</h6>
                    <p class="card-text mb-0">
                        <small class="text-muted">${email}</small>
                    </p>
                </div>
            </div>
        `);

        // 设置默认邮箱
        $('#notifyEmail').val(email);

        // 绑定生成报告按钮事件
        $('#generateReportBtn').off('click').on('click', function() {
            generateReport(username);
        });

        $modal.modal('show');
    }

    // 生成报告
    function generateReport(username) {
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();
        const notifyEmail = $('#notifyEmail').val();

        const data = {
            username: username,
            start_date: startDate,
            end_date: endDate,
            notify_email: notifyEmail
        };

        $.ajax({
            url: '/api/review/generate_report',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            xhrFields: {
                responseType: 'blob'
            },
            success: function(response, status, xhr) {
                const blob = new Blob([response], {
                    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                });

                const filename = xhr.getResponseHeader('content-disposition')
                    ?.split('filename=')[1]
                    ?.replace(/"/g, '') 
                    || 'review_report.xlsx';

                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = filename;
                link.click();

                $('#reportModal').modal('hide');
                showAlert('success', '报告生成成功！');
            },
            error: function() {
                showAlert('danger', '生成报告失败');
            }
        });
    }

    // 辅助函数
    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleString('zh-CN');
    }

    function getScoreClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        return 'bg-danger';
    }

    function showLoading() {
        // TODO: 实现加载动画
    }

    function hideLoading() {
        // TODO: 隐藏加载动画
    }

    function showAlert(type, message) {
        const alert = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('.review-container').prepend(alert);
        setTimeout(() => {
            $('.alert').alert('close');
        }, 3000);
    }
});

// 显示提交详情
function showCommitDetails(commitId) {
    $.ajax({
        url: `/api/gitlab/commits/${commitId}`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                showCommitModal(response.data);
            } else {
                showAlert('danger', '加载提交详情失败');
            }
        },
        error: function() {
            showAlert('danger', '加载提交详情失败');
        }
    });
}

// 添加显示提交详情模态框的函数
function showCommitModal(commit) {
    const $modal = $('#commitDetailsModal');
    const $info = $modal.find('.commit-info');
    const $changes = $modal.find('.changes-container');
    
    // 显示提交基本信息
    $info.html(`
        <div class="card">
            <div class="card-body">
                <h6 class="card-title">${commit.title}</h6>
                <p class="card-text mb-2">${commit.message}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <small class="text-muted">
                            提交者: ${commit.author_name} (${commit.author_email})
                        </small><br>
                        <small class="text-muted">
                            提交时间: ${formatDate(commit.committed_date)}
                        </small>
                    </div>
                    <div class="text-end">
                        <div class="mb-1">代码行数变更: 
                            <span class="text-success">+${commit.added_lines}</span> / 
                            <span class="text-danger">-${commit.removed_lines}</span>
                        </div>
                        <div class="progress" style="width: 150px">
                            <div class="progress-bar ${getScoreClass(commit.score)}" 
                                 role="progressbar" 
                                 style="width: ${commit.score}%">
                                评分: ${commit.score}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="card mt-3">
            <div class="card-body">
                <h6 class="card-title">评审意见</h6>
                <pre class="review-comments">${commit.review_comments}</pre>
            </div>
        </div>
    `);
    
    // 显示代码变更
    const changesHtml = commit.changes.map(change => `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span>${change.file}</span>
                <div>
                    <span class="badge bg-success">+${change.added_lines}</span>
                    <span class="badge bg-danger">-${change.removed_lines}</span>
                </div>
            </div>
            <div class="card-body">
                <pre class="diff-content">${escapeHtml(change.diff)}</pre>
            </div>
        </div>
    `).join('');
    
    $changes.html(changesHtml);
    
    $modal.modal('show');
}

// 添加 HTML 转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
} 