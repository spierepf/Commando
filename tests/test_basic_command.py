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
def basic_command_runner():
    return CommandRunner()

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
def sudo_command_runner(basic_command_runner, password):
    return SudoCommandRunner(password, basic_command_runner)

@pytest.fixture
def ssh_command_runner(basic_command_runner, hostname,username, password):
    return SshCommandRunner(hostname, username, password, basic_command_runner)

@pytest.fixture
def nested_command_runner(sudo_command_runner, hostname, username, password):
    return SshCommandRunner(hostname, username, password, sudo_command_runner)

@pytest.mark.parametrize('command, exitstatus', [('true', 0), ('false', 1)])
def test_command_runner_exitstatus(basic_command_runner, command, exitstatus):
    spawn = basic_command_runner.run(command)
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.exitstatus == exitstatus


def test_command_runner_before(basic_command_runner):
    text = random_string()
    spawn = basic_command_runner.run(f"echo {text}")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


def test_command_runner_with_pipe(basic_command_runner):
    text = random_string()
    spawn = basic_command_runner.run(f"echo {text} | cat -")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


@pytest.mark.parametrize('command, exitstatus', [('true', 0), ('false', 1)])
def test_sudo_command_runner_exitstatus(sudo_command_runner, command, exitstatus):
    spawn = sudo_command_runner.run(command)
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.exitstatus == exitstatus


def test_sudo_command_runner_before(sudo_command_runner):
    text = random_string()
    spawn = sudo_command_runner.run(f"echo {text}")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


def test_sudo_command_runner_with_pipe(sudo_command_runner):
    text = random_string()
    spawn = sudo_command_runner.run(f"echo {text} | cat -")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


@pytest.mark.parametrize('command, exitstatus', [('true', 0), ('false', 1)])
def test_ssh_command_runner_exitstatus(ssh_command_runner, command, exitstatus):
    spawn = ssh_command_runner.run(command)
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.exitstatus == exitstatus


def test_ssh_command_runner_before(ssh_command_runner):
    text = random_string()
    spawn = ssh_command_runner.run(f"echo {text}")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


def test_ssh_command_runner_with_pipe(ssh_command_runner):
    text = random_string()
    spawn = ssh_command_runner.run(f"echo {text} | cat -")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


@pytest.mark.parametrize('command, exitstatus', [('true', 0), ('false', 1)])
def test_nested_command_runner_exitstatus(nested_command_runner, command, exitstatus):
    spawn = nested_command_runner.run(command)
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.exitstatus == exitstatus


def test_nested_command_runner_before(nested_command_runner):
    text = random_string()
    spawn = nested_command_runner.run(f"echo {text}")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text


def test_nested_command_runner_with_pipe(nested_command_runner):
    text = random_string()
    spawn = nested_command_runner.run(f"echo {text} | cat -")
    spawn.expect(pexpect.EOF)
    spawn.close()

    assert spawn.before.strip() == text

