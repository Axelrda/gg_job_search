# Updating PYTHONPATH for Airflow

Airflow runs tasks in a different environment from your usual Python environment, which may lead to issues with Python not being able to find certain modules or files. To ensure Airflow has access to the necessary files, we need to add the project directory to our PYTHONPATH environment variable.

## Steps:

1. Identify your project's root directory. This directory should contain your `config.py` file and other project-related files.

    ```bash
    cd /path/to/your/project/directory
    ```
    
2. Add your project's root directory to the PYTHONPATH environment variable in your shell profile file (`~/.bashrc`, `~/.zshrc`, or similar), replace the `path/to/your/project` with your actual project directory.

    ```bash
    echo 'export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"' >> ~/.bashrc
    ```

3. Apply the changes made to the shell profile file.

    ```bash
    source ~/.bashrc
    ```

**Note:** The changes made here will only affect the current terminal session. For the changes to persist across sessions, you would need to add the export line to your shell's profile file (like `.bashrc` or `.zshrc`).

## Verification

To verify that the update has been successful, you can print the `PYTHONPATH` variable:

```bash
echo $PYTHONPATH
