module.exports = {
  apps: [
    {
      name: "mercadovoz-web",
      cwd: "/home/ubuntu/apps/mercadovoz/apps/web",
      script: "npm",
      args: "start -- -H 127.0.0.1 -p 3000",
      env: {
        NODE_ENV: "production",
      },
      instances: 1,
      autorestart: true,
      max_memory_restart: "512M",
    },
  ],
};
