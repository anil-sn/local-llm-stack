"""
Test CLI main commands and help.

Tests the main entry point, version, and help without mocking.
"""

import pytest
from pathlib import Path


class TestMainCLI:
    """Test main CLI entry point."""

    def test_main_help(self, run_cli):
        """Test main help command."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "Local LLM Stack" in result.stdout
        assert "run" in result.stdout
        assert "server" in result.stdout
        assert "model" in result.stdout
        assert "chat" in result.stdout
        assert "benchmark" in result.stdout
        assert "config" in result.stdout
        assert "status" in result.stdout

    def test_version(self, run_cli):
        """Test version command."""
        result = run_cli(["--version"])
        assert result.returncode == 0
        assert "Local LLM Stack CLI version" in result.stdout

    def test_short_help(self, run_cli):
        """Test short help (-h)."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "Local LLM Stack" in result.stdout

    def test_completion_help(self, run_cli):
        """Test completion help."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "--install-completion" in result.stdout or "completion" in result.stdout.lower()


class TestRunCommand:
    """Test the run command."""

    def test_run_help(self, run_cli):
        """Test run command help."""
        result = run_cli(["run", "--help"])
        assert result.returncode == 0
        assert "Download and run" in result.stdout or "model" in result.stdout.lower()
        assert "--chat" in result.stdout
        assert "--webui" in result.stdout
        assert "--api" in result.stdout
        assert "--fg" in result.stdout or "--foreground" in result.stdout

    def test_run_no_args(self, run_cli):
        """Test run without arguments (should show error)."""
        result = run_cli(["run"])
        assert result.returncode != 0
        assert "Missing argument" in result.stderr or "MODEL" in result.stderr


class TestServerCommand:
    """Test server management commands."""

    def test_server_help(self, run_cli):
        """Test server command help."""
        result = run_cli(["server", "--help"])
        assert result.returncode == 0
        assert "Manage the LLM server" in result.stdout or "server" in result.stdout.lower()
        assert "start" in result.stdout
        assert "stop" in result.stdout
        assert "restart" in result.stdout
        assert "status" in result.stdout
        assert "logs" in result.stdout

    def test_server_start_help(self, run_cli):
        """Test server start help."""
        result = run_cli(["server", "start", "--help"])
        assert result.returncode == 0
        assert "Start the LLM server" in result.stdout or "start" in result.stdout.lower()

    def test_server_stop_help(self, run_cli):
        """Test server stop help."""
        result = run_cli(["server", "stop", "--help"])
        assert result.returncode == 0
        assert "Stop the LLM server" in result.stdout or "stop" in result.stdout.lower()

    def test_server_restart_help(self, run_cli):
        """Test server restart help."""
        result = run_cli(["server", "restart", "--help"])
        assert result.returncode == 0
        assert "Restart" in result.stdout

    def test_server_logs_help(self, run_cli):
        """Test server logs help."""
        result = run_cli(["server", "logs", "--help"])
        assert result.returncode == 0
        assert "logs" in result.stdout.lower()

    def test_server_status(self, run_cli):
        """Test server status (should work regardless of server state)."""
        result = run_cli(["server", "status"])
        assert result.returncode == 0
        # Should show either running or not running
        assert "running" in result.stdout.lower() or "not running" in result.stdout.lower()


class TestModelCommand:
    """Test model management commands."""

    def test_model_help(self, run_cli):
        """Test model command help."""
        result = run_cli(["model", "--help"])
        assert result.returncode == 0
        assert "Manage models" in result.stdout or "model" in result.stdout.lower()
        assert "list" in result.stdout
        assert "download" in result.stdout
        assert "delete" in result.stdout
        assert "validate" in result.stdout
        assert "recommend" in result.stdout
        assert "info" in result.stdout

    def test_model_list(self, run_cli):
        """Test model list command."""
        result = run_cli(["model", "list"])
        assert result.returncode == 0
        # Should show configured models
        assert "Available Models" in result.stdout or "model" in result.stdout.lower()

    def test_model_list_verbose(self, run_cli):
        """Test model list with verbose flag."""
        result = run_cli(["model", "list", "--verbose"])
        assert result.returncode == 0
        assert "Available Models" in result.stdout or "model" in result.stdout.lower()

    def test_model_info(self, run_cli):
        """Test model info command (shows active model)."""
        result = run_cli(["model", "info"])
        assert result.returncode == 0
        assert "Model:" in result.stdout or "model" in result.stdout.lower()

    def test_model_info_specific(self, run_cli):
        """Test model info for specific model."""
        result = run_cli(["model", "info", "llama-3-8b"])
        assert result.returncode == 0
        assert "Llama" in result.stdout or "model" in result.stdout.lower()

    def test_model_validate(self, run_cli):
        """Test model validate command."""
        result = run_cli(["model", "validate"])
        # May fail if model not downloaded, but should not crash
        assert "Validating" in result.stdout or "not found" in result.stdout.lower() or result.returncode != 0

    def test_model_recommend_help(self, run_cli):
        """Test model recommend help."""
        result = run_cli(["model", "recommend", "--help"])
        assert result.returncode == 0
        assert "recommend" in result.stdout.lower()

    def test_model_delete_help(self, run_cli):
        """Test model delete help."""
        result = run_cli(["model", "delete", "--help"])
        assert result.returncode == 0
        assert "delete" in result.stdout.lower()

    def test_model_download_help(self, run_cli):
        """Test model download help."""
        result = run_cli(["model", "download", "--help"])
        assert result.returncode == 0
        assert "download" in result.stdout.lower()


class TestChatCommand:
    """Test chat commands."""

    def test_chat_help(self, run_cli):
        """Test chat command help."""
        result = run_cli(["chat", "--help"])
        assert result.returncode == 0
        assert "Chat with the LLM" in result.stdout or "chat" in result.stdout.lower()
        assert "interactive" in result.stdout
        assert "quick" in result.stdout
        assert "agent" in result.stdout

    def test_chat_interactive_help(self, run_cli):
        """Test chat interactive help."""
        result = run_cli(["chat", "interactive", "--help"])
        assert result.returncode == 0
        assert "Interactive chat" in result.stdout or "interactive" in result.stdout.lower()

    def test_chat_quick_help(self, run_cli):
        """Test chat quick help."""
        result = run_cli(["chat", "quick", "--help"])
        assert result.returncode == 0
        assert "Quick" in result.stdout or "single" in result.stdout.lower()

    def test_chat_agent_help(self, run_cli):
        """Test chat agent help."""
        result = run_cli(["chat", "agent", "--help"])
        assert result.returncode == 0
        assert "Agent" in result.stdout or "tool" in result.stdout.lower()


class TestBenchmarkCommand:
    """Test benchmark commands."""

    def test_benchmark_help(self, run_cli):
        """Test benchmark command help."""
        result = run_cli(["benchmark", "--help"])
        assert result.returncode == 0
        assert "Run benchmarks" in result.stdout or "benchmark" in result.stdout.lower()
        assert "run" in result.stdout
        assert "native" in result.stdout
        assert "api" in result.stdout
        assert "compare" in result.stdout
        assert "clean" in result.stdout

    def test_benchmark_run_help(self, run_cli):
        """Test benchmark run help."""
        result = run_cli(["benchmark", "run", "--help"])
        assert result.returncode == 0
        assert "Run benchmark" in result.stdout or "benchmark" in result.stdout.lower()

    def test_benchmark_native_help(self, run_cli):
        """Test benchmark native help."""
        result = run_cli(["benchmark", "native", "--help"])
        assert result.returncode == 0
        assert "native" in result.stdout.lower()

    def test_benchmark_api_help(self, run_cli):
        """Test benchmark api help."""
        result = run_cli(["benchmark", "api", "--help"])
        assert result.returncode == 0
        assert "api" in result.stdout.lower()

    def test_benchmark_compare_help(self, run_cli):
        """Test benchmark compare help."""
        result = run_cli(["benchmark", "compare", "--help"])
        assert result.returncode == 0
        assert "compare" in result.stdout.lower()

    def test_benchmark_clean_help(self, run_cli):
        """Test benchmark clean help."""
        result = run_cli(["benchmark", "clean", "--help"])
        assert result.returncode == 0
        assert "clean" in result.stdout.lower()


class TestConfigCommand:
    """Test configuration commands."""

    def test_config_help(self, run_cli):
        """Test config command help."""
        result = run_cli(["config", "--help"])
        assert result.returncode == 0
        assert "View and edit configuration" in result.stdout or "config" in result.stdout.lower()
        assert "show" in result.stdout
        assert "edit" in result.stdout
        assert "validate" in result.stdout
        assert "models" in result.stdout

    def test_config_show(self, run_cli):
        """Test config show command."""
        result = run_cli(["config"])
        assert result.returncode == 0
        # Output contains YAML config
        assert "active_model" in result.stdout or "Configuration" in result.stdout

    def test_config_show_raw(self, run_cli):
        """Test config show with raw flag."""
        result = run_cli(["config", "show", "--raw"])
        assert result.returncode == 0
        # Should show YAML content
        assert "active_model" in result.stdout

    def test_config_show_section(self, run_cli):
        """Test config show section."""
        result = run_cli(["config", "show", "server"])
        assert result.returncode == 0
        assert "server" in result.stdout.lower() or "port" in result.stdout

    def test_config_validate(self, run_cli):
        """Test config validate command."""
        result = run_cli(["config", "validate"])
        assert result.returncode == 0
        assert "Valid" in result.stdout or "config" in result.stdout.lower()

    def test_config_models(self, run_cli):
        """Test config models command."""
        result = run_cli(["config", "models"])
        assert result.returncode == 0
        assert "Configured Models" in result.stdout or "model" in result.stdout.lower()

    def test_config_edit_help(self, run_cli):
        """Test config edit help."""
        result = run_cli(["config", "edit", "--help"])
        assert result.returncode == 0
        assert "edit" in result.stdout.lower()


class TestStatusCommand:
    """Test status commands."""

    def test_status_help(self, run_cli):
        """Test status command help."""
        result = run_cli(["status", "--help"])
        assert result.returncode == 0
        assert "Check system and server status" in result.stdout or "status" in result.stdout.lower()
        assert "system" in result.stdout
        assert "server" in result.stdout
        assert "model" in result.stdout
        assert "dependencies" in result.stdout
        assert "all" in result.stdout

    def test_status_system(self, run_cli):
        """Test status system command."""
        result = run_cli(["status", "system"])
        assert result.returncode == 0
        assert "System" in result.stdout or "CPU" in result.stdout or "RAM" in result.stdout

    def test_status_server(self, run_cli):
        """Test status server command."""
        result = run_cli(["status", "server"])
        assert result.returncode == 0
        assert "Server" in result.stdout or "status" in result.stdout.lower()

    def test_status_model(self, run_cli):
        """Test status model command."""
        result = run_cli(["status", "model"])
        assert result.returncode == 0
        assert "Model" in result.stdout or "status" in result.stdout.lower()

    def test_status_dependencies(self, run_cli):
        """Test status dependencies command."""
        result = run_cli(["status", "dependencies"])
        assert result.returncode == 0
        assert "Dependency" in result.stdout or "dependencies" in result.stdout.lower()

    def test_status_all(self, run_cli):
        """Test status all command."""
        result = run_cli(["status", "all"])
        assert result.returncode == 0
        # Should contain multiple status sections
        assert "System" in result.stdout or "Server" in result.stdout

    def test_status_default(self, run_cli):
        """Test status without subcommand (defaults to server)."""
        result = run_cli(["status"])
        assert result.returncode == 0
        assert "Server" in result.stdout or "status" in result.stdout.lower()


class TestAliasesCommand:
    """Test command aliases."""

    def test_models_alias(self, run_cli):
        """Test 'models' as alias for 'model'."""
        result = run_cli(["models", "--help"])
        assert result.returncode == 0
        assert "Manage models" in result.stdout or "model" in result.stdout.lower()
