from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from app.cli import app
import os

runner = CliRunner()

def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CIPAM Translation Tool" in result.stdout

@patch("app.cli.Pipeline")
@patch("app.cli.os.path.exists")
def test_translate_command(mock_exists, mock_pipeline_cls):
    mock_exists.return_value = True
    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run.return_value = "output/input_hindi.txt"

    result = runner.invoke(app, ["translate", "input.txt", "--to", "hindi"])

    assert result.exit_code == 0
    mock_pipeline.run.assert_called_once_with("input.txt", "hindi", "txt")

@patch("app.cli.os.path.exists")
def test_translate_invalid_language(mock_exists):
    mock_exists.return_value = True
    result = runner.invoke(app, ["translate", "input.txt", "--to", "french"])
    assert result.exit_code == 1
    assert "Unsupported target language" in result.stdout

@patch("app.cli.os.path.exists")
def test_translate_unsupported_extension(mock_exists):
    mock_exists.return_value = True
    result = runner.invoke(app, ["translate", "input.csv", "--to", "hindi"])
    assert result.exit_code == 1
    assert "Unsupported file type" in result.stdout

@patch("app.cli.Prompt.ask")
@patch("app.cli.IntPrompt.ask")
@patch("app.cli.os.path.exists")
@patch("app.cli.Pipeline")
def test_interactive_main(mock_pipeline_cls, mock_exists, mock_int, mock_prompt):
    mock_prompt.return_value = "input.txt"
    mock_exists.return_value = True
    mock_int.side_effect = [1, 1]  # 1 for Hindi, 1 for TXT
    mock_pipeline = mock_pipeline_cls.return_value

    result = runner.invoke(app)
    assert result.exit_code == 0
    mock_pipeline.run.assert_called_once_with("input.txt", "hindi", "txt")
