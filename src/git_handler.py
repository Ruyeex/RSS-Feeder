"""Git operations for committing and pushing changes."""

import subprocess
import sys
from src.logger import setup_logger

logger = setup_logger(__name__)


def run_git_command(cmd, check=True):
    """
    Run a git command and return the result.
    
    Args:
        cmd: Git command to run (without 'git' prefix)
        check: Whether to raise exception on failure
        
    Returns:
        CompletedProcess object
    """
    full_cmd = f"git {cmd}"
    logger.debug(f"Running: {full_cmd}")
    
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            logger.debug(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            logger.debug(f"STDERR: {result.stderr.strip()}")
        
        if check and result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error running git command: {e}")
        raise


def setup_git(user_name, user_email):
    """
    Configure git user settings.
    
    Args:
        user_name: Git user name
        user_email: Git user email
    """
    logger.info(f"Configuring git user: {user_name} <{user_email}>")
    run_git_command(f'config user.name "{user_name}"')
    run_git_command(f'config user.email "{user_email}"')


def has_changes(file_path):
    """
    Check if there are staged or unstaged changes for a specific file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if there are changes, False otherwise
    """
    # Check for changes in working directory
    result_working = run_git_command(f'diff --quiet "{file_path}"', check=False)
    
    # Check for staged changes
    result_staged = run_git_command(f'diff --staged --quiet "{file_path}"', check=False)
    
    # If either check returned non-zero, there are changes
    has_changes_flag = result_working.returncode != 0 or result_staged.returncode != 0
    logger.debug(f"Changes detected in {file_path}: {has_changes_flag}")
    
    return has_changes_flag


def commit_and_push(file_path, branch="main"):
    """
    Commit and push changes to remote repository.
    
    Args:
        file_path: Path to the file to commit
        branch: Target branch name
    """
    try:
        # Add file to staging
        logger.info(f"Adding {file_path} to staging...")
        run_git_command(f'add "{file_path}"')
        
        # Check if there are actual changes
        if not has_changes(file_path):
            logger.info("No changes to commit")
            return
        
        # Commit
        logger.info("Committing changes...")
        run_git_command('commit -m "Update RSS feed"')
        
        # Pull with rebase to get latest remote changes
        logger.info(f"Pulling latest changes from {branch} with rebase...")
        result = run_git_command(
            f'pull --rebase origin {branch}',
            check=False
        )
        
        if result.returncode != 0:
            logger.warning("Pull/rebase conflict detected, attempting to abort...")
            run_git_command('rebase --abort', check=False)
            logger.error("Failed to pull and rebase. Aborting push.")
            sys.exit(1)
        
        # Push
        logger.info(f"Pushing to {branch}...")
        run_git_command(f'push origin {branch}')
        logger.info(f"✓ Successfully pushed to {branch}")
        
    except RuntimeError as e:
        logger.error(f"Git operation failed: {e}")
        sys.exit(1)
