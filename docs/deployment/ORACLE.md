# Oracle Cloud deployment — prepared, not executed

## Target

- Oracle Cloud `VM.Standard.A1.Flex` (ARM64)
- Ubuntu 24.04
- 2 OCPU, 12 GB RAM
- 50 GB persistent boot volume
- `/home/ubuntu/apps/mercadovoz`
- Nginx → Next.js on `127.0.0.1:3000`
- Nginx `/api/` → FastAPI on `127.0.0.1:8000`
- PM2 for Next.js; systemd for FastAPI; SQLite WAL outside Git

Oracle documents Ubuntu support and flexible CPU/memory for Ampere A1: [Arm-Based Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/References/arm.htm). Network Security Groups are preferred over broad security lists; OS firewall rules must also match OCI ingress: [OCI security-list reference](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/network/security-list.html).

## Prerequisites and boundaries

Do not begin P01 until valid HTTPS, access protection, backup/restore, environment secrets and the pilot lock are verified. Do not expose ports 3000 or 8000 publicly. Allow SSH only from an administrator CIDR; 80/443 may be opened only when Nginx/TLS is ready.

## Base host

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git nginx python3-venv python3-pip sqlite3 ufw
sudo mkdir -p /home/ubuntu/apps/mercadovoz/data/runtime
sudo chown -R ubuntu:ubuntu /home/ubuntu/apps
```

Install a supported ARM64 Node.js LTS from an official Node.js distribution or a reviewed package source, then install PM2 for the `ubuntu` user. Verify `node --version`, `npm --version` and `uname -m` before building.

## Checkout and Python

```bash
cd /home/ubuntu/apps
git clone git@github.com:lildavicho/mercadovoz.git
cd mercadovoz
git checkout main
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[api]'
.venv/bin/python -m unittest discover -s tests -v
```

The public repository does not contain secrets or pilot data. Create `/etc/mercadovoz/api.env` as root from `.env.example`, mode `0600`; never copy it into the checkout.

## Web build

```bash
cd /home/ubuntu/apps/mercadovoz/apps/web
npm ci
npm run typecheck
npm run build
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

Run the command printed by `pm2 startup`; do not paste credentials into it.

## API service

```bash
sudo cp scripts/deployment/mercadovoz-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mercadovoz-api
sudo systemctl status mercadovoz-api --no-pager
```

## Nginx

Replace `server_name` only after a hostname is available. Do not use a fake hostname for a real pilot.

```bash
sudo cp scripts/deployment/nginx-mercadovoz.conf /etc/nginx/sites-available/mercadovoz
sudo ln -s /etc/nginx/sites-available/mercadovoz /etc/nginx/sites-enabled/mercadovoz
sudo nginx -t
sudo systemctl reload nginx
```

Add a valid TLS certificate before exposing participant access. Set `NEXT_PUBLIC_API_URL=https://HOST/api` before the production build and `MERCADOVOZ_ALLOWED_ORIGINS=https://HOST` in the API environment.

## Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from ADMIN_CIDR to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Mirror only the required rules in the OCI NSG. Never add public ingress for 3000/8000.

## Data and backup

`MERCADOVOZ_DB=/home/ubuntu/apps/mercadovoz/data/runtime/mercadovoz-pilot.db`. Run `scripts/backup/backup_sqlite.sh` and complete a restore drill with synthetic data before P01. Backups must live outside the Git checkout and follow `BACKUP_RECOVERY.md`.

## Verification

```bash
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:3000/
curl --fail https://HOST/api/health
systemctl is-active mercadovoz-api nginx
pm2 status
```

Also verify `/api/docs`, `/api/openapi.json` and development `/api/interpret` return 404 in pilot mode; complete the private deployment checklist and rollback procedure. Deployment is a separate authorized operation, not part of repository bootstrap.
