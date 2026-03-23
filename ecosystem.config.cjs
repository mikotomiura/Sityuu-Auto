module.exports = {
  apps: [
    {
      name: "sityuu-auto",
      script: ".venv/bin/streamlit",
      args: "run src/app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true",
      cwd: "/root/Sityuu-Auto",
      interpreter: "none",
      env: {
        PATH: "/root/Sityuu-Auto/.venv/bin:/usr/local/bin:/usr/bin:/bin",
      },
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
    },
  ],
};
