module.exports = {
  apps: [{
    name: 'mcp-server',
    script: './start_safe.sh',
    interpreter: '/bin/bash',
    cwd: '/opt/workspace-boze/MCP_Server_Brose',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    restart_delay: 4000,
    kill_timeout: 5000,
    wait_ready: true,
    autostart: true,

    // 环境变量
    env: {
      NODE_ENV: 'production',
    },

    // 日志配置
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true,
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss',

    // 进程管理
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000,

    // 停止信号
    stop_signal: 'SIGINT',
    kill_signal: 'SIGTERM',
    kill_timeout: 5000,

    // 其他配置
    listen_timeout: 10000,
    shutdown_with_message: true,
  }]
};
