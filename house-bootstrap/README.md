# House bootstrap

Named installs only. No standing Hugging Face session.
Future programs are catalog rows. They do not install until enabled.

## Commands

```bash
chmod +x install.sh verify.sh add_package.py
./install.sh
./install.sh --dry-run
./verify.sh
```

Enable a future row then install only that id:

```bash
./add_package.py enable mlx-lm
./install.sh --only mlx-lm
```

Hugging Face rows stay disabled until a human names the file and the house path.
