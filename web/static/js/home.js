$(document).ready(function() {
    // 侧边栏切换
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
    });

    // 页面导航处理
    $('a[data-page]').on('click', function(e) {
        e.preventDefault();
        const page = $(this).data('page');
        const pageTitle = $(this).find('span').text();
        
        // 更新活动状态
        $('.components li').removeClass('active');
        $(this).closest('li').addClass('active');
        
        // 更新页面标题
        $('#currentPageTitle').text(pageTitle);
        
        // 加载对应的页面内容
        loadPage(page);
    });

    // 页面加载函数
    function loadPage(page) {
        let url;
        switch(page) {
            case 'review':
                url = '/review';
                break;
            case 'projects':
                url = '/projects';
                break;
            case 'developers':
                url = '/developers';
                break;
            default:
                url = '/review';
        }

        // 添加加载动画
        $('#pageContent').html('<div class="text-center p-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>');

        // 加载页面内容
        $.get(url, function(data) {
            $('#pageContent').html(data);
        }).fail(function() {
            $('#pageContent').html('<div class="alert alert-danger">加载页面失败</div>');
        });
    }

    // 默认加载代码评审页面
    loadPage('review');
});

// 全局函数：显示通知
function showNotification(message, type = 'info') {
    const notification = `
        <div class="alert alert-${type} alert-dismissible fade show notification" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    if (!$('.notification-container').length) {
        $('body').append('<div class="notification-container"></div>');
    }
    
    $('.notification-container').append(notification);
    
    // 5秒后自动关闭
    setTimeout(() => {
        $('.notification').alert('close');
    }, 5000);
} 