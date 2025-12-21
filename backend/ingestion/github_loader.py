"""
GitHub Repository Loader
Handles cloning and loading files from GitHub repositories.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import git
from git import Repo
from backend.utils import get_logger

logger = get_logger(__name__)


class GitHubLoader:
    """Load and manage GitHub repositories."""
    
    def __init__(self, local_path: Optional[Path] = None):
        """
        Initialize GitHub loader.
        
        Args:
            local_path: Base directory for cloning repos. 
                       Defaults to data/repositories
        """
        if local_path is None:
            from config.settings import settings
            local_path = settings.repositories_path
        
        self.local_path = Path(local_path)
        self.local_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"GitHubLoader initialized with path: {self.local_path}")
    
    def clone_repository(
        self, 
        repo_url: str, 
        repo_name: Optional[str] = None,
        branch: str = "main",
        token: Optional[str] = None
    ) -> Path:
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL (https or git format)
            repo_name: Custom name for local directory (auto-detected if None)
            branch: Branch to clone (default: main)
            token: GitHub personal access token for private repos
        
        Returns:
            Path to cloned repository
        
        Raises:
            Exception: If cloning fails
        """
        # Extract repo name from URL if not provided
        if repo_name is None:
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        
        clone_path = self.local_path / repo_name
        
        # Remove existing directory if it exists
        if clone_path.exists():
            logger.warning(f"Repository {repo_name} already exists. Removing...")
            shutil.rmtree(clone_path)
        
        # Add token to URL if provided (for private repos)
        if token and 'github.com' in repo_url:
            if repo_url.startswith('https://'):
                repo_url = repo_url.replace('https://', f'https://{token}@')
        
        try:
            logger.info(f"Cloning repository: {repo_url}")
            logger.info(f"Target path: {clone_path}")
            
            # Clone the repository
            repo = Repo.clone_from(
                repo_url, 
                clone_path,
                branch=branch,
                depth=1  # Shallow clone for faster cloning
            )
            
            logger.info(f"✅ Successfully cloned {repo_name}")
            logger.info(f"   Branch: {branch}")
            logger.info(f"   Commit: {repo.head.commit.hexsha[:8]}")
            
            return clone_path
            
        except git.exc.GitCommandError as e:
            logger.error(f"❌ Failed to clone repository: {e}")
            raise Exception(f"Git clone failed: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during cloning: {e}")
            raise
    
    def pull_latest(self, repo_path: Path) -> bool:
        """
        Pull latest changes from remote repository.
        
        Args:
            repo_path: Path to local repository
        
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            logger.info(f"✅ Pulled latest changes for {repo_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to pull latest changes: {e}")
            return False
    
    def get_commit_history(
        self, 
        repo_path: Path, 
        max_count: int = 100
    ) -> List[Dict]:
        """
        Get commit history from repository.
        
        Args:
            repo_path: Path to local repository
            max_count: Maximum number of commits to retrieve
        
        Returns:
            List of commit information dictionaries
        """
        try:
            repo = Repo(repo_path)
            commits = []
            
            for commit in repo.iter_commits(max_count=max_count):
                commits.append({
                    'hash': commit.hexsha,
                    'author': str(commit.author),
                    'email': commit.author.email,
                    'date': commit.committed_datetime,
                    'message': commit.message.strip(),
                    'files_changed': len(commit.stats.files)
                })
            
            logger.info(f"Retrieved {len(commits)} commits from {repo_path.name}")
            return commits
            
        except Exception as e:
            logger.error(f"❌ Failed to get commit history: {e}")
            return []
    
    def get_file_list(
        self, 
        repo_path: Path,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Get list of files from repository.
        
        Args:
            repo_path: Path to local repository
            extensions: List of file extensions to include (e.g., ['.py', '.js'])
            exclude_dirs: List of directory names to exclude
        
        Returns:
            List of file paths
        """
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.cpp', '.c', '.ts', '.jsx', 
                         '.tsx', '.go', '.rs', '.php', '.rb', '.swift']
        
        if exclude_dirs is None:
            exclude_dirs = [
                '.git', '__pycache__', 'node_modules', 'venv', 'env',
                '.venv', 'dist', 'build', '.pytest_cache', '.idea',
                '.vscode', 'target', 'bin', 'obj'
            ]
        
        files = []
        
        for file_path in repo_path.rglob('*'):
            # Skip if not a file
            if not file_path.is_file():
                continue
            
            # Skip if in excluded directory
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Skip if extension doesn't match
            if file_path.suffix not in extensions:
                continue
            
            files.append(file_path)
        
        logger.info(f"Found {len(files)} files in {repo_path.name}")
        return files
    
    def get_repository_info(self, repo_path: Path) -> Dict:
        """
        Get repository metadata.
        
        Args:
            repo_path: Path to local repository
        
        Returns:
            Dictionary with repository information
        """
        try:
            repo = Repo(repo_path)
            
            info = {
                'name': repo_path.name,
                'path': str(repo_path),
                'branch': repo.active_branch.name,
                'remote_url': repo.remotes.origin.url if repo.remotes else None,
                'last_commit': {
                    'hash': repo.head.commit.hexsha,
                    'author': str(repo.head.commit.author),
                    'date': repo.head.commit.committed_datetime,
                    'message': repo.head.commit.message.strip()
                },
                'total_commits': len(list(repo.iter_commits())),
                'is_dirty': repo.is_dirty()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Failed to get repository info: {e}")
            return {}
    
    def delete_repository(self, repo_path: Path) -> bool:
        """
        Delete a cloned repository.
        
        Args:
            repo_path: Path to repository to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if repo_path.exists():
                shutil.rmtree(repo_path)
                logger.info(f"✅ Deleted repository: {repo_path.name}")
                return True
            else:
                logger.warning(f"Repository not found: {repo_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to delete repository: {e}")
            return False
