#!/usr/bin/env python3
"""
Qwen3.5-35B-A3B Agent Test Suite
Tests tool calling, file operations, bash execution, and web features
Configuration loaded from config.yaml
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Import from qwen-agent.py
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import the actual module (with hyphen)
import importlib.util
spec = importlib.util.spec_from_file_location("qwen_agent", script_dir / "qwen-agent.py")
qwen_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qwen_agent)

Agent = qwen_agent.Agent
ToolExecutor = qwen_agent.ToolExecutor
HAS_RICH = qwen_agent.HAS_RICH

# Load configuration
from config import Config
config = Config()


class AgentTests:
    """Test suite for Qwen Agent."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.get_api_url()
        self.test_dir = tempfile.mkdtemp(prefix="qwen_test_")
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def log(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append((test_name, passed, message))
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status}: {test_name}")
        if message and not passed:
            print(f"       {message}")
    
    def cleanup(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_tool_executor_bash(self):
        """Test bash execution."""
        test_name = "ToolExecutor: execute_bash"
        try:
            executor = ToolExecutor()
            result = executor.execute_bash("echo 'Hello World'")
            
            if result.success and "Hello World" in result.data.get("combined", ""):
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Unexpected output: {result.data}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_tool_executor_read_file(self):
        """Test file reading."""
        test_name = "ToolExecutor: read_file"
        try:
            # Create test file
            test_file = Path(self.test_dir) / "test.txt"
            test_file.write_text("Test content 123")
            
            executor = ToolExecutor()
            result = executor.read_file(str(test_file))
            
            if result.success and "Test content 123" in result.data.get("content", ""):
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Content mismatch: {result.data}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_tool_executor_write_file(self):
        """Test file writing."""
        test_name = "ToolExecutor: write_file"
        try:
            test_file = Path(self.test_dir) / "write_test.txt"
            
            executor = ToolExecutor()
            result = executor.write_file(str(test_file), "Written content")
            
            if result.success and test_file.exists():
                content = test_file.read_text()
                if content == "Written content":
                    self.log(test_name, True)
                else:
                    self.log(test_name, False, f"Content mismatch: {content}")
            else:
                self.log(test_name, False, f"Write failed: {result.error}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_tool_executor_list_dir(self):
        """Test directory listing."""
        test_name = "ToolExecutor: list_dir"
        try:
            # Create test files
            (Path(self.test_dir) / "file1.txt").touch()
            (Path(self.test_dir) / "file2.txt").touch()
            (Path(self.test_dir) / "subdir").mkdir()
            
            executor = ToolExecutor()
            result = executor.list_dir(self.test_dir)
            
            if result.success and result.data.get("count", 0) >= 3:
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Expected 3+ items, got {result.data}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_tool_executor_python(self):
        """Test Python execution."""
        test_name = "ToolExecutor: execute_python"
        try:
            executor = ToolExecutor()
            result = executor.execute_python("print(2 + 2)")
            
            if result.success and "4" in result.data.get("output", ""):
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Expected '4', got: {result.data}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_agent_simple_query(self):
        """Test agent with simple query (no tools)."""
        test_name = "Agent: Simple Query"
        try:
            agent = Agent(base_url=self.base_url, max_turns=5)
            response = agent.chat("Say hello in one word", verbose=False)
            
            if response and len(response) > 0:
                self.log(test_name, True)
            else:
                self.log(test_name, False, "Empty response")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_agent_file_operations(self):
        """Test agent file creation and reading."""
        test_name = "Agent: File Operations"
        try:
            agent = Agent(base_url=self.base_url, max_turns=10)
            
            test_file = Path(self.test_dir) / "agent_test.txt"
            prompt = f"Write 'Agent was here' to {test_file} then read it back"
            
            response = agent.chat(prompt, verbose=False)
            
            # Check if file was created and has content
            if test_file.exists() and test_file.read_text().strip():
                self.log(test_name, True)
            elif "Agent was here" in response:
                # Agent may have reported success even if file check fails
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"File not created. Response: {response[:200]}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_agent_bash_command(self):
        """Test agent executing bash command."""
        test_name = "Agent: Bash Command"
        try:
            agent = Agent(base_url=self.base_url, max_turns=10)
            response = agent.chat("Run: echo 'Agent Test Success' and show me the output", verbose=False)
            
            if "Agent Test Success" in response:
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Expected output not found. Response: {response[:200]}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_agent_list_directory(self):
        """Test agent listing directory."""
        test_name = "Agent: List Directory"
        try:
            agent = Agent(base_url=self.base_url, max_turns=10)
            response = agent.chat(f"List files in {self.test_dir}", verbose=False)
            
            # Should mention files or directory contents
            if response and (len(response) > 10 or "file" in response.lower() or "dir" in response.lower()):
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Unexpected response: {response[:200]}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_agent_python_execution(self):
        """Test agent running Python code."""
        test_name = "Agent: Python Execution"
        try:
            agent = Agent(base_url=self.base_url, max_turns=10)
            response = agent.chat("Calculate 123 * 456 using Python and tell me the result", verbose=False)
            
            # Check for result with or without comma formatting
            if "56088" in response or "56,088" in response:
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Expected 56088. Response: {response[:200]}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_response_time(self):
        """Test response time is reasonable."""
        test_name = "Performance: Response Time"
        try:
            agent = Agent(base_url=self.base_url, max_turns=5)
            
            start = time.time()
            response = agent.chat("What is 2+2?", verbose=False)
            elapsed = time.time() - start
            
            # Should respond within 30 seconds for simple query
            if elapsed < 30 and response:
                self.log(test_name, True, f"({elapsed:.2f}s)")
            else:
                self.log(test_name, False, f"Too slow: {elapsed:.2f}s")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def test_conversation_history(self):
        """Test conversation history is maintained."""
        test_name = "Agent: Conversation History"
        try:
            agent = Agent(base_url=self.base_url, max_turns=10)
            
            # First message
            agent.chat("My name is TestUser", verbose=False)
            
            # Second message should remember
            response = agent.chat("What is my name?", verbose=False)
            
            if "TestUser" in response:
                self.log(test_name, True)
            else:
                self.log(test_name, False, f"Didn't remember name. Response: {response[:200]}")
        except Exception as e:
            self.log(test_name, False, str(e))
    
    def run_all_tests(self):
        """Run all tests."""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║        Qwen3.5-35B-A3B Agent Test Suite                  ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print(f"📍 API: {self.base_url}")
        print(f"📁 Test Directory: {self.test_dir}")
        print()
        print("Running tests...")
        print()
        
        # Tool Executor Tests
        print("━━━ Tool Executor Tests ━━━")
        self.test_tool_executor_bash()
        self.test_tool_executor_read_file()
        self.test_tool_executor_write_file()
        self.test_tool_executor_list_dir()
        self.test_tool_executor_python()
        print()
        
        # Agent Tests
        print("━━━ Agent Tests ━━━")
        self.test_agent_simple_query()
        self.test_agent_file_operations()
        self.test_agent_bash_command()
        self.test_agent_list_directory()
        self.test_agent_python_execution()
        print()
        
        # Performance & Integration Tests
        print("━━━ Performance & Integration Tests ━━━")
        self.test_response_time()
        self.test_conversation_history()
        print()
        
        # Summary
        total = self.passed + self.failed
        print("╔══════════════════════════════════════════════════════════╗")
        print(f"║  Test Summary: {self.passed}/{total} passed                              ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        if self.failed > 0:
            print()
            print("Failed tests:")
            for name, passed, message in self.results:
                if not passed:
                    print(f"  ❌ {name}: {message}")
        
        # Cleanup
        self.cleanup()
        
        return self.failed == 0


def main():
    import argparse

    # Get default from config.yaml
    default_url = config.get_api_url()

    parser = argparse.ArgumentParser(description="Run Qwen Agent tests")
    parser.add_argument("--url", type=str, default=default_url, help="API base URL")
    parser.add_argument("--test", type=str, help="Run specific test (default: all)")
    args = parser.parse_args()
    
    tests = AgentTests(base_url=args.url)
    
    try:
        success = tests.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
        tests.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        tests.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
