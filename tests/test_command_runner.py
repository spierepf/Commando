import os
import random
import string

from load_dotenv import load_dotenv
import pexpect
import pytest

from commando import CommandRunner, SudoCommandRunner, SshCommandRunner


def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


@pytest.fixture
def hostname():
    return "localhost"

@pytest.fixture
def username():
    return os.getenv("USER")

@pytest.fixture
def password():
    load_dotenv()
    return os.getenv("PASSWORD")


@pytest.fixture
def command_runner():
    return CommandRunner()

@pytest.fixture
def sudo_command_runner(command_runner, password):
    return SudoCommandRunner(password, command_runner)

@pytest.fixture
def ssh_command_runner(command_runner, hostname, username, password):
    return SshCommandRunner(hostname, username, password, command_runner)

@pytest.fixture
def nested_command_runner(ssh_command_runner, hostname, username, password):
    return SudoCommandRunner(password, ssh_command_runner)

def evaluate_exitstatus(runner: CommandRunner, command: str, exitstatus: int):
    spawn = runner.run(command)
    spawn.expect(pexpect.EOF)
    spawn.close()
    assert spawn.exitstatus == exitstatus

def evaluate_before(runner: CommandRunner, command: str):
    text = random_string()
    spawn = runner.run(command.format(text))
    spawn.expect(pexpect.EOF)
    spawn.close()
    assert spawn.before == text


EXITSTATUS_EXAMPLES = [('true', 0), ('false', 1)]

BEFORE_EXAMPLES = [
    'echo -n {}',
    'echo -n {} | cat -',
    'echo -n {} | nc -lN 60000 & sleep 0.1 ; nc localhost 60000 -w1'
]

SUDO_BEFORE_EXAMPLES = BEFORE_EXAMPLES + [
    'echo -n {} | nc -lN 502 & sleep 0.1 ; nc localhost 502 -w1'
]

@pytest.mark.parametrize('command, exitstatus', EXITSTATUS_EXAMPLES)
def test_command_runner_exitstatus(command_runner, command, exitstatus):
    evaluate_exitstatus(command_runner, command, exitstatus)


@pytest.mark.parametrize('command', BEFORE_EXAMPLES)
def test_command_runner_before(command_runner, command):
    evaluate_before(command_runner, command)

@pytest.mark.parametrize('command, exitstatus', EXITSTATUS_EXAMPLES)
def test_ssh_command_runner_exitstatus(ssh_command_runner, command, exitstatus):
    evaluate_exitstatus(ssh_command_runner, command, exitstatus)


@pytest.mark.parametrize('command', BEFORE_EXAMPLES)
def test_ssh_command_runner_before(ssh_command_runner, command):
    evaluate_before(ssh_command_runner, command)

@pytest.mark.parametrize('command, exitstatus', EXITSTATUS_EXAMPLES)
def test_sudo_command_runner_exitstatus(sudo_command_runner, command, exitstatus):
    evaluate_exitstatus(sudo_command_runner, command, exitstatus)


@pytest.mark.parametrize('command', SUDO_BEFORE_EXAMPLES)
def test_sudo_command_runner_before(sudo_command_runner, command):
    evaluate_before(sudo_command_runner, command)

@pytest.mark.parametrize('command, exitstatus', EXITSTATUS_EXAMPLES)
def test_nested_command_runner_exitstatus(nested_command_runner, command, exitstatus):
    evaluate_exitstatus(nested_command_runner, command, exitstatus)


@pytest.mark.parametrize('command', SUDO_BEFORE_EXAMPLES)
def test_nested_command_runner_before(nested_command_runner, command):
    evaluate_before(nested_command_runner, command)
