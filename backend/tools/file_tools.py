"""
File system operation tools for agents.
"""

import os
from typing import Optional
from langchain.tools import Tool
from pathlib import Path


class FileReadTool:
    """
    Read files from the file system.
    """
    
    def read_file(self, file_path: str, max_lines: Optional[int] = None) -> str:
        """
        Read content from a file.
        
        Args:
            file_path: Path to file to read
            max_lines: Maximum number of lines to read
            
        Returns:
            File content
        """
        try:
            # Security: Only allow reading from specific directories
            safe_base = Path("./workspace")
            file_path = safe_base / file_path
            
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if max_lines:
                    lines = [next(f) for _ in range(max_lines)]
                    content = ''.join(lines)
                    content += f"\n... (showing first {max_lines} lines)"
                else:
                    content = f.read()
            
            return f"Content of {file_path}:\n\n{content}"
            
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="read_file",
            description="Read content from a file. Use when you need to access file contents for analysis or processing.",
            func=self.read_file
        )


class FileWriteTool:
    """
    Write files to the file system.
    """
    
    def write_file(self, file_path: str, content: str, mode: str = "w") -> str:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file to write
            content: Content to write
            mode: Write mode ('w' for write, 'a' for append)
            
        Returns:
            Write status
        """
        try:
            # Security: Only allow writing to specific directories
            safe_base = Path("./workspace")
            safe_base.mkdir(exist_ok=True)
            file_path = safe_base / file_path
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return f"✓ Successfully wrote {len(content)} characters to {file_path}"
            
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="write_file",
            description="Write content to a file. Use when you need to save generated content, reports, or data.",
            func=lambda x: self.write_file(**eval(x))
        )


class FileSearchTool:
    """
    Search for files in the file system.
    """
    
    def search_files(self, pattern: str, directory: str = "./workspace") -> str:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: File name pattern (supports wildcards)
            directory: Directory to search in
            
        Returns:
            List of matching files
        """
        try:
            base_path = Path(directory)
            
            if not base_path.exists():
                base_path.mkdir(parents=True, exist_ok=True)
                return f"No files found (directory was empty)"
            
            # Search for matching files
            matches = list(base_path.rglob(pattern))
            
            if not matches:
                return f"No files found matching pattern: {pattern}"
            
            result = f"Found {len(matches)} file(s) matching '{pattern}':\n\n"
            for match in matches[:20]:  # Limit to 20 results
                size = match.stat().st_size if match.is_file() else 0
                result += f"- {match.relative_to(base_path)} ({size} bytes)\n"
            
            if len(matches) > 20:
                result += f"\n... and {len(matches) - 20} more files"
            
            return result
            
        except Exception as e:
            return f"Error searching files: {str(e)}"
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="search_files",
            description="Search for files by name pattern. Supports wildcards like *.pdf or report*.xlsx.",
            func=lambda x: self.search_files(**eval(x)) if isinstance(x, str) and x.startswith('{') else self.search_files(x)
        )
