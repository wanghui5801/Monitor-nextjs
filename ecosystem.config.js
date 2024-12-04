module.exports = {
  apps: [
    {
      name: 'server-monitor-frontend',
      cwd: './frontend',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:5000'
      },
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '500M',
      watch: false,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      merge_logs: true,
      build: {
        cmd: 'npm run build',
        cwd: './frontend'
      },
      exp_backoff_restart_delay: 100,
      wait_ready: true,
      listen_timeout: 50000,
      kill_timeout: 5000,
      restart_delay: 4000
    },
    {
      name: 'server-monitor-backend',
      script: './venv/bin/python',
      args: 'app.py',
      cwd: './backend',
      interpreter: 'none',
      env: {
        FLASK_ENV: 'production',
        FLASK_APP: 'app.py',
        SECRET_KEY: 'your-secret-key-here',
        DEBUG: 'False'
      },
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '300M',
      watch: false,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      merge_logs: true
    }
  ]
}; 